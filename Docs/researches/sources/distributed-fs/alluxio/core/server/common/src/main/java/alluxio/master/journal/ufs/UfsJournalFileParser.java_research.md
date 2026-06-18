# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFileParser.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFileParser.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFileParser.java

### Purpose
`UfsJournalFileParser` is a low-level parser for reading delimited journal protobuf entries from one UFS file.

### Important APIs, Types, And Functions
It implements `JournalFileParser` with `next()` and `close()`. It owns an `UnderFileSystem`, input stream, current location, and a reusable byte buffer used by `ProtoUtils.readRawVarint32()`.

### Control Flow
On construction it opens the UFS file. `next()` reads a protobuf-delimited length prefix; `-1` means EOF and returns null. It grows the buffer if needed, reads exactly the encoded entry body, and parses a `JournalEntry`. `close()` closes the input stream.

### State, Persistence, And Dependencies
State is the open input stream and reusable buffer. It does not mutate persistent data. Dependencies include `UnderFileSystem`, `UnderFileSystemConfiguration`, `JournalFileParser`, protobuf utilities, and Alluxio configuration.

### Integration Points
This parser supports tools or utilities that parse an individual UFS journal file outside the higher-level `UfsJournalReader` sequencing logic.

### Risks
Malformed length prefixes, truncated bodies, or huge entry lengths can raise I/O/protobuf errors or force buffer resizing. It does not understand checkpoints or sequence ordering; callers must provide the correct file and interpret entries.

### Test Signals
Cover empty files, multiple delimited entries, buffer growth beyond 1024 bytes, truncated varints/bodies, invalid protobuf bytes, close idempotence expectations, and UFS open failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/ufs/UfsJournalFileParser.java -->
