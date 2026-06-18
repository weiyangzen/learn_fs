# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawErasureCoderFactory.java

Purpose: factory for legacy Java Reed-Solomon raw coders.

Important APIs/types/functions: `CODER_NAME = "rs-legacy_java"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: factory methods create `RSLegacyRawEncoder` and `RSLegacyRawDecoder`; codec metadata returns `ErasureCodeConstants.RS_LEGACY_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: implements `RawErasureCoderFactory`; used for configurations requiring compatibility with the legacy RS codec.

Risks: legacy algorithm behavior differs from modern ISA-L-compatible RS. Tests should ensure registry mapping stays distinct from `rs_java`, and that old-format policies choose this factory only when intended.
