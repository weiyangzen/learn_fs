# subset-b-000325 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/benchzstd.c -->
# sources/compression/zstd/programs/benchzstd.c

## Purpose
`benchzstd.c` implements the zstd CLI benchmark path. It benchmarks compression, decompression, or both against in-memory samples loaded from files or generated synthetically. It reports throughput, compression ratio, and approximate compression memory, and it exposes the memory benchmark core used by higher-level tooling such as paramgrill and the zstd command line.

## Important APIs, types, and functions
The public entry points are `BMK_initAdvancedParams()`, `BMK_benchMem()`, `BMK_benchMemAdvanced()`, `BMK_benchFiles()`, `BMK_benchFilesAdvanced()`, and `BMK_syntheticTest()`. The result API uses `BMK_benchOutcome_t`, a tagged variant defined in the header, with `BMK_isSuccessful_benchOutcome()` and `BMK_extract_benchResult()` as the safe access pattern. Internally, `BMK_initCCtx()` maps benchmark advanced parameters and explicit `ZSTD_compressionParameters` into a reusable `ZSTD_CCtx`; `BMK_initDCtx()` prepares the decompression context. `local_defaultCompress()` and `local_defaultDecompress()` adapt zstd APIs to the generic timing harness in `benchfn.h`.

`BMK_benchMemAdvancedNoAlloc()` is the core benchmark. It receives preallocated pointer/size arrays and buffers, splits each file segment into benchmark chunks, configures `BMK_benchParams_t` for compression and decompression, runs `BMK_benchTimedFn()`, tracks best observed speeds, and validates roundtrip output with `XXH64` when running both directions. `BMK_benchCLevels()` loops over compression levels and normalizes display names. `BMK_loadFiles()` loads file inputs into one contiguous sample buffer with a parallel `fileSizes` array.

## Control flow
File benchmarking starts in `BMK_benchFilesAdvanced()`: validate input count and level range, optionally load a dictionary, compute a safe sample size with `BMK_findMaxMem()`, allocate the sample buffer and per-file sizes, load inputs, then call `BMK_benchCLevels()`. Synthetic benchmarking allocates a single sample, fills it with `LOREM_genBuffer()` for negative compressibility or `RDG_genBuffer()` otherwise, then follows the same compression-level loop.

Memory benchmarking starts in `BMK_benchMemAdvanced()`, which allocates arrays for source chunks, compressed chunks, decompressed result chunks, timed-function state, zstd contexts, and compressed/result buffers. It then delegates to the no-allocation core. Decode-only mode first calculates the decompressed size of every compressed segment with `ZSTD_findDecompressedSize()` and reallocates the result buffer to fit decoded output. Normal mode computes a chunk size from `adv->chunkSizeMax` and builds chunk pointer tables. Compression and decompression are timed independently until both timed states report completion.

## State and persistence behavior
The file has no persistent on-disk state beyond reading benchmark inputs. Runtime state is memory-local: zstd contexts, pointer tables, timing state, generated or loaded sample buffers, and display counters. The only externally visible state changes are writes to stdout/stderr for results and progress. Decode-only mode can copy the compressed source into the compressed buffer before timing. The result variant prevents callers from treating errors as valid benchmark data, but `BMK_extract_benchResult()` asserts rather than returning a recoverable error if misused.

## Dependencies and integration points
The implementation depends on `benchfn.h` and `timefn.h` for timing, `util.h` for file sizing and platform helpers, zstd static-linking APIs for context parameters, `datagen.h` and `lorem.h` for synthetic data, and `xxhash.h` for validation. It is integrated with the CLI through `benchzstd.h`; `BMK_syntheticTest()` and `BMK_benchFiles*()` are the command-facing entry points. It also integrates with advanced zstd compression parameters such as long-distance matching, row match finder, target compressed block size, literal compression mode, and worker count.

## Risks and edge cases
The benchmark is allocation-heavy and intentionally caps test size by probing available memory, so very large file sets may only be partially benchmarked. `BMK_loadFiles()` truncates the last loaded file if the buffer fills and sets `nbFiles = n` locally, which stops loading but does not update the caller's file count; downstream chunks for zero-sized entries must be tolerated. Decode-only mode requires frame content sizes to be known, so streams without content size cannot be benchmarked. Several internal errors call `exit()` through `CHECK_Z()`, making some parameter failures process-fatal rather than variant-returned. Throughput uses best observed timed runs, so tests should avoid comparing exact speeds.

## Test signals
Useful tests are CLI benchmark runs over one file, multiple files, decode-only compressed input with known and unknown content size, synthetic compressibility modes, dictionary benchmarking, and advanced flags such as workers, LDM, target block size, and row match finder. Regression checks should assert successful result tags, nonzero speeds for nonempty data, stable handling of empty or unreadable files, and roundtrip checksum warnings never appearing for valid zstd roundtrips.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/benchzstd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/benchzstd.h -->
# sources/compression/zstd/programs/benchzstd.h

## Purpose
`benchzstd.h` is the public benchmark interface for zstd program code. It defines the result shape, advanced benchmark options, benchmark modes, and entry points used by the CLI and parameter exploration tools.

## Important APIs, types, and functions
`BMK_benchResult_t` contains compressed size, compression speed, decompression speed, and compression memory. `BMK_benchOutcome_t` wraps that result as an error-or-value variant generated by `VARIANT_ERROR_RESULT()`. Callers must use `BMK_isSuccessful_benchOutcome()` before `BMK_extract_benchResult()`.

`BMK_mode_t` selects both directions, decode-only, or compress-only. `BMK_advancedParams_t` carries timing duration, maximum independent chunk size, target compressed block size, worker count, real-time priority, long-distance matching parameters, literal compression mode, and row match finder selection. The exported operations are `BMK_initAdvancedParams()`, `BMK_benchFiles()`, `BMK_benchFilesAdvanced()`, `BMK_syntheticTest()`, `BMK_benchMem()`, and `BMK_benchMemAdvanced()`.

## Control flow
The header separates simple and advanced call paths. Simple file and memory benchmark functions initialize default advanced parameters internally. Advanced calls accept caller-controlled `BMK_advancedParams_t` and either a single compression level range for file/synthetic tests or optional destination buffer control for memory tests. `BMK_benchMemAdvanced()` is the lowest-level public API and expects the caller to provide source segmentation in `fileSizes`.

## State and persistence behavior
This header declares no global mutable state. State is passed explicitly through input buffers, file tables, dictionaries, compression parameters, and advanced parameters. The variant result pattern is the key state contract: success is represented by tag zero, while error tags must not be extracted as benchmark results.

## Dependencies and integration points
The header depends on `stddef.h` and zstd static-linking APIs for `ZSTD_compressionParameters` and `ZSTD_ParamSwitch_e`. It is consumed by `benchzstd.c` and by zstd CLI code that needs benchmarking without depending on internal implementation details.

## Risks and edge cases
The comments require `nbFiles > 0` and require `sum(fileSizes) == srcSize`, but these are caller obligations for memory benchmarks. Misusing the variant extractor on an error aborts through an assertion. The comment for `BMK_mode_t` is inconsistent with the enum declaration in one place, so callers should trust enum names rather than the stale inline wording.

## Test signals
Compile-time tests should cover inclusion from C and C++ callers as applicable. API-level tests should verify default advanced parameters, valid/invalid compression level handling through the implementation, and variant behavior on success and error.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/benchzstd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/datagen.c -->
# sources/compression/zstd/programs/datagen.c

## Purpose
`datagen.c` generates deterministic pseudo-random data with configurable compressibility. It supports both in-memory generation for benchmarks and streaming generation to stdout for CLI data generation.

## Important APIs, types, and functions
The exported functions are `RDG_genBuffer()` and `RDG_genStdout()`. `RDG_rand()` is the local deterministic 32-bit generator. `RDG_fillLiteralDistrib()` builds an 8K literal distribution table using a 24.8 fixed-point probability. `RDG_genBlock()` is the core generator: it alternates literals and back-references according to `matchProba`, with a special sparse-data path when `matchProba >= 1.0`.

## Control flow
`RDG_genBuffer()` initializes the seed and literal table, derives a default literal probability from match probability when unset, then generates one block from position zero. `RDG_genStdout()` allocates a 32 KiB dictionary plus 128 KiB output block, generates an initial dictionary, repeatedly generates blocks with the dictionary as prefix, writes only the requested block portion to stdout, and slides the dictionary forward with `memcpy()`.

Inside `RDG_genBlock()`, position starts at `prefixSize`. If sparse generation is requested, it emits large zero runs separated by generated nonzero bytes. Otherwise it ensures the first byte exists, then repeatedly chooses between a match copy from the prior 32 KiB window or a run of literals. Match copy intentionally supports overlap, mirroring LZ-style repeated sequences.

## State and persistence behavior
There is no persistent state. Output is deterministic for a given `(matchProba, litProba, seed)` tuple. `RDG_genStdout()` mutates stdout mode to binary and writes raw bytes. All generator state is local: seed, literal table, rolling dictionary buffer, and current position.

## Dependencies and integration points
The file depends on `datagen.h`, `platform.h` for `SET_BINARY_MODE`, C stdlib/stdio/string functions, and zstd common `mem.h` for integer aliases. `benchzstd.c` uses `RDG_genBuffer()` to warm benchmark buffers and produce synthetic samples.

## Risks and edge cases
The function assumes the caller passes a valid writable buffer of the requested size. Floating-point probabilities are only loosely bounded; values above one trigger sparse mode, while negative literal probability is clamped inside distribution setup. `RDG_genStdout()` ignores `fwrite()` failures by assigning the result to an unused variable, so pipe errors may not be reported here. Very small buffers are handled by the position checks, but the generator's statistical properties are only meaningful for larger samples.

## Test signals
Tests should verify determinism for fixed seeds, differences across seeds, behavior at `matchProba` 0, typical mid-range probabilities, sparse mode at 1.0, zero-size buffer calls, and stdout generation lengths. Compression-ratio smoke tests can confirm that higher match probability generally produces more compressible output.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/datagen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/datagen.h -->
# sources/compression/zstd/programs/datagen.h

## Purpose
`datagen.h` declares the random data generator used by zstd programs and benchmarks. It exposes deterministic generation into a caller buffer or directly to stdout.

## Important APIs, types, and functions
`RDG_genBuffer(void* buffer, size_t size, double matchProba, double litProba, unsigned seed)` fills an existing buffer. `RDG_genStdout(unsigned long long size, double matchProba, double litProba, unsigned seed)` emits generated bytes to stdout. The header documents that `matchProba` controls compressibility, `litProba` controls byte variability and can be zero for default behavior, and the same parameter triplet produces the same content.

## Control flow
The header is a simple declaration boundary. C++ consumers are supported through `extern "C"`. Callers choose either memory generation or stdout generation; all generation logic lives in `datagen.c`.

## State and persistence behavior
No state is declared by the header. The API contract is deterministic output from explicit arguments. `RDG_genStdout()` has the side effect of writing to standard output.

## Dependencies and integration points
The only direct dependency is `stddef.h` for `size_t`. This minimal surface lets benchmark and CLI code generate samples without depending on zstd internals.

## Risks and edge cases
The header does not define error returns; allocation or I/O behavior is implementation-defined by `datagen.c`. Callers must pass valid writable storage to `RDG_genBuffer()` and should treat stdout generation as process-output side effect, not a recoverable streaming API.

## Test signals
Header-level validation is compile coverage from C and C++. Behavioral tests belong to `datagen.c` and should assert determinism, requested byte counts, and expected compressibility trends.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/datagen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/dibio.c -->
# sources/compression/zstd/programs/dibio.c

## Purpose
`dibio.c` implements dictionary-builder file I/O for the zstd CLI. It loads sample files, optionally splits files into chunks, limits memory use, trains a dictionary through zdict legacy/cover/fastCover APIs, and saves the resulting dictionary.

## Important APIs, types, and functions
The public entry point is `DiB_trainFromFiles()`. Supporting functions include `DiB_fileStats()` for precomputing load size and sample count, `DiB_loadFiles()` for loading sample bytes and sample-size metadata, `DiB_shuffle()` for deterministic input shuffling, `DiB_findMaxMem()` for allocation probing, `DiB_fillNoise()` for a guard band used by legacy training, and `DiB_saveDict()` for output persistence. `fileStats` records total loadable data, sample count, and whether any whole-file sample was excessively large.

## Control flow
Training starts by selecting display level from whichever zdict parameter struct is active. Input file names are shuffled in place so oversized datasets do not always sample only early files. `DiB_fileStats()` scans file sizes, skips invalid or empty files, caps whole-file samples at 128 KiB, or counts fixed-size chunks when `chunkSize > 0`. The main function estimates safe training data size from algorithm-specific memory multipliers, a 2 GiB hard cap, and optional user memory limit, then allocates source, sample-size, and dictionary buffers.

After validation, `DiB_loadFiles()` reads samples into one contiguous buffer and writes each sample length to `sampleSizes`. `DiB_trainFromFiles()` then dispatches to exactly one zdict family: `ZDICT_trainFromBuffer_legacy()`, `ZDICT_trainFromBuffer_cover()` or its optimizer, or `ZDICT_trainFromBuffer_fastCover()` or its optimizer. On success it writes the dictionary to `dictFileName`.

## State and persistence behavior
The function mutates the caller's `fileNamesTable` order through `DiB_shuffle()`. It persists one output file, the trained dictionary. Runtime state is otherwise local buffers and sample metadata. Errors frequently use `EXM_THROW()`, which prints and exits the process, even though the public function returns an int for zdict training failure. Display refresh state uses file-scope `g_displayClock`.

## Dependencies and integration points
The file depends on `platform.h` and `util.h` for large-file and size helpers, `timefn.h` for progress throttling, zstd common/debug/mem headers, `zstd_errors.h`, and `dibio.h` for the exported declaration and zdict parameter types. It is called by CLI dictionary-training commands and is tightly coupled to zdict's legacy, cover, and fastCover training APIs.

## Risks and edge cases
`DiB_findMaxMem()` loops until an allocation succeeds and does not explicitly stop at zero, so pathological allocators or tiny address spaces deserve attention. `DiB_trainFromFiles()` forbids fewer than five samples and warns when training data is too small for the target dictionary. Whole-file mode silently truncates large samples to 128 KiB and warns for very large samples; chunk mode can create many samples but requires `chunkSize <= 128 KiB`. Because file names are shuffled in place, callers that rely on original ordering must pass a disposable table.

## Test signals
Tests should cover legacy, cover, fastCover, and optimize paths; chunked and whole-file samples; too few samples; empty/unreadable samples; oversized samples; memory-limit truncation; output write failures; and deterministic shuffle effects. CLI tests should assert that a dictionary file is created and non-empty on success and that zdict errors surface as nonzero results or process errors as designed.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/dibio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/dibio.h -->
# sources/compression/zstd/programs/dibio.h

## Purpose
`dibio.h` declares the zstd program dictionary-training file I/O API. Its own comment makes clear it is designed for a single-threaded console application and may call `exit()` or print to stderr on errors.

## Important APIs, types, and functions
The sole public function is `DiB_trainFromFiles()`. It accepts an output dictionary path, maximum dictionary size, an input file-name table, file count, optional chunk size, one of the zdict parameter families, an optimize flag, and a memory limit. The function returns zero for success and nonzero for error when errors are recoverable through the implementation path.

## Control flow
The header does not implement control flow. It exposes one high-level operation that hides sample loading, memory limiting, zdict training-family selection, and dictionary saving behind a single call.

## State and persistence behavior
The API writes a dictionary file named by `dictFileName`. Based on the implementation contract, it may also mutate the input file-name table order and may terminate the process on fatal errors. No reusable context object or persistent handle is declared.

## Dependencies and integration points
The header defines `ZDICT_STATIC_LINKING_ONLY` and includes `../lib/zdict.h` for `ZDICT_legacy_params_t`, `ZDICT_cover_params_t`, and `ZDICT_fastCover_params_t`. It is integrated into the zstd CLI dictionary builder rather than a general-purpose library API.

## Risks and edge cases
Because it exposes raw pointer tables and mutable parameter structs, callers must ensure all pointers remain valid for the full call and that exactly one parameter family is selected. The console-app error behavior makes it risky for embedders that require non-fatal error reporting.

## Test signals
Compile coverage should validate callers can include the header with zdict static APIs. Integration tests should call `DiB_trainFromFiles()` with each parameter family and verify output dictionary creation, error behavior for too few samples, and memory-limit handling.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/dibio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/fileio.c -->
# sources/compression/zstd/programs/fileio.c

## Purpose
`fileio.c` is the main zstd CLI file I/O implementation. It owns preference/context allocation, source and destination safety checks, dictionary loading or mapping, compression to zstd/gzip/xz/lzma/lz4 when enabled, decompression and pass-through, multi-file output routing, progress reporting, source removal, file metadata transfer, sparse output, signal cleanup, and `--list` frame analysis.

## Important APIs, types, and functions
Public functions include version probes `FIO_zlibVersion()`, `FIO_lz4Version()`, and `FIO_lzmaVersion()`; preference/context lifecycle `FIO_createPreferences()`, `FIO_freePreferences()`, `FIO_createContext()`, and `FIO_freeContext()`; many `FIO_set*()` setters; `FIO_compressFilename()`, `FIO_compressMultipleFilenames()`, `FIO_decompressFilename()`, `FIO_decompressMultipleFilenames()`, `FIO_listMultipleFiles()`, `FIO_checkFilenameCollisions()`, `FIO_displayCompressionParameters()`, and `FIO_addAbortHandler()`.

Key internal types are `FIO_ctx_t`, which tracks total file count, current index, stdin/stdout involvement, processed file count, and byte totals; `FIO_SyncCompressIO`, the compression-side buffered reader/writer; `cRess_t`, compression resources including dictionary and `ZSTD_CStream`; `dRess_t`, decompression resources including dictionary, `ZSTD_DStream`, async write pool, and async read pool; and `fileInfo_t`, the `--list` accumulator.

## Control flow
Compression creates `cRess_t` with `FIO_createCResources()`, which validates and loads/maps the dictionary, adjusts patch-from memory/window parameters if needed, initializes sync buffers, configures all zstd compression parameters, and loads or references dictionary data. Single-file compression opens the source, checks directories/dictionary collision/exclude-compressed, opens the destination with overwrite safeguards, installs the interrupt cleanup handler, and dispatches by selected output format. `FIO_compressZstdFrame()` streams source data through `ZSTD_compressStream2()` until `ZSTD_e_end`, writes output through sparse-aware sync I/O, optionally adapts compression level based on frame progression, and reports progress. Multi-file compression either writes all inputs to one output after concat warnings or derives per-file names from suffix/out-dir/mirror settings.

Decompression creates `dRess_t` with a zstd decode stream, max-window limit, dictionary reference, and async read/write pools. `FIO_decompressSrcFile()` opens a source and disables async for small files. `FIO_decompressDstFile()` opens output, transfers metadata when safe, and calls `FIO_decompressFrames()`. Frame dispatch peeks at magic numbers and selects zstd, gzip, xz/lzma, lz4, or pass-through. Zstd decompression repeatedly calls `ZSTD_decompressStream()`, writes completed output jobs, consumes input, and requests more bytes based on zstd's size hint. Multi-file decompression mirrors compression's single-output versus derived-output routing.

The `--list` flow rejects stdin, opens each regular file, scans zstd and skippable frames by seeking over headers/blocks/checksums, displays per-file metadata, and aggregates totals.

## State and persistence behavior
Persistent effects include creating/truncating output files, preserving or transferring file permissions/timestamps, optionally removing source files on successful `--rm`, deleting partial destination artifacts on interrupt or failure, writing stdout in pipe modes, and reading dictionary/source files. Global mutable state includes `g_display_prefs`, `g_displayClock`, and `g_artefact` for signal cleanup. Static destination-name buffers in `FIO_determineCompressedName()` and `FIO_determineDstName()` are reused and explicitly not thread-safe. Preferences are mutable and may be adjusted during operation, for example sparse mode can be disabled for stdout and patch-from can update memory limits.

## Dependencies and integration points
The file depends on platform and utility helpers for filesystem, permissions, timestamps, console prompts, mirrored output directories, human-readable sizes, and large-file seeking. It uses `fileio_types.h` for preferences and dictionary state, `fileio_common.h` for display/error macros, `fileio_asyncio.h` for decompression read/write pools, zstd static APIs for streaming and frame inspection, optional zlib/liblzma/lz4 frame APIs behind compile flags, and OS APIs for mmap or Windows file mapping. It is the main bridge between CLI argument parsing and compression libraries.

## Risks and edge cases
The code intentionally calls `EXM_THROW()` for many fatal paths, which exits rather than returning an error. File safety is broad but subtle: overwrite prompts depend on display level and stdin usage, stdout disables auto sparse mode, multi-input single-output disables `--rm`, and signal cleanup only tracks one artifact path. Static filename buffers make name derivation non-reentrant. Patch-from mode has strict stream-size and window-size limits. Optional format support changes behavior at compile time. `FIO_openDstFile()` mutates sparse preferences based on destination type, which can affect subsequent files sharing the same prefs. Async decompression is disabled for small files but resource objects persist across multiple files, so set/reset ordering matters.

## Test signals
High-value tests include roundtrip compression/decompression for zstd with and without dictionaries, patch-from mode, stdout/stdin paths, overwrite refusal and force overwrite, `--rm` success and failure protection, directory and non-regular source rejection, sparse output behavior, multi-file single-output warnings, output-dir and output-dir-mirror naming, exclude-compressed filtering, async small-file disablement, optional gzip/xz/lzma/lz4 behavior per build flags, pass-through mode, corrupted/truncated/unknown headers, max-window errors, and `--list` aggregation over actual plus skippable frames.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/fileio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/fileio.h -->
# sources/compression/zstd/programs/fileio.h

## Purpose
`fileio.h` declares the zstd CLI file I/O API and the compression/decompression filename conventions. It exposes preference and context handles, option setters, single-file and multi-file operations, list mode, collision checks, abort handling, and optional backend version queries.

## Important APIs, types, and functions
Constants define stdin/stdout sentinels, null output, and supported compressed suffixes such as `.zst`, `.zstd`, `.gz`, `.xz`, `.lzma`, and `.lz4` plus tar-short variants. `FIO_prefs_t` is an opaque-ish preference structure from `fileio_types.h`, while `FIO_ctx_t` is forward-declared as mutable operation context.

The header exports lifecycle functions, setters for compression type, overwrite, adaptive mode, worker count, checksum, dictionary ID, LDM, sparse write, rsyncable, stream/source size hints, test mode, literal compression mode, progress/display, exclusion of already compressed files, block device allowance, patch-from mode, content-size flag, async I/O, pass-through, and mmap dictionary mode. Operational APIs are `FIO_compressFilename()`, `FIO_decompressFilename()`, `FIO_compressMultipleFilenames()`, `FIO_decompressMultipleFilenames()`, `FIO_listMultipleFiles()`, and `FIO_checkFilenameCollisions()`.

## Control flow
The header supports a two-object setup: create preferences and context, mutate preferences/context with setters according to parsed CLI options, then call a single-file or multi-file operation. Multi-file functions accept optional output mirror directory, output directory, single output file, suffix, dictionary, compression level, and compression parameters.

## State and persistence behavior
The API controls filesystem side effects through preferences: output creation, overwrite, sparse writes, test mode, source removal, stdout/stdin, pass-through, and dictionary mapping. Context tracks multi-file progress and aggregate byte counts internally. The header itself declares no globals but includes setters for global display preferences implemented in `fileio.c`.

## Dependencies and integration points
The header depends on `fileio_types.h`, `util.h` for `FileNamesTable`, and zstd static APIs for compression parameters. It is consumed by zstd CLI command handling and abstracts the lower-level streaming, format, and filesystem behavior implemented in `fileio.c`.

## Risks and edge cases
Callers must respect sentinel names exactly for stdin/stdout, keep file-name arrays valid for the duration of calls, and understand that many errors may terminate through implementation macros rather than cleanly returning. Setter order can matter for warnings and compatibility checks, for example adaptive or rsyncable modes with worker count. Multi-file calls have several mutually exclusive output modes that the caller must populate consistently.

## Test signals
Compile-level tests should include this header from CLI code with zstd static-linking enabled. API tests should exercise preference defaults, setter effects, single versus multi-file routing, suffix constants, and display/version functions across builds with and without optional format libraries.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/fileio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/programs/fileio_asyncio.c -->
# sources/compression/zstd/programs/fileio_asyncio.c

## Purpose
`fileio_asyncio.c` implements the asynchronous read/write pool abstraction used by file decompression paths. The current backend uses one worker thread per pool when multithreading is available, while retaining the same API for synchronous fallback and future OS-specific async implementations.

## Important APIs, types, and functions
The public functions are `AIO_supported()`, write-pool lifecycle and operations (`AIO_WritePool_create()`, `AIO_WritePool_free()`, `AIO_WritePool_setFile()`, `AIO_WritePool_getFile()`, `AIO_WritePool_acquireJob()`, `AIO_WritePool_enqueueAndReacquireWriteJob()`, `AIO_WritePool_releaseIoJob()`, `AIO_WritePool_sparseWriteEnd()`, `AIO_WritePool_closeFile()`, `AIO_WritePool_setAsync()`), and read-pool lifecycle and operations (`AIO_ReadPool_create()`, `AIO_ReadPool_free()`, `AIO_ReadPool_setFile()`, `AIO_ReadPool_getFile()`, `AIO_ReadPool_fillBuffer()`, `AIO_ReadPool_consumeBytes()`, `AIO_ReadPool_consumeAndRefill()`, `AIO_ReadPool_closeFile()`, `AIO_ReadPool_setAsync()`).

The generic internal layer is built around `IOPoolCtx_t` and `IOJob_t`. `AIO_IOPool_init()` creates jobs and optional thread pool, `AIO_IOPool_acquireJob()` and `AIO_IOPool_releaseIoJob()` manage the free-list, `AIO_IOPool_enqueueJob()` either submits to `POOL_add()` or runs synchronously, and `AIO_IOPool_setFile()` gates file changes on all jobs being completed.

## Control flow
Write jobs are acquired, filled by caller code, and enqueued. `AIO_WritePool_executeWriteJob()` writes through `AIO_fwriteSparse()`, updates `storedSkips`, and releases the job. Sparse writes accumulate zero-run skips and finalize the last zero byte in `AIO_fwriteSparseEnd()`.

Read pools enqueue reads immediately when a file is set. Each read job records an offset. Completed reads are appended to a completed-job list, and `AIO_ReadPool_getNextCompletedJob()` waits for the job matching `waitingOnOffset`, preserving logical input order even if a future backend completes out of order. `AIO_ReadPool_fillBuffer()` exposes either a job buffer directly or coalesces leftover bytes plus the next job into a separate buffer when the caller needs a contiguous minimum.

## State and persistence behavior
Persistent effects are limited to reading from and writing to the currently configured `FILE*`, closing files through close helpers, and sparse seek/write behavior. Runtime state includes available job stacks, completed read jobs, thread-pool active flag, mutex/condition variables, current held read job, read offsets, EOF flag, coalesced buffer, source buffer pointer/length, and write sparse skip count. File changes require all jobs to be joined and all acquired jobs released.

## Dependencies and integration points
The file depends on `fileio_asyncio.h`, `fileio_common.h` for display/error macros and sparse seek helpers, `platform.h`, zstd threading and pool abstractions, and `FIO_prefs_t` options such as `asyncIO`, `testMode`, and `sparseFileSupport`. `fileio.c` uses write pools and read pools in decompression and pass-through paths.

## Risks and edge cases
Threaded mode depends on `ZSTD_MULTITHREAD`; otherwise `AIO_supported()` is false and work runs synchronously. `ctx->storedSkips` is updated by write jobs and therefore relies on serialized execution; changing the pool to multiple write workers would need stronger ordering. Several invariants are asserted rather than recovered, such as available job counts and file state. Read completion scans a small fixed array, which is fine for `MAX_IO_JOBS` but should stay bounded. `AIO_WritePool_closeFile()` assumes a real file unless test mode is active; callers must not close stdout unexpectedly outside intended paths.

## Test signals
Tests should cover sync and async modes, switching async on/off after jobs have drained, ordered reads with multiple in-flight jobs, partial-buffer coalescing, EOF handling, read errors, sparse write zero-run finalization, test mode no-output behavior, small and large file decompression through `fileio.c`, and cleanup assertions that all jobs return before pool destruction.
<!-- END_FILE_RESEARCH: sources/compression/zstd/programs/fileio_asyncio.c -->
