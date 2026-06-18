# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/RSErasureEncoder.java

Purpose: high-level Reed-Solomon encoder that creates an `ErasureEncodingStep` backed by a raw RS encoder.

Important APIs and control flow: `prepareEncodingStep()` lazily creates a raw RS encoder via `CodecUtil.createRawEncoder(..., RS_CODEC_NAME, ...)`, selects data/parity blocks, and returns `ErasureEncodingStep`. `release()` releases the cached raw encoder. `preferDirectBuffer()` returns false despite possible native raw coder preference.

State and persistence: caches one raw encoder reference; no persistence.

Dependencies and integration: extends `ErasureEncoder`; raw coder choice comes from configuration/registry.

Risks and test signals: test raw coder fallback, cached encoder reuse, release, and parity output correctness across heap/direct chunks. The TODO about codec-specific raw coder selection should be tracked for `rs-legacy`.
