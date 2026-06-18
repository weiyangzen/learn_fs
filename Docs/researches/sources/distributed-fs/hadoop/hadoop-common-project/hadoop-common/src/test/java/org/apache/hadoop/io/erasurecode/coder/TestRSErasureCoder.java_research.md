
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestRSErasureCoder.java

Purpose: Tests block-level Reed-Solomon encoder and decoder behavior under several data/parity widths, erasure patterns, buffer types, and raw-coder configuration.

Important APIs and types: Uses `RSErasureEncoder`, `RSErasureDecoder`, inherited `TestErasureCoderBase`, `CodecUtil.IO_ERASURECODE_CODEC_RS_RAWCODERS_KEY`, and `RSRawErasureCoderFactory.CODER_NAME`.

Control flow: `setup()` chooses coder classes and ten chunks per synthetic block. Tests prepare layouts such as 10x4, 6x3, and 3x3, erase data blocks, parity blocks, or mixed sets, and invoke inherited encode/decode/compare flow. Some tests call `testCoding()` repeatedly or alternate direct and heap buffers.

State and persistence: Per-test in-memory block groups are mutated through erased flags and null chunk arrays. Class timeout is 300 seconds.

Dependencies and integration points: Exercises block-level RS over the raw-coder selection path, including configuration that forces the Java RS raw coder.

Risks: The matrix is order- and reuse-sensitive, so shared internal buffers in RS coders are a key failure point. It does not test invalid constructor options.

Test signals: Strong regression coverage for recoverability and buffer compatibility across RS layouts.
