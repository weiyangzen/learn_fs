# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibDeflater.java

Purpose: wrapper that adapts Java `Deflater` to Hadoop's `Compressor` interface for non-native zlib compression.

Important APIs and control flow: constructors mirror `Deflater` constructors. `compress()` delegates to `deflate(byte[],int,int)`. `reinit(Configuration)` resets, applies configured compression level, applies configured strategy when Java supports it, and falls back to `DEFAULT_STRATEGY` with a warning if unsupported.

State and persistence: inherited `Deflater` stream state is the only runtime state. No persistent storage.

Dependencies and integration: used by `ZlibFactory` when native zlib is not loaded. Implements `Compressor` and reads compression options through `ZlibFactory`.

Risks and test signals: test native-disabled fallback, unsupported strategy warnings, `reinit(null)`, and equivalence with `ZlibCompressor` for ordinary zlib streams. Callers must still invoke inherited `end()` to release native JDK zlib resources.
