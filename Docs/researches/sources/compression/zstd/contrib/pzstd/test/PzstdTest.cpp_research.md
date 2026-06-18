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
