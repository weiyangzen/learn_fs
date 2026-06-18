# subset-b-008673 grouped research

This grouped report covers the requested RocksDB portability, build, and table-reader sources. Each source file has a separate marked section so the reconciliation lane can split by source path.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_posix.h -->
# sources/storage-engines/rocksdb/port/port_posix.h

Purpose: POSIX port declarations for RocksDB's platform abstraction. It normalizes endian detection, cache-line sizing, synchronization primitives, thread aliases, direct CPU pause instructions, process helpers, page allocation, and crash/exit behavior for non-Windows builds.

Important APIs/types/functions: `port::Mutex`, `RWMutex`, and `CondVar` wrap `pthread_mutex_t`, `pthread_rwlock_t`, and `pthread_cond_t`; `Thread` aliases `std::thread`; `OnceType`/`InitOnce` wrap `pthread_once_t`; `AsmVolatilePause`, `PhysicalCoreID`, `cacheline_aligned_alloc/free`, `Crash`, `ImmediateExit`, `GetMaxOpenFiles`, `SetCpuPriority`, `GetProcessID`, and `GenerateRfcUuid` are the public port hooks.

Control flow: this header is mostly compile-time dispatch. It chooses platform endian headers, substitutes missing unlocked stdio/fdatasync APIs, defines `PREFETCH`, and exposes declarations implemented in POSIX source files.

State and persistence behavior: only synchronization objects own state. Persistence-related behavior is indirect through `ImmediateExit`, which avoids static destruction when background threads may still touch global objects.

Dependencies and integration points: consumed by `port/port.h`, env/file-system code, mutex users, cache-aligned structures, and low-level utilities. It depends on pthreads, endian headers, process IDs, and RocksDB namespace/port definitions.

Risks and test signals: endian/cache-line macros are build-sensitive; debug `Mutex::AssertHeld` does not prove current-thread ownership; platform fallback definitions need coverage on BSD, AIX, Solaris, Android, and Linux. Tests that exercise port primitives, cache alignment, process ID, UUID generation, and immediate-exit paths signal regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/port_posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/stack_trace.cc -->
# sources/storage-engines/rocksdb/port/stack_trace.cc

Purpose: implements RocksDB stack-trace capture and signal handling for supported POSIX/Mac builds, with no-op fallbacks for unsupported platforms such as Windows, Cygwin, and Solaris.

Important APIs/types/functions: `InstallStackTraceHandler`, `PrintStack`, `SaveStack`, `PrintAndFreeStack`, and `RegisterCrashCallback`. Internals include `GetExecutableName`, `PrintStackTraceLine`, `GetLldbScriptSelectThread`, `StackTraceHandler`, `TerminationHandler`, and `AtExit`.

Control flow: if stack tracing is disabled at compile time, exported functions return immediately. Otherwise `InstallStackTraceHandler` installs handlers for crash signals, ignores `SIGPIPE`, registers lightweight termination handlers, and relaxes ptrace restrictions where supported. `PrintStack` prefers LLDB/GDB depending on environment variables, forks a child debugger, waits for success, then falls back to `backtrace` plus `addr2line`/`atos`.

State and persistence behavior: global atomics track the thread currently handling a trace, whether exit has begun, and the crash callback. `SaveStack` mallocs a callstack that must be freed by `PrintAndFreeStack`. No persistent files are written.

Dependencies and integration points: used by tests, benchmarks, and debugging binaries that opt into stack traces. It depends on `execinfo`, `pthread`, `fork`, debugger executables, `/proc` or `sysctl`, `port/lang.h`, and process signal semantics.

Risks and test signals: signal handlers call non-async-signal-safe routines by design, so recursion/race handling is defensive but imperfect. Debugger invocation can hang or fail under ptrace restrictions. Environment variables `ROCKSDB_NO_STACK`, `ROCKSDB_DEBUG`, `ROCKSDB_LLDB_STACK`, `ROCKSDB_GDB_STACK`, and `ROCKSDB_BACKTRACE_STACK` should be covered by crash/debug tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/stack_trace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/stack_trace.h -->
# sources/storage-engines/rocksdb/port/stack_trace.h

Purpose: declares RocksDB's optional stack trace and crash callback interface.

Important APIs/types/functions: `InstallStackTraceHandler`, `PrintStack`, `PrintAndFreeStack`, `SaveStack`, `CrashCallback`, and `RegisterCrashCallback`.

Control flow: header-only declarations; platform selection happens in `stack_trace.cc`. Callers install handlers once, optionally register a single callback, and can explicitly save/print stack frames.

State and persistence behavior: the header exposes no state, but the implementation stores one process-wide callback and heap-allocated saved stacks.

Dependencies and integration points: included by unit-test, benchmark, and diagnostic code needing stack traces. It is namespace-scoped under `ROCKSDB_NAMESPACE::port`.

Risks and test signals: callback contracts are strict because callbacks run during fatal signals. Tests should verify no-op behavior on unsupported platforms and that saved stacks are freed through the matching API.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/stack_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/sys_time.h -->
# sources/storage-engines/rocksdb/port/sys_time.h

Purpose: supplies a portable substitute for `sys/time.h`, especially for Windows.

Important APIs/types/functions: `port::TimeVal`, `GetTimeOfDay`, and `LocalTimeR`.

Control flow: Windows builds define a local `TimeVal` and declare `GetTimeOfDay`; non-Windows builds include system time headers and inline `gettimeofday`/`localtime_r`.

State and persistence behavior: stateless time conversion/read wrappers; no persistence.

Dependencies and integration points: used by loggers, clocks, and timing code that needs a common `TimeVal` shape. Windows implementation lives in `port/win/port_win.cc`.

Risks and test signals: Windows `LocalTimeR` uses `localtime_s`, while POSIX uses `localtime_r`; return/null behavior should stay consistent. Logger timestamp tests and clock tests are good signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/sys_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/util_logger.h -->
# sources/storage-engines/rocksdb/port/util_logger.h

Purpose: selects a platform-specific logger implementation for low-level RocksDB port code.

Important APIs/types/functions: no direct API; on Windows it includes `port/win/win_logger.h`.

Control flow: compile-time include routing under `OS_WIN`.

State and persistence behavior: delegated to the included logger implementation.

Dependencies and integration points: lets code include one port logger header without hard-coding the Windows logger path.

Risks and test signals: unsupported platforms intentionally get no include from this file; build tests catch missing platform branches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/util_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/env_default.cc -->
# sources/storage-engines/rocksdb/port/win/env_default.cc

Purpose: defines `Env::Default()` for Windows and initializes RocksDB process-wide helper singletons before constructing the default Windows environment.

Important APIs/types/functions: `Env::Default`, internal `winenv_once_flag`, and `envptr`.

Control flow: `Env::Default()` initializes thread-local, compression-context, and sync-point singletons, then uses `std::call_once` to allocate one `port::WinEnv`.

State and persistence behavior: intentionally leaks the default `WinEnv` instead of destroying it, avoiding loader-lock deadlocks when statics are torn down while background threads may be live. No files are persisted.

Dependencies and integration points: ties `WinEnv` into RocksDB's global `Env` API. It depends on `ThreadLocalPtr`, `CompressionContextCache`, sync-point singletons, and `port/win/env_win.h`.

Risks and test signals: singleton initialization order matters. Env tests, sync-point tests, and Windows DLL/static-destruction scenarios are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/env_default.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/env_win.cc -->
# sources/storage-engines/rocksdb/port/win/env_win.cc

Purpose: implements Windows `SystemClock`, `FileSystem`, `Env` I/O helpers, and background-thread integration for RocksDB.

Important APIs/types/functions: `WinClock`, `WinFileSystem::Default`, file creation methods (`NewSequentialFile`, `NewRandomAccessFile`, `NewWritableFile`, `ReopenWritableFile`, `NewRandomRWFile`, `NewMemoryMappedFileBuffer`, `NewDirectory`), file operations (`DeleteFile`, `CreateDir`, `RenameFile`, `LinkFile`, `LockFile`, `GetFreeSpace`, `GetSectorSize`), `WinEnvThreads`, `WinEnv`, and defaults for `FileSystem::Default`/`SystemClock::Default`.

Control flow: `WinClock` prefers `GetSystemTimePreciseAsFileTime` or performance counters. `WinFileSystem` opens handles with Windows share/flag choices matching RocksDB tests and file modes, then wraps them in classes from `io_win.cc`. Directory and metadata methods use Windows attribute and handle APIs. `WinEnvThreads` delegates priority queues to `ThreadPoolImpl` and stores started threads for later joining. `WinEnv` is a `CompositeEnv` over the Windows filesystem and clock.

State and persistence behavior: file methods create, delete, rename, hard-link, lock, preallocate, map, and sync real files through Win32 handles. The clock is stateless after frequency/function-pointer initialization. Thread pools and `threads_to_join_` hold runtime state.

Dependencies and integration points: integrates with RocksDB `Env`, `FileSystem`, `SystemClock`, `ThreadStatusUpdater`, `IOSTATS_TIMER_GUARD`, Windows path macros from `port_win.h`, file wrappers from `io_win.h`, and `WinLogger`.

Risks and test signals: share modes are tuned for RocksDB tests that rename/delete open files. Direct I/O and mmap flags must align with `FileOptions`. `GetChildren` contains a suspicious `BOOL ret = -RX_FindNextFile(...)` idiom but relies on zero/nonzero semantics. Env, logger, WAL, file-lock, fault-injection, and auto-roll logger tests signal regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/env_win.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/env_win.h -->
# sources/storage-engines/rocksdb/port/win/env_win.h

Purpose: declares the Windows `Env`, `FileSystem`, `SystemClock`, and background-thread wrappers.

Important APIs/types/functions: `WinEnvThreads`, `WinClock`, `WinFileSystem`, `WinEnvIO`, and `WinEnv`.

Control flow: this header defines the override surface used by RocksDB's generic `Env`/`FileSystem` APIs. `WinEnv` delegates host-name calls to `WinEnvIO` and scheduling/thread calls to `WinEnvThreads`.

State and persistence behavior: `WinFileSystem` stores clock, page size, and allocation granularity; `WinEnvThreads` stores thread pools and joinable threads; persistence behavior is implemented in `env_win.cc` and `io_win.cc`.

Dependencies and integration points: includes Windows headers, `CompositeEnv`, `rocksdb/env.h`, `rocksdb/file_system.h`, `rocksdb/system_clock.h`, and `ThreadPoolImpl`.

Risks and test signals: override signatures must match RocksDB public interfaces; macro conflicts with Windows names are explicitly undefined. Build and Env API tests catch drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/env_win.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/io_win.cc -->
# sources/storage-engines/rocksdb/port/win/io_win.cc

Purpose: implements Windows file objects backing RocksDB's `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, `FSRandomRWFile`, memory-mapped buffers, directories, and file locks.

Important APIs/types/functions: `GetWindowsErrSz`, `IOErrorFromWindowsError`, `pread`, `pwrite`, `fallocate`, `ftruncate`, `GetUniqueIdFromFile`, `WinFileData`, `WinMmapReadableFile`, `WinMmapFile`, `WinSequentialFile`, `WinRandomAccessImpl`, `WinRandomAccessFile`, `WinWritableImpl`, `WinWritableFile`, `WinRandomRWFile`, `WinMemoryMappedBuffer`, `WinDirectory`, and `WinFileLock`.

Control flow: reads/writes use `ReadFile`/`WriteFile`, sometimes with `OVERLAPPED` offsets to emulate POSIX `pread`/`pwrite`. Mmap writes preallocate, create/resize mapping handles, map fixed-size views, append via `memcpy`, flush page ranges, and truncate on close. Direct-I/O paths assert sector-aligned offsets, sizes, and buffers. Writable close flushes file buffers and closes handles.

State and persistence behavior: `WinFileData` owns a Windows file handle and direct-I/O/sector metadata. Writable classes track `next_write_offset_`, reserved size, mmap view state, pending sync state, and mapping handles. `Sync`/`Fsync` call `FlushFileBuffers` or `FlushViewOfFile`; close paths release handles and mapping views.

Dependencies and integration points: constructed by `WinFileSystem` in `env_win.cc`; used by RocksDB file readers/writers, table cache, WAL, manifest, and random-RW code. Uses `IOSTATS_TIMER_GUARD` and sync-point test hooks.

Risks and test signals: `GetUniqueIdFromFile` returns 0, reducing cross-reader cache sharing. Direct I/O alignment is enforced mostly by assertions. Mmap append pads to pages and truncates on close, so close/sync tests matter. Fault-injection, file reader/writer, WAL, table, and direct-I/O tests are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/io_win.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/io_win.h -->
# sources/storage-engines/rocksdb/port/win/io_win.h

Purpose: declares Windows low-level file wrappers and error helpers used by `WinFileSystem`.

Important APIs/types/functions: error conversion helpers, `pread`, `pwrite`, `fallocate`, `ftruncate`, `GetUniqueIdFromFile`, and all Windows file wrapper classes.

Control flow: class declarations separate common handle state (`WinFileData`), common random-read behavior (`WinRandomAccessImpl`), common write behavior (`WinWritableImpl`), and concrete RocksDB FS interfaces.

State and persistence behavior: declarations expose state fields for handles, alignment, mapping regions, file offsets, sync state, and file locks.

Dependencies and integration points: depends on `rocksdb/file_system.h`, `rocksdb/status.h`, `AlignedBuffer`, and Windows APIs. `env_win.cc` instantiates these classes.

Risks and test signals: inheritance is deliberately mixed private/protected/public; changes can break polymorphic FS behavior. Direct-I/O contract comments should be tested by file-writer and random-access tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/io_win.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/port_win.cc -->
# sources/storage-engines/rocksdb/port/win/port_win.cc

Purpose: implements Windows equivalents for RocksDB's POSIX-style port primitives.

Important APIs/types/functions: UTF-8/UTF-16 conversion, `GetTimeOfDay`, `CondVar::Wait/TimedWait`, `PhysicalCoreID`, `InitOnce`, `opendir/readdir/closedir`, `truncate`/`Truncate`, `Crash`, `ImmediateExit`, `GetMaxOpenFiles`, `SetCpuPriority`, `GetProcessID`, and `GenerateRfcUuid`.

Control flow: condition variables adopt an already-held mutex and release ownership before returning. Directory iteration wraps `FindFirstFileEx` and `FindNextFile`. Truncation opens an existing file and calls `SetFileInformationByHandle`. UUID generation uses RPC UUID APIs.

State and persistence behavior: directory objects own find handles; truncation mutates files; crash aborts; immediate exit calls `_exit`; UUID generation returns an RFC-style string. CPU priority is a no-op.

Dependencies and integration points: used by `port_win.h`, Windows Env, logger time code, and generic RocksDB code expecting POSIX-like APIs.

Risks and test signals: condition-variable absolute-time conversion must match RocksDB timed wait expectations. Directory iteration and truncation error mapping are compatibility-sensitive. Port, Env, file-lock, and timing tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/port_win.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/port_win.h -->
# sources/storage-engines/rocksdb/port/win/port_win.h

Purpose: Windows port header for RocksDB's synchronization, allocation, path, thread-local, and platform helper APIs.

Important APIs/types/functions: `Mutex`, `RWMutex`, `CondVar`, `Thread` alias, `OnceType`, cache-line allocation helpers, `AsmVolatilePause`, pthread TLS shims, truncate/crash/exit/process/UUID helpers, UTF conversion helpers, and `RX_*` path/function macros.

Control flow: compile-time routing selects `std::thread` or `WindowsThread`, jemalloc or `_aligned_malloc`, UTF-16 Win32 APIs or ANSI APIs, and Windows SRW locks/condition variables.

State and persistence behavior: synchronization objects own mutex/SRW state; TLS keys map to Windows TLS slots; file persistence is delegated to declared truncate and Env/I/O implementations.

Dependencies and integration points: included through `port/port.h` on Windows; consumed across RocksDB core. It includes `win_thread.h`, Windows headers, and RocksDB port definitions.

Risks and test signals: Windows macro collisions are actively undefined; UTF filename mode changes ABI expectations for path strings. Build matrix coverage with MSVC, MinGW, `_POSIX_THREADS`, UTF filenames, and jemalloc is important.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/port_win.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_jemalloc.cc -->
# sources/storage-engines/rocksdb/port/win/win_jemalloc.cc

Purpose: plugs jemalloc into Windows RocksDB builds, including optional ZSTD custom allocation and global new/delete replacement.

Important APIs/types/functions: `JemallocAllocateForZSTD`, `JemallocDeallocateForZSTD`, `GetJeZstdAllocationOverrides`, `jemalloc_aligned_alloc`, `jemalloc_aligned_free`, and global `operator new/delete` overloads.

Control flow: only compiles on `OS_WIN` with `ROCKSDB_JEMALLOC`; optional ZSTD hooks compile only with static-linking ZSTD version 5+. New/new[] allocate with `je_malloc` and throw `std::bad_alloc` on failure; delete/delete[] call `je_free`.

State and persistence behavior: no persistence; it changes process allocation behavior when linked.

Dependencies and integration points: consumed by `port_win.h` cacheline allocation helpers and compression code needing ZSTD custom memory hooks.

Risks and test signals: global operator replacement is high blast-radius and must match linker/build assumptions. Allocator, compression, and Windows jemalloc build tests are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_jemalloc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_logger.cc -->
# sources/storage-engines/rocksdb/port/win/win_logger.cc

Purpose: implements RocksDB's Windows logger over a Win32 file handle.

Important APIs/types/functions: `WinLogger::Logv`, `Flush`, `CloseImpl`, `CloseInternal`, `DebugWriter`, and `GetLogFileSize`.

Control flow: `Logv` formats timestamp, microseconds, and thread id into a stack buffer, retries with a 30KB heap buffer if needed, appends a newline, and writes with `WriteFile`. Flush updates timing state but does not force disk flush except on close.

State and persistence behavior: owns a log file handle, atomic log size, last flush timestamp, and flush-pending flag. Close flushes file buffers and closes the handle.

Dependencies and integration points: created by `WinFileSystem::NewLogger`; uses `GetTimeOfDay`, `SystemClock`, `IOSTATS_TIMER_GUARD`, and Windows error formatting.

Risks and test signals: partial writes only assert in debug; `log_size_` adds intended write size when bytes were written. Auto-roll logger and env logger tests are primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_logger.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_logger.h -->
# sources/storage-engines/rocksdb/port/win/win_logger.h

Purpose: declares the Windows implementation of RocksDB `Logger`.

Important APIs/types/functions: `WinLogger` constructor, `Flush`, `Logv`, `GetLogFileSize`, `DebugWriter`, and protected `CloseImpl`.

Control flow: the header defines the logger's public override surface; formatting and handle operations are implemented in `win_logger.cc`.

State and persistence behavior: stores a Win32 file handle and counters used to persist log output.

Dependencies and integration points: included by `util_logger.h` and `env_win.cc`, depends on `rocksdb/env.h` and `SystemClock`.

Risks and test signals: lifetime/close behavior matters because log files may be renamed/deleted while open. Logger and auto-roll tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_thread.cc -->
# sources/storage-engines/rocksdb/port/win/win_thread.cc

Purpose: implements a Windows thread wrapper used when MinGW/std::thread support is not POSIX-thread backed.

Important APIs/types/functions: `WindowsThread::Init`, constructor/destructor, move assignment, `joinable`, `native_handle`, `hardware_concurrency`, `join`, `detach`, `swap`, and `Data::ThreadProc`.

Control flow: constructor binds callable arguments into `std::function<void()>`, stores them in shared `Data`, starts a thread with `_beginthreadex`, and transfers a heap-held `shared_ptr` to the thread proc. `join` waits with `WaitForSingleObject`, closes the handle, and rejects self-join. `detach` closes the handle without waiting.

State and persistence behavior: owns shared thread data, a native handle, and thread id. No persistence.

Dependencies and integration points: selected by `port_win.h` as `port::Thread` when `_POSIX_THREADS` is unavailable; used by `WinEnvThreads`.

Risks and test signals: destructor terminates if still joinable, matching `std::thread`; handle closure and detached lifetime rely on shared ownership. Thread, Env scheduling, and MinGW build tests are key.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_thread.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_thread.h -->
# sources/storage-engines/rocksdb/port/win/win_thread.h

Purpose: declares `WindowsThread`, a `std::thread`-like wrapper for Windows builds lacking suitable POSIX-thread-backed `std::thread`.

Important APIs/types/functions: templated constructor, move operations, `joinable`, `get_id`, `native_handle`, `hardware_concurrency`, `join`, `detach`, and `swap`.

Control flow: the templated constructor binds arguments and calls the hidden `Init`; all native implementation details are behind `Data`.

State and persistence behavior: stores shared implementation data and thread id; no persistence.

Dependencies and integration points: included by `port_win.h`; `std::swap` overload is supplied for compatibility with generic thread code.

Risks and test signals: template SFINAE must avoid stealing copy/move construction. Build tests and thread lifecycle tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/win_thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/xpress_win.cc -->
# sources/storage-engines/rocksdb/port/win/xpress_win.cc

Purpose: implements RocksDB's Windows XPRESS compression adapter using the Windows Compression API when `XPRESS` is enabled.

Important APIs/types/functions: `xpress::Compress`, `CompressWithMaxSize`, `Decompress`, `GetDecompressedSize`, and `DecompressToBuffer`.

Control flow: each operation creates a compressor or decompressor handle, wraps it in a RAII `unique_ptr`, calls `Compress`/`Decompress`, and handles the standard `ERROR_INSUFFICIENT_BUFFER` size-query pattern. Buffer-returning decompression allocates with `new[]` because callers delete with `delete[]`.

State and persistence behavior: stateless aside from transient compression handles and output buffers. No persistence.

Dependencies and integration points: included through `port/xpress.h` on Windows; integrates with RocksDB compression utilities when XPRESS is configured.

Risks and test signals: the implementation is absent unless both `OS_WIN` and `XPRESS` are defined. Error handling returns false/0/-1/null rather than `Status`. Compression round-trip and max-output-size tests are primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/xpress_win.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/xpress_win.h -->
# sources/storage-engines/rocksdb/port/win/xpress_win.h

Purpose: declares the Windows XPRESS compression API surface used by RocksDB.

Important APIs/types/functions: `Compress`, `CompressWithMaxSize`, `Decompress`, `GetDecompressedSize`, and `DecompressToBuffer` under `port::xpress`.

Control flow: declarations only; implementation is conditional in `xpress_win.cc`.

State and persistence behavior: no state in the header; implementation returns buffers or writes caller-provided buffers.

Dependencies and integration points: included by `port/xpress.h` for Windows builds.

Risks and test signals: caller ownership of `Decompress` return memory must remain consistent. Compression tests should cover empty input, corrupt input, and undersized output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/win/xpress_win.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/port/xpress.h -->
# sources/storage-engines/rocksdb/port/xpress.h

Purpose: platform dispatch header for XPRESS compression.

Important APIs/types/functions: no direct functions; it includes `port/win/xpress_win.h` on Windows and errors on POSIX.

Control flow: compile-time platform guard rejects POSIX XPRESS and exposes Windows XPRESS declarations.

State and persistence behavior: none.

Dependencies and integration points: used by compression code that wants XPRESS only where implemented.

Risks and test signals: build configuration must not enable XPRESS on POSIX. Build matrix tests catch this.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/port/xpress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/rocksdb.pc.in -->
# sources/storage-engines/rocksdb/rocksdb.pc.in

Purpose: CMake/pkg-config template for installed RocksDB metadata.

Important APIs/types/functions: pkg-config fields `prefix`, `includedir`, `libdir`, `Name`, `Description`, `URL`, `Version`, `Cflags`, and `Libs`.

Control flow: CMake substitutes `@...@` variables during installation to produce `rocksdb.pc`.

State and persistence behavior: persists install metadata used by downstream builds; it does not affect runtime state.

Dependencies and integration points: consumed by `pkg-config` clients compiling/linking against installed RocksDB.

Risks and test signals: missing private dependency libs may affect static linking consumers. Install/package tests and downstream compile checks are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/rocksdb.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/src.mk -->
# sources/storage-engines/rocksdb/src.mk

Purpose: Makefile source manifest defining RocksDB library, tool, test, benchmark, JNI, optional FAISS, range-tree, folly, and C/assembly source groups.

Important APIs/types/functions: variables include `LIB_SOURCES`, `LIB_SOURCES_ASM`, `LIB_SOURCES_C`, `WITH_FAISS_LIB_SOURCES`, `RANGE_TREE_SOURCES`, `TOOL_LIB_SOURCES`, `ANALYZER_LIB_SOURCES`, `MOCK_LIB_SOURCES`, `BENCH_LIB_SOURCES`, `STRESS_LIB_SOURCES`, `TEST_LIB_SOURCES`, `TOOLS_MAIN_SOURCES`, `BENCH_MAIN_SOURCES`, `TEST_MAIN_SOURCES`, `MICROBENCH_SOURCES`, and `JNI_NATIVE_SOURCES`.

Control flow: the make system includes these variables to assemble compilation units. A compiler probe conditionally enables PowerPC crc32c assembly/C sources. This subset's Windows/port/table files appear in `LIB_SOURCES`, so they are part of the RocksDB core library build.

State and persistence behavior: build metadata only; no runtime state. It determines which object files and tests are produced.

Dependencies and integration points: integrates with Makefile build targets and mirrors CMake/Buck-style source inventories. The listed tests include broad env, file, logger, table, compression, and utility coverage.

Risks and test signals: omissions or stale entries cause missing symbols or untested code. Whitespace/backslash errors can break make parsing. Full build, selected target build, and source-list consistency checks are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/src.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.cc -->
# sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.cc

Purpose: implements `AdaptiveTableFactory`, which can read multiple SST table formats while delegating writes to a configured table factory.

Important APIs/types/functions: constructor, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `NewAdaptiveTableFactory`.

Control flow: constructor fills missing factories with plain, block-based, and cuckoo defaults, and defaults writes to block-based. `NewTableReader` reads the SST footer, checks the table magic number, and dispatches to the matching factory. `NewTableBuilder` delegates directly to `table_factory_to_write_`.

State and persistence behavior: stores shared table factory pointers. It reads SST footer metadata but does not persist data itself; writes are delegated.

Dependencies and integration points: depends on table format magic numbers, `ReadFooterFromFile`, `TableFactory`, `RandomAccessFileReader`, and `WritableFileWriter`. It integrates with DB/table options where adaptive table support is selected.

Risks and test signals: unknown magic numbers return `NotSupported`; footer read failures propagate. Mixed-format DB/table tests and options-printing tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.h -->
# sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.h

Purpose: declares a `TableFactory` implementation that reads block-based, plain, or cuckoo tables adaptively.

Important APIs/types/functions: `AdaptiveTableFactory`, `Name`, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `Clone`.

Control flow: header defines the override surface and stores four factory pointers: one for writes and three read dispatch targets.

State and persistence behavior: state is only shared factory ownership. Persistence is handled by delegated table builders/readers.

Dependencies and integration points: included by options/table code that constructs adaptive factories; depends on RocksDB table and options interfaces.

Risks and test signals: `Clone` uses the default copy of shared pointers, so clone instances share underlying factories. Factory configuration and table-format compatibility tests matter.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.cc -->
# sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.cc

Purpose: implements the block-based table index reader for the standard binary-search index.

Important APIs/types/functions: `BinarySearchIndexReader::Create` and `NewIterator`.

Control flow: `Create` asserts valid inputs, optionally reads/prefetches the index block, drops it if it should remain cache-backed and unpinned, and constructs the reader. `NewIterator` obtains the index block through cache or file read, returns an error iterator on failure, otherwise asks `Block::NewIndexIterator` for a binary-search-capable iterator and transfers cache ownership to it.

State and persistence behavior: owns or references a cached index block through `CachableEntry`. No persistence; it reads table index blocks from SST files and may pin/cache them.

Dependencies and integration points: depends on `IndexReaderCommon`, `BlockBasedTable::Rep`, block cache lookup context, global sequence number handling, timestamp persistence, and table options for index block search type.

Risks and test signals: cache/pin/prefetch combinations affect lifetime and memory use. Iterator invalidation must preserve read errors. Block-based table reader, block cache, and partitioned/full-filter tests are useful.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.h -->
# sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.h

Purpose: declares the standard block-based table index reader that uses binary search over first keys of blocks.

Important APIs/types/functions: `BinarySearchIndexReader`, static `Create`, `NewIterator`, and `ApproximateMemoryUsage`.

Control flow: declaration inherits common index-block read/cache behavior from `BlockBasedTable::IndexReaderCommon`; constructor is private so callers use `Create`.

State and persistence behavior: stores index block state through the base common reader. Memory accounting includes index block memory and object size or malloc usable size.

Dependencies and integration points: used by block-based table reader when the table options select the binary-search index type. It depends on `index_reader_common.h`.

Risks and test signals: memory accounting depends on `ROCKSDB_MALLOC_USABLE_SIZE`; API drift with `IndexReaderCommon` can break table reads. Block-based table and memory usage tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.h -->
