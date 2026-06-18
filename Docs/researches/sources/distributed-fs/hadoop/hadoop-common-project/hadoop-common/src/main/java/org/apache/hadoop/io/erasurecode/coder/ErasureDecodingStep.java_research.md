# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecodingStep.java

Purpose: concrete decoding step that delegates chunk reconstruction to a `RawErasureDecoder`.

Important APIs and control flow: constructor stores input/output blocks, erased indexes, and raw decoder. `performCoding()` calls `rawDecoder.decode(inputChunks, erasedIndexes, outputChunks)`. Getters expose block arrays. `finish()` is only a TODO placeholder and does not release the raw decoder in this source version.

State and persistence: holds references to block arrays, erased indexes, and raw decoder resource. No persistence.

Dependencies and integration: created by high-level decoders and consumed by EC callers with chunk buffers.

Risks and test signals: verify erased-index/output-chunk alignment and raw decoder error propagation as `IOException`. Resource lifecycle must be handled by owning coders or future changes because this step's `finish()` currently does not release the raw decoder.
