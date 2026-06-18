<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_decoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_decoder.c

## Purpose
`jni_xor_decoder.c` implements the JNI wrapper for Hadoop's native XOR raw decoder, used for single-parity XOR reconstruction.

## Important APIs, Types, and Functions
It defines `XORDecoder` with an `IsalCoder`, input pointer array, and output pointer array. JNI exports are `initImpl()`, `decodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates and initializes the basic coder state. `decodeImpl()` retrieves the coder, maps all data plus parity inputs and output buffers, zeroes the first output, then XORs every non-null input byte into that output. `destroyImpl()` frees the native wrapper and clears the Java pointer.

## State and Persistence
Only the basic unit counts persist in `IsalCoder`; no GF tables are needed. Pointer arrays are per-call state inside the wrapper.

## Dependencies and Integration Points
It depends on `jni_common` for direct-buffer mapping and Java `NativeXORRawDecoder`.

## Risks and Edge Cases
Only `outputs[0]` is reconstructed, matching single-parity XOR assumptions. Erased indexes are accepted in the signature but not used directly. Allocation and direct-buffer failures are not robustly checked.

## Test Signals
Tests should cover recovery of any single missing data/parity chunk, decode after destroy, null inputs for erased chunks, offset correctness, and invalid multi-parity configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_decoder.c -->
