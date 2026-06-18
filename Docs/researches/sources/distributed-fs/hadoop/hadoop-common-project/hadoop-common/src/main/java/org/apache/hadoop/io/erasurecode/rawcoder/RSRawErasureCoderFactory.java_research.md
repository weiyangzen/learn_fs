# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawErasureCoderFactory.java

Purpose: factory for modern pure-Java Reed-Solomon raw coders.

Important APIs/types/functions: `CODER_NAME = "rs_java"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: factory methods instantiate `RSRawEncoder` and `RSRawDecoder` with supplied options. Metadata binds the factory to `ErasureCodeConstants.RS_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: implements `RawErasureCoderFactory`; typically used as fallback when native RS is unavailable or when Java implementation is configured.

Risks: must remain distinct from `rs_native` and `rs-legacy_java` in registry/config. Tests should verify metadata and factory outputs, plus higher-level fallback ordering.
