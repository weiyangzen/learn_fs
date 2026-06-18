# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread_local_storage.c

## Purpose
This Windows TLS implementation stores `ThreadLocalState` and detaches native threads from the JVM when threads or the process detach from the DLL.

## Important APIs, Control Flow, and State
`gTlsIndex` is lazily allocated with `TlsAlloc`. `threadLocalStorageGet` allocates the index if needed, calls `TlsGetValue`, and distinguishes a null value from API failure via `GetLastError`. `threadLocalStorageSet` writes with `TlsSetValue`. `detachCurrentThreadFromJvm` retrieves state, gets the JVM, detaches the current thread, logs failures, frees exception strings, and frees state. A PE TLS callback in `.CRT$XLB` calls detach on `DLL_THREAD_DETACH`, detaches and frees the TLS index on `DLL_PROCESS_DETACH`, and linker pragmas force the TLS directory and callback pointer to be retained.

## Dependencies and Integration Points
It depends on JNI, malloc, Windows APIs, and the platform TLS-callback loader behavior. `jni_helper.c` relies on it for per-thread environment state on Windows.

## Risks and Test Signals
The comments explicitly note a limitation: TLS callbacks may not work for explicit `LoadLibrary` use. The source also calls `detachCurrentThreadFromJvm(state)` in `threadLocalStorageSet` even though the helper is declared without parameters, which is a compile-risk signal for this file. Tests should compile this file on Windows, verify implicit DLL load detach behavior, exercise explicit load/unload if supported, and stress thread creation/destruction with active JNI state.
