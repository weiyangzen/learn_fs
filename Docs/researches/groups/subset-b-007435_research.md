# subset-b-007435 Research

Grouped research report for Hadoop HDFS native-client `libhdfs` and `libhdfspp` source files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/include/hdfs/hdfs.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/include/hdfs/hdfs.h

## Purpose
This is the public C ABI for legacy `libhdfs`, a JNI-backed HDFS client facade. It exports opaque filesystem and file handles, scalar typedefs (`tSize`, `tOffset`, `tTime`, `tPort`), file metadata structs, read statistics, hedged-read metrics, builder APIs, stream/open-future APIs, normal filesystem operations, zero-copy read APIs, and thread-local last-exception accessors. It also defines platform export/import macros so the same header can serve Unix shared libraries and Windows DLL clients.

## Important APIs, Control Flow, and State
Callers normally create a `hdfsBuilder`, configure NameNode, port, user, Kerberos ticket cache, and config strings, then call `hdfsBuilderConnect`; older `hdfsConnect*` entry points are deprecated. File access flows through `hdfsOpenFile` or `hdfsStreamBuilderBuild`, then read/write/seek/tell/flush/sync/close. Async open wraps Java `FutureDataInputStreamBuilder` through `hdfsOpenFileBuilder*` and `hdfsOpenFileFuture*`. Metadata paths allocate `hdfsFileInfo`, host arrays, block-size/capacity counters, or zero-copy `hadoopRzBuffer` instances that must be freed through matching functions. Errors are reported by return values plus `errno`; Java exception text is available per calling thread.

## Dependencies and Integration Points
The header depends on C system types and maps onto Hadoop Java `FileSystem`, `Path`, streams, block locations, permissions, and read-statistics classes through the implementation. It is also consumed by `libhdfspp/include/hdfspp/hdfs_ext.h` to keep C bindings compatible with legacy typedefs and file-info layout.

## Risks and Test Signals
This file is ABI-sensitive: struct layout, opaque typedef names, exported symbol names, ownership contracts, and errno semantics affect downstream native clients. Tests should cover builder lifetimes, default/local/URI NameNode handling, config lookup/freeing, read/write EOF and EINTR behavior, stream-builder validation, async open timeout/cancel, file-info allocation/freeing, host-array freeing, zero-copy EOF/freeing, statistics/metrics unsupported filesystems, and per-thread exception strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/include/hdfs/hdfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.c

## Purpose
`jclasses.c` initializes and serves cached JNI `jclass` global references for Java classes frequently used by `libhdfs`. It avoids repeated `FindClass` calls and centralizes the mapping from `CachedJavaClass` enum values to JVM class names.

## Important APIs, Control Flow, and State
The global `cachedJavaClasses` array stores a `jclass` and class-name string per enum entry. `initCachedClasses` is guarded by `jclassInitMutex` and `jclassesInitialized`, populates class-name strings, then loops through all entries calling `initCachedClass`. `initCachedClass` finds a local class, promotes it to a global reference, clears and returns any pending exception, and deletes the local reference. `getJclass` and `getClassName` are simple indexed accessors used by `invokeMethod` and constructor helpers.

## Dependencies and Integration Points
It depends on JNI, `exception.h` for pending-exception handling, `jni_helper.h` for local reference cleanup, and `os/mutexes.h` for cross-platform initialization locking. It must run after a JVM exists and before cached-class method invocation.

## Risks and Test Signals
The cache is process-long and has no eviction or global-ref cleanup, which is intentional but makes startup failures sticky: a missing Java dependency aborts class initialization before setting `jclassesInitialized`. The enum order must match the array use. Tests should verify idempotent concurrent initialization, failure on missing classes, valid global refs after local ref deletion, and all enum values having class names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.h

## Purpose
This header declares the `CachedJavaClass` enum, cache initialization/accessor functions, and string constants for Java and Hadoop class names used by JNI call sites in `libhdfs`.

## Important APIs, Control Flow, and State
`CachedJavaClass` enumerates Hadoop configuration, path, filesystem, stream, status, permission, read-statistics, async-builder, domain-socket, URI, byte-buffer, enum-set, exception-utils, and CompletableFuture classes, with `NUM_CACHED_CLASSES` as the count sentinel. `initCachedClasses(JNIEnv*)` is documented as idempotent and thread-safe; `getJclass` and `getClassName` retrieve the cached global reference and canonical slash-separated class name.

## Dependencies and Integration Points
The header depends on `<jni.h>` and is used by `jclasses.c`, `jni_helper.c`, and libhdfs operation implementations that need cached method calls. Macro constants provide compatibility for older code paths that call `FindClass` directly.

## Risks and Test Signals
Adding an enum requires updating initialization logic and potentially every switch/index consumer. The macro names and enum values are internal but widely shared. Tests should assert `NUM_CACHED_CLASSES` matches initialized entries, all cached classes resolve under the supported Hadoop classpath, and cached and macro class names stay consistent where both exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jclasses.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jni_helper.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jni_helper.c

## Purpose
`jni_helper.c` is the low-level JNI utility layer for `libhdfs`. It converts strings, invokes Java methods and constructors, expands the classpath, creates or attaches to the singleton JVM, initializes cached Java classes, manages thread-local `JNIEnv` state, stores last exception strings, and exposes helpers for object type checks, Hadoop configuration mutation, and enum lookup.

## Important APIs, Control Flow, and State
Method invocation flows through `invokeMethodOnJclass`: resolve method ID, infer return type from signature, call the correct JNI method variant, write into `jvalue`, then return and clear any exception. `findClassAndInvokeMethod` is for uncached/test/bootstrap calls; `invokeMethod` uses `jclasses` global refs. JVM setup is serialized by `jvmMutex`; `getGlobalJNIEnv` checks existing JVMs, builds `-Djava.class.path=` from `CLASSPATH` with `/*` expansion, appends whitespace-split `LIBHDFS_OPTS`, creates the VM if needed, and calls `FileSystem.loadFileSystems`. `getJNIEnv` uses quick TLS when available, otherwise platform TLS, creates `ThreadLocalState`, initializes cached classes, and arranges destructor-based detach. Last exception root cause and stack trace live in per-thread state.

## Dependencies and Integration Points
It integrates with JNI, Hadoop Java classes, `exception.h`, cached classes, platform path separators, directory scanning, mutexes, and platform TLS. Most `libhdfs` operations rely on this helper to translate C calls into Java `FileSystem` and stream calls.

## Risks and Test Signals
Classpath expansion, JVM singleton creation, `LIBHDFS_OPTS` tokenization, varargs method signatures, return-type parsing, local-reference cleanup, and TLS detach are high-risk. The helper does not handle every JNI primitive return type despite defining constants. Tests should cover null/UTF strings, constructor/method success and exception paths, malformed signatures, missing methods, classpath wildcard expansion, absent `CLASSPATH`, repeated calls from many threads, exception string replacement/freeing, enum fetch, and configuration set semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jni_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jni_helper.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jni_helper.h

## Purpose
This header publishes internal JNI helper contracts for string conversion, local-reference cleanup, method/constructor invocation, method ID lookup, object class introspection, JVM environment access, per-thread exception access, Java object type checks, Hadoop `Configuration#set`, and enum instance fetch.

## Important APIs, Control Flow, and State
`MethType` distinguishes static from instance method calls. `invokeMethod` takes a cached class enum and varargs matching the JNI signature; `findClassAndInvokeMethod` resolves a class name first and is documented mainly for bootstrap/tests. `getJNIEnv` creates or retrieves per-thread JNI state and may create the process JVM. `getLastTLSExceptionRootCause`, `getLastTLSExceptionStackTrace`, and `setTLSExceptionStrings` expose `ThreadLocalState` fields owned by the TLS layer.

## Dependencies and Integration Points
It includes `jclasses.h`, `<jni.h>`, stdio, stdlib, stdarg, and errno. The platform path separator macros are shared by classpath expansion in the implementation. Public libhdfs error APIs indirectly depend on the TLS exception functions.

## Risks and Test Signals
Because varargs are unchecked, mismatched signatures can crash or corrupt JNI calls. Returned C strings from `newCStr` are malloc-owned, Java local refs must be deleted by callers, and last-exception pointers are valid only until the next relevant call on the same thread. Tests should validate ownership, static/instance validation, null handling, and thread isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/jni_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/mutexes.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/mutexes.h

## Purpose
`mutexes.h` defines the cross-platform synchronization abstraction used by `libhdfs` during bootstrap. It declares the singleton JVM mutex, Java-class cache initialization mutex, and lock/unlock wrappers.

## Important APIs, Control Flow, and State
The file exposes `extern mutex jvmMutex` and `extern mutex jclassInitMutex`, where `mutex` is provided by the selected platform header. `jvmMutex` protects JVM creation, attachment, and TLS access; `jclassInitMutex` protects idempotent cached class initialization. `mutexLock` and `mutexUnlock` return platform error codes and log failures in implementations.

## Dependencies and Integration Points
The header includes `platform.h`, which resolves to POSIX pthread types or Windows `CRITICAL_SECTION`. It is consumed by `jni_helper.c`, `jclasses.c`, and platform-specific mutex implementations.

## Risks and Test Signals
The comment notes there is no user-called library initialization function, so static initialization is required on every platform. Tests should stress concurrent first calls into `getJNIEnv` and `initCachedClasses`, verify recursive locking where needed by JVM bootstrap, and build both POSIX and Windows implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/mutexes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/mutexes.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/mutexes.c

## Purpose
This POSIX implementation supplies the global `libhdfs` mutexes and lock wrappers using pthreads.

## Important APIs, Control Flow, and State
`jclassInitMutex` uses `PTHREAD_MUTEX_INITIALIZER`. `jvmMutex` is initialized by an ELF constructor function: it initializes `jvmMutexAttr`, sets it to `PTHREAD_MUTEX_RECURSIVE`, and initializes `jvmMutex`. `mutexLock` and `mutexUnlock` call `pthread_mutex_lock` and `pthread_mutex_unlock`, printing errors to stderr and returning the pthread error code.

## Dependencies and Integration Points
It depends on pthreads and `os/mutexes.h`. The recursive JVM mutex matters because JVM/bootstrap paths can re-enter helper code that also needs synchronized TLS or cached-class work.

## Risks and Test Signals
Constructor ordering is the main platform risk; all users assume the mutexes are ready before first libhdfs call. There is no destructor for `jvmMutexAttr`. Tests should compile on supported Unix linkers, verify recursive lock behavior, check concurrent JVM bootstrap, and fail builds where constructor attributes are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/mutexes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/platform.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/platform.h

## Purpose
This POSIX platform header maps `libhdfs` abstract mutex and thread ID types to pthread types and enables GCC-style printf format checking.

## Important APIs, Control Flow, and State
`TYPE_CHECKED_PRINTF_FORMAT(formatArg, varArgs)` expands to `__attribute__((format(printf,...)))`. `mutex` is `pthread_mutex_t`; `threadId` is `pthread_t`. There is no runtime control flow in this header.

## Dependencies and Integration Points
It includes `<pthread.h>` and is indirectly pulled into OS abstraction headers. It influences mutex, thread, and diagnostic function declarations throughout native `libhdfs`.

## Risks and Test Signals
This file is small but compile-portability sensitive. Tests should build with GCC/Clang on Unix-like platforms, verify attribute placement in consumers, and ensure no Windows-only macro assumptions leak into POSIX builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread.c

## Purpose
This file implements the `libhdfs` cross-platform thread abstraction on POSIX using pthreads.

## Important APIs, Control Flow, and State
`runThread` adapts a `threadProcedure(void*)` to the `pthread_create` signature by calling `t->start(t->arg)` and returning `NULL`. `threadCreate` starts the thread and stores the pthread ID in `t->id`; `threadJoin` blocks on `pthread_join`. Both print platform error codes to stderr and return the pthread error code.

## Dependencies and Integration Points
It depends on `os/thread.h`, pthreads, and stdio. Callers must keep the `thread` struct valid until the new thread reads its start function and argument.

## Risks and Test Signals
Lifetime of the `thread` struct passed to `pthread_create` is the main risk. The API does not support detached threads, return values, cancellation, or custom attributes. Tests should cover creation, join, failure propagation, and use under libhdfs async or helper code that depends on this abstraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread_local_storage.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread_local_storage.c

## Purpose
This POSIX TLS implementation stores per-thread `ThreadLocalState` for `libhdfs`, including the thread's `JNIEnv*` and last Java exception strings, and detaches native threads from the JVM on thread exit.

## Important APIs, Control Flow, and State
`gTlsKey` is lazily created under `jvmMutex` with `pthread_key_create`, using `hdfsThreadDestructor` as the destructor. `threadLocalStorageCreate` mallocs state and initializes exception fields to null. `threadLocalStorageGet` creates the key if needed and reads `pthread_getspecific`; `threadLocalStorageSet` writes with `pthread_setspecific` and destroys state on failure. `hdfsThreadDestructor` gets the `JavaVM` from `JNIEnv`, detaches the current thread, logs failures with Java thread ID/name if possible, frees exception strings, and frees the state.

## Dependencies and Integration Points
It depends on JNI, pthreads, `exception.h`, and `jni_helper.h`. `getJNIEnv` relies on these routines while holding `jvmMutex`.

## Risks and Test Signals
Destructor behavior is delicate because it calls back into JNI during thread teardown. Tests should cover lazy key creation, repeated get/set, thread-exit detach, exception-string freeing, many concurrent threads, and failure handling when Java thread introspection itself throws.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread.h

## Purpose
`thread.h` defines the platform-neutral thread abstraction for `libhdfs`.

## Important APIs, Control Flow, and State
It declares `threadProcedure` as `void (*)(void *)` and a `thread` struct containing platform `threadId`, start function, and argument pointer. `threadCreate` immediately starts a new thread based on that struct; `threadJoin` waits for completion.

## Dependencies and Integration Points
The header includes `platform.h` for `threadId`, mapping to `pthread_t` on POSIX and `HANDLE` on Windows. Platform implementations adapt the generic callback to `pthread_create` or `CreateThread`.

## Risks and Test Signals
The API leaves ownership and lifetime of the `thread` struct and `arg` to callers. It also omits return values, thread attributes, detaching, and cancellation. Tests should verify basic create/join on all platforms and ensure callers do not pass stack state that can disappear before the new thread starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread_local_storage.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread_local_storage.h

## Purpose
This header defines the cross-platform TLS contract for `libhdfs` per-thread JNI state and optional fast TLS macros.

## Important APIs, Control Flow, and State
When `HAVE_BETTER_TLS` is defined, `THREAD_LOCAL_STORAGE_GET_QUICK` and `THREAD_LOCAL_STORAGE_SET_QUICK` use a static `__thread struct ThreadLocalState *quickTlsEnv` inside the calling function to avoid platform TLS lookup after initialization. `ThreadLocalState` stores `JNIEnv *env`, `lastExceptionStackTrace`, and `lastExceptionRootCause`. The declared API creates state, gets/sets state for the current thread, and destroys state via `hdfsThreadDestructor`.

## Dependencies and Integration Points
It includes `<jni.h>` and is used by `jni_helper.c` plus POSIX/Windows TLS implementations. Public exception accessors depend on the string fields staying valid until replacement or thread teardown.

## Risks and Test Signals
Quick TLS is function-local static TLS, so behavior depends on compiler/linker support and macro expansion sites. The get routine requires external mutual exclusion. Tests should cover builds with and without `HAVE_BETTER_TLS`, per-thread isolation, destructor cleanup, and exception-string lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread_local_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/inttypes.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/inttypes.h

## Purpose
This compatibility header supplies the small subset of `<inttypes.h>` needed by `libhdfs` on Windows.

## Important APIs, Control Flow, and State
It defines `PRId64` and `PRIu64` using MSVC-style `I64d` and `I64u`, and typedefs `uint64_t` as `unsigned __int64`. There is no runtime state or control flow.

## Dependencies and Integration Points
It is included where code expects integer format macros or `uint64_t` but the Windows toolchain lacks a suitable standard header.

## Risks and Test Signals
Modern Windows compilers often provide `<stdint.h>`/`<inttypes.h>`; duplicate typedefs or macro conflicts are possible if include ordering changes. Tests should compile under the supported MSVC versions and verify format strings used with these macros print correct 64-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/inttypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/mutexes.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/mutexes.c

## Purpose
This Windows implementation supplies global `libhdfs` mutexes using `CRITICAL_SECTION`.

## Important APIs, Control Flow, and State
`jvmMutex` and `jclassInitMutex` are global critical sections. Because there is no simple static critical-section initializer, `initializeMutexes` calls `InitializeCriticalSection` for both and is registered as a CRT global initializer through the `.CRT$XCU` section. `mutexLock` and `mutexUnlock` call `EnterCriticalSection` and `LeaveCriticalSection`, returning 0.

## Dependencies and Integration Points
It depends on `<windows.h>` and `os/mutexes.h`. The implementation supports the same bootstrap synchronization used by `jni_helper.c` and `jclasses.c`.

## Risks and Test Signals
Correct CRT initializer retention is the main risk, especially across MSVC versions and static/shared library modes. Unlike POSIX wrappers, lock failures are not reported. Tests should build and load the DLL, call into libhdfs before any explicit initialization, and stress concurrent JVM/bootstrap access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/mutexes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/platform.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/platform.h

## Purpose
This Windows platform header fills Unix/POSIX compatibility gaps and maps `libhdfs` abstract synchronization/thread types to Windows types.

## Important APIs, Control Flow, and State
It defines `O_ACCMODE`, maps `PATH_MAX` to `MAX_PATH`, maps missing `EDQUOT` and `ESTALE` to Winsock constants, disables GCC printf-format checking, and redirects `snprintf`, `strncpy`, `strtok_r`, and `vsnprintf` to secure CRT variants. `mutex` is `CRITICAL_SECTION`; `threadId` is `HANDLE`.

## Dependencies and Integration Points
It includes stdio, Windows, and Winsock headers. It is used by mutex/thread abstraction headers and C code that assumes Unix-like errno and formatting APIs.

## Risks and Test Signals
Macro replacement of standard functions can alter signatures and edge behavior, especially variadic macro calls with empty argument lists. Winsock errno substitutions are approximate. Tests should compile all consumers with MSVC, validate safe truncation behavior, and verify path, errno, and thread/mutex type assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread.c

## Purpose
This file implements the `libhdfs` thread abstraction on Windows using `CreateThread` and wait handles.

## Important APIs, Control Flow, and State
`runThread` adapts the generic `threadProcedure` to the `DWORD WINAPI` signature, calls `t->start(t->arg)`, and returns 0. `threadCreate` calls `CreateThread`, stores the resulting `HANDLE` in `t->id`, and reports `GetLastError` on failure. `threadJoin` waits indefinitely with `WaitForSingleObject`, treating `WAIT_OBJECT_0` as success and logging `WAIT_FAILED` or unexpected waits.

## Dependencies and Integration Points
It depends on `os/thread.h` and Windows APIs. Higher-level code sees the same `threadCreate`/`threadJoin` contract as POSIX.

## Risks and Test Signals
The handle is never closed after join, so repeated use can leak handles unless managed elsewhere. Lifetime of the `thread` struct still matters. Tests should cover successful create/join, failure paths, handle cleanup expectations, and builds under both 32-bit and 64-bit Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread_local_storage.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread_local_storage.c

## Purpose
This Windows TLS implementation stores `ThreadLocalState` and detaches native threads from the JVM when threads or the process detach from the DLL.

## Important APIs, Control Flow, and State
`gTlsIndex` is lazily allocated with `TlsAlloc`. `threadLocalStorageGet` allocates the index if needed, calls `TlsGetValue`, and distinguishes a null value from API failure via `GetLastError`. `threadLocalStorageSet` writes with `TlsSetValue`. `detachCurrentThreadFromJvm` retrieves state, gets the JVM, detaches the current thread, logs failures, frees exception strings, and frees state. A PE TLS callback in `.CRT$XLB` calls detach on `DLL_THREAD_DETACH`, detaches and frees the TLS index on `DLL_PROCESS_DETACH`, and linker pragmas force the TLS directory and callback pointer to be retained.

## Dependencies and Integration Points
It depends on JNI, malloc, Windows APIs, and the platform TLS-callback loader behavior. `jni_helper.c` relies on it for per-thread environment state on Windows.

## Risks and Test Signals
The comments explicitly note a limitation: TLS callbacks may not work for explicit `LoadLibrary` use. The source also calls `detachCurrentThreadFromJvm(state)` in `threadLocalStorageSet` even though the helper is declared without parameters, which is a compile-risk signal for this file. Tests should compile this file on Windows, verify implicit DLL load detach behavior, exercise explicit load/unload if supported, and stress thread creation/destruction with active JNI state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread_local_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/unistd.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/unistd.h

## Purpose
This compatibility header provides the minimal `unistd.h` functionality expected by libhdfs code on Windows.

## Important APIs, Control Flow, and State
It includes `<Windows.h>` and defines `sleep(seconds)` as `Sleep((seconds) * 1000)`. There is no runtime state beyond the delegated Windows sleep call.

## Dependencies and Integration Points
It is included by cross-platform C code that uses Unix `sleep` but must also build on Windows.

## Risks and Test Signals
The macro evaluates `seconds` once but performs multiplication in the argument expression, so large values can overflow the Windows millisecond type. Tests should compile Windows consumers and validate expected sleep duration for small values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindCyrusSASL.cmake -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindCyrusSASL.cmake

## Purpose
This CMake find-module locates a host Cyrus SASL installation for libhdfs++ authentication support.

## Important APIs, Control Flow, and State
It searches for `sasl/sasl.h` and the `sasl2` library, then uses `find_package_handle_standard_args` to set `CYRUS_SASL_FOUND`. It publishes `CYRUS_SASL_INCLUDE_DIR` and `CYRUS_SASL_SHARED_LIB`, and marks both advanced. The comments explain why the project prefers the host installation rather than vendoring SASL: plugin/library version mismatches can produce `SASL_NOMECH`.

## Dependencies and Integration Points
`libhdfspp/CMakeLists.txt` includes this module via `CMAKE_MODULE_PATH`, then prefers Cyrus over GSASL when selecting SASL libraries and compile definitions.

## Risks and Test Signals
The module does not search custom names beyond CMake's normal prefix mechanisms, so `CYRUS_SASL_DIR`/`CMAKE_PREFIX_PATH` setup matters. Tests should configure with present, absent, required, and disabled Cyrus SASL, and verify include/library variables link a real client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindCyrusSASL.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindGSasl.cmake -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindGSasl.cmake

## Purpose
This CMake find-module locates GNU SASL (`gsasl`) as the fallback SASL provider for libhdfs++.

## Important APIs, Control Flow, and State
If `GSASL_INCLUDE_DIR` and `GSASL_LIBRARIES` are already cached, it sets quiet mode. It searches for `gsasl.h` and `gsasl`, invokes `FIND_PACKAGE_HANDLE_STANDARD_ARGS`, and marks the variables advanced. It sets `GSASL_FOUND`, `GSASL_INCLUDE_DIR`, and `GSASL_LIBRARIES`.

## Dependencies and Integration Points
The top-level libhdfs++ CMake file uses this module after Cyrus SASL. If Cyrus is unavailable and GSASL is found, it sets `USE_SASL` and `USE_GSASL` and links `GSASL_LIBRARIES`.

## Risks and Test Signals
The comments mention `GSASL_DEFINITIONS` but the file does not set it. Tests should cover discovery through `GSASL_DIR`/`CMAKE_PREFIX_PATH`, required/disabled package flags, and successful link of SASL-authentication code with only GSASL installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindGSasl.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMakeLists.txt

## Purpose
This is the main CMake build definition for libhdfs++. It configures dependencies, feature checks, optional docs/tests/examples/tools, Hadoop-tree import copying, object-library aggregation, static/shared library targets, and install layout.

## Important APIs, Control Flow, and State
The build requires CMake 3.5, C++17, Boost date_time 1.86, OpenSSL, Protobuf, absl, utf8_range, and threads. It fetches GoogleTest, validates `thread_local`, probes protobuf compiler/library compatibility, and configures valgrind if requested. SASL selection prefers Cyrus, falls back to GSASL, or fails unless `NO_SASL` is set. It defines Asio standalone flags, compiler flags, optional Doxygen target, and a `copy_on_demand` function for importing HDFS/common headers and protos when `HADOOP_BUILD` is true. It adds subdirectories, aggregates object targets into `hdfspp_static` and optionally `hdfspp`, installs headers/libraries, and defines `InstallToBuildDirectory`.

## Dependencies and Integration Points
It integrates Hadoop's `hadoop_add_dual_library` path when building inside Hadoop, otherwise creates standard CMake libraries. It wires third-party `uriparser2`, lib submodules, C bindings, examples, tests, and tools.

## Risks and Test Signals
Build risk is high around dependency versions, absl target names, SASL provider choice, fetched googletest network availability, MSVC shared builds, and imported Hadoop proto/header paths. Tests should run configure/build with `HADOOP_BUILD`, standalone, `HDFSPP_LIBRARY_ONLY`, `NO_SASL`, Cyrus, GSASL, shared/static, Unix, Apple, and MSVC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/doc/Doxyfile.in -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/doc/Doxyfile.in

## Purpose
This is the Doxygen template used by the libhdfs++ CMake `doc` target to generate API documentation.

## Important APIs, Control Flow, and State
It sets UTF-8 encoding, project name `libhdfspp`, output directory `doc`, two-space tab size, markdown support, and STL support. Its `INPUT` begins with `@PROJECT_SOURCE_DIR@/doc/mainpage.dox` and is configured by CMake into the build directory with variable substitution.

## Dependencies and Integration Points
`libhdfspp/CMakeLists.txt` calls `configure_file` and adds a `doc` custom target only when Doxygen is found. The template depends on source-tree documentation and headers being accessible at generation time.

## Risks and Test Signals
Documentation generation can silently omit APIs if `INPUT` paths drift from installed headers or source layout. Tests should configure with Doxygen present, run the `doc` target, and check that public headers such as `hdfspp.h`, `status.h`, and `hdfs_ext.h` appear in generated output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/doc/Doxyfile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/CMakeLists.txt

## Purpose
This CMake file is the examples entry point for libhdfs++, grouping C and C++ example programs.

## Important APIs, Control Flow, and State
It simply calls `add_subdirectory(c)` and `add_subdirectory(cc)`. There is no runtime state; it controls build inclusion when examples are enabled by the top-level CMake file.

## Dependencies and Integration Points
The parent build adds this directory only when `HDFSPP_LIBRARY_ONLY` is not set. Child directories define actual example executables linked against `hdfspp_static`, `tools_common`, x-platform helpers, and uriparser where needed.

## Risks and Test Signals
The file is straightforward, but missing child directories or disabled targets can break example coverage. Tests should configure a full build and verify both C and C++ example targets are generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/CMakeLists.txt

## Purpose
This CMake file groups the C API examples for libhdfs++.

## Important APIs, Control Flow, and State
It adds the `cat` and `connect_cancel` subdirectories. It carries no runtime state and exists to keep the example tree modular.

## Dependencies and Integration Points
It is reached from `examples/CMakeLists.txt` and delegates target creation to each example's CMake file. The child targets use the C extension API declared in `hdfspp/hdfs_ext.h`.

## Risks and Test Signals
Build tests should ensure both child C examples configure and link in full builds, and that `HDFSPP_LIBRARY_ONLY` excludes them through the parent rather than leaving dangling targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/cat/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/cat/CMakeLists.txt

## Purpose
This CMake file builds the C `cat_c` example that reads an HDFS file through the libhdfs++ C binding.

## Important APIs, Control Flow, and State
It defines cache variable `LIBHDFSPP_DIR`, adds include directories for installed libhdfs++ headers and `../../lib`, links against the lib directory, creates `cat_c` from `cat.c`, and links `hdfspp_static` plus `uriparser2`.

## Dependencies and Integration Points
The target depends on installed-style headers, internal helper headers (`common/util_c.h`, x-platform types), the static libhdfs++ library, and uriparser2. It demonstrates how an external-ish C consumer can use `hdfs_ext.h`.

## Risks and Test Signals
Hard-coded relative include `../../lib` and `LIBHDFSPP_DIR` defaulting may fail in unusual build trees. Tests should configure standalone and Hadoop builds, then compile and run `cat_c` against a test cluster or mocked endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/cat/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/cat/cat.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/cat/cat.c

## Purpose
This is a minimal C `cat` implementation over libhdfs++ C bindings. It parses an HDFS URI, connects, opens a file, reads it in 1 MiB chunks with positional reads, writes to stdout, and cleans up.

## Important APIs, Control Flow, and State
`main` requires one URI argument. It rejects non-`hdfs://` schemes, parses with `uri_parse`, configures a `hdfsBuilder` with host/port, connects via `hdfsBuilderConnect`, opens with `hdfsOpenFile`, loops on `hdfsPread` using `read_bytes_count` as offset, then closes file, disconnects filesystem, frees builder and URI, and calls `ShutdownProtobufLibrary_C`. Error paths call `hdfsGetLastError` into a stack buffer.

## Dependencies and Integration Points
It includes `hdfspp/hdfs_ext.h`, uriparser2, C utility cleanup, and x-platform types. It exercises compatibility between legacy `hdfs.h` APIs and libhdfs++ implementation.

## Risks and Test Signals
The example returns without freeing `uri`/builder on some early error paths and calls `hdfsFreeBuilder` after `hdfsBuilderConnect`, which may be unsafe if that connect consumes the builder under the inherited libhdfs contract. Tests should run success, malformed URI, unsupported scheme, connection failure, open failure, read error, close/disconnect failure, and valgrind cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/cat/cat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/CMakeLists.txt

## Purpose
This CMake file builds the C `connect_cancel_c` example demonstrating cancellation of pending libhdfs++ filesystem connection attempts.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, adds installed include/lib directories, creates `connect_cancel_c` from `connect_cancel.c` plus `$<TARGET_OBJECTS:x_platform_obj_c_api>`, links `hdfspp_static` and `uriparser2`, and adds `../../lib` as a private include directory.

## Dependencies and Integration Points
The target needs C bindings, x-platform syscall helpers for signal-safe output, and static libhdfs++. It is part of the C examples subtree.

## Risks and Test Signals
Object-library dependencies and private relative includes are sensitive to target names and build-tree layout. Build tests should verify the target links in full builds and that x-platform C API objects are available before this target is evaluated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/connect_cancel.c -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/connect_cancel.c

## Purpose
This C example demonstrates creating a disconnected libhdfs++ filesystem, connecting it, and canceling a pending connection from a SIGINT handler.

## Important APIs, Control Flow, and State
Global `hdfsFS fs` lets the signal handler call `hdfsCancelPendingConnection`. `main` sets logging level, registers `SIGINT`, requires no arguments, requires `HADOOP_CONF_DIR`, creates a builder from that directory, allocates a filesystem with `hdfsAllocateFileSystem`, connects with `hdfsConnectAllocated`, then disconnects and frees resources. The signal handler uses x-platform direct stdout writes to avoid malloc-heavy stdio/logging in signal context.

## Dependencies and Integration Points
It uses `hdfspp/hdfs_ext.h`, `common/util_c.h`, and x-platform syscall wrappers. It exercises builder-from-directory config loading, two-phase filesystem allocation/connect, cancellation, logging level, and protobuf shutdown.

## Risks and Test Signals
Calling complex library cancellation from a signal handler is inherently risky despite direct-output care. Error paths after `hdfsConnectAllocated` failure do not disconnect an allocated `fs`. Tests should cover missing `HADOOP_CONF_DIR`, allocation failure, successful connect, SIGINT during slow connect, repeated cancellation, and leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/connect_cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/CMakeLists.txt

## Purpose
This CMake file groups C++ libhdfs++ examples.

## Important APIs, Control Flow, and State
It adds `../../tools` as an include directory, then adds subdirectories `cat`, `gendirs`, `find`, and `connect_cancel`. It has no runtime state.

## Dependencies and Integration Points
The examples share `tools_common` helpers for URI parsing and filesystem connection. The parent examples directory includes this file only in non-library-only builds.

## Risks and Test Signals
The relative include path couples examples to the local tools layout. Build tests should verify all child targets configure after tools_common is defined and that disabling examples avoids these dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/cat/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/cat/CMakeLists.txt

## Purpose
This CMake file builds the C++ `cat` example.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, includes installed headers, links installed lib directories, creates executable `cat` from `cat.cc`, and links `tools_common` plus `hdfspp_static`.

## Dependencies and Integration Points
The target uses the C++ public API in `hdfspp/hdfspp.h` and helper functions from the tools tree. It is a basic example target for synchronous file open/read.

## Risks and Test Signals
Target name `cat` can collide with other build targets or system expectations in packaging contexts. Tests should build the example and run it against an HDFS test file, covering missing args, connect failure, open failure, read EOF, and protobuf shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/cat/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/cat/cat.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/cat/cat.cc

## Purpose
This C++ example reads an HDFS file and writes its contents to stdout using the libhdfs++ C++ API.

## Important APIs, Control Flow, and State
`main` requires a single path, parses it with `hdfs::parse_path_or_exit`, connects via `hdfs::doConnect`, opens with `FileSystem::Open`, wraps the raw `FileHandle*` in `std::unique_ptr`, and repeatedly calls `FileHandle::Read` into a static 1 MiB buffer. `Status::InvalidOffset` is treated as EOF; other non-OK statuses are fatal. It calls `google::protobuf::ShutdownProtobufLibrary` before exit.

## Dependencies and Integration Points
It includes `hdfspp/hdfspp.h`, protobuf cleanup, and `tools_common.h`. It demonstrates synchronous `FileSystem` and `FileHandle` ownership patterns: shared filesystem, raw opened handle transferred to RAII.

## Risks and Test Signals
The program passes the original `path` to `Open` rather than a normalized URI path, so accepted input forms depend on `doConnect` and filesystem path expectations. Tests should cover absolute paths, URI-like paths, empty/missing args, EOF handling, short reads, read errors, and handle deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/cat/cat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/CMakeLists.txt

## Purpose
This CMake file builds the C++ `connect_cancel` example.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, includes installed headers, links installed lib directories, creates `connect_cancel` from x-platform object files plus `connect_cancel.cc`, links `hdfspp_static`, and adds `../../lib` privately for internal headers.

## Dependencies and Integration Points
The target exercises `IoService`, `FileSystem::CancelPendingConnect`, configuration loading, and x-platform syscall helpers. It depends on object libraries created elsewhere in the build.

## Risks and Test Signals
The target is sensitive to object-library names and include ordering. Build tests should verify the target links in standalone and Hadoop-tree builds and that x-platform object dependencies are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/connect_cancel.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/connect_cancel.cc

## Purpose
This C++ example demonstrates canceling libhdfs++ filesystem connection attempts from a SIGINT handler while preserving orderly cleanup.

## Important APIs, Control Flow, and State
A global `std::shared_ptr<hdfs::FileSystem> fs` is visible to the signal handler. `main` loads default HDFS configuration into `Options`, creates an `IoService`, starts default workers, constructs `FileSystem::New(service, "", options)`, and calls `ConnectToDefaultFs`. The signal handler writes directly to stdout and calls `fs->CancelPendingConnect`, which should cause pending connect callbacks to complete with cancellation. Cleanup resets `fs`, stops the service, clears optional config, and shuts down protobuf.

## Dependencies and Integration Points
It uses public `hdfspp.h`, internal configuration loader headers, x-platform syscall wrappers, threads/signals, and protobuf cleanup. It models the async runtime lifecycle even though connect is invoked synchronously.

## Risks and Test Signals
The comments acknowledge signal-handler reentrancy hazards. Cancellation from an async signal while C++ objects are mutating is risky. Tests should cover no args, worker initialization failure, missing/default config, connection success/failure, SIGINT during connect, service stop after cancellation, and leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/connect_cancel.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/CMakeLists.txt

## Purpose
This CMake file builds the C++ `find` example.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, includes installed headers, links installed lib directories, creates executable `find` from `find.cc`, and links `tools_common` plus `hdfspp_static`.

## Dependencies and Integration Points
The target uses `FileSystem::Find` in both synchronous and asynchronous modes and common tools helpers for URI parsing and connection setup.

## Risks and Test Signals
The target name `find` can collide with packaging conventions. Tests should compile and run both sync and async modes against known directory trees with wildcard paths and names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/find.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/find.cc

## Purpose
This example implements a parallel-capable HDFS find tool using libhdfs++ synchronous and asynchronous `FileSystem::Find`.

## Important APIs, Control Flow, and State
`SyncFind` calls `fs->Find(path, name, defaultDepth, &results)` and prints `StatInfo::full_path`. `AsyncFind` creates a promise/future, captures status and a found flag, and registers a callback that prints batches, records the first error, resolves the promise on the final batch, and returns whether more results are wanted. `main` parses path, name, and `use_async`, connects with `doConnect(uri, true)`, dispatches sync or async, and shuts down protobuf.

## Dependencies and Integration Points
It uses `hdfspp/hdfspp.h`, `tools_common.h`, `std::future`, and protobuf cleanup. It demonstrates the batched callback contract for `Find`, including the callback's boolean continuation result.

## Risks and Test Signals
`std::stoi` can throw for invalid async flags. Async state is captured by reference and relies on the callback finishing before locals leave, enforced by `future.get`. Tests should cover no results, multiple batches, callback stop behavior, errors after partial results, invalid arguments, wildcard paths/names, and max-depth defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/find.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/CMakeLists.txt

## Purpose
This CMake file builds the C++ `gendirs` example.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, includes installed headers, links installed lib directories, creates executable `gendirs` from `gendirs.cc`, and links `tools_common` plus `hdfspp_static`.

## Dependencies and Integration Points
The target demonstrates asynchronous `FileSystem::Mkdirs` and common tools connection helpers. It is included from the C++ examples group.

## Risks and Test Signals
The example can generate a large number of async calls depending on input fanout/depth, so integration tests should use bounded trees. Build tests should verify target creation and linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/gendirs.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/gendirs.cc

## Purpose
This C++ example asynchronously creates a generated HDFS directory tree with specified depth and fanout.

## Important APIs, Control Flow, and State
`GenerateDirectories` recursively descends until `level == depth`; at leaves it creates a `std::promise<hdfs::Status>`, stores the future in a vector, and calls `fs->Mkdirs(path, 0755, true, handler)`. `main` parses path/depth/fanout, connects through `doConnect(uri, true)`, starts generation at `path + "/"`, waits for every future, reports the first non-OK status by exiting, prints completion, and shuts down protobuf.

## Dependencies and Integration Points
It uses `FileSystem::Mkdirs` async callbacks, futures/promises, URI parsing/connection helpers, and protobuf cleanup.

## Risks and Test Signals
Unbounded fanout/depth can create exponential futures and RPCs; invalid numeric args throw. Path concatenation can produce duplicate slashes. Tests should cover depth 0, fanout 0/1/N, invalid args, creation failure, partial failures, and resource behavior under moderate parallelism.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/gendirs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/block_location.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/block_location.h

## Purpose
This header defines C++ value types for HDFS block-location metadata returned by libhdfs++.

## Important APIs, Control Flow, and State
`DNInfo` stores hostname, IP address, network location, xfer/info/IPC/secure-info ports, with default ports `-1` and simple getters/setters. `BlockLocation` stores corruption flag, length, offset, and a vector of `DNInfo` datanodes. `FileBlockLocation` stores total file length, last-block-complete flag, under-construction flag, and a vector of blocks. All state is in-memory value data with copy-based setters.

## Dependencies and Integration Points
`FileSystem::GetBlockLocations` returns `std::shared_ptr<FileBlockLocation>`, and `hdfs_ext.h` exposes corresponding C structs. Implementations populate these from NameNode block reports.

## Risks and Test Signals
`BlockLocation` and `FileBlockLocation` primitive fields are not initialized by explicit constructors in this header, so users can observe indeterminate values if implementations forget to set them. Tests should cover default construction, complete population, empty block lists, corrupt blocks, under-construction files, and C/C++ conversion fidelity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/block_location.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/config_parser.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/config_parser.h

## Purpose
`ConfigParser` is the public parser facade for Hadoop XML configuration resources used by libhdfs++.

## Important APIs, Control Flow, and State
Constructors accept no path, one path, or a vector of config directories. The class is movable, owns an opaque `impl` through `std::unique_ptr`, and offers `LoadDefaultResources`, resource validation, typed getters for int/string/bool/double/URI, and options conversion through `get_options`/`get_options_or`. Getters return false on missing or uncastable values; `_or` variants return defaults.

## Dependencies and Integration Points
It includes `options.h`, `uri.h`, and `status.h`. Builder-from-directory C APIs and C++ tools use configuration loading to fill `Options`, especially `defaultFS`, HA services, and timeouts.

## Risks and Test Signals
Parsing and type conversion are hidden in the implementation, so API tests should validate missing files, empty directories, malformed XML, duplicate keys, final/default resource precedence, bool/int/double conversion, URI parsing failures, move semantics, and Options extraction for HA services.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/config_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/content_summary.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/content_summary.h

## Purpose
This header defines `ContentSummary`, the C++ representation of HDFS content summary results.

## Important APIs, Control Flow, and State
The struct stores length, file count, directory count, quota, space consumed, space quota, and path. Its constructor initializes defaults in the implementation. `str(bool include_quota)` formats in `hdfs_count` style, while `str_du()` formats in `hdfs_du` style.

## Dependencies and Integration Points
`FileSystem::GetContentSummary` fills this struct for async and sync callers. CLI tools or bindings can use the formatting helpers for Hadoop-compatible output.

## Risks and Test Signals
Formatting compatibility is externally visible. Tests should validate zero/default values, quota-included and quota-omitted output, large 64-bit counts, path handling, and mapping from NameNode proto fields into every member.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/content_summary.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/events.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/events.h

## Purpose
This header defines stable public event names and callback response types for libhdfs++ filesystem and file instrumentation.

## Important APIs, Control Flow, and State
Stable event constants include NameNode connect/read/write, DataNode connect/read/write, failover, empty endpoint, and pre-RPC retry events. `event_response` represents callback outcomes: OK, caught `std::exception`, caught unknown exception, or testing-only injected `Status`. Factory methods create responses and preserve exception text/status. `fs_event_callback` and `file_event_callback` are `std::function` types returning `event_response`.

## Dependencies and Integration Points
`FileSystem::SetFsEventCallback`, `FileHandle::SetFileEventCallback`, and C monitor APIs in `hdfs_ext.h` use these concepts. Internal RPC and reader code emits events.

## Risks and Test Signals
Callback exceptions must not escape worker threads. Stable event-name compatibility matters for monitoring consumers, while private events may appear. Tests should cover callback success, thrown standard and non-standard exceptions, test error injection, failover event values, and C/C++ monitor bridging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/fsinfo.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/fsinfo.h

## Purpose
`FsInfo` represents cluster-level HDFS capacity and block health information returned by libhdfs++.

## Important APIs, Control Flow, and State
The struct stores capacity, used, remaining, under-replicated blocks, corrupt blocks, missing blocks, missing replication-one blocks, and future blocks. Its constructor initializes defaults in the implementation. `str(fs_name)` formats the data in `hdfs_df` style.

## Dependencies and Integration Points
`FileSystem::GetFsStats` returns this type. Tools and C bindings can format or translate it to legacy `hdfsGetCapacity`/`hdfsGetUsed` style outputs.

## Risks and Test Signals
The key risks are 64-bit overflow/formatting and mismatch with Hadoop CLI output. Tests should validate field initialization, proto-to-struct mapping, formatting with nameservice/URI names, and large cluster values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/fsinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfs_ext.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfs_ext.h

## Purpose
`hdfs_ext.h` extends the legacy libhdfs C ABI with libhdfs++-specific functions for errors, cancellation, builder config reads, block locations, logging, event monitors, recursive find, snapshots, and two-phase filesystem connection.

## Important APIs, Control Flow, and State
It includes `hdfs/hdfs.h` for compatible typedefs and redefines `LIBHDFS_EXTERNAL`. Error APIs copy last thread error into a user buffer. Cancellation APIs cover file operations and pending filesystem connects. Builder extensions read strings/ints/longs from loaded config and can create builders from config directories. Block-location structs model file/block/datanode data and require `hdfsFreeBlockLocations`. Logging APIs set a global C hook, copy/free `LogData`, enable/disable components, and set levels. Monitor pre-attach APIs register callbacks for the next filesystem connect or file open on the current thread. Snapshot APIs and `hdfsFind` expose higher-level NameNode calls. `hdfsAllocateFileSystem`, `hdfsConnectAllocated`, and `hdfsCancelPendingConnection` support connect cancellation.

## Dependencies and Integration Points
It bridges C clients to libhdfs++ internals, while preserving legacy libhdfs types. It depends on `hdfspp/log.h` and stable event names matching `events.h`.

## Risks and Test Signals
This is ABI-sensitive and has mixed ownership rules. Callback reentrancy and thread-local monitor registration are high-risk. Tests should cover every allocation/free pair, logging hook concurrency, invalid logging levels/components, event monitor one-shot behavior, snapshot argument validation, find empty/error results, two-phase connect/cancel, and C struct conversion from C++ block locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfs_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfspp.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfspp.h

## Purpose
This is the primary public C++ libhdfs++ API. It declares datanode exclusion rules, file handles, filesystem construction, connection, file IO, metadata, namespace mutation, find, snapshot, event callback, and option inspection contracts.

## Important APIs, Control Flow, and State
`FileHandle` exposes async positional reads, sync positional/current reads, seeking, cancellation, file event callbacks, and byte counters. `FileSystem::New` constructs instances with owned or shared `IoService` plus user/options. Connection can target explicit server/service or `Options::defaultFS`, synchronously or asynchronously, and pending connects can be canceled. Filesystem methods provide async and sync variants for open, preferred block size, replication, times, stat, content summary, fs stats, listing, block locations, mkdirs, delete, rename, permissions, owner, recursive find, and snapshot operations. Listing and find callbacks return a boolean to request more batches.

## Dependencies and Integration Points
It includes all public value/error/config headers and uses `std::function`, `std::memory`, and `IoService`. Implementations integrate with NameNode RPC, DataNode readers, HA/failover, and tools/C bindings.

## Risks and Test Signals
Ownership is critical: raw `FileSystem*`/`FileHandle*`, shared or owned `IoService`, and destructor deadlock warnings for destroying a filesystem from callbacks. Tests should cover sync/async parity, cancellation, callback batching, permission/replication validation, EOF/invalid offset handling, event callbacks, service lifetime, snapshot operations, HA default FS, and destroying objects from safe and unsafe contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfspp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/ioservice.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/ioservice.h

## Purpose
`IoService` is the public async execution abstraction for libhdfs++, wrapping Boost.Asio `io_service` and documenting lifecycle/concurrency constraints.

## Important APIs, Control Flow, and State
Factory methods create raw or shared instances. Worker APIs initialize default or specified thread counts, add workers, and report count. `PostTask`/`PostLambda` enqueue deferred work, `Run` processes tasks, `Stop` stops workers, and `GetRaw` exposes the underlying `boost::asio::io_service` for Asio calls. The header explicitly warns that tasks and dependencies must outlive pending work, callbacks must avoid blocking IO/sleep and long-held locks, exceptions should not escape, and TLS should not be relied on for affinity.

## Dependencies and Integration Points
`FileSystem` can own or share an `IoService`, and nearly all async operations run through it. It depends on Boost.Asio, functional, memory, and `enable_shared_from_this`.

## Risks and Test Signals
Dangling references, blocked worker threads, callback exception handling, and stopped service behavior are central risks. Tests should cover worker counts, posting before/after stop, shared lifetime, exception capture/logging, direct raw Asio use, and async operation completion under concurrent workers. The `DISABLE_CONCURRENT_WORKERS` define should be validated or removed intentionally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/ioservice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/locks.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/locks.h

## Purpose
This header defines pluggable global mutex support for libhdfs++ so applications can coordinate access to non-thread-safe shared libraries, especially GSSAPI/Kerberos.

## Important APIs, Control Flow, and State
`Mutex` is an abstract lock/unlock/string interface that may throw `LockFailure`. `LockGuard` is an RAII wrapper that locks in the constructor and unlocks in the destructor. `LockManager` holds process-global mutex pointers, allows a one-time `InitLocks(Mutex *gssapi)`, exposes `getGssapiMutex`, and has test-only reset/default accessors. Static state includes a state mutex, `_finalized`, `gssapiMtx`, and test default mutex.

## Dependencies and Integration Points
Authentication code uses `LockManager::getGssapiMutex` to serialize GSSAPI calls. Applications embedding libhdfs++ can install their own mutex before constructing any `FileSystem`.

## Risks and Test Signals
One-time initialization order is crucial. Failure to acquire locks must become clean status failures, not deadlocks. Tests should cover default initialization, custom mutex install exactly once, concurrent `InitLocks`, throwing mutexes, RAII unlock on exceptions, and test reset isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/log.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/log.h

## Purpose
This header defines the C-facing log data contract and numeric log levels/components for libhdfs++.

## Important APIs, Control Flow, and State
Log levels range from trace to error. Component masks cover unknown, RPC, block reader, file handle, and filesystem. `LogData` carries component, level, file, line, function, and message-style fields used by C callbacks and copy/free helpers declared in `hdfs_ext.h`.

## Dependencies and Integration Points
The header is wrapped for C linkage where needed and is included by `hdfs_ext.h`. Internal logging code maps C++ log events to this stable C structure and component/level identifiers.

## Risks and Test Signals
The integer constants and struct layout are ABI-sensitive for C consumers. Logging callbacks may be concurrent and callback users do not own the incoming `LogData`. Tests should validate component masks, level filtering, copy/free deep-copy behavior, null/long messages, and callback concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/options.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/options.h

## Purpose
`options.h` defines libhdfs++ client configuration data, including NameNode HA service metadata and operational tunables.

## Important APIs, Control Flow, and State
`NamenodeInfo` stores nameservice, node name, and URI and provides host/port helpers. `Options` stores default filesystem URI, RPC/data timeouts, retry/failover behavior, cache and Kerberos/SASL settings, thread counts, block reader settings, and `services`, a map of nameservices to configured NameNodes. It is a plain configuration carrier populated by configuration parsers/builders and copied into `FileSystem`.

## Dependencies and Integration Points
It depends on `URI`, string, vector, and map. `ConfigParser`, `FileSystem::New`, HA connection logic, RPC retry, and authentication code consume these fields.

## Risks and Test Signals
Defaults and Hadoop XML key mapping are compatibility-sensitive. HA service maps must preserve all endpoints. Tests should validate default construction, `NamenodeInfo` host/port extraction, parser-to-options mapping, timeout units, retry limits, Kerberos/SASL toggles, and copy behavior into filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/statinfo.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/statinfo.h

## Purpose
`StatInfo` represents HDFS file, directory, and symlink metadata returned by libhdfs++.

## Important APIs, Control Flow, and State
The struct includes file type enum values, path, full path, length, permissions, owner, group, modification/access times, symlink target, block replication, block size, file ID, and child count. The constructor initializes defaults in the implementation. `str()` formats in `hdfs_ls` style.

## Dependencies and Integration Points
It is used by `GetFileInfo`, `GetListing`, `Find`, tools like `find`, and C conversions to `hdfsFileInfo`.

## Risks and Test Signals
Metadata formatting, permissions width, time units, and file type mapping must match Hadoop expectations. Tests should cover all file types, empty owner/group, symlinks, directories with child counts, large file IDs/sizes, listing batches, and conversion to legacy C structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/statinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/status.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/status.h

## Purpose
`Status` is libhdfs++'s value-type error carrier for synchronous returns and asynchronous callbacks.

## Important APIs, Control Flow, and State
An OK status has code 0. Factory methods create invalid argument, resource unavailable, unimplemented, server exception, generic error, authentication/authorization failure, canceled, path not found, invalid offset, not-a-directory, and mutex errors. `ok`, `is_invalid_offset`, `pathNotFound`, `code`, `ToString`, `notWorthRetry`, and server exception accessors expose classification. Codes map common cases to `std::errc` values and reserve non-errc codes from 256 for Hadoop/server-specific errors.

## Dependencies and Integration Points
Every libhdfs++ public API uses `Status`. Event responses, config validation, RPC retry/failover logic, C errno translation, and examples all depend on consistent code mapping.

## Risks and Test Signals
Changing codes can break retry decisions and C binding errno mapping. Tests should cover every factory, `ToString`, `notWorthRetry`, server exception class/detail preservation, equality-by-code assumptions if any, and mapping from NameNode Java exceptions such as StandbyException and AccessControlException.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/uri.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/uri.h

## Purpose
`URI` is libhdfs++'s URI parser/builder with encode/decode support for HDFS configuration and user paths.

## Important APIs, Control Flow, and State
`URI::parse_from_string` throws `uri_parse_error` on malformed input. Static `encode`/`decode` transform strings. Accessors and mutators cover scheme, host, optional port, path, path elements, query string, query elements, fragment, and full `str` output, with encoded-input/output flags. `Query` stores key/value pairs. Private helpers track authority, build encoded authority/path, parse paths, and store port as a signed internal field to represent absence.

## Dependencies and Integration Points
`Options::defaultFS`, `NamenodeInfo`, config parsing, tools, and connection logic use `URI`. It likely integrates with uriparser2 internally.

## Risks and Test Signals
Encoding semantics and optional port handling are central. Tests should cover empty URI, scheme-only, host/port, default port fallback, IPv6 if supported, encoded paths, query/fragment round trips, bad percent encodings, path element mutation, and ostream output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/uri.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/CMakeLists.txt

## Purpose
This CMake file defines the libhdfs++ implementation submodule graph.

## Important APIs, Control Flow, and State
It adds subdirectories for `x-platform`, `common`, `fs`, `reader`, `rpc`, `proto`, `connection`, and `bindings`. There is no runtime state; it controls build ordering and target discovery.

## Dependencies and Integration Points
The top-level CMake file later aggregates object libraries from these subdirectories into `hdfspp_static` and `hdfspp`. The bindings directory includes the C binding object target.

## Risks and Test Signals
Removing or reordering subdirectories can break object target availability. Configure tests should verify all expected object libraries are defined and aggregate targets include them exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/CMakeLists.txt

## Purpose
This CMake file groups libhdfs++ language bindings.

## Important APIs, Control Flow, and State
It adds the `c` subdirectory. There is no runtime behavior or persistent state.

## Dependencies and Integration Points
The parent `lib/CMakeLists.txt` includes this directory. The C binding target contributes object files to the main libhdfs++ libraries and provides the C ABI used by `hdfs_ext.h` examples.

## Risks and Test Signals
This is low-risk build plumbing. Tests should verify the C binding target is included in top-level object aggregation and that disabling or moving binding directories fails loudly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/c/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/c/CMakeLists.txt

## Purpose
This CMake file builds the libhdfs++ C binding object library and a standalone binding library target.

## Important APIs, Control Flow, and State
It creates `bindings_c_obj` as an object library from x-platform object files and `hdfs.cc`, then declares dependencies on `fs`, `rpc`, `reader`, `proto`, `common`, and `x_platform_obj`. It also creates `bindings_c` from `bindings_c_obj` and `x_platform_obj`.

## Dependencies and Integration Points
The top-level libhdfs++ library aggregates `bindings_c_obj` into `LIBHDFSPP_ALL_OBJECTS`, making C ABI functions part of the main library. C examples link the static library and include `hdfs_ext.h`.

## Risks and Test Signals
Object-library reuse can duplicate symbols if aggregate targets also include the same x-platform objects independently. The dependency list repeats several targets. Tests should link static and shared libraries, inspect exported C symbols, and build C examples to validate no missing or duplicate objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/c/CMakeLists.txt -->
