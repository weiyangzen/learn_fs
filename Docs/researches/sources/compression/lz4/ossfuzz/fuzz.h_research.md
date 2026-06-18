# sources/compression/lz4/ossfuzz/fuzz.h

## Purpose
`fuzz.h` defines the common libFuzzer-style entry point signature and shared compile-time fuzzing parameters for LZ4 fuzz targets.

## Important APIs, Types, And Functions
The key declaration is `int LLVMFuzzerTestOneInput(const uint8_t *src, size_t size);`. The file also defines `FUZZ_RNG_SEED_SIZE` with a default of 4 bytes and documents build macros such as `LZ4_DEBUG`, `LZ4_FORCE_MEMORY_ACCESS`, and `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`.

## Control Flow
There is no runtime control flow. The preprocessor supplies default seed size when a build system has not provided one, and the C++ guard keeps the entry-point declaration linkable from C++ fuzzing engines.

## State, Persistence, And Dependencies
The file holds no state. It depends on `stddef.h` and `stdint.h` for the fuzzer signature.

## Integration Points
Every fuzz target or standalone engine includes this interface either directly or through `fuzz_helpers.h`. OSS-Fuzz and libFuzzer discover `LLVMFuzzerTestOneInput()` through this ABI.

## Risks
The comments refer to zstd in a couple of places even though this is LZ4, which can mislead maintainers about macro names. Changing `FUZZ_RNG_SEED_SIZE` changes corpus interpretation because helpers consume that many leading bytes as deterministic seed material.

## Test Signals
Build signals include C and C++ compilation, custom `FUZZ_RNG_SEED_SIZE` builds, and standalone engine linkage against a target implementing `LLVMFuzzerTestOneInput()`.
