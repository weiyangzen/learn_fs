# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCodeLoader.c

## Purpose
`NativeCodeLoader.c` implements small JNI probes used by Java to discover which optional native features were compiled into the Hadoop native library and where the loaded native library resides.

## Important APIs, types, and functions
Exported JNI methods are `buildSupportsSnappy`, `buildSupportsOpenssl`, `buildSupportsIsal`, and `getLibraryName`. The feature probes return `JNI_TRUE` only when build-time macros `HADOOP_SNAPPY_LIBRARY`, `HADOOP_OPENSSL_LIBRARY`, or `HADOOP_ISAL_LIBRARY` are present. `getLibraryName` uses `dladdr` on Unix and `GetLibraryName` on Windows.

## Control flow
Each support method is compile-time branching only. `getLibraryName` asks the runtime loader for the module that contains the JNI function pointer and returns the path as a Java string, or `"Unavailable"` if the platform lookup fails.

## State and persistence
There is no mutable state. Results reflect compile-time options and the current process's loaded native module path.

## Dependencies and integration points
The file integrates Java `NativeCodeLoader` with native build configuration, optional compression/crypto/erasure-code libraries, `dladdr`, and Windows winutils helpers. Java code uses these methods to gate native accelerators and diagnostics.

## Risks and test signals
Risks include mismatches between build macros and actually loadable optional libraries, platform-specific path encoding, and missing return path if an unsupported platform macro set is used. Test signals include native builds with each optional feature on/off, Unix and Windows `getLibraryName` calls, and Java fallback behavior when support probes return false.
