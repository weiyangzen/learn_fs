# subset-b-000306 research

Grouped research report for the requested zstd contrib linux-kernel, match finder, premake, pzstd, recovery, and seekable-format files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/xxhash.h -->
# sources/compression/zstd/contrib/linux-kernel/test/include/linux/xxhash.h

## Purpose
This header is a self-contained xxHash compatibility implementation for the linux-kernel zstd test harness. It provides one-shot and streaming `xxh32`/`xxh64` APIs under kernel-style names so the imported zstd code can compile outside the kernel.

## Important APIs, Types, And Functions
It defines `struct xxh32_state`, `struct xxh64_state`, `xxh32`, `xxh64`, `xxhash`, reset/update/digest routines, and copy-state helpers. Internal helpers implement little-endian reads, rotations, primes, avalanche rounds, and accumulator merge logic.

## Control Flow
One-shot hashes initialize accumulators from the seed, consume 16- or 32-byte stripes, process remaining 4/8/1-byte tails, then avalanche. Streaming update stores short tail bytes in `mem32`/`mem64`, updates large-stripe accumulators when enough bytes arrive, and digest mirrors one-shot finalization.

## State And Persistence
State is entirely caller-owned in the streaming structs: seed, total length, four accumulators, memory size, and a small buffered tail. There is no persistence or allocation.

## Dependencies And Integration Points
The file depends on kernel-style integer/unaligned headers in the test include tree. It supports zstd code paths that use xxHash checksums while running the linux-kernel port tests in user space.

## Risks
Risks are endian and unaligned-access correctness, integer overflow dependence, and divergence from upstream xxHash behavior. Because all functions are `static inline`, ODR/link conflicts are avoided but compiler warnings can hide unused coverage.

## Test Signals
Coverage is indirect through linux-kernel zstd tests and seekable/pzstd checksum users. Strong signals are successful round trips and checksum validation paths that exercise both one-shot and streaming hash usage.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/include/linux/xxhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/macro-test.sh -->
# sources/compression/zstd/contrib/linux-kernel/test/macro-test.sh

## Purpose
This shell script validates macro hygiene for the linux-kernel zstd shim by compiling the imported module sources under multiple `ZSTD_DEPS_*` macro configurations.

## Important APIs, Types, And Functions
The script is organized around compiler invocations rather than exported functions. It builds preprocessor test cases for the dependency shim, include paths, and kernel-style replacement headers.

## Control Flow
It sets strict shell behavior, prepares compiler flags for the test include tree, and runs a sequence of compile/preprocess checks. A failing compiler command stops the script, making it suitable for make/CI use.

## State And Persistence
The only state is temporary compiler output or object/preprocessed files created by the commands. It does not persist runtime data.

## Dependencies And Integration Points
It depends on a POSIX shell, a C compiler, the linux-kernel test headers, and the zstd kernel-contrib source files. It integrates with the test Makefile lane for catching macro namespace regressions.

## Risks
The script is sensitive to compiler availability and exact include-path layout. It mostly verifies compilation, so semantic bugs can still pass.

## Test Signals
A zero exit status confirms that the selected macro combinations compile cleanly and that dependency feature gates in `zstd_deps.h` can be included without missing definitions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/macro-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/static_test.c -->
# sources/compression/zstd/contrib/linux-kernel/test/static_test.c

## Purpose
`static_test.c` is a small user-space test that verifies the static kernel-style decompression API can decode a known empty zstd frame.

## Important APIs, Types, And Functions
It defines a `CONTROL` assertion macro, the `kEmptyZstdFrame` byte sequence, `test_decompress_unzstd`, and `main`. The test exercises the unzstd/static decompression entry point through the linux-kernel shim.

## Control Flow
`main` calls the single decompression test. The test provides the embedded compressed frame, prepares output storage, invokes the static decompressor, and asserts that the result matches an empty payload and successful return status.

## State And Persistence
All state is stack/static test data. No files are written and no global state is persisted.

## Dependencies And Integration Points
It depends on the kernel-contrib test include tree and the zstd static decompression symbols compiled by the local Makefile. It complements `test.c`, which covers broader btrfs/f2fs-like flows.

## Risks
Because it only uses an empty frame, it mainly catches linkage/API regressions, not large-window or dictionary behavior.

## Test Signals
Successful process exit indicates that the static decompression wiring and an empty zstd frame path work.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/static_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/test.c -->
# sources/compression/zstd/contrib/linux-kernel/test/test.c

## Purpose
`test.c` is the main user-space functional test for the linux-kernel zstd module port. It models filesystem consumer patterns such as btrfs compression/decompression, unzstd use, f2fs parameter queries, and stack usage checks.

## Important APIs, Types, And Functions
It defines `test_data_t`, `create_test_data`, `free_test_data`, `test_btrfs`, `test_decompress_unzstd`, `test_f2fs`, stack sentinel helpers, `test_stack_usage`, and `main`. It exercises workspace-bound queries, cctx/dctx creation, streaming APIs, and one-shot compression/decompression wrappers.

## Control Flow
`main` creates deterministic test data, runs each scenario, reports progress to stderr, then frees buffers. Compression tests allocate workspaces, compress sample data, decompress it back, and compare. Stack tests fill/check a sentinel area around calls.

## State And Persistence
State is heap-allocated input/compressed/output buffers plus temporary workspaces. There is no persistent storage.

## Dependencies And Integration Points
The file integrates with `linux_zstd.h`, shim kernel headers, and the exported symbols from `zstd_common_module.c`, `zstd_compress_module.c`, and `zstd_decompress_module.c`.

## Risks
The test relies on deterministic buffer sizing and approximate consumer behavior; it is not a fuzzer. Stack checks are compiler/optimization sensitive.

## Test Signals
Passing output covers workspace sizing, streaming reset/end behavior, static decompression, level bounds, and stack footprint regressions for kernel consumers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_common_module.c -->
# sources/compression/zstd/contrib/linux-kernel/zstd_common_module.c

## Purpose
This file turns common zstd entropy/error helpers into a Linux kernel module export surface.

## Important APIs, Types, And Functions
It exports `FSE_readNCount`, `HUF_readStats`, `HUF_readStats_wksp`, `ZSTD_isError`, `ZSTD_getErrorName`, and `ZSTD_getErrorCode` with `EXPORT_SYMBOL_GPL`, then declares dual BSD/GPL licensing and the module description.

## Control Flow
There is no runtime control flow beyond module loading. The included zstd common implementation provides the actual logic; this wrapper only exposes selected symbols.

## State And Persistence
No module-owned mutable state or persistence exists. State belongs to callers and the imported zstd routines.

## Dependencies And Integration Points
It depends on the kernel-contrib common source aggregation headers and Linux module macros. Compress and decompress modules rely on these common helpers when built as split kernel modules.

## Risks
Export-set drift is the main risk: missing or wrongly licensed exports break module linkage for compressor/decompressor users.

## Test Signals
The linux-kernel tests and macro compile checks confirm that common symbols are visible and linkable.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_common_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_compress_module.c -->
# sources/compression/zstd/contrib/linux-kernel/zstd_compress_module.c

## Purpose
This module adapts zstd compression APIs to kernel-style names and workspace-based allocation semantics.

## Important APIs, Types, And Functions
It exports level queries, `zstd_compress_bound`, parameter selection, cctx workspace bounds, cctx/cdict creation/free, one-shot compression, cstream workspace/reset/stream/flush/end functions, external sequence producer registration, and `zstd_compress_sequences_and_literals`. `zstd_cctx_init`, `ZSTD_FORWARD_IF_ERR`, and external-sequence workspace helpers are important internal glue.

## Control Flow
Callers query parameters/workspace sizes, initialize contexts over caller-provided memory, then use one-shot or streaming compression. Streaming initialization sets pledged size unknown, frame flags, and workspace, while subsequent stream calls forward to zstd internals.

## State And Persistence
Compression state lives in caller-provided workspaces and zstd context structs. The module persists no data across calls except what the caller keeps in the context.

## Dependencies And Integration Points
It includes zstd compression sources and kernel dependency shims. Filesystem/kernel consumers use the exported `zstd_*` names from `linux_zstd.h`.

## Risks
Workspace-bound correctness is critical; underestimates can corrupt or fail kernel callers. Parameter translation, external sequence producer setup, and deprecated/static API use must stay aligned with upstream zstd internals.

## Test Signals
`test.c` exercises btrfs-like compression, streaming output, level bounds, and workspace APIs. Macro tests catch include/dependency regressions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_compress_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_decompress_module.c -->
# sources/compression/zstd/contrib/linux-kernel/zstd_decompress_module.c

## Purpose
This module adapts zstd decompression APIs to Linux kernel naming and workspace semantics.

## Important APIs, Types, And Functions
Exports include error helpers, dctx/ddict workspace and lifetime functions, `zstd_init_dctx`, one-shot decompression, ddict decompression, dstream workspace/init/reset/stream, `zstd_find_frame_compressed_size`, and `zstd_get_frame_header`.

## Control Flow
Callers allocate a workspace according to the bound function, initialize a dctx or dstream with custom memory, then call one-shot or streaming decompression. The wrapper functions mostly forward directly to zstd internals with type aliases from `linux_zstd.h`.

## State And Persistence
All decompression state is held in caller-owned contexts and dictionaries. The module itself has no persistent mutable state.

## Dependencies And Integration Points
It depends on the decompression source aggregation, `zstd_deps.h`, and kernel module export macros. It is the decompression counterpart consumed by btrfs/f2fs-style kernel code and the user-space test harness.

## Risks
Window-size and workspace-bound mismatches can cause caller allocation failures. Frame-header forwarding must preserve zstd error codes so kernel consumers can distinguish short input from corruption.

## Test Signals
`test.c` and `static_test.c` cover one-shot, streaming, ddict/static-adjacent, frame-size, and header paths sufficiently for linkage and common behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_decompress_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_deps.h -->
# sources/compression/zstd/contrib/linux-kernel/zstd_deps.h

## Purpose
`zstd_deps.h` supplies the dependency abstraction layer that lets upstream zstd sources compile in the Linux kernel environment or the local user-space kernel test harness.

## Important APIs, Types, And Functions
It defines feature blocks for common memory functions, allocator stubs, 64-bit division via `div_u64`, assertion mapping through `WARN_ON`, IO/debug macros, and stdint-style integer inclusion. `ZSTD_malloc`, `ZSTD_free`, and `ZSTD_calloc` intentionally return no heap allocation in kernel mode.

## Control Flow
The header is controlled by `ZSTD_DEPS_*` macros. Each block emits exactly the needed replacement definitions when the corresponding zstd source component requests them.

## State And Persistence
No state is owned. It controls compile-time behavior and allocation policy only.

## Dependencies And Integration Points
It integrates imported zstd C files with Linux headers such as `linux/kernel.h`, `linux/math64.h`, `linux/printk.h`, and test stubs under `test/include`.

## Risks
Macro ordering is fragile: definitions must appear before zstd internals include dependency blocks. Allocator stubbing means code paths requiring heap allocation must be avoided or converted to workspace APIs.

## Test Signals
`macro-test.sh`, `test.c`, and module compilation validate that all requested dependency blocks are present and kernel-compatible.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/zstd_deps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.c -->
# sources/compression/zstd/contrib/match_finders/zstd_edist.c

## Purpose
This file implements an edit-distance-based external match finder that converts similarities between a dictionary and source into zstd `ZSTD_Sequence` entries.

## Important APIs, Types, And Functions
The public entry is `ZSTD_eDist_genSequences`. Internal state types include `ZSTD_eDist_state`, `ZSTD_eDist_match`, and `ZSTD_eDist_partition`. Important helpers are `ZSTD_eDist_diag`, `ZSTD_eDist_compare`, `ZSTD_eDist_insertMatch`, `ZSTD_eDist_combineMatches`, `ZSTD_eDist_convertMatchesToSequences`, Hamming/Levenshtein distance helpers, and validation code.

## Control Flow
`ZSTD_eDist_genSequences` allocates diagonal and match buffers, recursively compares dictionary/source ranges via Myers-style forward/backward diagonals, records matching runs, optionally applies heuristics for expensive regions, sorts/combines contiguous matches, and emits zstd sequences with offsets/literal lengths.

## State And Persistence
State is per-call heap memory allocated through zstd custom memory macros and freed before return. No persistent index is retained.

## Dependencies And Integration Points
It depends on `zstd_edist.h`, `mem.h`, zstd sequence definitions, and `qsort`. It integrates with zstd's external sequence producer API for experimental match-finder research.

## Risks
Worst-case edit-distance work is expensive; heuristics trade optimality for speed. Buffer allocation uses `srcSize`/diagonal counts and lacks broad defensive reporting. Sequence conversion must preserve valid offsets into the dictionary/source.

## Test Signals
There is no direct test in this subset. Indirect signals would come from external sequence producer users validating compression correctness and from internal assertions when enabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.h -->
# sources/compression/zstd/contrib/match_finders/zstd_edist.h

## Purpose
This header exposes the edit-distance match finder API for generating zstd sequences from a dictionary/source pair.

## Important APIs, Types, And Functions
It includes static-linking zstd declarations and declares `ZSTD_eDist_genSequences(ZSTD_Sequence* sequences, const void* dict, size_t dictSize, const void* src, size_t srcSize, int useHeuristics)`.

## Control Flow
Callers provide an output sequence buffer and two byte ranges. The implementation computes matching regions and returns the number of generated sequences; enabling heuristics allows faster but potentially non-optimal match scripts.

## State And Persistence
The header defines no state. All state is owned by the implementation call.

## Dependencies And Integration Points
It depends on zstd's static sequence API. It is intended to plug into zstd experimental external sequence workflows and research match-finder comparisons.

## Risks
The function contract does not declare output buffer capacity, so callers must know how much space to provide. The API is experimental and tied to static zstd internals.

## Test Signals
Expected tests should compare generated sequences for known inputs, validate compression with external sequences, and run with heuristics both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/premake/premake4.lua -->
# sources/compression/zstd/contrib/premake/premake4.lua

## Purpose
This is a minimal GENie/premake4 example that loads the zstd premake helper and instantiates a sample solution.

## Important APIs, Types, And Functions
It calls `dofile('zstd.lua')`, defines solution `example`, declares `Debug`/`Release` configurations, and calls `project_zstd('../../lib/')`.

## Control Flow
Premake evaluates the helper file first, then executes `project_zstd` to create a static zstd library project against the relative lib directory.

## State And Persistence
It writes no state itself; premake generation creates project files externally when invoked.

## Dependencies And Integration Points
It depends on premake4/GENie and the adjacent `zstd.lua`. It demonstrates how downstream users can embed zstd as a generated static library.

## Risks
The hard-coded relative path only works from the contrib/premake location. This file is an example, not a production multi-platform project definition.

## Test Signals
Running premake/GENie from this directory should generate a solution containing the zstd static library target.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/premake/premake4.lua -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/premake/zstd.lua -->
# sources/compression/zstd/contrib/premake/zstd.lua

## Purpose
`zstd.lua` provides a reusable premake function for defining zstd as a static C library project.

## Important APIs, Types, And Functions
The exported function is `project_zstd(dir, compression, decompression, deprecated, dictbuilder, legacy)`. It normalizes the source directory, defaults feature toggles, declares project `zstd`, adds common/compress/decompress/dictBuilder/deprecated/legacy files conditionally, sets include directories, and defines `XXH_NAMESPACE=ZSTD_` plus `ZSTD_LEGACY_SUPPORT`.

## Control Flow
Feature booleans are normalized first. Disabling compression also disables dictbuilder/deprecated; disabling decompression disables legacy/deprecated. Premake file globs are then registered in feature order.

## State And Persistence
State is premake project metadata emitted during generation, not runtime state.

## Dependencies And Integration Points
It integrates zstd's `lib` layout with GENie/premake4-based consumers.

## Risks
Glob patterns and legacy version selection must stay synchronized with zstd's source tree. Optional feature interactions can surprise users expecting deprecated code without both compression/decompression.

## Test Signals
Successful project generation and compilation with varied feature combinations validate this helper.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/premake/zstd.lua -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/ErrorHolder.h -->
# sources/compression/zstd/contrib/pzstd/ErrorHolder.h

## Purpose
`ErrorHolder` centralizes first-error capture for pzstd worker, reader, and writer code.

## Important APIs, Types, And Functions
The class exposes `setError`, `hasError`, `getError`, and `check(condition, message)`. A mutex protects the stored string so multiple worker threads can report failures safely.

## Control Flow
Callers use `check` after operations; on false it records the message and returns false. Later code polls `hasError` to stop queues/workers and `pzstdMain` prints the captured error for the current input.

## State And Persistence
State is an in-memory error string guarded by a mutex. Only the first or latest recorded error is retained for the process; nothing is persisted.

## Dependencies And Integration Points
It is embedded in `SharedState` and used by `Pzstd.cpp` compression/decompression flows and file-open logic.

## Risks
If multiple workers fail, message ordering is nondeterministic. Callers must consistently check `hasError` to avoid continuing after failure.

## Test Signals
Behavior is indirectly covered by pzstd round-trip and failure-path tests; direct tests would validate thread-safe set/check behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/ErrorHolder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Logging.h -->
# sources/compression/zstd/contrib/pzstd/Logging.h

## Purpose
`Logging.h` provides pzstd's verbosity-controlled stderr logging and progress-line update helper.

## Important APIs, Types, And Functions
It defines log levels such as error/info/verbose/debug and class `Logger` with `operator()`, `update`, `clear`, and `logsAt`.

## Control Flow
Callers construct a logger with the parsed verbosity. Normal logs emit formatted messages when the level is enabled; update/clear manage progress text by rewriting or clearing the active line.

## State And Persistence
State is the verbosity threshold and progress-line bookkeeping. Output is transient stderr text.

## Dependencies And Integration Points
`SharedState` owns a `Logger`, and `Pzstd.cpp` uses it for frame starts, progress, ratios, prompts, and errors.

## Risks
Progress updates can interleave with worker output if future code logs outside the main writer path. Format-string usage requires trusted static formats.

## Test Signals
Option tests validate verbosity parsing; runtime pzstd tests indirectly exercise logging without asserting exact stderr.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Makefile -->
# sources/compression/zstd/contrib/pzstd/Makefile

## Purpose
The pzstd Makefile builds the deprecated parallel zstd CLI, its object files, and its unit/integration tests against the local zstd library.

## Important APIs, Types, And Functions
Targets include the pzstd binary, object directories, clean/install/test variants, and test binaries for options, pzstd round trips, and utility classes. Variables control compiler, flags, library paths, thread support, and platform-specific settings.

## Control Flow
The Makefile compiles C++ sources under pzstd, links against zstd/common threading pieces, builds GoogleTest-style unit tests when available, and offers test targets that execute binaries.

## State And Persistence
It writes build artifacts, dependency files, binaries, and test outputs under build directories. No runtime state is persisted by the Makefile itself.

## Dependencies And Integration Points
It depends on make, a C++ compiler, zstd lib/common sources, platform libraries, and optional test infrastructure. It is the build integration point for all pzstd files in this subset.

## Risks
Pzstd is deprecated and uses deprecated zstd APIs. Platform flags, pthread linkage, and local library path assumptions are common portability risks.

## Test Signals
`make test`/related targets provide the strongest signal by building and running options, round-trip, pzstd, and utility tests.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Options.cpp -->
# sources/compression/zstd/contrib/pzstd/Options.cpp

## Purpose
`Options.cpp` parses pzstd command-line arguments and turns zstd-like CLI options into an `Options` configuration.

## Important APIs, Types, And Functions
Important helpers are `defaultNumThreads`, `parseUnsigned`, `getArgument`, `notSupported`, `usage`, `Options::Options`, `Options::parse`, and `Options::getOutputFile`.

## Control Flow
Parsing scans argv, maps long options to short options, handles combined short options and numeric compression levels, validates multi-file/stdin/output restrictions, expands recursive file lists when enabled, rejects unsupported dictionaries/benchmarks/sparse mode, checks console safety, and adjusts verbosity for pipe/multi-file modes.

## State And Persistence
It mutates an `Options` instance: thread count, compression level, mode flags, input files, output file, checksum flag, and verbosity. It also sets `g_utilDisplayLevel` for zstd utility code.

## Dependencies And Integration Points
It depends on zstd static APIs, `util.h` for file traversal/link checks, console macros, and `ScopeGuard`. `main.cpp` calls it before `pzstdMain`.

## Risks
CLI compatibility is partial; unsupported zstd options fail. Symlink filtering and recursive expansion depend on platform utility behavior. Console-safety checks can differ across environments.

## Test Signals
`OptionsTest.cpp` broadly covers valid inputs, bad arguments, output naming, multi-file restrictions, verbosity, keep/remove, test mode, checksum, stdin/stdout, and message options.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Options.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Options.h -->
# sources/compression/zstd/contrib/pzstd/Options.h

## Purpose
`Options.h` declares the pzstd configuration object and parameter derivation logic used by the CLI and worker pipeline.

## Important APIs, Types, And Functions
`Options` stores `numThreads`, `maxWindowLog`, `compressionLevel`, `decompress`, `inputFiles`, `outputFile`, overwrite/remove/write/checksum/verbosity flags, `WriteMode`, and parse `Status`. It declares `parse`, `determineParameters`, and `getOutputFile`.

## Control Flow
`determineParameters` calls `ZSTD_getParams`, disables content-size flag, applies checksum selection, caps `windowLog` to `maxWindowLog`, and re-adjusts compression params.

## State And Persistence
The struct is plain in-memory configuration passed by const reference through pzstd.

## Dependencies And Integration Points
It includes static zstd APIs and is consumed by `main.cpp`, `Pzstd.h`, `Pzstd.cpp`, and tests.

## Risks
Changing defaults affects CLI compatibility and frame sizing. The max window cap is also tied to pzstd skippable-frame size assumptions.

## Test Signals
`OptionsTest.cpp` validates parsed values and `getOutputFile`; round-trip tests validate derived compression parameters.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Pzstd.cpp -->
# sources/compression/zstd/contrib/pzstd/Pzstd.cpp

## Purpose
`Pzstd.cpp` implements pzstd's parallel compression/decompression engine and CLI file-processing loop.

## Important APIs, Types, And Functions
Public functions are `pzstdMain`, `asyncCompressChunks`, `asyncDecompressFrames`, and `writeFile`. Key helpers include `handleOneInput`, file open helpers, zstd buffer adapters, `compress`, `decompress`, `calculateStep`, `readData`, and `writeData`.

## Control Flow
`pzstdMain` iterates inputs, opens files, selects output names, runs `handleOneInput`, and optionally deletes sources after successful close. Compression uses a reader thread to split input into frame-sized `BufferWorkQueue`s, a worker `ThreadPool` to compress each frame, and the writer to emit a pzstd skippable frame plus compressed data in order. Decompression reads pzstd skippable frame headers when present to parallelize frame decompression; otherwise it falls back to one serial decompression task.

## State And Persistence
`SharedState` holds logger, error holder, and zstd stream resource pools. Queues carry buffers between threads. Persistent effects are output files and optional input removal.

## Dependencies And Integration Points
It integrates `Options`, `SkippableFrame`, `Buffer`, `WorkQueue`, `ThreadPool`, `ResourcePool`, zstd streaming APIs, and stdio/file utilities.

## Risks
Concurrency correctness depends on queue finish ordering and `ErrorHolder` polling. `calculateStep` asserts window logs <=23 because skippable frame sizes are 32-bit. Writer waits for compressed frame size before output, so broken worker finish can deadlock.

## Test Signals
`PzstdTest.cpp` and `RoundTripTest.cpp` cover small/large/highly-compressible round trips, while utility tests cover queues and pools used by this flow.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Pzstd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Pzstd.h -->
# sources/compression/zstd/contrib/pzstd/Pzstd.h

## Purpose
`Pzstd.h` declares the pzstd engine API, shared runtime state, and cross-thread pipeline functions.

## Important APIs, Types, And Functions
It declares `pzstdMain`, class `SharedState`, `asyncCompressChunks`, `asyncDecompressFrames`, and `writeFile`. `SharedState` owns `Logger`, `ErrorHolder`, and either a `ResourcePool<ZSTD_CStream>` or `ResourcePool<ZSTD_DStream>` initialized from `Options`.

## Control Flow
`SharedState` construction selects compression or decompression resources. Compression resources are initialized with `ZSTD_initCStream_advanced`; decompression resources use `ZSTD_initDStream`. Destruction resets pools before member teardown because pool factories capture `this`.

## State And Persistence
Shared state is process-local and shared by all worker tasks for one pzstd invocation. It caches zstd stream objects for reuse.

## Dependencies And Integration Points
It includes pzstd utility headers and zstd static-linking APIs. `Pzstd.cpp` implements the declared functions.

## Risks
The resource pools must outlive checked-out stream pointers. Factory failure produces null resources that callers must handle.

## Test Signals
Engine and utility tests indirectly validate shared state construction, stream reuse, and pipeline function contracts.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Pzstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.cpp -->
# sources/compression/zstd/contrib/pzstd/SkippableFrame.cpp

## Purpose
This file implements pzstd's 12-byte skippable-frame header used to prefix each independently compressed frame with its compressed size.

## Important APIs, Types, And Functions
It implements `SkippableFrame::SkippableFrame(uint32_t size)` and static `SkippableFrame::tryRead(ByteRange bytes)`.

## Control Flow
The constructor writes little-endian magic, payload-size field, and next-frame size into the fixed array. `tryRead` validates byte count, magic, and payload-size field, returning the encoded frame size or `0` when the bytes are not a pzstd header.

## State And Persistence
State is the frame-size field and a 12-byte array embedded in the object. The bytes become persistent only when `writeFile` writes them to an output stream.

## Dependencies And Integration Points
It depends on `mem.h` little-endian helpers and `Range`. Compression writes these headers; decompression uses them to split frames for parallelism.

## Risks
A legitimate following frame size of zero is indistinguishable from invalid/missing header. Sizes are limited to 32 bits, constraining frame sizing.

## Test Signals
Round-trip pzstd tests exercise writing/reading headers; fallback decompression behavior covers invalid header paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.h -->
# sources/compression/zstd/contrib/pzstd/SkippableFrame.h

## Purpose
`SkippableFrame.h` declares pzstd's small metadata frame placed before each zstd frame to enable parallel decompression.

## Important APIs, Types, And Functions
`SkippableFrame` exposes `kSize`, the constructor, `tryRead`, `data`, and `frameSize`. Constants include zstd skippable magic `0x184D2A50` and a 4-byte content-size field.

## Control Flow
Callers construct a header with the compressed frame size, write `data()`, and later call `tryRead` on 12 bytes from input to recover the next frame size.

## State And Persistence
The object is a fixed-size byte array plus numeric frame size. Persisted output is embedded in pzstd streams as skippable frames.

## Dependencies And Integration Points
It depends on pzstd `ByteRange`. It is central to `Pzstd.cpp` compression output and decompression frame discovery.

## Risks
The format is pzstd-specific and only backward-compatible as a zstd skippable frame. Consumers must still handle normal zstd streams without these headers.

## Test Signals
Pzstd round-trip and fallback tests validate that headers are generated and interpreted correctly.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/SkippableFrame.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/main.cpp -->
# sources/compression/zstd/contrib/pzstd/main.cpp

## Purpose
`main.cpp` is the pzstd executable entry point.

## Important APIs, Types, And Functions
It defines `main(int argc, const char** argv)`, constructs `Options`, invokes `Options::parse`, and on success calls `pzstdMain`.

## Control Flow
If parsing returns `Failure`, it exits nonzero. If parsing returns `Message` for help/version, it exits zero without running compression. Otherwise it delegates to the engine and returns its status.

## State And Persistence
The entry point owns only the stack `Options` object. Persistent effects are produced by `pzstdMain`.

## Dependencies And Integration Points
It includes `Options.h` and `Pzstd.h`, tying CLI parsing to the pzstd engine.

## Risks
Exit-code semantics depend on `Options::Status`; changes to parse status mapping directly affect scripts invoking pzstd.

## Test Signals
`OptionsTest.cpp` validates parse statuses; round-trip tests exercise the engine beneath this entry point.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/OptionsTest.cpp -->
# sources/compression/zstd/contrib/pzstd/test/OptionsTest.cpp

## Purpose
This GoogleTest file verifies pzstd command-line parsing and output-file derivation.

## Important APIs, Types, And Functions
It defines equality helpers for `Options`, argument-vector helpers, expectation macros, and tests for valid inputs, output naming, multiple files, thread parsing, compression levels, unsupported/invalid options, keep/remove behavior, verbosity, test mode, checksum flags, stdin/stdout, and help/version messages.

## Control Flow
Each test constructs argv-like arrays, calls `Options::parse`, and compares the resulting `Options` fields or expected failure/message status.

## State And Persistence
State is local test data. It may inspect platform null-output naming but does not write files.

## Dependencies And Integration Points
It depends on GoogleTest, `Options.h`, and platform null-device conventions. It guards the behavior used by `main.cpp`.

## Risks
Tests mock argv behavior but do not fully cover console detection or recursive filesystem expansion.

## Test Signals
These tests are the primary regression signal for pzstd CLI compatibility and validation rules.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/OptionsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/PzstdTest.cpp -->
# sources/compression/zstd/contrib/pzstd/test/PzstdTest.cpp

## Purpose
`PzstdTest.cpp` provides integration-style tests for pzstd compression/decompression across input sizes and compressibility patterns.

## Important APIs, Types, And Functions
It uses pzstd `Options`, round-trip helpers, temporary files, and test cases `SmallSizes`, `LargeSizes`, disabled extremely large size coverage, and `ExtremelyCompressible`.

## Control Flow
Tests generate deterministic input files, run pzstd compression and decompression with configured thread counts/levels, and compare source with decompressed output.

## State And Persistence
The tests create temporary files and compressed/decompressed outputs, then clean them through helper utilities.

## Dependencies And Integration Points
It depends on pzstd engine APIs, zstd behavior, file utilities, and GoogleTest. It validates the full `Pzstd.cpp` pipeline.

## Risks
Large-size coverage has a disabled extremely large test, so 32-bit size boundary issues remain lower-signal in normal test runs.

## Test Signals
Passing tests indicate ordered frame output, decompression reconstruction, and behavior with highly compressible data.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/PzstdTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/RoundTrip.h -->
# sources/compression/zstd/contrib/pzstd/test/RoundTrip.h

## Purpose
`RoundTrip.h` provides reusable pzstd test helpers for compressing, decompressing, and comparing files.

## Important APIs, Types, And Functions
It defines `check(source, decompressed)` for byte comparison and `roundTrip(Options& options)` to run compression then decompression using pzstd output naming.

## Control Flow
`roundTrip` invokes `pzstdMain` for compression, mutates options to decompression mode against the `.zst` output, invokes pzstd again, and calls `check` on the original and decompressed files.

## State And Persistence
It creates and reads temporary files as part of tests. State is managed by the caller's options and filesystem artifacts.

## Dependencies And Integration Points
It depends on `Pzstd.h`, `Options`, C++ file streams, and test file naming conventions.

## Risks
Mutating the same `Options` object can hide bugs if caller assumptions change. File cleanup is outside this helper.

## Test Signals
Used by round-trip tests to verify whole-pipeline losslessness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/RoundTrip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/RoundTripTest.cpp -->
# sources/compression/zstd/contrib/pzstd/test/RoundTripTest.cpp

## Purpose
This standalone randomized round-trip test exercises pzstd with generated inputs and option combinations.

## Important APIs, Types, And Functions
It defines generator helpers for input files and options, then `main` runs repeated round trips.

## Control Flow
The test generates input content, constructs pzstd options with varied compression settings/thread counts, calls the shared round-trip helper, and exits nonzero on failure.

## State And Persistence
Temporary input, compressed, and decompressed files are created during runs. Persistent state is limited to test artifacts if cleanup fails.

## Dependencies And Integration Points
It depends on `RoundTrip.h`, pzstd engine code, and standard random/file utilities. It complements deterministic GoogleTest cases.

## Risks
Randomized coverage can be nondeterministic if seed behavior changes. It may miss edge cases unless configured for enough iterations and sizes.

## Test Signals
Successful runs provide broad losslessness evidence across generated file contents.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/test/RoundTripTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Buffer.h -->
# sources/compression/zstd/contrib/pzstd/utils/Buffer.h

## Purpose
`Buffer.h` implements a reference-counted byte-buffer slice abstraction used to move chunks through pzstd queues without copying whole allocations.

## Important APIs, Types, And Functions
`Buffer` exposes constructors from size or shared storage, `data`, `range`, `size`, `empty`, `use_count`, `advance`, `subtract`, and `splitAt`.

## Control Flow
Readers allocate a buffer, fill it, and split off populated prefixes. Compression/decompression code advances consumed input and splits produced output based on zstd buffer positions.

## State And Persistence
State is a shared underlying allocation plus begin/end range pointers or offsets. Lifetime is controlled by shared ownership; no persistence exists.

## Dependencies And Integration Points
It depends on `Range.h` and standard smart pointers. `Pzstd.cpp` and `BufferWorkQueue` use it heavily.

## Risks
Range-splitting must maintain valid boundaries and shared lifetime. Incorrect size accounting can break backpressure or frame-size calculations.

## Test Signals
`BufferTest.cpp` covers construction, shared ownership counts, advance/subtract, and split behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/FileSystem.h -->
# sources/compression/zstd/contrib/pzstd/utils/FileSystem.h

## Purpose
`FileSystem.h` provides a small portability wrapper for file status, size, regular-file, and directory checks.

## Important APIs, Types, And Functions
It aliases platform `stat`/`_stat64` as `file_status` and defines `status`, `file_size`, `is_regular_file`, and `is_directory` overloads using `StringPiece`.

## Control Flow
Functions call the platform stat routine, populate `std::error_code` on failure, and query mode bits to classify files.

## State And Persistence
No persistent state is owned. Calls read filesystem metadata only.

## Dependencies And Integration Points
`Pzstd.cpp` uses these helpers for input-size estimation and directory rejection. `Options.cpp` uses zstd `util.h` for broader traversal, so this file is focused on lightweight checks.

## Risks
Stat behavior differs across Windows/POSIX, especially symlinks and large files. Callers must inspect `error_code`.

## Test Signals
Indirect pzstd file-processing tests exercise size/directory behavior; direct unit tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/FileSystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Likely.h -->
# sources/compression/zstd/contrib/pzstd/utils/Likely.h

## Purpose
`Likely.h` defines branch prediction hint macros for pzstd utility code.

## Important APIs, Types, And Functions
It exposes `LIKELY(x)` and `UNLIKELY(x)`, mapping to `__builtin_expect` when available and to plain expressions otherwise.

## Control Flow
The header has compile-time conditional behavior only; runtime flow is whatever caller expressions produce.

## State And Persistence
No state or persistence exists.

## Dependencies And Integration Points
It is available for pzstd utility code that wants compiler branch hints without hard-coding GCC/Clang builtins.

## Risks
Overuse or wrong hints can degrade performance. Macro expressions should avoid side effects that are surprising under macro expansion.

## Test Signals
Compilation on supported and fallback compilers is the main signal.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Likely.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Portability.h -->
# sources/compression/zstd/contrib/pzstd/utils/Portability.h

## Purpose
`Portability.h` provides small cross-platform definitions needed by pzstd.

## Important APIs, Types, And Functions
The file centralizes platform-specific includes or macros used by other utilities, keeping source files less cluttered.

## Control Flow
Behavior is compile-time conditional on platform macros.

## State And Persistence
No state is owned and nothing is persisted.

## Dependencies And Integration Points
It is included by `Pzstd.cpp` and utility code to normalize platform details around files and binary mode handling.

## Risks
Because it is small and broad, any macro change can affect multiple translation units. Platform coverage depends on build/test availability.

## Test Signals
Successful pzstd compilation on POSIX and Windows-like configurations validates this header.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Portability.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Range.h -->
# sources/compression/zstd/contrib/pzstd/utils/Range.h

## Purpose
`Range.h` implements a lightweight pointer/iterator range used for byte slices and string-like views in pzstd.

## Important APIs, Types, And Functions
It defines `Range<Iter>`, character-pointer detection helpers, aliases such as `ByteRange`/`StringPiece`, and methods for `begin`, `end`, `data`, `size`, `empty`, `advance`, and `subtract`.

## Control Flow
Constructors create begin/end pairs from pointers, arrays, or pointer+size. Mutators move the start or end inward, enabling cheap slice consumption.

## State And Persistence
State is just two iterators/pointers. It owns no memory and persists nothing.

## Dependencies And Integration Points
`Buffer`, `SkippableFrame`, file-system helpers, and tests use ranges to avoid copying byte/string data.

## Risks
Ranges are non-owning, so lifetime and boundary correctness belong to callers. Advancing beyond end would be a logic bug.

## Test Signals
`RangeTest.cpp` covers constructors, mutation, string conversion, and char-pointer behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Range.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ResourcePool.h -->
# sources/compression/zstd/contrib/pzstd/utils/ResourcePool.h

## Purpose
`ResourcePool.h` provides a thread-safe reusable pool for expensive mutable resources such as zstd streams.

## Important APIs, Types, And Functions
`ResourcePool<T>` takes a factory and free function, exposes `get()` returning `unique_ptr<T, Deleter>`, and returns resources to the pool when the custom deleter runs.

## Control Flow
`get` pops an available resource or creates one, increments `inUse_`, and hands it out. The deleter pushes non-null resources back and decrements `inUse_`. Destruction asserts no resources are checked out and frees cached resources.

## State And Persistence
State is a mutex, resource vector, factory/free closures, and in-use count. No disk persistence exists.

## Dependencies And Integration Points
`SharedState` uses it for `ZSTD_CStream` and `ZSTD_DStream` reuse across worker tasks.

## Risks
The pool must outlive all returned unique pointers. Resources must be reset by callers before reuse because the pool does not sanitize them.

## Test Signals
`ResourcePoolTest.cpp` covers reuse, factory/free counts, and thread safety.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ResourcePool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ScopeGuard.h -->
# sources/compression/zstd/contrib/pzstd/utils/ScopeGuard.h

## Purpose
`ScopeGuard.h` implements a small RAII cleanup helper for pzstd.

## Important APIs, Types, And Functions
`ScopeGuard<Function>` stores a callable, runs it in the destructor unless dismissed, and `makeScopeGuard` infers the template type.

## Control Flow
Callers create guards after acquiring files, queues, or other resources. Normal scope exit or early returns trigger cleanup; `dismiss` disables it after ownership is released manually.

## State And Persistence
State is the callable and an active/dismissed flag. No persistence exists.

## Dependencies And Integration Points
`Pzstd.cpp` uses scope guards for file closes, queue finishing, error printing, and progress clearing. `Options.cpp` uses it for recursive file-list cleanup.

## Risks
Destructor callables should not throw. Captured references must remain valid until guard destruction.

## Test Signals
`ScopeGuardTest.cpp` checks dismissal and execution on scope exit.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ScopeGuard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ThreadPool.h -->
# sources/compression/zstd/contrib/pzstd/utils/ThreadPool.h

## Purpose
`ThreadPool.h` implements pzstd's simple FIFO worker pool.

## Important APIs, Types, And Functions
`ThreadPool` owns a vector of worker threads and a `WorkQueue<std::function<void()>>`. It exposes a constructor, destructor, and `add`.

## Control Flow
The constructor starts N threads that repeatedly pop tasks and execute them. The destructor finishes the task queue and joins all threads. `add` pushes a copyable `std::function`.

## State And Persistence
State is thread objects and the task queue. There is no persisted state.

## Dependencies And Integration Points
`Pzstd.cpp` uses one pool for compression/decompression workers and a one-thread pool for reader tasks. Tests cover ordering and destruction behavior.

## Risks
Queued lambdas cannot capture move-only objects directly because tasks are `std::function`. Exceptions escaping tasks would terminate the process.

## Test Signals
`ThreadPoolTest.cpp` validates FIFO-ish completion assumptions, job draining before destruction, and adding work during joining.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ThreadPool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/WorkQueue.h -->
# sources/compression/zstd/contrib/pzstd/utils/WorkQueue.h

## Purpose
`WorkQueue.h` provides the blocking producer/consumer queues used to connect pzstd reader, worker, and writer threads.

## Important APIs, Types, And Functions
Template `WorkQueue<T>` exposes `push`, `pop`, `setMaxSize`, `finish`, and `waitUntilFinished`. `BufferWorkQueue` wraps `WorkQueue<Buffer>` and tracks total queued bytes atomically.

## Control Flow
`push` blocks when a bounded queue is full unless finished; `pop` blocks until data or finish; `finish` wakes all readers/writers. `BufferWorkQueue::size` waits until finish so compressed frame size is final before the writer emits the pzstd header.

## State And Persistence
State is queue contents, condition variables, done flag, max size, and byte count. No persistence exists.

## Dependencies And Integration Points
This is core to `Pzstd.cpp` ordering/backpressure. Thread pool tasks also use `WorkQueue<std::function<void()>>`.

## Risks
Incorrect finish ordering can deadlock producers or readers. `BufferWorkQueue::push` increments size before checking push success, so callers rely on normal non-finished use.

## Test Signals
`WorkQueueTest.cpp` covers single-threaded, SPSC, SPMC, MPMC, bounded queues, failed push, setMaxSize, and byte-size tracking.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/WorkQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/BufferTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/BufferTest.cpp

## Purpose
This test verifies `Buffer` construction, ownership sharing, and slice mutation.

## Important APIs, Types, And Functions
It defines a custom deleter and tests constructors, `use_count`, `advance`, `splitAt`, `subtract`, `range`, and `size`.

## Control Flow
Tests allocate buffers, copy/split them, inspect shared ownership counts, mutate ranges, and assert resulting first/last bytes and sizes.

## State And Persistence
State is local heap buffers and shared pointers. No files are written.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/Buffer.h`. It protects pzstd queue buffer behavior.

## Risks
Tests focus on normal boundaries; additional negative tests would be needed for invalid split/advance inputs.

## Test Signals
Passing tests support correctness of buffer slicing used by zstd stream adapters.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/BufferTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/RangeTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/RangeTest.cpp

## Purpose
This test validates `Range` constructors and mutating slice operations.

## Important APIs, Types, And Functions
It covers empty ranges, pointer/array/string-style constructors, `advance`, `subtract`, `data`, `begin`, `end`, `size`, and conversion to `std::string` for verification.

## Control Flow
Tests create ranges over static strings, move the begin/end boundaries, and compare contents against expected substrings.

## State And Persistence
Only stack/static string data is used. No persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/Range.h`. It protects non-owning views used by buffers, filesystem helpers, and skippable frames.

## Risks
It does not exercise invalid lifetime scenarios because those are caller responsibility.

## Test Signals
Passing tests indicate basic range math is stable.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/RangeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ResourcePoolTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/ResourcePoolTest.cpp

## Purpose
This test verifies `ResourcePool` reuse, cleanup, and thread safety.

## Important APIs, Types, And Functions
It creates integer resources through factory/free lambdas and exercises `ResourcePool<int>::get` with nested scopes and multiple threads.

## Control Flow
The full test checks that returned resources are reused and freed once at pool destruction. The thread-safe test concurrently checks out resources and validates expected values/counters.

## State And Persistence
State is local counters and heap integers owned by the pool. No disk persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/ResourcePool.h`. It supports confidence in zstd stream pooling used by pzstd workers.

## Risks
The tests cover simple resources, not zstd stream reset discipline.

## Test Signals
Passing tests validate the pool's lock-protected checkout/return lifecycle.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ResourcePoolTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ScopeGuardTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/ScopeGuardTest.cpp

## Purpose
This test checks the basic RAII behavior of `ScopeGuard`.

## Important APIs, Types, And Functions
It uses `makeScopeGuard`, `dismiss`, and destructor execution.

## Control Flow
One test creates a guard and dismisses it, ensuring the failure callback is not run. Another creates a guard that sets a flag and verifies the flag after scope exit.

## State And Persistence
Only local booleans are mutated. No persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/ScopeGuard.h`. It protects cleanup patterns used throughout pzstd.

## Risks
It does not cover move semantics or exception behavior.

## Test Signals
Passing tests show normal cleanup and dismissal work.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ScopeGuardTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ThreadPoolTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/ThreadPoolTest.cpp

## Purpose
This file tests `ThreadPool` task execution and shutdown behavior.

## Important APIs, Types, And Functions
It uses `ThreadPool::add`, atomics, sleeps, and result vectors in tests for ordering, all-jobs-finished, and add-job-while-joining behavior.

## Control Flow
Tests enqueue multiple tasks, let the pool destructor join workers, then inspect completed counters/results. One test attempts to enqueue after destruction has begun to document behavior.

## State And Persistence
State is local vectors and atomics. No files are written.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/ThreadPool.h`. It validates the worker executor used by pzstd compression and decompression.

## Risks
Timing-sensitive tests can be flaky across slow or heavily loaded systems.

## Test Signals
Passing tests support that queued work drains and worker threads join cleanly.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ThreadPoolTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/WorkQueueTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/WorkQueueTest.cpp

## Purpose
This test suite validates the blocking queue behavior that underpins pzstd's thread pipeline.

## Important APIs, Types, And Functions
It defines helper worker structs and tests `WorkQueue::push`, `pop`, `finish`, `setMaxSize`, bounded queues, failed push after finish, and `BufferWorkQueue::size`.

## Control Flow
Tests run single-threaded queue operations, producer/consumer patterns with one or many threads, bounded backpressure scenarios, and size accounting that waits for finish.

## State And Persistence
State is local queues, threads, vectors, atomics, and buffers. No persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest, `WorkQueue.h`, `Buffer.h`, and C++ threading. It directly protects `Pzstd.cpp` queue semantics.

## Risks
Some tests use sleeps to force scheduling, which can be timing-sensitive.

## Test Signals
Passing tests provide strong confidence for queue synchronization, finish wakeups, and pzstd writer size accounting.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/WorkQueueTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/Makefile -->
# sources/compression/zstd/contrib/recovery/Makefile

## Purpose
This Makefile builds the `recover_directory` helper for splitting a multi-frame zstd archive back into per-frame files.

## Important APIs, Types, And Functions
Targets compile `recover_directory.c` against the local zstd library and provide cleaning/build rules. Variables select compiler, flags, and zstd library paths.

## Control Flow
The default build compiles the C source and links with zstd utility/library objects. Clean targets remove generated artifacts.

## State And Persistence
It creates the recovery executable and intermediate build files.

## Dependencies And Integration Points
It depends on make, a C compiler, and zstd library/util sources. It is the build entry for `recover_directory.c`.

## Risks
Relative paths and static-link expectations must match the zstd tree. It is a contrib tool, so build coverage may be less frequent than core zstd.

## Test Signals
Successful build plus manual recovery on multi-frame archives validates the Makefile path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/recover_directory.c -->
# sources/compression/zstd/contrib/recovery/recover_directory.c

## Purpose
`recover_directory.c` recovers individual files from a concatenated multi-frame zstd file, such as output from recursive zstd compression.

## Important APIs, Types, And Functions
It defines `ZstdFrames`, `usage`, `readFile`, `computePadding`, and `main`. It uses `ZSTD_findFrameCompressedSize`, `ZSTD_createDCtx`, `ZSTD_decompressStream`, and zstd utility file-size helpers.

## Control Flow
The program reads the whole archive into memory, walks frames to count them and find max frame size, allocates an output name buffer and decompression buffer, then iterates frames. Each frame is decompressed into `${PREFIX}<padded-index>` with a reset dctx.

## State And Persistence
State includes the full compressed file in memory, a reusable decompression buffer, output filename buffer, and dctx. Persistent effects are recovered output files.

## Dependencies And Integration Points
It depends on zstd static APIs and `util.h`. It is a standalone contrib utility for disaster recovery or archive inspection.

## Risks
It loads the entire input file into memory and exits on first error. It assumes each frame maps to one desired output file and does not recover original filenames.

## Test Signals
Manual tests should create a multi-frame zstd file, run recovery, and compare each recovered file with expected frame payloads.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/recover_directory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/Makefile -->
# sources/compression/zstd/contrib/seekable_format/examples/Makefile

## Purpose
This Makefile builds seekable-format example programs demonstrating streaming compression, decompression, parallel compression, and parallel processing.

## Important APIs, Types, And Functions
It defines zstd library paths, example targets, thread-enabled library target for multithreaded examples, compile/link flags, and clean rules.

## Control Flow
Targets build `zstd_seekable` support with each example source and link against the local zstd library/common pool/threading pieces as needed.

## State And Persistence
It writes example binaries and intermediate object files.

## Dependencies And Integration Points
It depends on make, a C compiler, local zstd lib sources, and pthread/threading support for parallel examples.

## Risks
Relative paths and static library naming must match the zstd source tree. Multithreaded targets require platform threading support.

## Test Signals
Successful build and running examples on sample files validate the seekable-format API integration.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_compression.c -->
# sources/compression/zstd/contrib/seekable_format/examples/parallel_compression.c

## Purpose
This example compresses independent frames in parallel and then writes a seekable zstd file with a generated seek table.

## Important APIs, Types, And Functions
It defines `state`, `job`, pending-list helpers, `compressFrame`, `finishFrame`, `compressFile_orDie`, and `main`. It uses zstd thread pool APIs, `ZSTD_compress`, `XXH64`, and raw seekable-table APIs `ZSTD_seekable_createFrameLog`, `ZSTD_seekable_logFrame`, and `ZSTD_seekable_writeSeekTable`.

## Control Flow
The main loop reads fixed-size frame chunks, submits jobs to a pool, and each job compresses/checksums its chunk. Completion inserts jobs into an ordered pending list protected by a mutex; contiguous completed IDs are flushed to output and logged. After joining workers, the seek table is serialized.

## State And Persistence
Runtime state includes output file, mutex, next frame ID, pending list, frame log, and per-job buffers. Persistent output is `<input>.zst` or stdout.

## Dependencies And Integration Points
It integrates zstd's pool/threading, xxHash, and seekable-format raw table API.

## Risks
Jobs call `exit` on failure from worker threads. Frame size must fit zstd compress bound into 32-bit table fields. Pending list ordering is essential for valid output.

## Test Signals
A produced file should be readable by seekable decompression examples/tests and preserve input bytes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_processing.c -->
# sources/compression/zstd/contrib/seekable_format/examples/parallel_processing.c

## Purpose
This example demonstrates parallel random access over a seekable zstd file by summing bytes in each frame independently.

## Important APIs, Types, And Functions
It defines `sum_job`, `sumFrame`, `sumFile_orDie`, and `main`, using `ZSTD_seekable_initFile`, `ZSTD_seekable_getNumFrames`, `ZSTD_seekable_getFrameDecompressedSize`, and `ZSTD_seekable_decompressFrame`.

## Control Flow
The program opens the seekable file, reads the frame count, creates one job per frame, and runs jobs in a zstd pool. Each job opens its own file handle and seekable object, decompresses one frame, computes a byte sum, and stores it for final aggregation.

## State And Persistence
State is per-job frame number/sum plus transient decompressed buffers. It does not modify files.

## Dependencies And Integration Points
It depends on zstd's pool and seekable decompression API. It illustrates multi-reader integration for applications that process frames independently.

## Risks
Opening the file once per job is simple but expensive. Very large frames allocate full decompressed frame buffers.

## Test Signals
Running it on a known seekable file should produce a deterministic sum; comparing with an uncompressed byte-sum validates correctness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/parallel_processing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_compression.c -->
# sources/compression/zstd/contrib/seekable_format/examples/seekable_compression.c

## Purpose
This example shows basic streaming compression into the zstd seekable format.

## Important APIs, Types, And Functions
It defines allocation/file helpers, `compressFile_orDie`, `createOutFilename_orDie`, and `main`. It uses `ZSTD_seekable_createCStream`, `ZSTD_seekable_initCStream`, `ZSTD_seekable_compressStream`, and `ZSTD_seekable_endStream`.

## Control Flow
The program reads an input file in chunks, feeds the seekable compressor until input is consumed, flushes the stream/table with repeated `endStream` calls, and writes output to `<input>.zst`.

## State And Persistence
State is input/output FILEs, input/output buffers, and a seekable compression stream. Persistent output is the compressed seekable file.

## Dependencies And Integration Points
It depends on zstd static APIs and `zstd_seekable.h`. It is the simplest producer example for downstream users.

## Risks
It exits on errors and is not designed as a robust CLI. Frame-size choices trade random-access granularity against ratio.

## Test Signals
Output should decompress with seekable decompression examples and pass byte comparison with the source.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression.c -->
# sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression.c

## Purpose
This example extracts a byte range from a seekable zstd file using file-backed random access.

## Important APIs, Types, And Functions
It defines allocation/file helpers, `fseek_orDie`, `decompressFile_orDie`, and `main`. It uses `ZSTD_seekable_create`, `ZSTD_seekable_initFile`, and `ZSTD_seekable_decompress`.

## Control Flow
The program opens a seekable file, initializes a seekable decompressor, allocates an output buffer for the requested range, decompresses from start offset to end offset, and writes bytes to stdout.

## State And Persistence
State is a FILE handle, seekable object, and output buffer. It writes decompressed bytes to stdout only.

## Dependencies And Integration Points
It integrates the public file-based seekable decompression API with standard stdio.

## Risks
Large requested ranges allocate full output size. It assumes valid numeric offsets and exits on first error.

## Test Signals
Comparing extracted ranges with the original uncompressed file validates correctness.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression_mem.c -->
# sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression_mem.c

## Purpose
This example demonstrates in-memory seekable decompression for small seekable zstd files.

## Important APIs, Types, And Functions
It defines `MAX_FILE_SIZE`, allocation/file helpers, `decompressFile_orDie`, and `main`. It uses `ZSTD_seekable_initBuff` and `ZSTD_seekable_decompress`.

## Control Flow
The program reads the entire compressed file into memory, initializes the seekable object over that buffer, decompresses the requested range into an output buffer, and writes it to stdout.

## State And Persistence
State is the in-memory compressed file buffer, output range buffer, and seekable object. It persists no files.

## Dependencies And Integration Points
It depends on zstd static APIs and demonstrates the buffer-backed seekable API.

## Risks
It caps input size and requires the source buffer to remain alive while the seekable object is used. Large ranges allocate full decompressed output.

## Test Signals
Range comparisons with original data and parity with file-backed decompression validate this path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/examples/seekable_decompression_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/tests/Makefile -->
# sources/compression/zstd/contrib/seekable_format/tests/Makefile

## Purpose
This Makefile builds and runs the seekable-format test binary.

## Important APIs, Types, And Functions
It defines zstd library paths, source lists, compile/link flags, a `seekable_tests` target, test/run targets, and clean rules.

## Control Flow
The build compiles `seekable_tests.c` with `zstdseek_compress.c` and the seekable decompression implementation, links against zstd, then test targets execute the resulting binary.

## State And Persistence
It creates the test executable and intermediate artifacts.

## Dependencies And Integration Points
It depends on make, a C compiler, zstd lib sources, and the seekable-format implementation files.

## Risks
Relative path drift or missing static library artifacts can break the build. It exercises asserts, so release builds with `NDEBUG` would weaken checks.

## Test Signals
`make test` should run `seekable_tests` and print all success messages.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/tests/seekable_tests.c -->
# sources/compression/zstd/contrib/seekable_format/tests/seekable_tests.c

## Purpose
`seekable_tests.c` is the main unit/regression test for zstd seekable format compression, decompression, seek-table access, and hang regressions.

## Important APIs, Types, And Functions
It defines a custom buffer-backed file wrapper with `readBuffWithTotal` and `seekBuffWithTotal`, then tests seekable cstream/dstream APIs, seek-table APIs, malformed inputs, empty compression header behavior, and repeated seek/decompress calls.

## Control Flow
`main` runs numbered tests using `assert` and `goto _test_error` failure exits. It compresses buffers, initializes seekable objects from memory or custom callbacks, validates frame metadata, checks malformed data returns errors rather than hanging, and verifies repeated forward/backward range reads.

## State And Persistence
State is heap buffers and in-memory compressed seekable data. It writes no persistent files.

## Dependencies And Integration Points
It depends on `zstd_seekable.h` and the seekable compress/decompress implementations. It is the primary regression signal for the contrib format.

## Risks
Assertions disappear under `NDEBUG`. Test data is small, so huge-frame and file-backed edge cases need additional coverage.

## Test Signals
Success messages confirm round-trip, metadata access, malformed input handling, empty stream header, and efficient repeated decompression behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/tests/seekable_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstd_seekable.h -->
# sources/compression/zstd/contrib/seekable_format/zstd_seekable.h

## Purpose
`zstd_seekable.h` declares the public API and format constants for zstd's seekable format, which splits compressed data into independently compressed frames followed by a seek table.

## Important APIs, Types, And Functions
It declares `ZSTD_seekable_CStream`, `ZSTD_seekable`, `ZSTD_seekTable`, `ZSTD_frameLog`, compression APIs, raw frame-log/seek-table APIs, buffer/file/custom decompression initialization, range/frame decompression APIs, frame metadata accessors, `offsetToFrameIndex`, and custom read/seek callback types.

## Control Flow
Compression clients create/init a cstream, call `compressStream`, optionally `endFrame`, then repeat `endStream` until the current frame and seek table are flushed. Decompression clients initialize from a buffer, FILE, or callbacks, then decompress ranges or whole frames using seek-table metadata.

## State And Persistence
Opaque objects hold stream state, seek-table metadata, callback/file references, and decompressor reuse state. The persistent on-disk format stores zstd frames plus a final skippable seek table.

## Dependencies And Integration Points
It depends on `zstd.h` and C stdio. Examples, tests, and `zstdseek_compress.c` implement/use this contract.

## Risks
Compressed/decompressed frame sizes are stored in bounded fields; callers must keep backing buffers/files alive for initialized objects. API is contrib-level and less stable than core zstd.

## Test Signals
`seekable_tests.c` and examples validate compression, seek-table metadata, buffer/file/custom input, and range/frame decompression.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstd_seekable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstdseek_compress.c -->
# sources/compression/zstd/contrib/seekable_format/zstdseek_compress.c

## Purpose
`zstdseek_compress.c` implements seekable-format compression and raw seek-table serialization.

## Important APIs, Types, And Functions
It defines `framelogEntry_t`, `ZSTD_frameLog`, `ZSTD_seekable_CStream`, frame-log allocation/free helpers, `ZSTD_seekable_create/freeCStream`, `ZSTD_seekable_initCStream`, `ZSTD_seekable_logFrame`, `ZSTD_seekable_compressStream`, `ZSTD_seekable_endFrame`, `ZSTD_seekable_writeSeekTable`, and `ZSTD_seekable_endStream`.

## Control Flow
Initialization resets frame counters, validates max frame size, configures checksum, and initializes zstd cstream. `compressStream` limits input to the current frame budget, updates compressed/decompressed sizes and optional XXH64 checksum, and ends the frame when full. `endFrame` flushes zstd, logs frame metadata, and resets for the next frame. `writeSeekTable` streams a skippable seek table incrementally, preserving position across small output buffers. `endStream` finishes the final frame then writes the table.

## State And Persistence
The cstream stores a zstd stream, frame log vector, current frame sizes, checksum state, max frame size, and seek-table write cursor. Persistent output is zstd frames followed by the serialized seek table.

## Dependencies And Integration Points
It depends on zstd static APIs, `zstd_errors.h`, `mem.h`, xxHash, and `zstd_seekable.h`. Examples and tests call both high-level streaming and raw frame-log APIs.

## Risks
Frame counts and sizes are bounded by `ZSTD_SEEKABLE_MAXFRAMES` and 32-bit fields. Incremental table writing is offset-sensitive. Empty input still logs an empty frame, which tests expect to begin with a zstd magic header.

## Test Signals
`seekable_tests.c` validates round trip, table metadata, malformed input behavior, empty compression, and repeated range reads; parallel compression example exercises raw frame-log serialization.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstdseek_compress.c -->
