# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/DummyErasureCodec.java

Purpose: test/performance codec that creates dummy encoders/decoders which avoid real erasure math.

Important APIs and control flow: extends `ErasureCodec`; `createEncoder()` returns `DummyErasureEncoder`, and `createDecoder()` returns `DummyErasureDecoder`, both using inherited coder options.

State and persistence: no additional state beyond `ErasureCodec`.

Dependencies and integration: integrates dummy high-level coders into the same codec abstraction used by real RS/XOR/HHXOR codecs.

Risks and test signals: useful as a test signal itself for isolating HDFS pipeline overhead. Verify it is not selected accidentally for production schemas unless explicitly configured.
