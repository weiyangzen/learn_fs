# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/HHXORErasureCodec.java

Purpose: concrete high-level Hitchhiker-XOR codec.

Important APIs and control flow: constructor delegates to `ErasureCodec`; `createEncoder()` returns `HHXORErasureEncoder`, and `createDecoder()` returns `HHXORErasureDecoder`.

State and persistence: no additional state beyond base codec fields.

Dependencies and integration: selected by `CodecUtil` for `hhxor` schemas and bridges to HH-XOR coder classes that compose RS and XOR raw coders.

Risks and test signals: integration tests should verify `hhxor` schema resolution and that generated coders receive the expected data/parity counts. HH-XOR has stronger assumptions about parity counts and sub-packetization in the coder step classes.
