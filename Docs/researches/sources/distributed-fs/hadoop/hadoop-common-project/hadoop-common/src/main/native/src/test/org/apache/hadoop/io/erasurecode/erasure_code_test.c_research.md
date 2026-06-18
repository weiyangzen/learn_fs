# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/io/erasurecode/erasure_code_test.c

## Purpose
`erasure_code_test.c` is a native smoke and correctness test for Hadoop's ISA-L erasure coding bridge. It demonstrates encoder/decoder use and verifies that combinations of up to three missing data/parity units can be reconstructed.

## Important APIs, types, and functions
The test calls `build_support_erasurecode`, `load_erasurecode_lib`, `initEncoder`, `encode`, `initDecoder`, `decode`, and `dumpDecoder`. It uses `IsalEncoder`, `IsalDecoder`, data/parity unit arrays, and ISA-L headers such as `erasure_code.h`, `gf_util.h`, and `erasure_coder.h`.

## Control flow
The test skips successfully if native erasure coding is not compiled in. Otherwise it loads ISA-L, allocates six data units and three parity units of 1024 bytes, fills data with deterministic pseudo-random bytes, encodes parity, builds an `allUnits` array, and exhaustively iterates triples of erased indexes. For one, two, or three distinct erased units it nulls the inputs, decodes into output buffers, compares reconstructed bytes to backups, restores pointers, and fails on any mismatch.

## State and persistence
All state is heap memory local to the process. The test does not persist outputs. It intentionally leaks some allocations at process exit, which is acceptable for a short test binary but not a reusable library pattern.

## Dependencies and integration points
It depends on Hadoop's native ISA-L loader/wrapper and the external ISA-L erasure coding library. It is built and run by the native test configuration when ISA-L support is present.

## Risks and test signals
Risks include insufficient allocation failure checks, no cleanup, fixed coding parameters, and only deterministic random data. Passing the test signals basic encode/decode correctness for RS(6,3) with chunk size 1024 and up to three erasures, plus successful dynamic loading of the erasure coding library.
