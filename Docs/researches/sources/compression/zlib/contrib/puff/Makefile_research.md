# sources/compression/zlib/contrib/puff/Makefile

## Purpose
This makefile provides a simple non-CMake build and coverage test workflow for the `puff` deflate decompressor.

## Important APIs, Types, and Functions
Targets include `puff`, object dependencies for `puff.o` and `pufftest.o`, smoke `test`, coverage binary `puft`, coverage target `cov`, and `clean`. It uses `cc`, `gcov`, `xxd`, shell pipelines, and raw byte sequences.

## Control Flow
The default `puff` target links `puff.o` and `pufftest.o`. `test` runs `puff zeros.raw`. `puft` builds with GCC coverage flags. `cov` removes old coverage files, runs many valid and invalid deflate byte streams through `puft`, checks expected exit codes for malformed cases, and finally runs `gcov -n puff.c`. `clean` removes binaries, objects, and coverage output.

## State and Persistence
Creates local binaries (`puff`, `puft`), object files, `.gcov`, `.gcda`, and `.gcno` files. The coverage target reads `zeros.raw` and generated binary stdin streams.

## Dependencies and Integration Points
Integrates with `puff.c`, `puff.h`, `pufftest.c`, `zeros.raw`, `xxd`, POSIX shell, and gcov. It is a lightweight alternative to the CMake test setup.

## Risks and Edge Cases
The coverage target assumes `xxd`, `gcov`, and shell exit-code semantics. It hardcodes expected return codes from `pufftest`, so changes to error-code mapping require updates. `CFLAGS=-O` is minimal and may not reflect production warnings or sanitizer settings.

## Test Signals
The `cov` target is a strong branch/error-path signal: it feeds crafted deflate inputs expected to exercise success and many failure paths, then reports coverage for `puff.c`.
