
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/PassthroughCodec.java

## Purpose
`PassthroughCodec` is a special read-only codec that registers an extension but performs no decompression. It lets jobs disable automatic decompression for files whose extension would otherwise map to a real codec.

## Important APIs and Types
It implements `Configurable` and `CompressionCodec`. Public constants are `CLASSNAME`, `OPT_EXTENSION`, and `DEFAULT_EXTENSION`. Nested `PassthroughDecompressorStream` delegates reads/skips/availability directly to the wrapped input. Nested `StubDecompressor` satisfies the codec interface but performs no real decompression.

## Control Flow
`setConf()` reads `io.compress.passthrough.extension`, prepending a dot if needed. `getDefaultExtension()` returns and logs the registered fake extension. All output/compressor APIs throw `UnsupportedOperationException`. Input stream creation returns a passthrough stream regardless of the supplied decompressor.

## State and Persistence
State is the configuration and selected extension string. The stream keeps the original input stream reference and does not maintain decompression state.

## Dependencies and Integration
Designed for `io.compression.codecs` registration and `CompressionCodecFactory` suffix selection. It intentionally does not implement `SplittableCompressionCodec`.

## Risks
This codec only disables decompression; it does not validate that bytes are compressed or uncompressed. Registering it for a common extension like `.gz` changes job semantics globally for that factory configuration. Output APIs are unsupported and will fail if used by writers.

## Test Signals
Coverage is mainly through codec factory behavior and consumers that configure passthrough. The class has clear unsupported-operation paths that should be tested when used in write-capable contexts.
