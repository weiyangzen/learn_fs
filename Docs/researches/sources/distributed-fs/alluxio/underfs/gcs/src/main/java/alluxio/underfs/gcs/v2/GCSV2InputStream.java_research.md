## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2InputStream.java

### Purpose
`GCSV2InputStream` is a non-thread-safe input stream over the Google Cloud Storage client library. It provides efficient offset reads and skips by using `ReadChannel.seek` instead of reading and discarding bytes.

### Important APIs, Types, And Functions
The constructor captures bucket, key, `Storage` client, and initial position. Overrides include `read()`, `read(byte[], int, int)`, `skip(long)`, and `close()`. `openStream()` creates the `ReadChannel` and seeks to `mPos`.

### Control Flow
The channel is opened lazily on the first read or skip. Reads wrap target buffers in `ByteBuffer`, update `mPos` on successful reads, and return `-1` at EOF. `skip` advances `mPos`, opens the channel if needed, and seeks directly to the new position.

### State, Persistence, And Dependencies
State is the current position, one-byte buffer, and optional `ReadChannel`. Persistent data remains in GCS. It depends on `com.google.cloud.storage.Storage`, `BlobId`, and `ReadChannel`.

### Integration Points
`GCSV2UnderFileSystem.openObject` creates this stream with `OpenOptions.getOffset()`. It provides the stream behavior used by Alluxio object-store reads under GCS v2.

### Risks
`skip` returns the requested count without checking object length, so EOF is only observed by a later read. The stream is not synchronized and should not be shared across threads. `close` does not null the channel, so reads after close rely on channel behavior.

### Test Signals
There is no direct test in this subset. Useful tests would verify offset reads, skip beyond EOF, empty-buffer reads returning zero, lazy open, and StorageException-to-IOException wrapping.
