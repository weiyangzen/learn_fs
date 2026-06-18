<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_decoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_decoder.c

## Purpose
`jni_rs_decoder.c` is the JNI wrapper for Hadoop's native Reed-Solomon raw decoder.

## Important APIs, Types, and Functions
It defines wrapper struct `RSDecoder` containing `IsalDecoder decoder` plus input and output pointer arrays. JNI exports are `initImpl()`, `decodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates and zeroes `RSDecoder`, initializes the embedded decoder, and stores the pointer in Java `nativeCoder`. `decodeImpl()` retrieves the native coder, rejects use after close, reads erased indexes, maps all data/parity input direct buffers and output buffers, calls `decode()`, and releases the erased-index array. `destroyImpl()` frees the wrapper and clears the Java native pointer.

## State and Persistence
The embedded `IsalDecoder` persists across decode calls and caches decode matrices for repeated erasure patterns. Java owns the lifecycle through the native pointer field.

## Dependencies and Integration Points
It depends on `jni_common`, `erasure_coder`, and Java `NativeRSRawDecoder`. It reconstructs erased data or parity chunks into Java direct output buffers.

## Risks and Edge Cases
`malloc` is not checked before `memset`. If `decode()` fails internally, the JNI wrapper does not inspect a return code. Direct-buffer validity and erased-index bounds are assumed to be validated by Java.

## Test Signals
Tests should cover single/multiple erased data and parity chunks, repeated erasure patterns, decode after destroy, invalid erased indexes, and insufficient available inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_decoder.c -->
