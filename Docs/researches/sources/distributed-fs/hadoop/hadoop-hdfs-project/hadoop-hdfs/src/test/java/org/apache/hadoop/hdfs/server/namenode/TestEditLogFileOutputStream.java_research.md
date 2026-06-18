# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileOutputStream.java

## Purpose
`TestEditLogFileOutputStream` validates low-level edit-log output stream write, preallocation, flush, close, and abort behavior. It is narrowly focused on `EditLogFileOutputStream` rather than full NameNode replay.

## Important APIs, Types, And Functions
The class uses `EditLogFileOutputStream`, `NameNodeLayoutVersion.CURRENT_LAYOUT_VERSION`, `EditLogFileOutputStream.MIN_PREALLOCATION_LENGTH`, `setReadyToFlush`, `flushAndSync`, `writeRaw`, `close`, and `abort`. Test setup disables fsync for speed and deletes the shared test edits file before and after each test.

## Control Flow
`testRawWrites` creates a stream, writes a small byte array, flushes, and expects the file to expand to the minimum preallocation length. A second small write should reuse preallocated space and keep the same file length. A larger multi-buffer write exceeding the current allocation should grow the file to four times the minimum length. The remaining tests exercise `close` then `abort`, `close` then `close`, and `abort` then `abort` sequences for HDFS-2011 regressions.

## State And Persistence Behavior
The central persisted state is the physical edit-log file length. The test confirms file size includes preallocated space beyond valid edit bytes and that repeated lifecycle operations do not corrupt internal stream state or throw `NullPointerException`. A second `close` is expected to surface an IOException that identifies use of an aborted output stream.

## Dependencies And Integration Points
This class integrates only with local filesystem test directories, `Configuration`, and Hadoop IO cleanup helpers. It underpins higher-level edit-log tests by ensuring the raw stream honors allocation and lifecycle contracts.

## Risks And Test Signals
Risks include excessive or missing preallocation, lifecycle calls leaving partially initialized fields, and repeated close/abort sequences masking real stream state. Test signals are exact file lengths after flushes, no exception for close-abort and abort-abort, and an expected diagnostic on close-close.
