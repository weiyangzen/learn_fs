<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/FilePosition.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/FilePosition.java

## Purpose
Tracks the current absolute and buffer-relative read position for a prefetching stream. It binds a `BufferData` block to an absolute file offset and records per-buffer read statistics.

## Important APIs, Types, And Functions
Key methods are `setData`, `buffer`, `data`, `absolute`, `setAbsolute`, `relative`, `isWithinCurrentBuffer`, `blockNumber`, `isLastBlock`, `invalidate`, `bufferFullyRead`, `incrementBytesRead`, and read-stat accessors.

## Control Flow
Construction validates file and block sizes and creates `BlockData`; no position is valid until `setData`. `setData` validates offsets, duplicates the buffer, stores the buffer start and read-start offsets, seeks the duplicate to the requested read offset, and resets counters. Reads then advance the duplicate buffer externally while `incrementBytesRead` updates statistics. `setAbsolute` only moves within the current buffer; otherwise it leaves state unchanged.

## State And Persistence
State is in-memory: `BlockData`, current `BufferData`, duplicated `ByteBuffer`, `bufferStartOffset`, `readStartOffset`, and counters. `invalidate` clears the active buffer and marks offsets invalid.

## Dependencies And Integration Points
Used by prefetching input stream code to decide whether a seek can stay inside the current buffer, whether the current block is fully consumed, and which block should be released or cached.

## Risks
`isWithinCurrentBuffer` treats `pos == bufferEndOffset` as inside, allowing position at limit. Callers must pair `incrementBytesRead` with actual reads or `bufferFullyRead` will be wrong. Duplicated buffers share content but not position, so direct use of the original `BufferData` buffer can diverge from `FilePosition`.

## Test Signals
Cover zero-length files, start/read offsets at buffer boundaries, in-buffer and out-of-buffer seeks, last-block detection, invalid access exceptions, and single-byte versus bulk-read counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/FilePosition.java -->
