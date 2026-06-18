# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCodeLoader.java

Purpose: environment-gated verification that Hadoop native code loading is available when the test run explicitly requires it.

Important APIs and types: `NativeCodeLoader.isNativeCodeLoaded`, `getLibraryName`, `buildSupportsOpenssl`, `ZlibFactory.getLibraryName`, `OpensslCipher.getLibraryName`, and system property `require.test.libhadoop`.

Control flow: if `require.test.libhadoop` is absent or false, the test logs and returns. If required, it fails when libhadoop is not loaded, then asserts native Hadoop and zlib library names are non-empty and OpenSSL library name is available when the build reports OpenSSL support.

State and persistence: reads JVM system properties and native loader static state; no files are written.

Dependencies and integration points: validates native library integration for compression and crypto paths without making the whole suite require native artifacts by default.

Risks: CI environments differ in native library availability, names are platform-specific, and forcing the property can expose build/linker issues. Test signals are a conditional `fail` plus non-empty library-name assertions.
