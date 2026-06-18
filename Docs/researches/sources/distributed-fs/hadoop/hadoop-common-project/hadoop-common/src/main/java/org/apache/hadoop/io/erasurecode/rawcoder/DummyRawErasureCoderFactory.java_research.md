# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawErasureCoderFactory.java

Purpose: factory binding Hadoop's dummy erasure codec name to no-op raw encoder/decoder implementations.

Important APIs/types/functions: constant `CODER_NAME = "dummy_dummy"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, and `getCodecName()`.

Control flow: creation simply instantiates `DummyRawEncoder` or `DummyRawDecoder` with the supplied `ErasureCoderOptions`; codec metadata returns `ErasureCodeConstants.DUMMY_CODEC_NAME`.

State and persistence: stateless factory.

Dependencies and integration: implements `RawErasureCoderFactory`, so it can be selected by the raw coder registry/configuration path used by Hadoop erasure coding.

Risks: users must not treat this as data-protecting; it is for tests or performance isolation. Tests should verify registry metadata, factory creation with varied coder options, and that dummy coders are not selected accidentally for real RS/XOR policies.
