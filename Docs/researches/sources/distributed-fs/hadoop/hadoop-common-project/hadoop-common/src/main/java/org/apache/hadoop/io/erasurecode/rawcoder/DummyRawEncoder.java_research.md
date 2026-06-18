# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawEncoder.java

Purpose: test/performance-isolation encoder that performs no parity math and is intended to produce zero parity.

Important APIs/types/functions: constructor with `ErasureCoderOptions`; overrides `doEncode(ByteArrayEncodingState)` and `doEncode(ByteBufferEncodingState)`.

Control flow: the base encoder validates and dispatches to the matching override; both overrides return immediately. As with the dummy decoder, the comment assumes output buffers have already been reset, but this class itself does not zero them.

State and persistence: stateless and resource-free.

Dependencies and integration: instantiated by `DummyRawErasureCoderFactory`; integrates with the same raw encoder public API as real coders, so it can isolate block-management overhead from codec work.

Risks: stale output content is possible if upstream callers do not zero outputs before calling the dummy encoder. Tests should verify whether the surrounding erasure-code framework zeroes outputs, and should also cover normal validation, zero-length fast path, and direct/heap paths.
