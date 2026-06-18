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
