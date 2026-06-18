<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.c

## Purpose
`jni_common.c` provides shared JNI utilities for the native erasure-code raw coders. It loads ISA-L, stores/retrieves native coder pointers, and maps Java direct-buffer arrays plus offsets to native pointer arrays.

## Important APIs, Types, and Functions
Functions are `loadLib()`, `setCoder()`, `getCoder()`, `getInputs()`, and `getOutputs()`. They operate on Java fields/methods `nativeCoder` and `allowVerboseDump()`.

## Control Flow
`loadLib()` delegates to `load_erasurecode_lib()` and throws `UnsatisfiedLinkError` if an error string is returned. `setCoder()` locates the Java `nativeCoder` field and stores a native pointer. `getCoder()` reads verbosity through a Java callback, gets `nativeCoder`, and updates the native coder's verbose flag. `getInputs()` and `getOutputs()` validate array lengths, copy Java int offsets, obtain each direct buffer address, add offsets, and fill native pointer arrays.

## State and Persistence
No static state is owned here. Native coder pointers persist in Java object fields, while buffer pointer arrays are per-call data owned by wrapper structs.

## Dependencies and Integration Points
It depends on ISA-L loading, `erasure_coder.h`, JNI direct buffers, and Java raw-coder classes. All RS/XOR JNI files use these utilities.

## Risks and Edge Cases
The buffer helpers do not check `GetDirectBufferAddress()` for null before offset arithmetic, so non-direct buffers can cause invalid pointers. Local references from `GetObjectArrayElement()` are not deleted in the loops. If an exception is thrown during field/method lookup, later code may continue unless callers check pending exceptions.

## Test Signals
Tests should cover null native coder after destroy, non-direct buffers, bad array lengths, offset handling, verbose mode propagation, missing `nativeCoder` field, and library-load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.c -->
