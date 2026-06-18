<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_erasure_code_native.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_erasure_code_native.c

## Purpose
`jni_erasure_code_native.c` exposes global native ISA-L erasure-code library operations to Java.

## Important APIs, Types, and Functions
JNI exports are `ErasureCodeNative.loadLibrary()` and `ErasureCodeNative.getLibraryName()`.

## Control Flow
`loadLibrary()` calls shared `loadLib()`, which initializes the ISA-L loader or throws `UnsatisfiedLinkError`. `getLibraryName()` checks `isaLoader` and throws if the library has not been loaded; otherwise it returns the stored resolved library name as a Java string.

## State and Persistence
It reads global `isaLoader` initialized by `isal_load.c`. No additional state is stored.

## Dependencies and Integration Points
It depends on `jni_common.h`, `isal_load.h`, and Java `ErasureCodeNative`. Java callers should invoke `loadLibrary()` before native raw coders are used.

## Risks and Edge Cases
If the loader is partially initialized after a failed load, `getLibraryName()` behavior depends on `isaLoader->libname` being set. There is no unload path.

## Test Signals
Tests should cover library-name calls before and after load, missing-library errors, and successful native RS/XOR coder creation after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_erasure_code_native.c -->
