# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java

Purpose: factory for ISA-L native XOR raw coders.

Important APIs/types/functions: `CODER_NAME = "xor_native"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: simple factory methods instantiate native XOR encoder/decoder and return codec metadata for `ErasureCodeConstants.XOR_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: plugs into the `RawErasureCoderFactory` registry/configuration path for XOR policies.

Risks: native creation can fail at class load or construction if ISA-L/Hadoop native code is unavailable. Tests should cover name/codec metadata, native-enabled construction, and higher-level fallback to Java XOR when this factory cannot instantiate.
