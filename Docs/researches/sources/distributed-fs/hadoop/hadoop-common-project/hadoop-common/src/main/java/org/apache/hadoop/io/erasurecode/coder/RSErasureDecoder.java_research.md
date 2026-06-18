# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureDecoder.java

Purpose: high-level Reed-Solomon decoder that creates an `ErasureDecodingStep` backed by a raw RS decoder.

Important APIs and control flow: `prepareDecodingStep()` obtains input/output block arrays, lazily creates a raw decoder through `CodecUtil.createRawDecoder(..., RS_CODEC_NAME, ...)`, and returns `ErasureDecodingStep` with erased indexes. `release()` releases the cached raw decoder.

State and persistence: caches one raw decoder reference; no persistence.

Dependencies and integration: extends `ErasureDecoder` and relies on `CodecUtil`/`CodecRegistry` raw coder fallback.

Risks and test signals: test all erased-index combinations up to parity count, raw coder fallback, release behavior, and configuration propagation. A TODO in the paired encoder notes codec-specific raw coder selection may need refinement.
