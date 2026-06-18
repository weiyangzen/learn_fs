
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable1.java

Purpose: Intended interoperability test with Java XOR encoding and native XOR decoding.

Important APIs and types: Extends `TestXORRawCoderBase`, requires `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = XORRawErasureCoderFactory.class`, and sets `decoderFactoryClass = NativeXORRawErasureCoderFactory.class`.

Control flow: Setup selects asymmetric factories and enables dumps. Inherited XOR tests perform single-erasure recovery and negative scenarios with mixed buffer modes.

State and persistence: In-memory chunks only; native decoder resources would be used if the decoder factory field is honored.

Dependencies and integration points: Intended to ensure Java XOR parity can be consumed by native XOR decoder.

Risks: Because `TestRawCoderBase.createDecoder()` uses `encoderFactoryClass`, this class may currently instantiate the Java factory for decoding too, reducing true interoperability coverage.

Test signals: Useful inherited XOR matrix under native availability, but asymmetric factory behavior should be audited.
