
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable1.java

Purpose: Intended interoperability test with Java RS encoding and native RS decoding over the shared RS matrix.

Important APIs and types: Extends `TestRSRawCoderBase`, gates on `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = RSRawErasureCoderFactory.class`, and sets `decoderFactoryClass = NativeRSRawErasureCoderFactory.class`.

Control flow: Setup runs before inherited RS tests, enabling verbose dumps and selecting asymmetric factories. The inherited tests then encode, erase, decode, and compare for many 6x3 and 10x4 layouts.

State and persistence: Uses in-memory chunks and potentially native decoder resources if instantiated.

Dependencies and integration points: Should verify wire-format compatibility between Java RS parity generation and native RS decoding.

Risks: `TestRawCoderBase.createDecoder()` instantiates `encoderFactoryClass` rather than `decoderFactoryClass`, so this class may currently run Java-to-Java instead of Java-to-native, weakening the interoperability signal.

Test signals: Native availability gate and inherited RS matrix exist, but factory-instantiation behavior should be checked before relying on this as true interoperability coverage.
