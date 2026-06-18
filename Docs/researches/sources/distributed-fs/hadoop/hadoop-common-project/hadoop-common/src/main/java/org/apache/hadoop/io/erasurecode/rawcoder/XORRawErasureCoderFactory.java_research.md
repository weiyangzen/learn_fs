# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawErasureCoderFactory.java

Purpose: factory for pure-Java XOR raw coders.

Important APIs/types/functions: `CODER_NAME = "xor_java"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: instantiates `XORRawEncoder`/`XORRawDecoder` and reports `ErasureCodeConstants.XOR_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: implements `RawErasureCoderFactory`; Java fallback or configured implementation for XOR codec.

Risks: ensure XOR policies use one parity unit or higher-level validation prevents unsupported shapes. Tests should verify metadata, object creation, and registry/fallback behavior relative to `xor_native`.
