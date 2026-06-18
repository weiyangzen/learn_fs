
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable2.java

Purpose: Intended interoperability test with native XOR encoding and Java XOR decoding.

Important APIs and types: Extends `TestXORRawCoderBase`, gates on `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = NativeXORRawErasureCoderFactory.class`, and sets `decoderFactoryClass = XORRawErasureCoderFactory.class`.

Control flow: Setup selects factories and verbose dumps, then inherited XOR tests encode, erase, decode, and compare under direct/heap buffer modes and negative cases.

State and persistence: In-memory test chunks and potentially native encoder resources; no filesystem state.

Dependencies and integration points: Intended to prove native XOR output is decodable by Java XOR implementation.

Risks: The base decoder factory bug means this may currently run native-to-native rather than native-to-Java. Native library absence skips the class.

Test signals: Provides native-gated XOR matrix coverage, but true interop signal depends on fixing or confirming base factory use.
