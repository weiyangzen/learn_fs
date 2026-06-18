<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_encoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_encoder.c

## Purpose
`jni_xor_encoder.c` implements the JNI wrapper for Hadoop's native XOR raw encoder.

## Important APIs, Types, and Functions
It defines `XOREncoder`, containing an `IsalCoder`, data input pointers, and parity output pointers. JNI exports are `initImpl()`, `encodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates and initializes basic unit counts. `encodeImpl()` retrieves the native coder, maps direct-buffer inputs and outputs, copies the first input chunk into `outputs[0]`, then XORs each remaining data input into that parity buffer. `destroyImpl()` frees and clears the native pointer.

## State and Persistence
The native object persists only unit-count metadata and reusable pointer arrays. No matrices or dynamic libraries are involved in the XOR algorithm itself.

## Dependencies and Integration Points
It uses `jni_common` and Java `NativeXORRawEncoder`. It shares the same raw-coder lifecycle as the RS JNI wrappers.

## Risks and Edge Cases
The code assumes at least one data input and one parity output. It only writes the first parity output, so Java must restrict XOR coding to one parity unit. Allocation and non-direct-buffer failures are not fully guarded.

## Test Signals
Parity known-answer tests, offset tests, repeated encode calls, closed-coder error handling, and Java validation for parity count are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_encoder.c -->
