<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_encoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_encoder.c

## Purpose
`jni_rs_encoder.c` is the JNI wrapper for Hadoop's native Reed-Solomon raw encoder.

## Important APIs, Types, and Functions
It defines `RSEncoder`, embedding `IsalEncoder encoder` and arrays of input/output pointers. JNI exports are `initImpl()`, `encodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates, zeroes, initializes the encoder, and stores the native pointer in Java. `encodeImpl()` retrieves the coder, rejects closed instances, maps data inputs and parity outputs from direct-buffer arrays plus offsets, and calls `encode()`. `destroyImpl()` frees the native wrapper and clears `nativeCoder`.

## State and Persistence
The `IsalEncoder` stores encode matrix and GF tables for reuse across calls. Pointer arrays are overwritten on each encode call.

## Dependencies and Integration Points
It integrates Java `NativeRSRawEncoder` with `erasure_coder.c` and ISA-L through `jni_common`.

## Risks and Edge Cases
Allocation failure is not checked. Java must guarantee input/output array sizes, direct buffers, valid offsets, and supported data/parity counts. Encode return value is ignored.

## Test Signals
Known-answer parity tests, offset handling, repeated calls, closed-coder errors, non-direct buffer rejection, and max-unit boundary tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_encoder.c -->
