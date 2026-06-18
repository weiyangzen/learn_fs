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
