# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderFactory.java

Purpose: factory interface for creating paired raw erasure encoders/decoders and exposing coder/codec names for configuration.

Important APIs/types/functions: `createEncoder(ErasureCoderOptions)`, `createDecoder(ErasureCoderOptions)`, `getCoderName()`, `getCodecName()`.

Control flow: no implementation logic; concrete factories bind names such as `rs_java`, `rs_native`, `xor_java`, and dummy coders to raw coder classes.

State and persistence: interface only.

Dependencies and integration: consumed by Hadoop's erasure-code raw coder selection layer; implementors in this set cover Java, native, legacy, XOR, and dummy coders.

Risks: factory metadata drives configuration behavior, so name collisions or wrong codec names can route production policies to incompatible implementations. Tests should enumerate factories, assert unique coder names, and verify codec-name mapping to `ErasureCodeConstants`.
