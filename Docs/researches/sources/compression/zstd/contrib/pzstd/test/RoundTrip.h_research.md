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
