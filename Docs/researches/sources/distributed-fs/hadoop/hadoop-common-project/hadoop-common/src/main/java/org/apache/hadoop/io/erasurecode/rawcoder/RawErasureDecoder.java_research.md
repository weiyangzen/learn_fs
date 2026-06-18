# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureDecoder.java

Purpose: abstract public-facing base for low-level raw erasure decoding over `ByteBuffer`, `byte[][]`, and `ECChunk`.

Important APIs/types/functions: synchronized `decode()` overloads; abstract `doDecode()` overloads; option accessors; `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

Control flow: `ByteBuffer` decode constructs `ByteBufferDecodingState`, returns early for zero length, snapshots input positions, dispatches direct buffers to `doDecode(ByteBuffer...)` or converts heap buffers to byte arrays, then advances non-null input positions by consumed length. Byte-array decode builds `ByteArrayDecodingState` and dispatches. ECChunk decode unwraps via `CoderUtil.toBuffers`.

State and persistence: owns immutable `ErasureCoderOptions`; otherwise intended stateless, though subclasses may cache matrices/native handles. Decode methods are synchronized to protect mutable subclass decoder state.

Dependencies and integration: superclass for Java RS/XOR, legacy, native, dummy decoders; integrates with `ECChunk` and raw state classes.

Risks: output position semantics rely on implementations; heap ByteBuffer conversion requires array-backed buffers. Tests should cover input position advancement, zero-length return, erased/null semantics, direct-vs-heap dispatch, ECChunk all-zero handling, release behavior in subclasses, and synchronized cache safety.
