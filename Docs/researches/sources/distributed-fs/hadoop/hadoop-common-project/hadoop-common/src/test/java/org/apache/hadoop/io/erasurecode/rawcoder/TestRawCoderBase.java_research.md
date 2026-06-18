
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawCoderBase.java

Purpose: Shared raw erasure coder harness for byte-buffer and chunk-level encode/decode correctness, negative input/output cases, release semantics, and input-position contracts.

Important APIs and types: Extends `TestCoderBase`; manages `RawErasureCoderFactory`, `RawErasureEncoder`, and `RawErasureDecoder`. Provides `testCoding()`, `performTestCoding()`, `ensureOnlyLeastRequiredChunks()`, `testAfterRelease()`, `testInputPosition()`, `createEncoder()`, and `createDecoder()`.

Control flow: Tests configure factories and erasure indexes, generate data chunks, optionally corrupt inputs/outputs, encode parity, check input mutation rules, erase chunks, remove redundant inputs, decode, compare recovered chunks, and validate input buffer positions. Negative paths expect too many erasures or bad buffers to fail.

State and persistence: Mutable factory classes, coders, buffer mode, `allowChangeInputs`, chunk size, and erased indexes are inherited per test instance. No filesystem persistence.

Dependencies and integration points: Underpins all raw RS/XOR/native/dummy/interoperability tests and uses `LambdaTestUtils` for closed-coder assertions.

Risks: `createDecoder()` instantiates `encoderFactoryClass` instead of `decoderFactoryClass`, which can invalidate asymmetric interoperability tests. Random corruption may make failures variable.

Test signals: Central contract coverage for raw coder correctness, resource release idempotence, and ByteBuffer semantics.
