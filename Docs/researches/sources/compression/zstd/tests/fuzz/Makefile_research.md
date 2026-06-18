# sources/compression/zstd/tests/fuzz/Makefile

## Purpose
This Makefile builds zstd fuzz targets and seed corpora support artifacts. It can build regression-driver linked targets by default or link against an external fuzzing engine.

## Targets, variables, and control flow
It includes `../../lib/libzstd.mk`, derives include flags for lib, programs, seekable format, and external sequence producer code, and defines warning/sanitizer-friendly compile flags. `FUZZ_SRC` combines fuzz helpers, zstd common/compress/decompress/dict/legacy sources, `util.c`, and the default sequence producer. It builds two object families: round-trip objects with `-DFUZZING_ASSERT_VALID_SEQUENCE` and decompression objects without it. `FUZZ_TARGETS` lists all fuzz binaries, including the targets researched in this subset. Pattern rules compile source-origin-prefixed object names; target rules link each fuzzer with C++ and `$(LIB_FUZZING_ENGINE)`. It also builds `libregression.a` from `regression_driver.o`, downloads/unzips corpora, and cleans generated objects/binaries.

## State, dependencies, risks, and test signals
State includes many generated `.o` files, fuzzer executables, `libregression.a`, and optional `corpora/` archives. Dependencies are make, C/C++ compilers, archiver, zstd source layout, optional network tools for corpora, and optional `THIRD_PARTY_SEQ_PROD_OBJ`. Risks include object-name substitution fragility, stale object families after flag changes, and C files linked by C++ requiring compatibility flags. Pass signals are successful `make all`, individual target builds, and regression execution via `fuzz.py`.
