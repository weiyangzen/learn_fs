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
