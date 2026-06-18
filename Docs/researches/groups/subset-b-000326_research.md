# subset-b-000326 research

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/fileio_asyncio.h -->
# sources/compression/zstd/programs/fileio_asyncio.h

## Purpose

This header declares zstd CLI asynchronous file I/O pools. It abstracts read and write buffering behind pool contexts so `fileio` can overlap disk I/O with compression work while retaining a serial worker-thread implementation today.

## Important APIs, Types, and Functions

`IOPoolCtx_t` stores common pool state: thread pool, active flag, job array, current `FILE*`, mutex, available job stack, and job buffer size. `ReadPoolCtx_t` adds EOF/offset tracking, held current job, coalescing buffer, exposed `srcBuffer`, completed job queue, and completion condition variable. `WritePoolCtx_t` adds sparse-write skip accounting. `IOJob_t` carries target context, file, buffer, used byte count, and offset. Public APIs create/free pools, set async mode, set/get/close files, acquire/release/enqueue write jobs, end sparse writes, consume/refill read buffers, and report `AIO_supported()`.

## Control Flow, State, and Persistence

Callers create a read or write pool with a maximum buffer size, set a file, then repeatedly consume read buffers or enqueue filled write jobs. The file pointer belongs to the pool until close/free. Job ownership is explicit: acquired jobs must be released or queued, queued jobs must not be touched, and file switching requires all queued work to finish.

## Dependencies and Integration Points

It depends on zstd common types, `FIO_prefs_t`, `platform.h`, `util.h`, `pool.h`, and `threading.h`. The implementation is consumed by `fileio.c` and exposed indirectly through CLI options such as `--asyncio` and `--no-asyncio`.

## Risks and Test Signals

Main risks are race conditions around job arrays, stale file pointers when switching files, buffer lifetime misuse by consumers retaining `srcBuffer`, and sparse-write finalization ordering. Tests should exercise async on/off paths, stdin/stdout style files, sparse output, close/free while queues are empty, and large inputs that require coalescing.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/fileio_asyncio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/fileio_common.h -->
# sources/compression/zstd/programs/fileio_common.h

## Purpose

This header centralizes common file-I/O macros for the zstd CLI: byte-unit helpers, display/progress macros, zstd error checking wrappers, and portable large-file seeking/telling.

## Important APIs, Types, and Functions

It declares external globals `g_display_prefs` and `g_displayClock`, then defines `DISPLAY*`, `DISPLAY_PROGRESS`, `DISPLAY_SUMMARY`, `DISPLAYUPDATE`, `EXM_THROW`, `CHECK_V`, and `CHECK`. `LONG_SEEK` and `LONG_TELL` resolve to `fseeko`, `ftello`, MSVC 64-bit calls, MinGW variants, or Windows `SetFilePointerEx` helpers depending on platform.

## Control Flow, State, and Persistence

Display updates are gated by verbosity, progress policy, and a refresh interval of roughly one sixth of a second. `EXM_THROW` prints through the display layer and exits, so callers treat failed zstd operations as fatal in paths using `CHECK`.

## Dependencies and Integration Points

It depends on zstd error helpers, `FIO_display_prefs_t`, `platform.h`, and `timefn.h`. It is included by CLI file I/O modules and `zstdcli.c`.

## Risks and Test Signals

Macros evaluate some arguments multiple times (`MAX`, `MIN`, display varargs) and `EXM_THROW` terminates the process. Large-file seeking is platform-sensitive. Tests should include quiet/verbose/progress behavior, 32-bit large-file builds, Windows seek/tell builds, and zstd API error propagation.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/fileio_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/fileio_types.h -->
# sources/compression/zstd/programs/fileio_types.h

## Purpose

This header defines shared preference and dictionary data structures used by zstd CLI file I/O, compression, decompression, and dictionary handling code.

## Important APIs, Types, and Functions

`FIO_progressSetting_e` controls automatic, never, or always progress display. `FIO_display_prefs_t` stores display level and progress policy. `FIO_compressionType_t` selects zstd, gzip, xz, lzma, or lz4 output. `FIO_prefs_t` is the central mutable preferences object, covering algorithm parameters, sparse/dict/checksum options, adaptive and LDM settings, stream-size hints, source removal and overwrite behavior, async I/O, memory/thread limits, block-device/pass-through behavior, patch mode, and mmap dictionary policy. `FIO_Dict_t` owns loaded or mapped dictionary data plus a Windows handle when needed.

## Control Flow, State, and Persistence

The file has no logic; it is a contract for state populated by `zstdcli.c` and consumed by `fileio` routines. Preferences are process-local and persist only for the CLI invocation.

## Dependencies and Integration Points

It enables `ZSTD_STATIC_LINKING_ONLY` before including `zstd.h`, so internal/advanced zstd parameter types are visible. It integrates with `fileio.h`, `fileio_asyncio.h`, and CLI parsing.

## Risks and Test Signals

`FIO_prefs_t` contains many interdependent fields where defaults matter. Tests should cover option translation from CLI flags, compression format selection, mmap versus malloc dictionaries, async toggles, and pass-through/block-device policy.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/fileio_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/lorem.c -->
# sources/compression/zstd/programs/lorem.c

## Purpose

This file implements a deterministic lorem-ipsum text generator used by zstd tests and benchmarks to produce printable, compressible sample data with text-like repetition.

## Important APIs, Types, and Functions

Public functions are `LOREM_genBuffer()` and `LOREM_genBlock()`. Internally it keeps a static word pool, weights by word length, a generated distribution table, and generator globals `g_ptr`, `g_nbChars`, `g_maxChars`, and `g_randRoot`. Helpers initialize the weighted distribution, produce pseudo-random numbers, write truncation-safe final characters, generate words/sentences/paragraphs, and emit the canonical first sentence.

## Control Flow, State, and Persistence

`LOREM_genBlock()` initializes output pointers and seed, lazily builds the global word distribution once, optionally writes the first sentence, then generates paragraphs until the buffer is full or one paragraph is produced in non-fill mode. If a word would overrun the requested size, `writeLastCharacters()` terminates the buffer with punctuation, spaces, and newline when possible.

## Dependencies and Integration Points

It depends only on `lorem.h`, `assert.h`, `limits.h`, and `string.h`. Test programs such as `datagen` and `fullbench` compile it for synthetic input generation.

## Risks and Test Signals

The implementation is explicitly not thread-safe because generation state is global. It asserts `size < INT_MAX` and relies on static distribution initialization without locking. Tests should verify deterministic output for fixed seeds, exact byte counts, first-sentence behavior, non-fill mode, tiny buffer boundaries, and sequential repeated calls.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/lorem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/lorem.h -->
# sources/compression/zstd/programs/lorem.h

## Purpose

This header exposes the lorem-ipsum generator API for zstd tools and tests.

## Important APIs, Types, and Functions

`LOREM_genBuffer(void* buffer, size_t size, unsigned seed)` fills exactly the requested buffer size with deterministic compressible text. `LOREM_genBlock(void* buffer, size_t size, unsigned seed, int first, int fill)` adds control over whether to include the canonical first sentence and whether to fill the whole buffer or emit at most one paragraph, returning the number of bytes generated.

## Control Flow, State, and Persistence

The header declares a synchronous generation contract only. State is implementation-local in `lorem.c`, and output is written directly into the caller-provided memory.

## Dependencies and Integration Points

It includes `<stddef.h>` for `size_t` and is used by `datagen`, benchmark programs, and tests needing text-like synthetic data.

## Risks and Test Signals

Callers must provide a valid writable buffer and should not expect thread safety from the implementation. Tests should compile both C and C++ inclusions, verify return values from `LOREM_genBlock()`, and compare deterministic output across seeds and sizes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/lorem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/platform.h -->
# sources/compression/zstd/programs/platform.h

## Purpose

This portability header normalizes compiler, large-file, POSIX, console, binary-mode, sparse-file, symbol-list, priority, and sleep feature detection for zstd programs.

## Important APIs, Types, and Functions

It defines MSVC warning/security compatibility macros, detects 64-bit targets, enables large-file macros on 32-bit systems, computes `PLATFORM_POSIX_VERSION`, exposes `IS_CONSOLE()`, `SET_BINARY_MODE()`, `SET_SPARSE_FILE_MODE()`, `ZSTD_SPARSE_DEFAULT`, `ZSTD_START_SYMBOLLIST_FRAME`, `ZSTD_SETPRIORITY_SUPPORT`, and `ZSTD_NANOSLEEP_SUPPORT`. On Windows, `IS_CONSOLE()` checks both `_isatty()` and `GetConsoleMode()`.

## Control Flow, State, and Persistence

There is no runtime persistence except inline Windows console detection. Most behavior is decided at preprocessing time, so the same source compiles different code paths depending on OS and feature-test macros.

## Dependencies and Integration Points

It conditionally includes `unistd.h`, `stdio.h`, `io.h`, `fcntl.h`, `windows.h`, and `winioctl.h`. Nearly every zstd CLI support module includes it before platform-sensitive system headers.

## Risks and Test Signals

Feature detection can accidentally expose or hide APIs on unusual libc/OS combinations. Tests should cover Windows console behavior, POSIX large-file seeking, macOS sparse default, non-POSIX fallback builds, and build matrices for Linux, BSD, MinGW, MSVC, Cygwin, and AIX-like targets.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/timefn.c -->
# sources/compression/zstd/programs/timefn.c

## Purpose

This file implements cross-platform monotonic or best-available high-resolution timing helpers for zstd benchmarks, progress refreshes, and tracing.

## Important APIs, Types, and Functions

`UTIL_getTime()` has platform-specific implementations: Windows `QueryPerformanceCounter`, macOS `mach_absolute_time`, POSIX `clock_gettime(CLOCK_MONOTONIC)`, C11 `timespec_get`, or C90 `clock()` fallback. Common helpers are `UTIL_getSpanTimeNano()`, `UTIL_getSpanTimeMicro()`, `UTIL_clockSpanMicro()`, `UTIL_clockSpanNano()`, `UTIL_waitForNextTick()`, and `UTIL_support_MT_measurements()`.

## Control Flow, State, and Persistence

Windows and macOS paths lazily cache conversion factors in static variables. Span helpers subtract opaque nanosecond counters. `UTIL_waitForNextTick()` busy-waits until clock resolution advances. The fallback `clock()` path marks multi-threaded measurements unsupported.

## Dependencies and Integration Points

It includes `timefn.h` and `platform.h`, plus platform timing headers. `fileio_common.h`, benchmark code, and `zstdcli_trace.c` use these helpers.

## Risks and Test Signals

Clock APIs abort on unexpected failures. Busy-waiting can cost CPU, and `clock()` measures process CPU time rather than wall time. Tests should validate monotonic spans, nonzero tick waits, `UTIL_support_MT_measurements()` by platform, and benchmark stability on Windows/macOS/Linux/C11 fallback builds.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/timefn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/timefn.h -->
# sources/compression/zstd/programs/timefn.h

## Purpose

This header declares zstd's precise-time abstraction used by CLI progress display, benchmarks, and trace logging.

## Important APIs, Types, and Functions

`PTime` is a 64-bit nanosecond counter type using `uint64_t` when available or `unsigned long long` otherwise. `UTIL_time_t` wraps a `PTime` and has `UTIL_TIME_INITIALIZER`. Declared functions obtain current time, wait for a clock tick, report multi-thread measurement support, and compute elapsed nanoseconds or microseconds. `SEC_TO_MICRO` defines one million microseconds per second.

## Control Flow, State, and Persistence

The header exposes an opaque relative-time contract: absolute `UTIL_time_t` values are not meaningful, only differences between two values are.

## Dependencies and Integration Points

It conditionally includes `<stdint.h>` or `<inttypes.h>` and is used by `timefn.c`, `fileio_common.h`, benchmark code, and tracing.

## Risks and Test Signals

Consumers must not persist or compare absolute timestamps across processes. Tests should compile under C89/C99/C++ modes, verify initializer use, and confirm elapsed-time helpers match expected units.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/timefn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/util.c -->
# sources/compression/zstd/programs/util.c

## Purpose

This file implements zstd CLI utility behavior: user confirmation, stat/chmod/chown/utime wrappers, file-type checks, console fakes for tests, file size and human-readable formatting, file-list loading/merging/expansion, mirrored output directory creation, and CPU core counting.

## Important APIs, Types, and Functions

Public functions mirror `util.h`. File metadata APIs include `UTIL_stat`, `UTIL_fstat`, `UTIL_setFileStat`, `UTIL_setFDStat`, `UTIL_utime`, `UTIL_chmod`, and file-type predicates. File-list APIs include `UTIL_createFileNamesTable_fromFileList`, `UTIL_allocateFileNamesTable`, `UTIL_mergeFileNamesTable`, `UTIL_expandFNT`, and `UTIL_createExpandedFNT`. Output directory helpers include `UTIL_createMirroredDestDirName` and `UTIL_mirrorSourceFilesDirectories`. Core counting is implemented per Windows, Apple, Linux, FreeBSD, other BSD/Cygwin, and fallback.

## Control Flow, State, and Persistence

Metadata wrappers optionally trace nested calls via global `g_traceFileStat` and `g_traceDepth`. File-list loading stats the list path, permits regular files, FIFOs, and `/dev/fd` or `/proc/self/fd` style paths, reads up to 50 MB, converts newlines to NUL separators, and assembles an owned `FileNamesTable`. Directory expansion recursively walks platform directory APIs and optionally skips symlinks. Mirrored output rejects path components equal to `..`, trims leading root/current-directory markers, creates unique parent directories, and copies source directory modes where possible. Core counts are cached in static variables.

## Dependencies and Integration Points

It depends on `platform.h`, libc filesystem APIs, Windows APIs, POSIX directory APIs, and zstd common `U64`. `zstdcli.c`, `fileio`, test binaries, benchmark tools, and CLI shell tests rely on it.

## Risks and Test Signals

Risks include platform-specific stat semantics, permission/owner update failures hidden as counts, file-list memory limits, pathname edge cases in mirrored output, symlink recursion policy, and static core-count caching that can conflate logical and physical calls if called in a different order on some platforms. Tests should cover file lists from files/FIFOs/fd paths, symlink filtering, `..` rejection, output-dir mirroring, mtime/permissions preservation, console fake flags, block/FIFO detection, and core-count fallbacks.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/util.h -->
# sources/compression/zstd/programs/util.h

## Purpose

This header declares zstd CLI portability utilities for console policy, filesystem metadata, file-list management, directory mirroring, sleeps/priority, and CPU core counts.

## Important APIs, Types, and Functions

It defines `UTIL_fseek`, `UTIL_sleep`, `UTIL_sleepMilli`, `SET_REALTIME_PRIORITY`, `UTIL_STATIC`, `stat_t`, `mode_t`, `PATH_SEP`, and `STRDUP`. It declares confirmation and console helpers, stat/set-stat/chmod/utime wrappers, file-type checks, size helpers, `UTIL_HumanReadableSize_t`, extension and directory-mirroring functions, `FileNamesTable`, file-list create/merge/expand/search APIs, and `UTIL_countCores` plus physical/logical wrappers.

## Control Flow, State, and Persistence

The header describes ownership conventions: some file tables own buffers, read-only tables borrow names, merge consumes inputs, and `UTIL_refFilename` requires preallocated capacity. Actual persistence is limited to process-local utility globals in `util.c`.

## Dependencies and Integration Points

It includes `platform.h`, C/POSIX headers, zstd `mem.h`, and conditionally `libgen.h`. It is a core include for CLI, file I/O, tests, and benchmark support.

## Risks and Test Signals

Consumers must respect table ownership and borrowed-name lifetimes. Platform macros can alter ABI-visible typedefs. Tests should compile across Windows/POSIX, validate file table ownership/freeing, exercise `UTIL_HAS_CREATEFILELIST` and `UTIL_HAS_MIRRORFILELIST`, and verify path separator behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/windres/verrsrc.h -->
# sources/compression/zstd/programs/windres/verrsrc.h

## Purpose

This tiny header provides the minimal Windows resource constants needed to build `zstd.res` from `zstd.rc` when the normal Windows SDK definitions are unavailable or intentionally minimized.

## Important APIs, Types, and Functions

It defines `VS_VERSION_INFO`, `VS_FFI_FILEFLAGSMASK`, `VOS_NT_WINDOWS32`, `VFT_DLL`, and `VFT2_UNKNOWN`. There are no functions or types.

## Control Flow, State, and Persistence

There is no control flow or runtime state. Constants are consumed at resource compilation time.

## Dependencies and Integration Points

It integrates with the `programs/windres` resource build path for Windows version metadata.

## Risks and Test Signals

The risk is stale or incomplete resource constants causing incorrect Windows version resources. Test signals are successful resource compilation and inspection of generated executable metadata on Windows/MinGW builds.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/windres/verrsrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/zstdcli.c -->
# sources/compression/zstd/programs/zstdcli.c

## Purpose

This is the zstd command-line entry point. It parses executable aliases and CLI options, initializes preferences, dispatches to compression, decompression, test, list, benchmark, and dictionary-training subsystems, and handles process-level cleanup.

## Important APIs, Types, and Functions

Key helpers include `checkLibVersion`, `exeNameMatch`, `usage`, `usageAdvanced`, `badUsage`, numeric parsers for unsigned/int/size suffixes, `longCommandWArg`, dictionary parameter parsers, adaptive/compression parameter parsers, `setMaxCompression`, `printVersion`, `printDefaultCParams`, `printActualCParams`, `init_cLevel`, `init_nbWorkers`, and `main`. `zstd_operation_mode` selects compress, decompress, test, bench, train, or list. Global tuning state tracks overlap and LDM parameters.

## Control Flow, State, and Persistence

`main()` creates `FIO_prefs_t`, `FIO_ctx_t`, and filename tables, maps program names such as `zstdmt`, `unzstd`, `zstdcat`, `gzip`, `xz`, and `lz4` variants to default modes, then walks arguments. Long and short options update local variables and preference objects; `--filelist` inputs are loaded and merged; recursive paths are expanded; symlinks are ignored unless forced. It then branches to list, benchmark, dictionary training, compression, or decompression/test. Before dispatch it validates console safety, output mode, compression levels, dictionary/patch conflicts, progress policy, and memory limits. `_end` frees contexts/tables, handles optional pause, finishes tracing, and returns the operation result.

## Dependencies and Integration Points

It integrates with `fileio.h`, `fileio_common.h`, `fileio_asyncio.h`, `benchzstd.h`, `dibio.h`, `zstdcli_trace.h`, zstd library APIs, and utility filesystem helpers. Environment variables `ZSTD_CLEVEL` and `ZSTD_NBTHREADS` influence defaults.

## Risks and Test Signals

The parser has many interacting modes, optional build features, and alias-specific defaults. Risks include malformed numeric suffix handling, stdout/stderr console policy regressions, incorrect filelist merge semantics, multi-thread default differences, format-specific behavior, and conflicting dictionary/patch options. Tests should cover help/version, bad arguments, memory suffixes, output-dir validation, gzip compatibility, pass-through, recursive/filelist input, async toggles, benchmark/train/list modes, and cleanup on early returns.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/zstdcli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/zstdcli_trace.c -->
# sources/compression/zstd/programs/zstdcli_trace.c

## Purpose

This file implements optional zstd CLI trace logging. When `ZSTD_TRACE` is enabled, it overrides weak zstd trace hooks and records compression/decompression metrics as CSV rows.

## Important APIs, Types, and Functions

Public APIs are `TRACE_enable(filename)` and `TRACE_finish()`. Internal state includes `g_traceFile`, `g_mutexInit`, `g_mutex`, and `g_enableTime`. `TRACE_log()` extracts compression level and worker count from trace params and writes algorithm, version, method, mode, level, workers, dictionary size, input/output sizes, duration, ratio, and speed. Hook overrides are `ZSTD_trace_compress_begin/end` and `ZSTD_trace_decompress_begin/end`.

## Control Flow, State, and Persistence

`TRACE_enable()` appends to the target file and writes a CSV header when the path was not already a regular file. It initializes a mutex and starts a relative clock. Begin hooks return nanoseconds since enable; end hooks compute durations and log rows under the mutex. `TRACE_finish()` closes the file and destroys the mutex. In non-trace builds the APIs are no-ops.

## Dependencies and Integration Points

It depends on `timefn`, `util`, zstd static APIs, `zstd_trace.h`, and threading macros. `zstdcli.c` enables it via `--trace`.

## Risks and Test Signals

Risks include trace file open failure silently disabling output, division by compressed size when malformed trace data reports zero, mutex initialization failure, and version mismatch assertions. Tests should cover appending/header behavior, concurrent compression with multiple workers, disabled-trace builds, and CSV content for compress and decompress paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/zstdcli_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/zstdcli_trace.h -->
# sources/compression/zstd/programs/zstdcli_trace.h

## Purpose

This header exposes the minimal trace-control API for the zstd CLI.

## Important APIs, Types, and Functions

`TRACE_enable(char const* filename)` starts logging trace output to a path. `TRACE_finish(void)` shuts tracing down and releases resources. There are no public structs or constants.

## Control Flow, State, and Persistence

The header intentionally hides all trace state. Implementations either enable CSV logging and zstd hook overrides or compile to no-ops when tracing support is disabled.

## Dependencies and Integration Points

It is included by `zstdcli.c` and implemented by `zstdcli_trace.c`.

## Risks and Test Signals

Callers should pair enable with finish through normal cleanup. Tests should verify builds with and without `ZSTD_NOTRACE`, that `--trace` accepts a filename, and that cleanup runs on normal and early-return CLI paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/zstdcli_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/zstdgrep -->
# sources/compression/zstd/programs/zstdgrep

## Purpose

This shell script implements `zstdgrep` and alias-compatible `zegrep`/`zfgrep` behavior by decompressing zstd inputs with `zstdcat` and piping them into grep.

## Important APIs, Types, and Functions

Environment variables `GREP` and `ZCAT` override the grep and decompressor commands. The script parses grep options that take arguments, recognizes `-e` and `-f`, handles `--`, `-`, `-h`, and arbitrary short options, and derives extended/fixed grep mode from its executable name.

## Control Flow, State, and Persistence

It first separates grep options from the pattern and file list. With no files, it runs decompression on stdin and greps stdin. With files, it optionally forces `-H` labels for multiple files, then loops over inputs and pipes each decompressed stream to grep with `--label`. Exit status is 1 if any grep invocation fails, otherwise 0.

## Dependencies and Integration Points

It depends on POSIX `sh`, `grep`, and `zstdcat`. CLI tests wrap it through `tests/cli-tests/bin/zstdgrep`.

## Risks and Test Signals

The script builds `grep_args` as a string and intentionally disables globbing around unquoted expansion, so unusual option values with whitespace are risky. `-f` mode ignores the normal pattern and feeds `-` as grep's pattern-file argument. Tests should cover stdin, multiple files with labels, `-e`, `-f`, `-h`, alias names, bad compressed files, and overridden `GREP`/`ZCAT`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/zstdgrep -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/zstdless -->
# sources/compression/zstd/programs/zstdless

## Purpose

This shell script implements `zstdless` by configuring `less` to transparently decompress zstd files through `zstd -cdfq`.

## Important APIs, Types, and Functions

Environment variable `ZSTD` overrides the zstd executable. The script exports `LESSOPEN="|-${zstd} -cdfq %s"` and then `exec`s `less "$@"`.

## Control Flow, State, and Persistence

It has no persistent state beyond the exported `LESSOPEN` environment for the `less` process. All user arguments are passed directly to `less`, not zstd.

## Dependencies and Integration Points

It depends on POSIX `sh`, `less`, and zstd. CLI tests wrap it through `tests/cli-tests/bin/zstdless`.

## Risks and Test Signals

Behavior depends on `less` supporting `LESSOPEN` and on shell/environment quoting. Tests should cover valid compressed input, pass-through of less flags, missing files, and custom `ZSTD` paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/zstdless -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/DEPRECATED-test-zstd-speed.py -->
# sources/compression/zstd/tests/DEPRECATED-test-zstd-speed.py

## Purpose

This deprecated Python script continuously benchmarks zstd branches and emails warnings when speed or compression ratio regresses relative to previous results.

## Important APIs, Types, and Functions

Core helpers include `execute`, `does_command_exist`, `send_email`, `send_email_with_attachments`, `git_get_branches`, `git_get_changes`, `get_last_results`, `benchmark_and_compare`, `update_config_file`, `double_check`, and `test_commit`. Command-line arguments define test files, email recipients, dictionary, repo URL, speed/ratio thresholds, load limit, compression level range, sleep interval, timeout, dry-run, and verbosity.

## Control Flow, State, and Persistence

The script validates test files and dictionary, requires `mail` or `mutt`, clones the repo into `speedTest/zstd` if needed, writes `speedTest.pid`, then loops forever. On each tick it fetches branches, detects new commits, builds gcc/clang/32-bit binaries, records MD5/compiler metadata, benchmarks files, appends result files, and sends alerts. It persists commit markers and result/log/email files under `speedTest`.

## Dependencies and Integration Points

It depends on Git, make, gcc, clang, taskset on Linux, mail/mutt, and zstd program make targets. It is superseded by `automated_benchmarking.py`.

## Risks and Test Signals

Risks include `shell=True` command construction, no filename-with-space support, persistent pid cleanup only on keyboard interrupt, load-average dependence, external email tools, and branch-name result-file collisions. Test signals are mostly operational: dry-run path, clone/build success, result parsing, timeout handling, alert generation, and cleanup of `speedTest.pid`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/DEPRECATED-test-zstd-speed.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/Makefile -->
# sources/compression/zstd/tests/Makefile

## Purpose

This Makefile builds zstd test programs and defines the main test targets for fuzzing, streaming, benchmarking, CLI tests, compatibility checks, valgrind runs, and format-specific coverage.

## Important APIs, Types, and Functions

It imports `../lib/libzstd.mk`, derives zstd object lists, configures multithread flags, and defines targets including `fullbench`, `fuzzer`, `zstreamtest`, sanitizer variants, `paramgrill`, `datagen`, `decodecorpus`, `poolTests`, `checkTag`, `test`, `check`, `test-cli-tests`, `update-cli-tests`, `test32`, `test-all`, `test-valgrind`, `test-lz4`, and clean helpers. Variables such as `ZSTD_LEGACY_SUPPORT`, `DEBUGLEVEL`, `PYTHON`, `FUZZERTEST`, `ZSTREAM_TESTTIME`, `QEMU_SYS`, and `CLI_TEST_ARGS` tune behavior.

## Control Flow, State, and Persistence

Build targets compile library objects into local test executables, often with separate multithread and 32-bit object prefixes. Test targets build prerequisites, run binaries with configured time limits, invoke `playTests.sh` and `cli-tests/run.py`, and remove generated artifacts through `clean`.

## Dependencies and Integration Points

It integrates the zstd library, programs directory, fuzz directory, CLI test harness, Python scripts, shell tools, QEMU prefixes, valgrind, diff/gdiff, and platform-specific OS detection.

## Risks and Test Signals

Risks include fragile platform filters, unavailable 32-bit toolchains, dynamic-library targets documented as broken, long-running fuzz tests, and generated temporary files. Passing `make check`, `make test`, `make test32`, `make test-cli-tests`, and selected sanitizer/valgrind targets are the primary signals.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/automated_benchmarking.py -->
# sources/compression/zstd/tests/automated_benchmarking.py

## Purpose

This Python script benchmarks zstd builds for open pull requests or local/current builds and reports compression/decompression speed regressions.

## Important APIs, Types, and Functions

It fetches PR metadata from GitHub with `get_new_open_pr_builds`, identifies latest merge hashes, clones/builds repos with `clone_and_build`, parses benchmark output, benchmarks individual files or dictionary directories, computes regressions, and drives modes through `main`. CLI options include directory, levels, iterations, emails, frequency, mode, and dictionary file.

## Control Flow, State, and Persistence

In current mode it builds the parent repo; in fast/onetime/continuous modes it chooses release or open PR builds. It runs `zstd -qb<level>` repeatedly and keeps the maximum speed across iterations. Continuous mode sleeps between checks. It persists previous PR state in `prev_prs.pk` and creates clone directories named for user/hash.

## Dependencies and Integration Points

It depends on GitHub API access, git, make, Python stdlib modules, zstd benchmark output format, and optionally `mutt` for email alerts. It is wired into `tests/Makefile` target `automated_benchmarking`.

## Risks and Test Signals

Risks include unauthenticated GitHub API rate limits, `os.system` command interpolation, broad `rm -rf zstd-{user}-{sha}`, fragile parsing by splitting on spaces and locating `MB/s`, and an apparent early `return regressions` indentation inside the dictionary loop. Tests should cover output parsing fixtures, clone path construction, no-file handling, current/onetime modes, dictionary regressions, and failure behavior when API/build commands fail.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/automated_benchmarking.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/checkTag.c -->
# sources/compression/zstd/tests/checkTag.c

## Purpose

This small C tool validates that a release tag is compatible with the compiled `ZSTD_VERSION_STRING`.

## Important APIs, Types, and Functions

`validate(tag)` requires a tag beginning with `v`, longer than the version string plus prefix, and whose characters after `v` start with `ZSTD_VERSION_STRING`. `main()` expects exactly one tag argument, prints version and tag, then returns 0 for compatible, 1 for mismatch, or 2 for incorrect usage.

## Control Flow, State, and Persistence

There is no persistent state. Runtime flow is argument validation, diagnostic printing, version prefix comparison, and exit code selection.

## Dependencies and Integration Points

It includes `zstd.h` and is built by the tests Makefile. It is intended for automated release/tag checks.

## Risks and Test Signals

The compatibility rule allows arbitrary suffixes after the exact version prefix. Tests should cover missing args, no `v` prefix, too-short tags, exact version with no suffix, compatible suffixes, and mismatched major/minor/patch values.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/checkTag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/check_size.py -->
# sources/compression/zstd/tests/check_size.py

## Purpose

This Python helper checks that a file exists and does not exceed a byte-size limit.

## Important APIs, Types, and Functions

It reads exactly two arguments, `FILE` and `SIZE_LIMIT`, converts the limit with `int()`, checks `os.path.exists`, computes `os.path.getsize`, and exits 1 with a diagnostic if the file is missing or too large.

## Control Flow, State, and Persistence

The script has no persistent state and performs a single validation per invocation.

## Dependencies and Integration Points

It depends on Python 3 and the stdlib. It is suitable for Makefile or CI size gates.

## Risks and Test Signals

It accepts directories as existing paths, for which `getsize` reports directory metadata size on some platforms. It imports `subprocess` unused. Tests should cover usage errors, non-integer limits, missing files, exact limit equality, over-limit files, and platform behavior for directories if used in CI.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/check_size.py -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/args.sh -->
# sources/compression/zstd/tests/cli-tests/basic/args.sh

## Purpose

This CLI test exercises invalid zstd arguments and expects the harness to capture failures/output for exact-output comparison.

## Important APIs, Types, and Functions

It invokes `zstd --blah`, `zstd -xz`, malformed `--adapt=min=1,maxx=2 file.txt`, and malformed `--train-cover=k=48,d=8,steps32 file.txt`, printing each command first with `println`.

## Control Flow, State, and Persistence

There is no setup or cleanup. Each command is run sequentially without `set -e`, so failures do not stop the script.

## Dependencies and Integration Points

It depends on CLI test wrappers `zstd` and `println`. It targets parser branches in `zstdcli.c`.

## Risks and Test Signals

The useful signal is stable rejection of unknown short/long options and malformed parameter lists. If a command unexpectedly succeeds or changes diagnostics, the CLI exact-output tests should fail.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/args.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/help.sh -->
# sources/compression/zstd/tests/cli-tests/basic/help.sh

## Purpose

This CLI test verifies short and advanced help commands.

## Important APIs, Types, and Functions

It runs `zstd -h`, `zstd -H`, and `zstd --help`, printing command labels with `println`.

## Control Flow, State, and Persistence

`set -e` makes any nonzero help command fail the test. No files are created.

## Dependencies and Integration Points

It depends on test wrappers `zstd` and `println`, and targets `usage()` plus `usageAdvanced()` in `zstdcli.c`.

## Risks and Test Signals

Signals are successful exit status and stable help text. Build-feature-dependent help content must be accounted for by the CLI test harness outputs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/help.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/memlimit.sh -->
# sources/compression/zstd/tests/cli-tests/basic/memlimit.sh

## Purpose

This CLI test validates `--memory`/memory-limit numeric parsing and suffix validation.

## Important APIs, Types, and Functions

It creates `file`, checks invalid suffixes such as `32LB`, `32LiB`, `32A`, random trailing text, and nonnumeric `hello`, then checks accepted suffixes with `1`, `1K`, `1KB`, `1KiB`, `1M`, `1MB`, `1MiB`, `1G`, `1GB`, `1GiB`, `3G`, `3GB`, and `3GiB`. It expects `4G`, `4GB`, and `4GiB` to overflow/reject. `die` reports unexpected results.

## Control Flow, State, and Persistence

The script creates and removes `file` and removes `file.zst` after successful accepted cases. It exits 0 after cleanup.

## Dependencies and Integration Points

It targets `readU32FromCharChecked`, `NEXT_UINT32`, and memory-limit handling in `zstdcli.c`.

## Risks and Test Signals

Main signals are accepted binary suffixes and rejection of trailing garbage or 32-bit unsigned overflow. Cleanup assumes output file name `file.zst`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/memlimit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/output_dir.sh -->
# sources/compression/zstd/tests/cli-tests/basic/output_dir.sh

## Purpose

This CLI test verifies that empty output directory arguments are rejected.

## Important APIs, Types, and Functions

It runs `zstd -r * --output-dir-mirror=""` and `zstd -r * --output-dir-flat=""`, failing with `die` if either succeeds.

## Control Flow, State, and Persistence

No files are intentionally created. The script exits 0 after both negative checks.

## Dependencies and Integration Points

It depends on recursive support and targets `--output-dir-flat` and `--output-dir-mirror` validation in `zstdcli.c`.

## Risks and Test Signals

Signals are nonzero status and diagnostics for empty strings. The glob `*` depends on the harness working directory containing at least one input-like path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/output_dir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/version.sh -->
# sources/compression/zstd/tests/cli-tests/basic/version.sh

## Purpose

This CLI test verifies version-reporting commands.

## Important APIs, Types, and Functions

It runs `zstd -V` and `zstd --version`.

## Control Flow, State, and Persistence

`set -e` fails the script on either nonzero status. No files are created.

## Dependencies and Integration Points

It targets `printVersion()` in `zstdcli.c` through the test wrapper `zstd`.

## Risks and Test Signals

Signals include successful exit status and stable version text, including verbosity-dependent or feature-dependent details controlled by the harness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/basic/version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/cmp_size -->
# sources/compression/zstd/tests/cli-tests/bin/cmp_size

## Purpose

This shell utility compares two file sizes for CLI tests without printing sizes in traced command output.

## Important APIs, Types, and Functions

It supports `-h`/`--help`, validates that argument 2 and argument 3 are files, obtains sizes with `wc -c`, and applies one comparison operator: `-eq`, `-ne`, `-lt`, `-le`, `-gt`, or `-ge`.

## Control Flow, State, and Persistence

`set -e` aborts on failed commands except the final test expression naturally becomes the process status. The script has no persistent state.

## Dependencies and Integration Points

It depends on POSIX `sh`, `test`, and `wc`, and is available on the CLI test `PATH`.

## Risks and Test Signals

Arguments are unquoted in `test -f` and redirection, so paths with spaces/globs are unsafe. Unknown operators fall through with status from an empty case arm. Tests should cover every operator, missing files, help output, and filenames without shell metacharacters.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/cmp_size -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/datagen -->
# sources/compression/zstd/tests/cli-tests/bin/datagen

## Purpose

This wrapper exposes the configured datagen binary to CLI shell tests.

## Important APIs, Types, and Functions

It executes `"$DATAGEN_BIN" $@`, forwarding all arguments.

## Control Flow, State, and Persistence

There is no state or cleanup. Exit status is the wrapped datagen exit status.

## Dependencies and Integration Points

It depends on `DATAGEN_BIN` being set by the CLI test harness.

## Risks and Test Signals

Unquoted `$@` can split arguments containing whitespace. Tests should verify harness setup exports a valid executable and that common datagen options work through the wrapper.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/datagen -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/die -->
# sources/compression/zstd/tests/cli-tests/bin/die

## Purpose

This helper terminates a CLI shell test with an error message.

## Important APIs, Types, and Functions

It calls `println "${*}"` to stderr and exits 1.

## Control Flow, State, and Persistence

The script always fails and has no persistent state.

## Dependencies and Integration Points

It depends on the sibling `println` helper being on `PATH`.

## Risks and Test Signals

It collapses all arguments into one string. The signal is simple: any path invoking `die` should mark the test failed with a visible diagnostic.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/die -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/println -->
# sources/compression/zstd/tests/cli-tests/bin/println

## Purpose

This helper prints a newline-terminated message for CLI tests.

## Important APIs, Types, and Functions

It runs `printf '%b\n' "${*}"`, interpreting backslash escapes in the joined argument string.

## Control Flow, State, and Persistence

There is no state. Exit status is `printf`'s status.

## Dependencies and Integration Points

It depends on POSIX `sh` and `printf`. Many CLI tests use it for stable command labels and diagnostics.

## Risks and Test Signals

Because `%b` interprets escapes, test messages containing backslashes can be transformed. Tests rely on deterministic output from this helper.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/println -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/unzstd -->
# sources/compression/zstd/tests/cli-tests/bin/unzstd

## Purpose

This wrapper invokes the configured `unzstd` symlink/binary under the optional execution prefix used by CLI tests.

## Important APIs, Types, and Functions

It derives `zstdname=$(basename $0)`, then runs either `"$ZSTD_SYMLINK_DIR/$zstdname" $@` or `$EXEC_PREFIX "$ZSTD_SYMLINK_DIR/$zstdname" $@`.

## Control Flow, State, and Persistence

There is no state. Exit status is the wrapped executable status.

## Dependencies and Integration Points

It depends on `ZSTD_SYMLINK_DIR` and optional `EXEC_PREFIX`, supporting QEMU or other emulator prefixes in `tests/Makefile`.

## Risks and Test Signals

Unquoted `$@` and `$EXEC_PREFIX` can split arguments. Tests should verify alias behavior is preserved because zstd mode is selected from executable basename.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/unzstd -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstd -->
# sources/compression/zstd/tests/cli-tests/bin/zstd

## Purpose

This wrapper invokes the configured `zstd` binary or symlink for CLI tests, optionally through an execution prefix.

## Important APIs, Types, and Functions

It derives its basename and dispatches to `$ZSTD_SYMLINK_DIR/$zstdname`, with `$EXEC_PREFIX` prepended when set.

## Control Flow, State, and Persistence

The script is stateless and returns the underlying command status.

## Dependencies and Integration Points

It depends on `ZSTD_SYMLINK_DIR` and optional `EXEC_PREFIX`. It is the primary command used by CLI shell tests.

## Risks and Test Signals

Unquoted forwarding can mishandle arguments with whitespace. Test signals are that `zstd` options reach the intended binary and emulator-prefixed runs work.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstd -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstdcat -->
# sources/compression/zstd/tests/cli-tests/bin/zstdcat

## Purpose

This wrapper invokes the configured `zstdcat` alias for CLI tests.

## Important APIs, Types, and Functions

It uses its basename to choose `$ZSTD_SYMLINK_DIR/zstdcat`, optionally prefixed by `$EXEC_PREFIX`, forwarding all arguments.

## Control Flow, State, and Persistence

It is stateless and returns the wrapped command status.

## Dependencies and Integration Points

It depends on alias symlink setup and is used where decompression-to-stdout behavior must be tested.

## Risks and Test Signals

The same unquoted argument-forwarding risk applies. Tests should verify alias-selected pass-through/stdout defaults and emulator execution.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstdcat -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstdgrep -->
# sources/compression/zstd/tests/cli-tests/bin/zstdgrep

## Purpose

This wrapper exposes the configured `zstdgrep` script to CLI tests.

## Important APIs, Types, and Functions

It executes `"$ZSTDGREP_BIN" $@`.

## Control Flow, State, and Persistence

The wrapper is stateless and returns `zstdgrep`'s status.

## Dependencies and Integration Points

It depends on `ZSTDGREP_BIN` being set by the CLI test harness and delegates to `programs/zstdgrep`.

## Risks and Test Signals

Unquoted `$@` can mishandle whitespace arguments. Tests should cover good and bad compressed paths through the wrapper.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstdgrep -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstdless -->
# sources/compression/zstd/tests/cli-tests/bin/zstdless

## Purpose

This wrapper exposes the configured `zstdless` script to CLI tests.

## Important APIs, Types, and Functions

It executes `"$ZSTDLESS_BIN" $@`.

## Control Flow, State, and Persistence

The wrapper is stateless and returns the wrapped command status.

## Dependencies and Integration Points

It depends on `ZSTDLESS_BIN` and delegates to `programs/zstdless`.

## Risks and Test Signals

Unquoted `$@` can mishandle whitespace arguments. Tests should confirm less options and file arguments pass through as intended.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/bin/zstdless -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/cltools/setup -->
# sources/compression/zstd/tests/cli-tests/cltools/setup

## Purpose

This setup script prepares shared files for command-line tool tests such as `zstdgrep` and `zstdless`.

## Important APIs, Types, and Functions

It writes `1234` to `file` and compresses it with `zstd file`.

## Control Flow, State, and Persistence

`set -e` aborts on setup failure. It persists `file` and `file.zst` in the test working directory for subsequent test scripts.

## Dependencies and Integration Points

It depends on the CLI test `zstd` wrapper and is associated with `tests/cli-tests/cltools`.

## Risks and Test Signals

The setup assumes default compression keeps the source file. Signals are existence and validity of both plain and compressed files for later tests.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/cltools/setup -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/cltools/zstdgrep.sh -->
# sources/compression/zstd/tests/cli-tests/cltools/zstdgrep.sh

## Purpose

This CLI test checks basic `zstdgrep` behavior on good and bad paths.

## Important APIs, Types, and Functions

It runs `zstdgrep "1234" file file.zst` and then `zstdgrep "1234" bad.zst`, with labels emitted by `println`.

## Control Flow, State, and Persistence

`set -e` means the second command is expected by the harness exact-output/status model; if it returns nonzero directly under `set -e`, the script exits there. It does not create files itself and depends on setup.

## Dependencies and Integration Points

It depends on `cltools/setup`, `zstdgrep`, and `println`.

## Risks and Test Signals

Signals are successful matching across plain/compressed inputs and appropriate failure/diagnostics for missing compressed input.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/cltools/zstdgrep.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/cltools/zstdless.sh -->
# sources/compression/zstd/tests/cli-tests/cltools/zstdless.sh

## Purpose

This CLI test checks `zstdless` invocation, option forwarding to `less`, and bad-path behavior.

## Important APIs, Types, and Functions

It runs `zstdless file.zst`, `zstdless -N file.zst`, and `zstdless bad.zst >&2`, labeling each step.

## Control Flow, State, and Persistence

`set -e` fails on unexpected nonzero status. No files are created; it depends on the cltools setup output.

## Dependencies and Integration Points

It depends on `zstdless`, `less`, `println`, and the compressed test file.

## Risks and Test Signals

The `-N` check ensures flags are interpreted by `less`, not zstd. Test behavior can vary if `less` is unavailable or configured differently in the harness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/cltools/zstdless.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/format.sh -->
# sources/compression/zstd/tests/cli-tests/common/format.sh

## Purpose

This shared shell helper provides format-detection utilities for CLI compression-format tests.

## Important APIs, Types, and Functions

It sources `common/platform.sh`, defines `zstd_supports_format()` by grepping `zstd -h` for `--format=<name>`, and defines `format_extension()` mapping `zstd` to `zst`, `gzip` to `gz`, and all other names to themselves.

## Control Flow, State, and Persistence

The file defines functions only and has no persistent state beyond variables imported from `platform.sh`.

## Dependencies and Integration Points

It is used by `compression/format.sh` and depends on the test `zstd` wrapper plus `$INTOVOID`.

## Risks and Test Signals

Feature detection depends on help text remaining stable. Tests should cover each optional format build and correct extension mapping.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/format.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/mtime.sh -->
# sources/compression/zstd/tests/cli-tests/common/mtime.sh

## Purpose

This shared shell helper asserts file modification-time equality across platforms.

## Important APIs, Types, and Functions

It sources `platform.sh`, selects `stat -c %Y` by default or `stat -f %m` on Darwin/BSD, and defines `assertSameMTime(file1, file2)`.

## Control Flow, State, and Persistence

The assertion reads both mtimes, prints them, and calls `die` if they differ. It has no persistent state.

## Dependencies and Integration Points

It depends on platform `stat` syntax and the `die` helper. CLI tests that check metadata preservation source it.

## Risks and Test Signals

Timestamp granularity and filesystem behavior can differ by platform. Tests should account for platforms where compression/decompression may round or not preserve subsecond data.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/mtime.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/permissions.sh -->
# sources/compression/zstd/tests/cli-tests/common/permissions.sh

## Purpose

This shared shell helper asserts file permission modes in CLI tests.

## Important APIs, Types, and Functions

It sources `platform.sh`, selects `stat -c %a` by default or `stat -f %Lp` on Darwin/BSD, and defines `assertFilePermissions(file, expected)` plus `assertSamePermissions(file1, file2)`.

## Control Flow, State, and Persistence

Each assertion reads numeric modes and calls `die` on mismatch. No state is persisted.

## Dependencies and Integration Points

It depends on platform `stat` and `die`, and supports tests for `UTIL_setFileStat`/permission preservation behavior.

## Risks and Test Signals

Mode formatting differs across systems and umask can affect created files. Tests should set predictable permissions before assertions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/permissions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/platform.sh -->
# sources/compression/zstd/tests/cli-tests/common/platform.sh

## Purpose

This shared shell helper normalizes platform variables for zstd CLI tests.

## Important APIs, Types, and Functions

It sets `UNAME`, `isWindows`, `INTOVOID`, `DEVDEVICE`, `MD5SUM`, `DIFF`, `hasMT`, and `NON_DETERMINISTIC`. Function `md5hash()` emits a 32-character hash line. It selects `/dev/random` on GNU, `/dev/zero` generally, `NUL` on Windows, platform-specific md5 commands, and `gdiff` on SunOS.

## Control Flow, State, and Persistence

At source time it probes multithreading by running `zstd -v -T2` and probes deterministic build status with `zstd -vv --version`. Results become shell variables for later tests.

## Dependencies and Integration Points

It depends on `uname`, `zstd`, `grep`, `md5sum` or `md5`, `dd`, and `diff`/`gdiff`. Many CLI tests source it directly or through other common helpers.

## Risks and Test Signals

Probe output is coupled to CLI diagnostics. `dd status=none` may not exist on some older systems. Tests should verify sourced variables on Linux, macOS, BSD, SunOS, and Windows shells.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/common/platform.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/adapt.sh -->
# sources/compression/zstd/tests/cli-tests/compression/adapt.sh

## Purpose

This CLI test verifies adaptive compression mode and that adaptation still occurs when progress output is disabled.

## Important APIs, Types, and Functions

It pipes `zstd -f file --adapt -c` to `zstd -t`, generates a 100 MB file with `datagen`, then runs high-verbosity adaptive compression at level 19 with `--zstd=wlog=10` and greps for the "faster speed , lighter compression" adaptation message, both with and without `--no-progress`.

## Control Flow, State, and Persistence

`set -e` aborts on any failed command or missing grep match. It creates `file100M` in the test directory.

## Dependencies and Integration Points

It targets adaptive settings in `zstdcli.c` and downstream file I/O/compression adaptation logic. It depends on `datagen`, `zstd`, and `grep`.

## Risks and Test Signals

The test is large and message-string sensitive. Slow or resource-limited systems may make it expensive. Signals are valid compressed output and explicit adaptation diagnostics.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/adapt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/basic.sh -->
# sources/compression/zstd/tests/cli-tests/compression/basic.sh

## Purpose

This CLI test covers core compression flags and verifies resulting frames with `zstd -t`.

## Important APIs, Types, and Functions

It tests default compression, `-f`, `-z`, `-k`, `-C`, `--check`, `--no-check`, `--`, `-o`, compact `-fo`, stdout via `-c` and `--stdout`, stdin pipe compression, gzip stdout keep-source behavior when gzip alias exists, and `--rm` source removal.

## Control Flow, State, and Persistence

`set -e` stops on failures. The script creates or overwrites `file.zst`, `file-out.zst`, and `file-rm.zst`, and ensures `file-rm` is removed after `--rm`.

## Dependencies and Integration Points

It exercises `zstdcli.c` option parsing and `fileio` compress/test paths through the test wrappers, plus optional gzip alias behavior.

## Risks and Test Signals

Signals are valid compressed output, correct stdout behavior, kept source when stdout is used, and successful source deletion for file outputs. It assumes a baseline `file` fixture exists.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/compress-literals.sh -->
# sources/compression/zstd/tests/cli-tests/compression/compress-literals.sh

## Purpose

This CLI test verifies explicit literal compression mode toggles across normal and fast compression levels.

## Important APIs, Types, and Functions

It pipes compressed output into `zstd -t` for `--no-compress-literals` at `-1`, `-19`, and `--fast=1`, and for `--compress-literals` at `-1` and `--fast=1`.

## Control Flow, State, and Persistence

`set -e` fails on any invalid output or CLI failure. No files are created because all outputs use stdout.

## Dependencies and Integration Points

It targets `literalCompressionMode` parsing in `zstdcli.c` and the zstd compression parameter passed into file I/O.

## Risks and Test Signals

Signals are that both forced modes produce decodable frames across selected strategies. The test does not assert ratio or whether literals were actually encoded as requested beyond successful parameter acceptance.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/compress-literals.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/format.sh -->
# sources/compression/zstd/tests/cli-tests/compression/format.sh

## Purpose

This CLI test verifies compression and test-mode behavior for zstd and optional alternate formats.

## Important APIs, Types, and Functions

It sources `common/format.sh`, compresses `file` with `--format=zstd`, tests `file.zst`, then loops through `gzip`, `lz4`, `xz`, and `lzma` when advertised by help output. For each supported format it writes a file with the expected extension, tests it, and tests stdout compression using `zstd -t --format=<format>`.

## Control Flow, State, and Persistence

`set -e` stops on errors. It creates format-specific compressed files in the working directory.

## Dependencies and Integration Points

It targets format selection in `zstdcli.c`, extension mapping in `fileio`, and optional compression backend support.

## Risks and Test Signals

Feature detection depends on help text. Signals are successful encode/decode/test for every compiled-in format and correct file extensions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/format.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/golden.sh -->
# sources/compression/zstd/tests/cli-tests/compression/golden.sh

## Purpose

This CLI test compresses the golden compression corpus recursively and validates the results, including target block size and a historical block-splitter corruption case.

## Important APIs, Types, and Functions

It copies `$ZSTD_REPO_DIR/tests/golden-compression/` into `golden/`, runs recursive forced compression with `--output-dir-mirror golden-compressed/`, tests the compressed tree, repeats with `--target-compressed-block-size=1024`, and finally tests `-19 --zstd=mml=7` for PR #3517 coverage.

## Control Flow, State, and Persistence

`set -e` stops on any failed compression or test. It creates `golden/` and `golden-compressed/` trees.

## Dependencies and Integration Points

It depends on the golden corpus, recursive CLI support, mirrored output directories, and zstd test mode.

## Risks and Test Signals

The corpus path must exist. Signals are recursive mirroring, valid frames for all corpus files, target compressed block sizing not corrupting data, and regression coverage for the block splitter/min-match case.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/golden.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/gzip-compat.sh -->
# sources/compression/zstd/tests/cli-tests/compression/gzip-compat.sh

## Purpose

This CLI test verifies gzip-compatible alias behavior when a gzip symlink is available.

## Important APIs, Types, and Functions

Inside a command-existence guard, it tests `gzip --fast`, `gzip --best`, `gzip -n`, `gzip --no-name`, and stdout `gzip -c --no-name`. It decompresses generated `file.gz` with the gzip alias and uses `grep -qv file` to assert `-n`/`--no-name` do not embed the original filename.

## Control Flow, State, and Persistence

`set -e` fails on unexpected command errors. It creates and removes `file.gz` through compression/decompression cycles.

## Dependencies and Integration Points

It depends on `$ZSTD_SYMLINK_DIR/gzip` and targets executable-name routing plus gzip-specific option handling in `zstdcli.c`.

## Risks and Test Signals

The guard uses `command -v` through command substitution in an `if`, which depends on shell behavior but is typical in this harness. Signals are gzip alias level mapping, decompression compatibility, source restoration, and filename suppression.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/cli-tests/compression/gzip-compat.sh -->
