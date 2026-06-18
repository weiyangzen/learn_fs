# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogFileInputStream.java

## Purpose
`TestEditLogFileInputStream` covers edit-log input streams backed by HTTP URLs, protobuf `ByteString` values, and local files. It targets read completeness, length detection, operation checksum validation, and handling of files filled by failed preallocation.

## Important APIs, Types, And Functions
The tests use `EditLogFileInputStream.fromUrl`, `EditLogFileInputStream.fromByteString`, `EditLogFileInputStream.scanEditLog`, `EditLogFileOutputStream`, `FSEditLogOp.MkdirOp`, `FSImageTestUtil.countEditLogOpTypes`, `URLConnectionFactory`, mocked `HttpURLConnection`, `ByteString`, and `FSEditLogLoader.EditLogValidation`. `FAKE_LOG_DATA` reuses the legacy Hadoop 0.20 edit sequence from `TestEditLog`.

## Control Flow
`testReadURL` mocks an HTTP connection returning edit-log bytes, status OK, and a `Content-Length`; it reads the stream and checks operation counts and reported length. `testByteStringLog` performs the same validation against an in-memory `ByteString`. `testScanCorruptEditLog` writes two mkdir operations, flushes the log, corrupts the last four checksum bytes, then confirms `scanNextOp` reads the first transaction and fails on the corrupt second transaction. `testScanEditThatFailedDuringPreAllocate` creates a file containing only `0xff` bytes and expects scan validation to classify the header as corrupt and report no end txid.

## State And Persistence Behavior
The file-based tests create real edit-log files and mutate bytes in place with `RandomAccessFile`. They verify that persisted checksums are not advisory: corruption during scan produces an `IOException` and protects replay. The preallocation test models an aborted writer that left trailer bytes only, ensuring a JournalNode can move such a file aside rather than treating it as valid metadata.

## Dependencies And Integration Points
The URL path integrates edit-log loading with web transfer through `URLConnectionFactory`, while the byte-string path supports in-memory/protobuf transport use cases. Local-file tests integrate with `EditLogFileOutputStream` layout creation, permission-status serialization, and loader validation.

## Risks And Test Signals
Important risks are silent acceptance of corrupt operations, incorrect HTTP length accounting, and startup blockage from all-`OP_INVALID` preallocated files. Test signals include exact operation counts for `OP_ADD`, `OP_SET_GENSTAMP_V1`, and `OP_CLOSE`, stream length equality, expected checksum failure text, `hasCorruptHeader()`, and invalid end txid.
