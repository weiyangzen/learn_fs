# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncodingStep.java

Purpose: concrete encoding step that delegates parity generation to a `RawErasureEncoder`.

Important APIs and control flow: constructor stores input/output blocks and raw encoder. `performCoding()` calls `rawEncoder.encode(inputChunks, outputChunks)`. Getters expose block arrays. `finish()` is a no-op in this source version.

State and persistence: holds block arrays and raw encoder reference. No persistence.

Dependencies and integration: created by high-level encoders and invoked by chunk-level EC execution.

Risks and test signals: test chunk length validation through raw encoders and output chunk mutation. Resource lifecycle must be handled by owning coders or future changes because this step's `finish()` currently does not release the raw encoder.
