# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawDecoder.java

Purpose: pure-Java XOR decoder for single-erasure XOR parity schemes.

Important APIs/types/functions: constructor; `doDecode(ByteBufferDecodingState)`; `doDecode(ByteArrayDecodingState)`.

Control flow: each decode resets the single output, reads the first erased index, skips that input position, and XORs all remaining input bytes into output. ByteBuffer code uses absolute `get/put` over positions/limits; byte-array code uses offsets and `decodeLength`.

State and persistence: stateless.

Dependencies and integration: extends `RawErasureDecoder`, uses `CoderUtil`, and is created by `XORRawErasureCoderFactory`.

Risks: it assumes exactly one output/erased index, as XOR with one parity unit cannot recover multiple erasures; base validation prevents erasures greater than parity count. Null inputs other than the erased index would cause failures in the loop, so caller null set must be valid. Tests should cover data and parity erasure, direct/heap equality, null input behavior, and output zeroing before accumulation.
