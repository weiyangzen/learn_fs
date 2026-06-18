# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawDecoder.java

Purpose: test/performance-isolation decoder that performs no reconstruction math and leaves outputs as the zeroed buffers prepared by caller-side state handling.

Important APIs/types/functions: constructor with `ErasureCoderOptions`; overrides `doDecode(ByteBufferDecodingState)` and `doDecode(ByteArrayDecodingState)`.

Control flow: after `RawErasureDecoder` validates parameters and builds state, these overrides return immediately. The class comment says it returns zero bytes, but this implementation relies on the base/caller path or external setup for zeroed outputs; unlike RS/XOR implementations it does not explicitly call `CoderUtil.resetOutputBuffers`.

State and persistence: stateless; no caches or resources.

Dependencies and integration: created by `DummyRawErasureCoderFactory` for `DUMMY_CODEC_NAME`; useful when measuring HDFS erasure-code plumbing without codec cost.

Risks: if outputs are not already zeroed by upstream code, this decoder can expose stale output contents. Tests should assert intended zero-output semantics, decode validation bypass expectations, and that it still enforces normal raw decoder input/output validation through the base class.
