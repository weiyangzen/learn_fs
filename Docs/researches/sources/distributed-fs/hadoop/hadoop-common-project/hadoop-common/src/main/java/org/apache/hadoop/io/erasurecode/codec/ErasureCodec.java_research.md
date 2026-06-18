# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/ErasureCodec.java

Purpose: abstract high-level erasure codec base that owns schema/options, creates encoder/decoder instances, and supplies a block grouper.

Important APIs and control flow: constructor extracts schema from `ErasureCodecOptions` and creates `ErasureCoderOptions` with `allowChangeInputs=false` and verbose dump disabled. Getters expose name, schema, codec options, and coder options. Abstract `createEncoder()`/`createDecoder()` are implemented by concrete codecs. `createBlockGrouper()` creates a `BlockGrouper` and attaches the schema.

State and persistence: stores schema, codec options, and coder options in memory. Protected setters allow subclasses to replace options.

Dependencies and integration: created reflectively by `CodecUtil`; used by EC manager logic to obtain coders and grouping behavior.

Risks and test signals: test schema-to-coder-option count propagation, block grouper schema assignment, and subclass option mutation. Default `allowChangeInputs=false` is an integration contract with raw coders.
