
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable2.java

Purpose: Intended interoperability test with native RS encoding and Java RS decoding over the shared RS matrix.

Important APIs and types: Extends `TestRSRawCoderBase`, requires `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = NativeRSRawErasureCoderFactory.class`, and sets `decoderFactoryClass = RSRawErasureCoderFactory.class`.

Control flow: Setup selects asymmetric factories and verbose dumps. Inherited RS tests prepare erasure layouts, run mixed direct/heap buffers, encode, decode, and verify recovered chunks.

State and persistence: May allocate native encoder resources through the selected factory; all buffers are in-memory.

Dependencies and integration points: Intended to guard parity format compatibility from native RS output to Java RS decoder input.

Risks: The base `createDecoder()` uses `encoderFactoryClass`, so this class may currently instantiate native for both encode and decode, not native-to-Java. That undermines the named interoperability purpose.

Test signals: Provides inherited RS coverage under native-code gating, but the asymmetric decoder field should be fixed or audited for true interop validation.
