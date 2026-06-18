# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/AbstractNativeRawDecoder.java

Purpose: base class for native raw erasure decoders, providing lock-protected ByteBuffer decode plumbing and byte-array fallback conversion.

Important APIs and control flow: `doDecode(ByteBufferDecodingState)` takes a read lock, rejects use after native coder close (`nativeCoder == 0`), records input/output buffer positions as offset arrays, and calls subclass `performDecodeImpl()`. `doDecode(ByteArrayDecodingState)` logs a performance advisory, converts arrays to ByteBuffer state, delegates, then copies decoded output bytes back to arrays. `preferDirectBuffer()` returns true.

State and persistence: contains a `ReentrantReadWriteLock` and a private native pointer field used by JNI. No persistence; native lifecycle is coordinated by subclasses/raw coder base classes.

Dependencies and integration: extends `RawErasureDecoder`; used by native ISA-L decoders. Subclasses implement JNI bridge method `performDecodeImpl()`.

Risks and test signals: test decode after release, concurrent decode/release locking in subclasses, heap-array fallback correctness, and buffer position preservation/advancement by raw coder framework. Native pointer visibility is intentionally private for JNI use.
