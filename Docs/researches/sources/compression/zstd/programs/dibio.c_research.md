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
