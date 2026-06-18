
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Compressor.java

## Purpose
`Compressor` is the pluggable streaming compression engine interface used by `CompressorStream`, `BlockCompressorStream`, and `CodecPool`.

## Important APIs and Types
Methods include `setInput`, `needsInput`, `setDictionary`, `getBytesRead`, `getBytesWritten`, `finish`, `finished`, `compress`, `reset`, `end`, and `reinit(Configuration)`.

## Control Flow
Callers feed input when `needsInput()` is true, request finalization with `finish()`, drain compressed output using `compress()`, then either `reset()` for another stream or `end()` for permanent cleanup. `reinit()` lets pooled compressors adopt a new configuration before reuse.

## State and Persistence
Implementations own all compression state, byte counters, direct/native resources, and pending input/output buffers. The interface does not persist data itself.

## Dependencies and Integration
Implemented by zlib, gzip, Snappy, LZ4, ZStandard, native bzip2, and dummy bzip2 compressor classes. `CodecPool` relies on `reset`, `reinit`, and implementation class identity.

## Risks
Counter semantics are part of higher-level framing: `BlockCompressorStream` depends on `getBytesRead()` for block lengths. Incorrect `finished()` or `needsInput()` behavior can hang stream loops. `end()` must make native resources unreachable without leaving reusable pooled instances in a bad state.

## Test Signals
Codec-specific compressor/decompressor tests, `TestCodecPool`, block stream tests, and native bzip2 tests cover expected lifecycle transitions.
