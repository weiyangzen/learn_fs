# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodeNative.java

Purpose: native erasure-code library availability probe and library-name accessor.

Important APIs and control flow: static initialization checks `NativeCodeLoader.isNativeCodeLoaded()`, calls native `initIDs()`, and sets `nativeLoaded` based on success. `checkNativeCodeLoaded()` throws a `RuntimeException` when unavailable. `isNativeCodeLoaded()` exposes the boolean, and `getLibraryName()` is native.

State and persistence: static boolean `nativeLoaded` is process-local. No persistence.

Dependencies and integration: used by native raw coder implementations and factories to determine ISA-L/native support. Depends on Hadoop native loader and JNI symbols.

Risks and test signals: test no-native and native-loaded paths, error messages from `checkNativeCodeLoaded()`, and library-name availability. Static initialization can hide root causes because it catches `Throwable`.
