# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureEncoder.java

Purpose: abstract public-facing base for low-level raw erasure encoding over `ByteBuffer`, `byte[][]`, and `ECChunk`.

Important APIs/types/functions: `encode()` overloads; abstract `doEncode()` overloads; data/parity/all-unit accessors; `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

Control flow: `ByteBuffer` encode validates through `ByteBufferEncodingState`, returns for zero length, snapshots input positions, dispatches direct buffers to `doEncode(ByteBuffer...)` or converts heap buffers to byte arrays, then advances non-null input positions by encoded length. Byte-array encode constructs `ByteArrayEncodingState` and dispatches. ECChunk encode unwraps using `ECChunk.toBuffers`.

State and persistence: stores immutable `ErasureCoderOptions`; subclasses may hold schema matrices or native handles.

Dependencies and integration: superclass for Java, native, legacy, XOR, and dummy encoders; entry point used by higher-level Hadoop erasure coding.

Risks: encoder methods are not synchronized unlike decoder methods, so stateful encoders must handle thread-safety themselves. Tests should cover cursor advancement, direct/heap behavior, zero-length calls, output initialization by implementations, `allowChangeInputs()` effects, and ECChunk wrapping.
