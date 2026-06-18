<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.h

## Purpose
`jni_common.h` declares shared JNI utility functions for native erasure-code raw coders.

## Important APIs, Types, and Functions
It exposes `loadLib()`, `setCoder()`, `getCoder()`, `getInputs()`, and `getOutputs()`, plus includes JNI and `erasure_coder.h`.

## Control Flow
There is no runtime flow in the header. It defines the utility surface that RS and XOR native wrappers call during initialization, encode/decode, and destruction.

## State and Persistence
No state is declared here except the native pointer contract implied by `setCoder()`/`getCoder()`.

## Dependencies and Integration Points
It sits between Java raw-coder classes and native erasure-code structs.

## Risks and Edge Cases
Consumers must pass arrays of the expected sizes and direct buffers. The header does not encode constness or ownership, so misuse can corrupt Java-owned buffers.

## Test Signals
Compile tests for all JNI coder files and runtime encode/decode tests with offset arrays validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.h -->
