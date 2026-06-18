# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/RSErasureCodec.java

Purpose: concrete high-level Reed-Solomon erasure codec.

Important APIs and control flow: constructor delegates to `ErasureCodec`; `createEncoder()` returns `RSErasureEncoder`; `createDecoder()` returns `RSErasureDecoder`.

State and persistence: no additional state beyond inherited schema/options.

Dependencies and integration: selected for `rs` and currently also `rs-legacy` by `CodecUtil`; uses RS high-level coders which lazily create raw RS coders.

Risks and test signals: test codec class resolution for both RS names and raw coder fallback. The TODO in `CodecUtil` around `rs-legacy` means legacy behavior may need separate validation outside this thin class.
