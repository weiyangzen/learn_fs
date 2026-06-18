# subset-b-000284 research

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/lorem.c -->
# sources/compression/lz4/programs/lorem.c

Purpose: implements the lorem ipsum data generator used by LZ4 test/benchmark tooling to produce printable, text-like, compressible input. It replaces pure entropy-style random data with repeated words, sentences, and paragraphs that better exercise text compression behavior.

Important APIs/functions: exports `LOREM_genBlock()` and `LOREM_genBuffer()` from `lorem.h`. Internal helpers initialize word lengths, pack the static word table into `g_wordBuffer`, construct `g_distrib` weighted by word length, generate pseudo-random numbers with `LOREM_rand()`, and emit words/sentences/paragraphs with punctuation and capitalization. `LOREM_genBlock()` supports `first` and `fill` controls; `LOREM_genBuffer()` always starts with the canonical first sentence and fills the requested size.

Control flow: first use lazily initializes global word metadata and the weighted distribution. Generation seeds `g_randRoot`, writes the optional first sentence, then loops over paragraphs until either the output buffer is full or `fill` is false. Near buffer end, `generateLastWord()` and `writeLastCharacters()` ensure termination with punctuation, spaces, and possibly newline without writing past `g_maxChars`.

State and persistence: this file uses process-global mutable state for the destination pointer, current count, maximum size, PRNG root, word distribution, and lazily allocated word buffer. The source explicitly notes it is sequential-only and not safe for concurrent calls. `g_wordBuffer` is intentionally process-lifetime storage and is not freed.

Dependencies/integration: depends only on `lorem.h` and C runtime allocation/string/assert headers. It is built into `datagen` through the tests Makefile target, providing synthetic inputs for CLI and library validation.

Risks: concurrent calls race on globals; `assert(size < INT_MAX)` is not a runtime error path in release builds; the lazy allocation aborts on failure. The weighted distribution assumes `DISTRIB_SIZE_MAX` remains large enough for the static word table and weights.

Test signals: indirectly exercised by `tests/Makefile` targets that build `datagen` and use it throughout `test-lz4-*`, fuzzer, frametest, huge-file, dictionary, and memory tests.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/lorem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/lorem.h -->
# sources/compression/lz4/programs/lorem.h

Purpose: public header for the lorem ipsum generator used by LZ4 program tests and data generation.

Important APIs/types: declares `LOREM_genBuffer(void* buffer, size_t size, unsigned seed)` for filling a buffer with generated text and `LOREM_genBlock(void* buffer, size_t size, unsigned seed, int first, int fill)` for controlled partial/block generation returning bytes produced.

Control flow contract: callers provide a writable buffer and seed; `first` controls whether the standard opening sentence is emitted and `fill` controls whether generation stops after one paragraph or continues to fill the buffer.

State and persistence: the header exposes no state, but the implementation behind it is globally stateful and sequential-only.

Dependencies/integration: includes `<stddef.h>` for `size_t`. Included by `lorem.c` and consumers such as datagen/lorem output code in the programs tree.

Risks: no include guard in this header, so repeated inclusion relies on declarations being compatible. The API does not surface allocation or initialization failures from the implementation.

Test signals: validated indirectly whenever `datagen` builds and generated data is used in CLI round trips and benchmark/fuzzer targets.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/lorem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/lz4-exe.rc.in -->
# sources/compression/lz4/programs/lz4-exe.rc.in

Purpose: Windows resource template for the LZ4 executable, embedding version and product metadata into the generated `.rc` file.

Important fields: `FILEVERSION` and `PRODUCTVERSION` use `@LIBVER_MAJOR@`, `@LIBVER_MINOR@`, and `@LIBVER_PATCH@`; string metadata includes company, description, internal name `@PROGNAME@`, original filename `@PROGNAME@.@EXT@`, product name, product version, and copyright.

Control flow/state: declarative resource data only; substitutions happen in the build system before Windows resource compilation.

Dependencies/integration: consumed by Windows build tooling or CMake/configure logic that replaces `@...@` tokens and compiles the result into the executable.

Risks: stale token replacement would produce invalid resource metadata; copyright year range is fixed in the template; resource language/codepage is hard-coded as `040904B0` and translation `0x0409, 1200`.

Test signals: covered by Windows/package build success rather than runtime tests; version consistency is related to `checkTag.c` and release/version tests.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/lz4-exe.rc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/lz4cli.c -->
# sources/compression/lz4/programs/lz4cli.c

Purpose: top-level command-line interface for the `lz4` program and its symlink-compatible modes (`lz4cat`, `unlz4`, `lz4c`). It parses user options, chooses operation mode, configures preferences, and dispatches to compression, decompression, list, and benchmark backends.

Important APIs/functions: `main()` owns parser state and dispatch. Helpers include `usage*()`, `badusage()`, `lastNameFromPath()`, `exeNameMatch()`, `readU32FromChar()`, `longCommandWArg()`, `determineOpMode()`, `init_nbWorkers()`, and `init_cLevel()`. It calls `LZ4IO_*` APIs for file I/O, `BMK_*` APIs for benchmarks, and hidden legacy compression entry points declared locally.

Control flow: startup creates `LZ4IO_prefs_t`, sets default overwrite off, applies executable-name behavior, then scans arguments. Long and aggregated short options update mode, compression level, block settings, dictionary, checksum flags, sparse mode, remove-source behavior, threading, recursion, and benchmark controls. After argument parsing it expands recursive file lists when available, validates console stdin/stdout safety, auto-derives output names, handles test/list/benchmark modes, sets notification level, and invokes the selected `LZ4IO` or benchmark operation.

State and persistence: all parser state is local except `displayLevel` and `g_lz4c_legacy_commands`. Environment variables `LZ4_NBWORKERS` and `LZ4_CLEVEL` provide runtime defaults. The program may remove source files when `--rm` is set, may overwrite depending on preferences, and allocates temporary file-name buffers/lists freed in `_cleanup`.

Dependencies/integration: includes `platform.h`, `util.h`, `lz4conf.h`, `bench.h`, `lz4io.h`, `lz4hc.h`, and `lz4.h`. It is the integration point between user-facing CLI syntax and lower-level frame/legacy I/O in `lz4io.c`.

Risks: parser complexity and aggregated short options create compatibility edge cases; `readU32FromChar()` can overflow for very large digit strings; auto-output decompression depends on exact `.lz4` suffix; console refusal behavior is platform-dependent; `--rm` delegates destructive removal after successful I/O; legacy `lz4c` commands intentionally take precedence in that mode.

Test signals: `tests/Makefile` exercises option parsing, basic compression/decompression, multiple files, legacy mode, content size, dictionary, sparse, skippable frames, huge files, test mode, list mode, memory tests, platform/QEMU tests, and symlink modes.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/lz4cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/lz4conf.h -->
# sources/compression/lz4/programs/lz4conf.h

Purpose: compile-time configuration header for LZ4 programs.

Important macros: `LZ4_CLEVEL_DEFAULT`, `LZ4IO_MULTITHREAD`, `LZ4_NBWORKERS_DEFAULT`, `LZ4_NBWORKERS_MAX`, and `LZ4_BLOCKSIZEID_DEFAULT`. Defaults enable multithreading on Windows and disable it elsewhere unless the build overrides the macro.

Control flow/state: preprocessor-only configuration. Runtime code in `lz4cli.c`, `lz4io.c`, and `threadpool.c` uses these macros to select parser defaults, cap workers, choose single-thread or multi-thread paths, and size default blocks.

Dependencies/integration: included by CLI, I/O, and threadpool implementation. It is a build-system contract because command-line `CPPFLAGS` can override each value.

Risks: enabling `LZ4IO_MULTITHREAD` on POSIX requires pthread support but cannot be verified here; excessive `LZ4_NBWORKERS_MAX` raises resource pressure; mismatched default block size expectations can affect frame layout and checkFrame tests.

Test signals: `check_stdvars.sh` helps ensure compile-time overrides propagate; `tests/Makefile` has multiconfig, memory-usage, and CLI/thread-related targets that expose misconfiguration.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/lz4conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/lz4io.c -->
# sources/compression/lz4/programs/lz4io.c

Purpose: implements LZ4 file/stream I/O for the CLI: frame and legacy compression, decompression, pass-through, sparse output, dictionaries, metadata preservation, multithreaded chunk processing, and `--list` inspection.

Important APIs/types/functions: public APIs include `LZ4IO_defaultPreferences()`, setters, `LZ4IO_compressFilename()`, `LZ4IO_compressMultipleFilenames()`, `LZ4IO_decompressFilename()`, `LZ4IO_decompressMultipleFilenames()`, legacy compression functions used by `lz4cli.c`, and `LZ4IO_displayCompressedFilesInfo()`. Key internal types include `LZ4IO_prefs_s`, `cRess_t`, `dRess_t`, `WriteRegister`, `ReadTracker`, compression/decompression job descriptors, buffer pools, and compressed-file info structs.

Control flow: preferences are created with conservative defaults, then CLI setters mutate them. Compression opens source/destination, prepares LZ4F preferences, optionally loads a dictionary, selects single-thread or multi-thread implementation, compresses either one-shot or block/chunk loop, writes frame headers/end marks, copies file metadata, optionally removes the source, and reports timing. Legacy compression writes legacy magic and per-block little-endian sizes. Decompression creates frame resources, opens destination once or per file, repeatedly calls `selectDecoder()` for concatenated streams, handles LZ4F, legacy, skippable, and pass-through cases, writes sparse output unless in test mode, copies metadata, and optionally removes sources. `--list` scans frame headers and skips block payloads to summarize frame types, block types, checksums, compressed/uncompressed sizes, and ratios.

State and persistence: global display/timing state (`g_displayLevel`, `g_time`) controls progress output. `g_magicRead` carries a magic number from legacy decoding to the next stream. Static `nbFrames` inside `selectDecoder()` tracks concatenated stream position. File-system effects include creating/truncating outputs, sparse seeks, metadata/ownership/time copying, and optional source deletion. Threaded paths allocate threadpools and pass ownership of buffers through job descriptors.

Dependencies/integration: depends on `platform.h`, `timefn.h`, `util.h`, `lz4conf.h`, `lz4io.h`, `lz4.h`, `lz4hc.h`, `lz4frame.h`, `xxhash.h`, and `threadpool.h`. It is the core backend for CLI operations selected in `lz4cli.c`.

Risks: many fatal errors call `exit()` through `END_PROCESS`, so library-like callers cannot recover. Multi-thread paths require careful lifetime rules for stack job descriptors and buffer ownership; output ordering relies on `WriteRegister`. Sparse writing uses seeks and can fail on unsupported destinations. Pass-through is allowed only under specific preference combinations. Disabling checksum validation with `--no-crc` reduces corruption detection. `--list` mostly skips payloads and can only report content size when present in frame headers.

Test signals: covered by CLI round trips, dictionary tests, content-size tests, sparse tests, skippable-frame tests, legacy multiple-file tests, huge-file tests, `--list` tests, valgrind memory tests, `checkFrame`, fuzzers/frametest, and decompression partial tests.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/lz4io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/lz4io.h -->
# sources/compression/lz4/programs/lz4io.h

Purpose: public file/stream I/O interface used by the CLI to configure and run LZ4 compression, decompression, and listing.

Important APIs/types: defines special names `stdinmark`, `stdoutmark`, `NULL_OUTPUT`, and platform `nulmark`; opaque `LZ4IO_prefs_t`; processing functions for single and multiple files; preference setters for workers, dictionary, pass-through, overwrite, test mode, block size/mode/checksums, notification level, sparse output, content size, remove-source, and favor decompression speed; and `LZ4IO_displayCompressedFilesInfo()`.

Control flow contract: callers allocate preferences with `LZ4IO_defaultPreferences()`, mutate settings, run an operation, then free preferences. Functions return `0` for success and non-zero counts/errors for missing/skipped files.

State and persistence: preferences are heap-owned by the caller. Operations may write output files, preserve metadata, use stdout/stdin, and remove source files depending on preferences.

Dependencies/integration: included by `lz4cli.c` and implemented by `lz4io.c`; uses `<stddef.h>` only in the interface.

Risks: some setters are not documented as NULL-safe; actual error handling may terminate the process in the implementation. `NULL_OUTPUT` is the string `null`, while platform null device is `nulmark`.

Test signals: all CLI tests exercise this interface indirectly; `--list` has dedicated list tests.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/lz4io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/platform.h -->
# sources/compression/lz4/programs/platform.h

Purpose: central portability header for compiler quirks, 64-bit/large-file support, POSIX detection, console detection, binary mode, and sparse-file enablement.

Important macros/functions: sets MSVC warning/security compatibility macros, defines `__64BIT__` based on architecture probes, enables `_FILE_OFFSET_BITS=64`/large-file macros where needed, derives `PLATFORM_POSIX_VERSION`, defines `IS_CONSOLE(stdStream)`, `SET_BINARY_MODE(file)`, and `SET_SPARSE_FILE_MODE(file)`.

Control flow/state: preprocessor feature detection selects platform-specific includes and implementations. On Windows, `IS_CONSOLE()` is an inline function using `_isatty`, `_get_osfhandle`, and `GetConsoleMode`; sparse mode uses `DeviceIoControl(FSCTL_SET_SPARSE)`.

Dependencies/integration: included before many program headers, especially `util.h`, `lz4cli.c`, and `lz4io.c`, to make file offsets and console behavior consistent.

Risks: feature detection must happen before system headers that depend on feature-test macros; platform probes can miss new architectures or unusual libc environments; console detection impacts CLI safety decisions.

Test signals: platform/QEMU tests, 32-bit/64-bit interop, huge-file tests, and Windows builds exercise this portability layer.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/threadpool.c -->
# sources/compression/lz4/programs/threadpool.c

Purpose: provides a small `TPool` abstraction for LZ4 program jobs, with a no-thread fallback, a Windows completion-port implementation, and a POSIX pthread implementation.

Important APIs/functions: implements `TPool_create()`, `TPool_free()`, `TPool_submitJob()`, and `TPool_jobsCompleted()`. Internal POSIX helpers include `TPool_thread()`, `TPool_shutdown()`, `isQueueFull()`, and `TPool_submitJob_internal()`. Windows uses `WorkerThread()` and completion-port postings.

Control flow: if `LZ4IO_MULTITHREAD` is false, submitted jobs run synchronously. Windows creates worker threads bound to an I/O completion port and uses a semaphore/event pair to enforce queue capacity and completion waits. POSIX creates a circular job queue guarded by mutex/conditions; submitters block when full, workers pop and execute jobs, completion waits until the queue is empty and no threads are busy, and free triggers shutdown plus joins.

State and persistence: threadpool instances own worker handles/threads, queues, synchronization primitives, and shutdown flags. The no-thread fallback returns a static non-NULL singleton. Jobs borrow or own their argument according to caller discipline.

Dependencies/integration: depends on `lz4conf.h` and `threadpool.h`, plus Windows API or pthreads. `lz4io.c` uses it for compression/decompression worker and writer queues.

Risks: caller must keep job arguments alive until execution or transfer ownership; queue sizing can block submitters; POSIX shutdown lets active queued work drain only insofar as threads continue past shutdown conditions; Windows casts job arguments through `LPOVERLAPPED`, which is intentional but type-unsafe.

Test signals: multithreaded compression/decompression behavior is covered by CLI tests when built with `LZ4IO_MULTITHREAD=1`; memory tests can catch leaks in job ownership paths.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/threadpool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/threadpool.h -->
# sources/compression/lz4/programs/threadpool.h

Purpose: declares the `TPool` threadpool interface used by program-level LZ4 I/O.

Important APIs/types: opaque `TPool`; `TPool_create(int nbThreads, int queueSize)`, `TPool_free()`, `TPool_submitJob(TPool*, void (*)(void*), void*)`, and `TPool_jobsCompleted()`.

Control flow contract: creation requires at least one thread and queue slot in threaded builds; submit can block when the queue is full; completion waits for all queued/running jobs; free waits for running jobs before releasing resources.

State and persistence: callers own the pool pointer and must manage job argument lifetimes. The implementation may be synchronous when multithreading is disabled.

Dependencies/integration: consumed by `lz4io.c`; implemented by `threadpool.c`; exported with C linkage for C++ callers.

Risks: no cancellation API; no per-job status channel; errors inside jobs typically terminate via surrounding code's fatal macros.

Test signals: indirectly covered by threaded LZ4 I/O tests and build variants.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/threadpool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/timefn.c -->
# sources/compression/lz4/programs/timefn.c

Purpose: portable nanosecond-resolution timing implementation for progress, benchmark, and final throughput reporting.

Important APIs/functions: implements `TIME_getTime()`, `TIME_span_ns()`, `TIME_clockSpan_ns()`, `TIME_waitForNextTick()`, and `TIME_support_MT_measurements()`.

Control flow: platform selection uses `QueryPerformanceCounter` on Windows, `mach_absolute_time` on Apple, `clock_gettime(CLOCK_MONOTONIC)` when available, C11 `timespec_get` when safe, and C90 `clock()` as fallback. Common helpers subtract counters and busy-wait until a new tick for measurement accuracy.

State and persistence: Windows and Apple paths lazily cache frequency/timebase in static variables. Returned `TIME_t` values are relative counters and meaningful only for differences.

Dependencies/integration: included by `lz4io.c` for progress refresh and final timing; used by benchmark-related code through the program timing API.

Risks: fallback `clock()` is CPU time and not suitable for multi-thread wall-clock measurement; failure of platform timing calls aborts the process; `TIME_waitForNextTick()` spins.

Test signals: throughput/progress paths are indirectly exercised by CLI and benchmark tests; `TIME_support_MT_measurements()` gates warning behavior in multithreaded final timing.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/timefn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/timefn.h -->
# sources/compression/lz4/programs/timefn.h

Purpose: public timing API for LZ4 program code.

Important APIs/types: `Duration_ns` unsigned nanosecond duration, `TIME_t` wrapper struct, `TIME_INITIALIZER`, `TIME_getTime()`, `TIME_waitForNextTick()`, `TIME_support_MT_measurements()`, `TIME_span_ns()`, and `TIME_clockSpan_ns()`.

Control flow contract: callers take two `TIME_t` measurements and compute a duration; absolute values are not meaningful.

State and persistence: no exposed mutable state; implementation may cache platform timing constants.

Dependencies/integration: consumed by `lz4io.c` and other program tools needing portable timing; C++ compatible via `extern "C"`.

Risks: API assumes unsigned duration subtraction without clock wrap handling beyond practical counter size; multi-thread suitability depends on implementation path.

Test signals: exercised indirectly through progress/timing output in CLI and benchmark runs.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/timefn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/util.c -->
# sources/compression/lz4/programs/util.c

Purpose: implements platform-specific CPU/core counting used to choose default worker counts for compression.

Important APIs/functions: `UTIL_countCores()` with implementations for Windows (`GetSystemInfo`), Apple (`sysctlbyname("hw.logicalcpu")`), Linux/POSIX/BSD (`sysconf(_SC_NPROCESSORS_ONLN)` or FreeBSD sysctls), and fallback returning `1`.

Control flow: each platform implementation caches the detected count in a static variable where appropriate, falls back to one core if the query is unavailable, and on some FreeBSD sysctl failures reports an error and exits.

State and persistence: static cached core count persists for the process; no external state is modified.

Dependencies/integration: includes `util.h`, which pulls in `platform.h` and type definitions. `lz4io.c` uses this via `LZ4IO_defaultNbWorkers()`.

Risks: CPU topology detection is approximate; cached values do not reflect CPU hotplug; FreeBSD unexpected sysctl errors terminate; fallback may underutilize systems.

Test signals: indirectly covered when thread defaults are initialized; build portability tests cover compile-time availability of platform APIs.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/util.h -->
# sources/compression/lz4/programs/util.h

Purpose: shared utility header for program code, combining integer typedefs, large-file seek/stat abstractions, sleep/priority macros, file metadata helpers, string/allocation helpers, and recursive file-list generation.

Important APIs/types/functions: typedefs `BYTE`, `U16`, `S16`, `U32`, `S32`, `U64`, `S64`; `UTIL_fseek`; `UTIL_countCores()`; sleep and priority macros; `stat_t`; `UTIL_realloc()`, `UTIL_sameString()`, `UTIL_isRegFile()`, `UTIL_isRegFD()`, `UTIL_isDirectory()`, `UTIL_getOpenFileSize()`, `UTIL_getFileSize()`, `UTIL_getTotalFileSize()`, `UTIL_setFileStat()`, `UTIL_createFileList()`, and `UTIL_freeFileList()`.

Control flow: many helpers are `UTIL_STATIC` inline/static for header-only use. File-list creation copies input files into a contiguous name buffer, recursively expands directories on Windows or POSIX systems, grows buffers with `UTIL_realloc()`, and returns both a pointer table and backing buffer.

State and persistence: helpers are stateless except for filesystem side effects. `UTIL_setFileStat()` changes timestamps, ownership on POSIX, and mode. Recursive list creation allocates caller-owned memory.

Dependencies/integration: depends on `platform.h` and system stat/time/dir APIs. Used heavily by `lz4cli.c` for recursive inputs and console/file checks, and by `lz4io.c` for metadata, sizes, sparse seeks, and output preservation.

Risks: many functions return `0` both for errors and zero-sized/non-regular files; `UTIL_realloc()` frees the old pointer on failure by design; recursive traversal has no cycle/symlink policy beyond directory checks; metadata preservation may fail partially and returns negative error count.

Test signals: recursive/multiple-file CLI tests, huge-file tests, list tests, and standard-variable/build portability checks exercise these helpers indirectly.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/Makefile -->
# sources/compression/lz4/tests/Makefile

Purpose: orchestrates LZ4 test program builds and integration tests for CLI, library, frame API, fuzzers, benchmarks, installation, ABI, platform, memory, and freestanding scenarios.

Important targets/variables: sets `LIBDIR`, `PRGDIR`, warning/debug/user flags, include paths, `LZ4`, `TEST_FILES`, `FUZZER_TIME`, and `NB_LOOPS`. Builds `fullbench`, `fuzzer`, `frametest`, `roundTripTest`, `datagen`, `checkFrame`, decompression partial tests, `abiTest`, and `checkTag`. Test targets include `test-lz4-*`, `test-amalgamation`, `test-install`, `test-interop-32-64`, `test-platform`, `test-mem`, and `test-freestanding`.

Control flow: includes shared make definitions, defines build recipes, then gates many runtime tests behind `POSIX_ENV=Yes`. Test targets compose smaller shell scripts and generated data pipelines, with separate target sets for essentials, full CLI, 32-bit, fuzzer, frametest, memory, and install/list validation.

State and persistence: creates binaries, object files, temporary `tmp*` files, version-test directories, symlinks for `lz4c/unlz4/lz4cat`, and generated amalgamation `lz4_all.c`; `clean` removes these artifacts and delegates clean to lib/programs.

Dependencies/integration: integrates library sources, program sources, shell/Python tests, QEMU variables, valgrind, md5 tools, and installed liblz4 checks.

Risks: broad environment assumptions for POSIX tests; 32-bit and QEMU targets depend on toolchain availability; temporary-file naming discipline is important to avoid deleting unrelated files; recursive make must propagate user flags.

Test signals: this file is itself the central test signal map for the researched program files and exposes targeted coverage for compression, decompression, parser, dictionary, sparse, skippable, content-size, huge files, ABI, CMake install, and memory behavior.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/abiTest.c -->
# sources/compression/lz4/tests/abiTest.c

Purpose: validates ABI compatibility expectations by building against headers and linking to liblz4, then performing a streaming round trip on a provided file.

Important APIs/functions: global `LZ4_stream_t` and `LZ4_streamDecode_t` test ABI-visible struct availability. `roundTripTest()` uses `LZ4_compress_fast_continue()`, `LZ4_setStreamDecode()`, and `LZ4_decompress_safe_continue()`. Helpers compare buffers, read files, detect directories, and report version strings.

Control flow: `main()` prints compile-time and linked library versions, requires one filename, loads it into memory, compresses/decompresses via streaming APIs, validates size and byte equality, and exits non-zero on usage/allocation/I/O/round-trip errors.

State and persistence: uses global stream state to test ABI struct layout and zero-initialization. Reads the input file only; no persistent output is written.

Dependencies/integration: includes `xxhash.h`, `lz4.h`, and `lz4frame.h`; Makefile target links with `-llz4` and Python `test-lz4-abi.py` coordinates ABI scenarios.

Risks: loads entire input into memory; `getFileSize()` returns `0` for errors and zero-size files; `loadFile()` calls `fclose(f)` even when a directory path may have produced NULL on some platforms.

Test signals: `abiTests` in the Makefile runs the higher-level ABI test suite; successful output says no problem detected.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/abiTest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/checkFrame.c -->
# sources/compression/lz4/tests/checkFrame.c

Purpose: verifies that compressed LZ4 frame block size metadata and actual decoded block sizes match expected values.

Important APIs/functions: `createCResources()` allocates buffers and an `LZ4F_decompressionContext_t`; `frameCheck()` reads compressed input, calls `LZ4F_getFrameInfo()` and `LZ4F_decompress()`, checks `blockSizeID` and decoded block sizes, and detects unfinished streams; `main()` parses `-b#`, `-B#`, verbosity, and file argument.

Control flow: command-line parsing requires both block size ID and block size. For each frame, the checker consumes frame info, then alternates partial reads and decompression calls. It tracks whether a block is split across input reads and validates full block sizes except final/end-of-frame cases.

State and persistence: local resource struct owns buffers and decompression context. Static display/no-prompt/pause variables control CLI behavior. No output files are written.

Dependencies/integration: includes `util.h`, `lz4frame.h` multiple times intentionally to test header idempotence/static-linking mode, `lz4.h`, and `xxhash.h`. Built by the Makefile and used by frame-related tests.

Risks: assumes expected values are supplied correctly; block-size validation has special handling around frame checksums/end marks; errors return numeric codes through `EXM_THROW`.

Test signals: Makefile builds `checkFrame`; content-size/frame tests and direct target execution can detect regressions in frame header/block emission.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/checkFrame.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/checkTag.c -->
# sources/compression/lz4/tests/checkTag.c

Purpose: release/version validation tool that checks whether a tag string is compatible with the compiled LZ4 version.

Important APIs/functions: `validate()` requires a tag starting with `v`, longer than `LZ4_VERSION_STRING`, and whose characters after `v` begin with the exact version string. `main()` handles usage, prints version/tag, and exits `0`, `1`, or `2`.

Control flow/state: no persistent state; purely validates a single command-line argument.

Dependencies/integration: includes `lz4.h` for `LZ4_VERSION_STRING`; built by the Makefile as `checkTag`.

Risks: intentionally permits any suffix after the first three-version string, so pre-release/build metadata policy must be enforced elsewhere if needed. It rejects tags exactly equal in length to the version plus `v` because it requires additional suffix length.

Test signals: useful in automated release/tag checks; not part of normal compression round trips.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/checkTag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/check_liblz4_version.sh -->
# sources/compression/lz4/tests/check_liblz4_version.sh

Purpose: shell helper to verify that a binary is dynamically linked against `liblz4`.

Important commands: runs `ldd "$1"` through `grep liblz4` under `set -e`, causing failure if the dependency is absent or `ldd` fails.

Control flow/state: no persistent state; one positional argument is expected.

Dependencies/integration: depends on POSIX shell, `ldd`, and `grep`; used by install/linkage tests around shared-library builds.

Risks: Linux-specific `ldd` behavior; unquoted `$1` in the script can break paths with spaces; static links intentionally fail this check.

Test signals: success is any `ldd` line containing `liblz4`; failure exits non-zero through `set -e`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/check_liblz4_version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/check_stdvars.sh -->
# sources/compression/lz4/tests/check_stdvars.sh

Purpose: validates that standard make variables supplied by users (`CC`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `LDLIBS`) propagate into recursive compile and link commands.

Important logic: reads a build log path from argv, defines marker flags, classifies non-comment/non-echo lines as compile when they contain ` -c ` or link when they look like compiler invocations without `-c`, then checks compile lines for CC/CFLAGS/CPPFLAGS markers and link lines for LDFLAGS/LDLIBS markers.

Control flow/state: accumulates seen/ok counters and a `fail` flag. `report()` emits missing-marker diagnostics. Exits `1` on any missing marker, otherwise prints a success summary.

Dependencies/integration: POSIX shell only; intended to consume dry-run verbose make logs produced with injected marker definitions.

Risks: line classification is heuristic and compiler-name based; paths/commands with unusual spacing may be misclassified; it checks marker presence rather than semantic ordering.

Test signals: direct success/failure output from this script protects the build system's user-variable propagation.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/check_stdvars.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/cmake/CMakeLists.txt -->
# sources/compression/lz4/tests/cmake/CMakeLists.txt

Purpose: CMake installation-consumption smoke test for LZ4's exported package configuration.

Important commands: requires CMake `3.5...4.0.2`, calls `find_package(lz4 CONFIG REQUIRED)`, checks `LZ4::lz4` exists, checks `LZ4::lz4_shared` has `LOCATION` and `INTERFACE_INCLUDE_DIRECTORIES`, then builds two `decompress-partial` executables linked against `LZ4::lz4_shared` and `lz4::lz4`.

Control flow/state: configure-time fatal errors catch missing exported targets/properties; build-time linking catches unusable imported targets. No runtime test is declared here.

Dependencies/integration: uses the adjacent `tests/decompress-partial.c` source and an installed/exported LZ4 CMake package.

Risks: `LOCATION` is not always preferred for modern CMake imported target workflows, but this test intentionally verifies the property is populated. It assumes both uppercase and lowercase namespace targets are exported.

Test signals: configure/build success indicates installed CMake package targets are discoverable and usable by downstream C projects.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/cmake/CMakeLists.txt -->
