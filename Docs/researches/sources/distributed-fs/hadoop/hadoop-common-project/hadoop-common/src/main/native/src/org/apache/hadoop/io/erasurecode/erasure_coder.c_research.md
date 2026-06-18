<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.c

## Purpose
`erasure_coder.c` implements Hadoop's native Reed-Solomon encode/decode control logic on top of ISA-L GF and erasure-code primitives. It builds Cauchy encode matrices, prepares decode matrices, caches decoder state, and invokes ISA-L vector operations.

## Important APIs, Types, and Functions
Implemented APIs are `initCoder()`, `allowVerbose()`, `initEncoder()`, `initDecoder()`, `encode()`, `decode()`, `clearDecoder()`, and `generateDecodeMatrix()`. Internal helpers include `initEncodeMatrix()`, `compare()`, and `processErasures()`.

## Control Flow
Encoder initialization creates a Cauchy encode matrix and precomputes parity tables from rows below the data identity portion. `encode()` zeros parity outputs and calls `h_ec_encode_data()`. Decoder initialization builds the same encode matrix. Each decode call maps available non-null inputs into `decodeIndex`, skips matrix regeneration when the erasure pattern is unchanged, otherwise clears per-call state, records erased indexes, inverts the selected data matrix, builds rows for missing data or parity, initializes GF tables, and calls `h_ec_encode_data()` to reconstruct outputs.

## State and Persistence
`IsalEncoder` persists the encode matrix and parity `gftbls`. `IsalDecoder` persists encode matrix plus cached decode indexes, erasure flags, erased indexes, temporary/invert/decode matrices, generated tables, and real input pointers. This state lives inside native coder objects owned by Java and freed by JNI wrappers.

## Dependencies and Integration Points
It depends on `gf_util`, `erasure_code`, `dump`, and `erasure_coder.h`. JNI encoder/decoder files allocate wrapper structs embedding `IsalEncoder` or `IsalDecoder`.

## Risks and Edge Cases
`MMAX` and `KMAX` statically bound all arrays; Java must not request configurations beyond those limits. `decode()` ignores the return from `processErasures()`, so matrix-generation failures do not stop recovery. `generateDecodeMatrix()` does not check the invert return value. Null input handling assumes enough non-null inputs are present.

## Test Signals
Tests should cover RS encode known answers, single and multiple erased data/parity recovery, repeated decode with identical erasures to exercise caching, oversized data/parity unit rejection in Java, and failure cases for too many erasures or insufficient inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.c -->
