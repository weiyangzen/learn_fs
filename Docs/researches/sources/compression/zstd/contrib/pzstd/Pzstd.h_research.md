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
