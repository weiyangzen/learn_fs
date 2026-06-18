# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawEncoder.java

Purpose: base class for native raw erasure encoders, providing lock-protected ByteBuffer encode plumbing and byte-array fallback conversion.

Important APIs and control flow: `doEncode(ByteBufferEncodingState)` takes a read lock, rejects closed native coder state, records input/output positions, derives `dataLen` from the first input's remaining bytes, and calls subclass `performEncodeImpl()`. `doEncode(ByteArrayEncodingState)` logs a performance advisory, converts arrays to ByteBuffers, delegates, then copies output bytes back. `preferDirectBuffer()` returns true.

State and persistence: contains a `ReentrantReadWriteLock` and private native pointer field for JNI. No persistence.

Dependencies and integration: extends `RawErasureEncoder`; native RS/XOR encoders subclass it and implement `performEncodeImpl()`.

Risks and test signals: test encode after close, direct-buffer preference propagation, heap-array conversion correctness, input/output offset calculation, and concurrent release behavior in concrete native encoders. Assumes all inputs have the same remaining length as input zero.
