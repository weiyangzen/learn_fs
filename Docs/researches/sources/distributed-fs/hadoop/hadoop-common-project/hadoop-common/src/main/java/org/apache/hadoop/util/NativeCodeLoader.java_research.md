# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCodeLoader.java

## Purpose

`NativeCodeLoader` loads Hadoop's native library and exposes whether native code and build features are available.

## Important APIs, Types, And Functions

Static initialization attempts to load the Hadoop native library and records `nativeCodeLoaded`. Public APIs include `isNativeCodeLoaded()`, `getLibraryName()`, `buildSupportsIsal()`, and `buildSupportsOpenssl()`.

## Control Flow, State, And Persistence

Class loading performs a one-time native-library load, logs success or failure, and stores the result in static fields. Feature queries are native methods and should only be used when the library is loaded by callers that can tolerate native linkage failures. State is JVM-static native load status; persistence is outside the process in installed shared libraries.

## Dependencies And Integration Points

It depends on SLF4J and native JNI symbols packaged with Hadoop. Compression, crypto, erasure coding, native I/O, and `NativeLibraryChecker` use it to decide whether to use accelerated paths.

## Risks And Test Signals

Static initialization is one-shot per classloader, so tests need classloader isolation or careful assumptions. Missing/incorrect native libraries degrade features or fail checks. Tests should cover no-native fallback, library-name reporting when loaded, feature false paths, and logging.
