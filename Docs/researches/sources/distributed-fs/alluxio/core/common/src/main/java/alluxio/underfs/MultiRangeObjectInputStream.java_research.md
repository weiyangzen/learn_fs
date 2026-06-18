<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/MultiRangeObjectInputStream.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/MultiRangeObjectInputStream.java

Purpose: abstract input stream for object stores that reads data through bounded range requests instead of holding one long stream to object end. It is designed for chunked reads and efficient skips.

Important APIs and control flow: constructor stores range chunk size. `read()` and `read(byte[],off,len)` lazily `openStream`, delegate to the current range stream, advance `mPos`, and close the range stream once `mPos >= mEndPos`. `skip` closes any current stream, advances `mPos`, and opens a new range. `openStream` rejects closed streams and non-positive chunk sizes, computes the next range end aligned to the chunk boundary, and calls abstract `createStream(startPos,endPos)`.

State, persistence, and integration: maintains current logical position, current range end, and backing input stream. Dependencies are concrete object-store subclasses that implement byte-range `createStream`. Risks include `skip` returning `n` even if beyond content length, undefined behavior for invalid ranges delegated to subclasses, and not thread-safe state. Test signals should cover chunk-boundary reopening, close idempotency, invalid chunk size, skip behavior, and EOF across ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/MultiRangeObjectInputStream.java -->
