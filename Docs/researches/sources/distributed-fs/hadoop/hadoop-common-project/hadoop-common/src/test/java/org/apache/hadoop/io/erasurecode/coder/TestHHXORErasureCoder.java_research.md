
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHXORErasureCoder.java

Purpose: Concrete block-level HHXOR coder tests across direct and heap buffers, coder reuse, configuration-driven raw RS selection, and multiple erasure layouts.

Important APIs and types: Inherits `TestHHErasureCoderBase`; sets `HHXORErasureEncoder`, `HHXORErasureDecoder`, `numChunksInBlock = 10`, and `subPacketSize = 2`. Uses `CodecUtil.IO_ERASURECODE_CODEC_RS_RAWCODERS_KEY` to force `RSRawErasureCoderFactory` in one case.

Control flow: Each JUnit test calls `prepare()` with a 10x4 or 6x3 layout and selected erased data/parity indexes, then runs `testCoding()` one or more times. Some tests alternate direct and heap buffers to stress reused coder state.

State and persistence: Encoder/decoder instances may be reused within inherited harness calls; all data is in-memory chunks.

Dependencies and integration points: Integrates the HHXOR block coder with raw RS coder configuration and the sub-packet harness.

Risks: Native/default raw coder choices can change behavior unless configuration pins Java RS. Complex multi-erasure cases can expose sub-packet ordering bugs.

Test signals: Covers data erasures, parity erasures, combined erasures, repeated calls, and mixed buffer modes.
