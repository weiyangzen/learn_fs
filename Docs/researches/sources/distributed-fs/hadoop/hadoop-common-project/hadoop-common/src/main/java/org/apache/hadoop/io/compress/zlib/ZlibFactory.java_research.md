# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibFactory.java

Purpose: central factory and configuration helper for choosing native or built-in zlib compressor/decompressor implementations.

Important APIs and control flow: static initialization calls `loadNativeZLib()`, which checks `NativeCodeLoader` plus native zlib compressor/decompressor readiness and logs success/failure. Factory methods return native `ZlibCompressor`/`ZlibDecompressor` or Java `BuiltInZlibDeflater`/`BuiltInZlibInflater`. Direct decompression is available only for native zlib. Setter/getter methods store compression strategy and level as enum values in `Configuration`.

State and persistence: a static boolean `nativeZlibLoaded` controls factory choices; `setNativeZlibLoaded()` exists for tests. Configuration keys persist only in caller-provided `Configuration`.

Dependencies and integration: integrates Hadoop compression codecs with native zlib, Java fallback classes, `Configuration`, `NativeCodeLoader`, and `DirectDecompressor`.

Risks and test signals: test native-loaded and native-disabled branches, direct decompressor null fallback, configuration round trips, and library-name access when native is absent. Static mutable state must be isolated in tests.
