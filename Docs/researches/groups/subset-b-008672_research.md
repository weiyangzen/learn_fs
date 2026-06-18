# subset-b-008672 Research

Grouped research report for RocksDB options parsing tests and POSIX/portable runtime support files. Each section preserves the exact source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_test.cc -->
# Research: sources/storage-engines/rocksdb/options/options_test.cc

## Purpose
This file is the central unit-test suite for RocksDB option parsing, option serialization, persisted OPTIONS-file parsing, option sanity checking, and object-registry based configuration. It exercises both newer `ConfigOptions`/`Configurable` paths and older convenience APIs so compatibility is preserved while options continue to move to typed registration.

## Important APIs, Types, And Functions
The tests target public and internal option helpers including `GetColumnFamilyOptionsFromMap`, `GetDBOptionsFromMap`, `GetColumnFamilyOptionsFromString`, `GetDBOptionsFromString`, `GetOptionsFromString`, `GetStringFromDBOptions`, `GetStringFromColumnFamilyOptions`, `GetStringFromMutableDBOptions`, `GetMutableDBOptionsFromStrings`, `StringToMap`, `MapToString`, `PersistRocksDBOptions`, and `RocksDBOptionsParser::Parse`/`Verify*`.

Fixtures and helper types include `OptionsTest`, `OptionsOldApiTest`, `OptionsParserTest`, `OptionsSanityCheckTest`, `OptionTypeInfoTest`, and `ConfigOptionsTest`. Local test doubles cover unregistered table factories, custom environments, event listeners, table properties collectors, and mock file checksum factories. The file also directly exercises `OptionTypeInfo` for primitive, enum, struct, array, vector, static type-map, parse, serialize, compare, prepare, validate, and flag behavior.

## Control Flow
The first block validates map and string parsing into `ColumnFamilyOptions`, `DBOptions`, and merged `Options`, checking both successful assignment and failure preservation when bad values or unknown keys are provided. It covers scalar values, memory-size suffixes, enum strings, nested structs, colon-separated legacy encodings, pointer/object factories, caches, filter policies, compression options, blob options, temperatures, timestamps, and mutable-only filtering.

The middle of the file validates round trips. Randomized option objects are serialized to strings, parsed back, decomposed/recomposed through immutable and mutable option structures, and compared with `RocksDBOptionsParser::Verify*`. `StringToMap` and `MapToString` are stressed with nested braces, empty braced values, random malformed strings, escaping, and single-entry round trips so generated map values remain embeddable in `key=value;` contexts.

The parser-focused tests write temporary OPTIONS files through a special filesystem, then parse sections such as `[Version]`, `[DBOptions]`, and `[CFOptions "name"]`. They assert rejection of missing or duplicate required sections, invalid default-CF ordering, invalid versions, duplicate CF entries, and conditional unknown-option behavior based on persisted RocksDB version. Dump-and-parse tests persist multiple column families with unusual names and pointer-valued options, then verify parsed DB/CF options and per-option maps.

The sanity-check tests persist options and then vary prefix extractors, table factories, merge operators, compaction filters, compaction filter factories, file checksum factories, and `persist_user_defined_timestamps` under exact, loosely compatible, and disabled sanity levels. The parameterization runs with `ignore_unsupported_options` both true and false.

## State And Persistence Behavior
Most tests are pure in-memory configuration transformations. Parser tests create and delete temporary files such as `test-rocksdb-options.ini`, `test-persisted-options.ini`, and `OPTIONS` through the fixture filesystem, including persisted RocksDB OPTIONS metadata. No real DB data is written, but the test simulates durable options files that DB reopen flows rely on.

The object registry is mutated during tests to register comparators, environments, event listeners, and table-property collector factories. Several randomly initialized CF options allocate raw `compaction_filter` pointers, and the tests explicitly delete those pointers after verification. A custom filesystem read counter is used to assert readahead behavior while parsing large persisted option files.

## Dependencies And Integration Points
The suite integrates with RocksDB option implementation files (`options_helper`, `options_parser`, configurable wrappers), table factories and filter policies, caches, memtable factories, merge operators, object registry, file checksum factories, LevelDB option conversion, test randomizers, special environment/filesystem helpers, and the port stack-trace handler used by `main`.

It is a regression net for DB reopen safety because `RocksDBOptionsParser::VerifyRocksDBOptionsFromFile` determines whether current runtime options are compatible with persisted metadata. It also protects Java and other bindings indirectly because those layers commonly use the same string and map option APIs.

## Risks And Edge Cases
The test file is intentionally broad and can become brittle when option defaults or serialization names change. Failures often indicate either an intentional compatibility change requiring test updates or a real break in persisted OPTIONS compatibility. Pointer-valued option comparisons are subtle: some unregistered or unsupported objects may serialize by name only, compare loosely, or be skipped depending on `ConfigOptions`.

Error-path assertions are important because parsers should leave destination options unchanged on invalid input. Escaping and nested brace parsing are high-risk because options strings are embedded in OPTIONS files where comments, separators, CF names, and object config payloads can collide. The legacy API section duplicates much of the modern coverage and must remain aligned until those APIs are actually removed.

## Test Signals
The file is itself the test signal and is run as a gtest binary. Strong indicators are exact/loose verification status, round-trip equality, parser rejection of malformed OPTIONS files, object-registry creation success, `OptionTypeInfo` mismatch names, and `RUN_ALL_TESTS()` success. Good future regressions should include new option fields in map/string/serialization paths, persisted-version unknown-option behavior, and unchanged-destination checks for every new parser failure mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/options/options_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/jemalloc_helper.h -->
# Research: sources/storage-engines/rocksdb/port/jemalloc_helper.h

## Purpose
This header centralizes RocksDB's optional jemalloc integration. When `ROCKSDB_JEMALLOC` is enabled, it includes the appropriate jemalloc headers, declares non-standard jemalloc APIs as weak symbols on platforms that support weak linkage, and provides `HasJemalloc()` for runtime availability checks.

## Important APIs, Types, And Functions
The main API is `static inline bool HasJemalloc()`. On MSVC/Windows with `ROCKSDB_JEMALLOC`, it always returns true because weak symbols are not available and the build selection implies jemalloc use. On other non-FreeBSD builds, the header declares weak `extern "C"` symbols for `mallocx`, `rallocx`, `xallocx`, `sallocx`, `dallocx`, `sdallocx`, `nallocx`, `mallctl`, `mallctlnametomib`, `mallctlbymib`, `malloc_stats_print`, and `malloc_usable_size`, then returns true only if all required symbols are non-null.

Compatibility macros such as `JEMALLOC_ALLOCATOR`, `JEMALLOC_RESTRICT_RETURN`, `JEMALLOC_NOTHROW`, `JEMALLOC_ALLOC_SIZE`, `JEMALLOC_CXX_THROW`, and `JEMALLOC_USABLE_SIZE_CONST` smooth differences across jemalloc versions and FreeBSD headers.

## Control Flow
Compilation first handles a clang/glibc `posix_memalign()` declaration issue by including `<mm_malloc.h>` before jemalloc can redeclare the function. If `ROCKSDB_JEMALLOC` is not defined, the header contributes no jemalloc declarations. If it is defined, platform branches select `<malloc_np.h>` on FreeBSD or mangled `<jemalloc/jemalloc.h>` elsewhere.

At runtime, non-MSVC `HasJemalloc()` only checks weak symbol addresses. It does not allocate memory or prove the process's default allocator is jemalloc; it establishes that the jemalloc extension API is link-visible.

## State And Persistence Behavior
The header has no persistent state and performs no allocation itself. Its declarations affect later code paths that may query allocator stats, usable sizes, or jemalloc controls. Weak symbols allow RocksDB to be built with jemalloc-aware code while tolerating binaries where the allocator library is absent.

## Dependencies And Integration Points
Consumers include RocksDB memory accounting and malloc statistics paths that need optional jemalloc APIs. The header depends on build macros (`ROCKSDB_JEMALLOC`, `OS_WIN`, `_MSC_VER`, `__FreeBSD__`, `__GLIBC__`, clang/GCC feature macros) and system/jemalloc headers.

## Risks And Edge Cases
`HasJemalloc()` can return true even if the main allocation path is not jemalloc, because it only checks symbol availability. Conversely, requiring all listed symbols means partial or older jemalloc installations can be treated as unavailable. Weak declarations are compiler/linker sensitive, while MSVC cannot support the same runtime detection. The clang/glibc ordering workaround is fragile if include order changes before this header.

## Test Signals
Coverage is usually compile/link and allocator-integration testing rather than a dedicated unit test. Useful signals include successful builds with and without `ROCKSDB_JEMALLOC`, FreeBSD and Windows builds, runtime stats paths handling `HasJemalloc()==false`, and symbol-resolution tests against older jemalloc versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/jemalloc_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/lang.h -->
# Research: sources/storage-engines/rocksdb/port/lang.h

## Purpose
This header defines small language/compiler compatibility utilities used across RocksDB. It hides compiler-specific attributes for fallthrough, sanitizer annotations, static object lifetime policy, debug assertions, and compile-time CPU feature macros.

## Important APIs, Types, And Functions
`FALLTHROUGH_INTENDED` maps to `[[clang::fallthrough]]`, `[[gnu::fallthrough]]`, or a no-op statement. `DECLARE_DEFAULT_MOVES(Name)` declares defaulted noexcept move construction and move assignment. `STATIC_AVOID_DESTRUCTION(Type, name)` either creates a normal static object under ASAN/Valgrind or a leaked heap-backed static reference in production. `kMustFreeHeapAllocations` records which mode is active.

`TSAN_SUPPRESSION` maps to `__attribute__((no_sanitize("thread")))` when thread sanitizer is detected. `DEBUG_FAIL(msg)` expands to an assertion failure with a grouping message. `ASSERT_FEATURE_COMPAT_HEADER()` is a static assertion sentinel. The header also normalizes `__SSE4_2__`, `__PCLMUL__`, and `__POPCNT__` based on `__AVX__`, `NO_PCLMUL`, and `NO_POPCNT`.

## Control Flow
All behavior is selected by preprocessor checks. ASAN is detected through clang `__has_feature(address_sanitizer)` or GCC `__SANITIZE_ADDRESS__`; Valgrind runs force the same heap-freeing mode. TSAN detection is normalized so clang feature detection defines the GCC-style `__SANITIZE_THREAD__` macro before `TSAN_SUPPRESSION` is chosen.

## State And Persistence Behavior
No runtime persistence is present. The most important state effect is static object lifetime: production builds intentionally avoid non-trivial static destruction by leaking heap-allocated singletons, while sanitizer/Valgrind builds use true static objects so leak detectors and heap cleanup can observe destructors.

## Dependencies And Integration Points
The header integrates with many RocksDB files that need portable annotations, singleton/static registries, sanitizer-specific behavior, or CPU feature gates for optimized code. It depends only on compiler and build-system macros.

## Risks And Edge Cases
`STATIC_AVOID_DESTRUCTION` intentionally trades leak reports for destruction-order safety in production-like builds. Any code relying on static destructors will behave differently under sanitizer and non-sanitizer builds. CPU feature inference from `__AVX__` is a compatibility convenience, not runtime CPU detection, so it must only be used for compile-time guarded code paths. `DEBUG_FAIL` depends on `assert`, so behavior changes under `NDEBUG`.

## Test Signals
Signals are mostly build-matrix based: clang, GCC, MSVC-like macro environments, ASAN, TSAN, Valgrind, and feature-disabled builds. Runtime tests indirectly validate static registries and optimized code compiled under the normalized CPU feature macros.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/lang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/likely.h -->
# Research: sources/storage-engines/rocksdb/port/likely.h

## Purpose
This tiny portability header provides branch prediction macros for hot code paths. It preserves LevelDB-style `LIKELY` and `UNLIKELY` names while using compiler intrinsics when available.

## Important APIs, Types, And Functions
`LIKELY(x)` expands to `__builtin_expect((x), 1)` on GCC-compatible compilers version 4 or newer, and `UNLIKELY(x)` expands to `__builtin_expect((x), 0)`. On other compilers both macros evaluate to the expression itself.

## Control Flow
There is no runtime control flow beyond expression evaluation. The macro result is used by the compiler to bias branch layout and prediction metadata. The fallback preserves semantics without optimization hints.

## State And Persistence Behavior
No state is stored and no persistent behavior exists. The only effect is generated code shape in branches where callers apply the macros.

## Dependencies And Integration Points
The header depends on `__GNUC__` version macros. It is included by performance-sensitive RocksDB code that wants portable branch hints without depending directly on compiler builtins.

## Risks And Edge Cases
Arguments are still evaluated exactly once because the macros wrap the expression once. Misusing branch hints can hurt performance by biasing layout incorrectly, but it should not change correctness. Non-GCC compilers receive no hint unless they also define compatible GCC macros.

## Test Signals
There is typically no direct unit test. Compile coverage across supported compilers and performance tests on hot paths are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/likely.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/malloc.h -->
# Research: sources/storage-engines/rocksdb/port/malloc.h

## Purpose
This header conditionally includes platform malloc headers needed for `malloc_usable_size`-style APIs. It keeps malloc header selection behind RocksDB build macros so most builds avoid non-portable declarations.

## Important APIs, Types, And Functions
The file does not define its own functions or types. If `ROCKSDB_MALLOC_USABLE_SIZE` is defined, it includes `<malloc_np.h>` on FreeBSD (`OS_FREEBSD`) and `<malloc.h>` elsewhere.

## Control Flow
All behavior is preprocessor-driven. Builds that do not opt into `ROCKSDB_MALLOC_USABLE_SIZE` get only the include guard and no system malloc declarations.

## State And Persistence Behavior
There is no runtime state or persistence. The header only affects declaration availability for consumers that query allocator usable sizes.

## Dependencies And Integration Points
Consumers are memory accounting or allocation-size code paths that need `malloc_usable_size` or equivalent declarations. The header depends on build macros selecting both feature use and FreeBSD-specific header naming.

## Risks And Edge Cases
`malloc_usable_size` is non-standard and allocator-specific. Including the wrong header for a platform can break compilation, while enabling the feature with an allocator that does not support the expected API can break builds or runtime assumptions. Keeping this header minimal reduces cross-platform exposure.

## Test Signals
Build coverage with `ROCKSDB_MALLOC_USABLE_SIZE` enabled and disabled is the main signal. Runtime memory-accounting tests should tolerate feature absence and validate reported usable sizes only on supported allocator/platform combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/malloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/mmap.cc -->
# Research: sources/storage-engines/rocksdb/port/mmap.cc

## Purpose
This file implements `MemMapping`, RocksDB's RAII wrapper around anonymous memory mappings. It provides lazy-zeroed mappings and best-effort huge-page mappings across POSIX and Windows.

## Important APIs, Types, And Functions
The key methods are `MemMapping::~MemMapping`, move constructor, move assignment, `MemMapping::AllocateAnonymous`, `MemMapping::AllocateHuge`, and `MemMapping::AllocateLazyZeroed`. POSIX builds use `mmap`/`munmap`; Windows builds use `CreateFileMapping`, `MapViewOfFile`, `UnmapViewOfFile`, and `CloseHandle`.

## Control Flow
Destruction unmaps `addr_` when present and closes the Windows page-file handle when present. Move assignment guards self-assignment, destroys the current mapping, byte-copies the source object into the destination, and placement-news the source back to an empty `MemMapping`, transferring ownership without double-unmapping.

`AllocateAnonymous` initializes a default empty mapping, stores the requested length, returns immediately for zero length, optionally selects huge-page flags, then calls the platform mapping API. POSIX maps private anonymous read/write memory and normalizes `MAP_FAILED` to `nullptr`. Windows creates a page-file mapping and then maps a writable view.

## State And Persistence Behavior
State is `addr_`, `length_`, and on Windows `page_file_handle_`. The mapping is anonymous process memory, not file-backed persistent storage. `AllocateLazyZeroed` relies on operating-system zero-fill and possible overcommit; `AllocateHuge` requests huge pages when compile-time support exists but returns a null address on failure rather than throwing.

## Dependencies And Integration Points
The implementation depends on `port/mmap.h`, platform memory APIs, `assert`, placement new, and `Slice` exposure from the header. Callers use this for large in-memory arrays or buffers where lazy zeroing or huge pages can reduce initialization overhead or improve locality.

## Risks And Edge Cases
Failure is represented as `Get()==nullptr` while `Length()` still records the requested size, so callers must check the pointer before use. Huge-page support is compile-time and runtime dependent; requesting huge pages can fail because of OS policy, privileges, or pool size. The destructor asserts `munmap` success but otherwise ignores errors. Move assignment uses `memcpy` over the object, which is currently safe only because the class owns raw handles and no non-trivial members.

## Test Signals
Useful tests allocate zero, small, and large mappings; validate zero initialization; write/read the memory; move mappings; and verify no double unmap under sanitizers. Platform tests should cover huge-page failure fallback and Windows handle cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/mmap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/mmap.h -->
# Research: sources/storage-engines/rocksdb/port/mmap.h

## Purpose
This header declares `MemMapping`, an RAII wrapper for anonymous mapped memory, plus `TypedMemMapping<T>`, a typed array view over the same mapping. It hides POSIX and Windows include differences and exposes simple allocation APIs to RocksDB internals.

## Important APIs, Types, And Functions
`MemMapping::kHugePageSupported` is a compile-time boolean based on `MAP_HUGETLB` or `FILE_MAP_LARGE_PAGES`. `AllocateHuge(size_t)` requests huge-page backing. `AllocateLazyZeroed(size_t)` requests ordinary anonymous zeroed mapping. Copy construction/assignment are deleted, move operations are supported, and the destructor releases the mapping.

Accessors are `Get()`, `Length()`, and `AsSlice()`. `TypedMemMapping<T>` inherits from `MemMapping`, accepts a moved mapping, returns typed `T*` from `Get()`, exposes `Count()` as bytes divided by `sizeof(T)`, and provides `operator[]`.

## Control Flow
Callers construct mappings only through the static allocation methods because the default constructor is private. A returned mapping can be tested by `Get()`. Moving transfers ownership and leaves the source empty. `AsSlice()` creates a zero-copy `Slice` over the mapped range without validating non-nullness.

## State And Persistence Behavior
The object stores a raw mapped address and requested length, plus a Windows file-mapping handle when needed. The mapping is process-local anonymous memory and does not persist beyond process lifetime. The header documents that lazy-zeroed mappings may use OS overcommit on Linux but may require page-file backing on other platforms.

## Dependencies And Integration Points
The header includes Windows port headers before `windows.h`-related APIs, or `<sys/mman.h>` on POSIX. It integrates with `rocksdb::Slice` so mapped bytes can be passed to RocksDB helpers without copying. Typed mappings are useful where metadata arrays can live in mmapped zeroed memory.

## Risks And Edge Cases
`Length()` is the requested length, not necessarily a proven usable extent if allocation failed. `AsSlice()` on a failed non-zero allocation yields a null pointer with non-zero size, so callers must check `Get()`. `TypedMemMapping<T>::operator=(MemMapping&&)` lacks an explicit `return *this;` in this version, which is undefined behavior if the assignment expression value is used. The typed wrapper also does not enforce alignment beyond what the OS mapping naturally provides.

## Test Signals
Compile tests should instantiate `TypedMemMapping` assignment and indexing. Runtime tests should cover failure checks, slice creation, move transfer, zero-length mappings, huge-page support reporting, and typed counts for sizes not divisible by `sizeof(T)`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port.h -->
# Research: sources/storage-engines/rocksdb/port/port.h

## Purpose
This header is the main platform-selection entry point for RocksDB's port layer. It includes the POSIX or Windows port implementation header and defines a weak Linux thread-yield/abort hook used by long-running RocksDB threads.

## Important APIs, Types, And Functions
The important behavior is conditional inclusion of `port/port_posix.h` when `ROCKSDB_PLATFORM_POSIX` is defined or `port/win/port_win.h` when `OS_WIN` is defined. On Linux it declares weak `extern "C" bool RocksDbThreadYieldAndCheckAbort()` and defines `ROCKSDB_THREAD_YIELD_CHECK_ABORT()` to call it when linked, otherwise return false. On non-Linux builds, the macro always returns false.

## Control Flow
Compilation selects exactly the platform-specific port header according to build macros. At runtime, Linux callers of `ROCKSDB_THREAD_YIELD_CHECK_ABORT()` perform a null check on the weak hook before calling it. This lets external embedders provide optional cooperative yielding or abort behavior without forcing a hard dependency.

## State And Persistence Behavior
The header stores no state. The weak hook can influence control flow in long-running operations by reporting an abort request, but it does not persist any information itself.

## Dependencies And Integration Points
Nearly all RocksDB internals include `port/port.h` for mutexes, condition variables, thread utilities, endian constants, cacheline allocation, stack traces, and platform primitives supplied by the selected port header. The Linux hook is a temporary integration point for embedders that need to adjust thread priority or interrupt expensive loops.

## Risks And Edge Cases
If neither POSIX nor Windows macros are defined, required port symbols will be missing at compile time. The weak hook has process-global C linkage, so embedders must ensure the symbol is safe, fast, and callable from RocksDB worker threads. Since it is a macro, callers must handle a simple boolean and cannot observe detailed abort reasons.

## Test Signals
Builds on POSIX and Windows are the primary signal. Linux integration tests can provide a strong `RocksDbThreadYieldAndCheckAbort` symbol and verify long-running loops observe true while default builds see false.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_dirent.h -->
# Research: sources/storage-engines/rocksdb/port/port_dirent.h

## Purpose
This header provides a portable directory-iteration surface for code that expects POSIX-style `DIR`, `dirent`, `opendir`, `readdir`, and `closedir`. POSIX platforms use system declarations directly, while Windows receives RocksDB port declarations.

## Important APIs, Types, And Functions
On POSIX it includes `<dirent.h>` and `<sys/types.h>`. On Windows it declares `ROCKSDB_NAMESPACE::port::dirent` with `char d_name[_MAX_PATH]`, an opaque `DIR`, and functions `opendir(const char*)`, `readdir(DIR*)`, and `closedir(DIR*)`. The Windows declarations are re-exported into `ROCKSDB_NAMESPACE` with `using` declarations.

## Control Flow
There is no runtime logic in this header. Preprocessor branches select either system APIs or the Windows shim declarations. Implementations for the Windows functions live in the Windows port sources.

## State And Persistence Behavior
The header has no persistent state. `DIR` instances returned by `opendir` are runtime directory handles owned by callers until `closedir`.

## Dependencies And Integration Points
Filesystem and environment code can include this header to avoid scattering `#ifdef OS_WIN` around directory iteration. It depends on `ROCKSDB_PLATFORM_POSIX`, `OS_WIN`, `_MAX_PATH`, and the selected platform port implementation.

## Risks And Edge Cases
The Windows `dirent` shim exposes only `d_name`, not full POSIX metadata fields. Code using fields such as `d_type` would not be portable through this abstraction. `_MAX_PATH` can truncate or reject long Windows paths depending on implementation details in the corresponding port source.

## Test Signals
Directory listing tests through RocksDB `Env` and direct Windows port tests should cover empty directories, long names, Unicode/escaped paths where supported, close behavior, and parity with POSIX callers that only use `d_name`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_example.h -->
# Research: sources/storage-engines/rocksdb/port/port_example.h

## Purpose
This file is a specification template for adding a new RocksDB platform port. It does not implement a working port; it documents the minimal types, constants, and functions that a `port_<platform>.h` file must provide.

## Important APIs, Types, And Functions
The required surface includes `port::kLittleEndian`, `port::Mutex` with `Lock`, `Unlock`, and `AssertHeld`, `port::CondVar` with `Wait`, `Signal`, and `SignalAll` semantics, `port::OnceType`, `LEVELDB_ONCE_INIT`, and `port::InitOnce`. Comments describe lock ownership requirements, condition-variable wakeup behavior, and fast optional debug checking.

## Control Flow
The example sketches how callers use `OnceType` and `InitOnce` for one-time initialization. The mutex and condition-variable methods are declarations only; platform implementations must supply blocking, wakeup, and initialization behavior consistent with the comments.

## State And Persistence Behavior
There is no actual state in this file beyond placeholder declarations. Real ports must maintain mutex state, condition-variable wait queues, and once-control state. None of these are persistent beyond process lifetime.

## Dependencies And Integration Points
`port/port.h` points new platform authors at this file when adding a platform-specific port header. The specification descends from LevelDB's port abstraction and underpins RocksDB synchronization and one-time initialization throughout the codebase.

## Risks And Edge Cases
The file can become stale relative to richer real port headers such as POSIX and Windows, which now include more APIs than this minimal example. It also contains a typo in the example method name `SignallAll`, while real code expects `SignalAll`. Port authors must compare against active port headers, not this template alone.

## Test Signals
For a new port, successful compilation is only the first signal. Synchronization tests, DB stress, environment tests, and once-initialization tests are needed to validate the semantics described here.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_example.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_posix.cc -->
# Research: sources/storage-engines/rocksdb/port/port_posix.cc

## Purpose
This file implements the POSIX side of RocksDB's port abstraction when not building for Windows. It supplies pthread-backed synchronization, one-time initialization, process utilities, cacheline-aligned allocation, CPU/core helpers, page-size discovery, CPU priority adjustment, immediate exit/crash helpers, open-file-limit inspection, and Linux UUID generation.

## Important APIs, Types, And Functions
`PthreadCall` wraps pthread return codes, aborting on unexpected errors while allowing `ETIMEDOUT` and `EBUSY` for timed waits and try-locks. `Mutex` implements construction with optional adaptive mutexes, `Lock`, `Unlock`, `TryLock`, and debug `AssertHeld`. `CondVar` implements `Wait`, `TimedWait`, `Signal`, and `SignalAll`. `RWMutex` implements read/write locks and try-lock variants.

Other exported functions include `PhysicalCoreID`, `InitOnce`, `Crash`, `ImmediateExit`, `GetMaxOpenFiles`, `cacheline_aligned_alloc`, `cacheline_aligned_free`, `SetCpuPriority`, `GetProcessID`, and `GenerateRfcUuid`. File-scope `GetPageSize` initializes `port::kPageSize`, and `kDefaultToAdaptiveMutex` records whether the build defaults mutex construction to adaptive pthread mutexes.

## Control Flow
Mutex construction optionally creates a `pthread_mutexattr_t` with `PTHREAD_MUTEX_ADAPTIVE_NP` when adaptive mutex support is compiled and requested. Lock and wait methods update a debug-only `locked_` flag around pthread calls so `AssertHeld` can catch misuse in non-`NDEBUG` builds. Condition waits release and reacquire the underlying mutex through pthread APIs.

`PhysicalCoreID` prefers `sched_getcpu()` on supported Linux x86_64 builds, falls back to CPUID APIC ID on x86, and returns `-1` elsewhere. `GetMaxOpenFiles` uses `getrlimit(RLIMIT_NOFILE)` and caps at `int` max. Cacheline allocation uses `posix_memalign` when available, falls back for ASAN/GCC corner cases, and frees with `free`. CPU priority uses Linux scheduler/nice calls and no-ops elsewhere. UUID generation reads `/proc/sys/kernel/random/uuid` and accepts only 36-character results.

## State And Persistence Behavior
State lives in POSIX kernel synchronization primitives and process settings. No RocksDB database state is persisted here. `SetCpuPriority` can persistently change scheduler/nice state for the target thread/process in the running OS process. `kPageSize` is initialized once at program startup from `sysconf` or defaults to 4 KiB.

## Dependencies And Integration Points
The implementation backs `port/port_posix.h`, which is included through `port/port.h` by core RocksDB code. It depends on pthreads, scheduler/resource/time/process syscalls, CPUID headers on x86, `util/string_util.h` for error strings, and build macros such as `ROCKSDB_PTHREAD_ADAPTIVE_MUTEX`, `ROCKSDB_DEFAULT_TO_ADAPTIVE_MUTEX`, `ROCKSDB_SCHED_GETCPU_PRESENT`, and `OS_LINUX`.

## Risks And Edge Cases
`PthreadCall` aborts the process on unexpected pthread errors, which is appropriate for low-level invariant failures but harsh if callers misuse synchronization. The debug `locked_` flag is not a recursive ownership tracker and is compiled out in release. Adaptive mutex behavior depends on non-portable pthread extensions. `SetCpuPriority` ignores syscall failures, so permission or scheduler limitations are silent. `GenerateRfcUuid` is Linux `/proc` specific and returns false outside that environment or when the file cannot be read.

## Test Signals
Threading tests should cover mutex, try-lock, condition wait/timed wait timeout, broadcasts, RW lock read/write exclusion, and one-time initialization. Portability tests should cover allocation alignment, page-size sanity, open-file-limit retrieval, process ID, UUID format on Linux, and graceful behavior when priority changes lack permission.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_posix.cc -->
