# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java

Purpose: factory for ISA-L native Reed-Solomon raw coders.

Important APIs/types/functions: `CODER_NAME = "rs_native"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: creation instantiates `NativeRSRawEncoder` or `NativeRSRawDecoder`, triggering native-code checks/initialization. Metadata binds the coder to `ErasureCodeConstants.RS_CODEC_NAME`.

State and persistence: stateless factory.

Dependencies and integration: implements `RawErasureCoderFactory`; selected by Hadoop raw coder configuration for RS policies when native support is preferred/available.

Risks: factory creation can fail if native code is not loaded, unlike Java factories. Tests should verify metadata names, successful creation under native-enabled builds, and fallback behavior in higher-level registry code when native creation is unavailable.
