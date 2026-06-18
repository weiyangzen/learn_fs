## sources/distributed-fs/alluxio/underfs/kodo/src/main/java/alluxio/underfs/kodo/KodoOutputStream.java

### Purpose
`KodoOutputStream` buffers Kodo writes to a local temporary file, then uploads the completed file to Kodo on close.

### Important APIs, Types, And Functions
The constructor chooses a temporary directory, creates a UUID file, and wraps a file output stream in a buffered digest stream when MD5 is available. `write` and `flush` delegate to the local stream. `close` is guarded by `AtomicBoolean`, closes the local stream, uploads through `KodoClient.uploadFile`, and deletes the temporary file.

### Control Flow
All bytes are written locally first. Closing performs the only remote persistence step. Upload exceptions are logged but not rethrown because `close` does not declare `IOException`.

### State, Persistence, And Dependencies
State includes key, temp file, Kodo client, local output stream, optional MD5 digest, and closed flag. Temporary local state is deleted on close; durable state is the uploaded Kodo object.

### Integration Points
`KodoUnderFileSystem.createObject` returns this stream for object writes.

### Risks
Upload failures are swallowed after logging, so callers may believe close succeeded. MD5 is computed but not used for upload metadata or exposed through `ContentHashable`. Large writes require local disk capacity equal to the object size.

### Test Signals
`KodoOutputStreamTest` covers constructor IO failure, write delegation, flush delegation, and temp-file deletion on close.
