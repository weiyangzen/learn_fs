# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecoder.java

Purpose: high-level Hitchhiker-XOR decoder that composes RS raw decoding with XOR raw encoding for piggyback recovery.

Important APIs and control flow: lazily creates and caches an RS raw decoder and XOR raw encoder through `CodecUtil`. `prepareDecodingStep()` builds concatenated input blocks, erased indexes, output blocks, and returns `HHXORErasureDecodingStep`. `release()` releases both cached raw coders.

State and persistence: caches raw decoder/encoder references in memory. No persistence.

Dependencies and integration: extends `ErasureDecoder`, uses `ErasureCodeConstants.RS_CODEC_NAME` and `XOR_CODEC_NAME`, and delegates complex recovery to HH-XOR decoding step.

Risks and test signals: test cached raw coder reuse and release, native/raw fallback selection, and erased-index/output alignment for single and multiple erasures. The raw coder configuration must be present for both RS and XOR.
