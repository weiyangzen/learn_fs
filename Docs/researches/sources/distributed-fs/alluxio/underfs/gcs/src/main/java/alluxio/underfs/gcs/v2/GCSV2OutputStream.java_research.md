## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/v2/GCSV2OutputStream.java

### Purpose
`GCSV2OutputStream` streams writes directly into GCS using the v2 `WriteChannel`, avoiding the legacy local-temporary-file upload path.

### Important APIs, Types, And Functions
It extends `OutputStream` and implements `ContentHashable`. Constructor validates the bucket and prepares `BlobInfo`. `write` methods lazily create the write channel, update an MD5 digest when available, and write `ByteBuffer`s. `close()` closes the channel or creates an empty blob. `getContentHash()` returns a stored GCS MD5 only for empty-object creation.

### Control Flow
The first write opens `mClient.writer(mBlobInfo)`. Byte-array writes pass through `ByteBuffer.wrap`; single-byte writes use a preallocated buffer. `close` is guarded by `AtomicBoolean`; if no data was written, it creates the object via `Storage.create`.

### State, Persistence, And Dependencies
State includes the bucket/key, `Storage` client, write channel, MD5 digest, closed flag, and optional content hash. The object persists in GCS when the write channel closes or the empty blob is created.

### Integration Points
`GCSV2UnderFileSystem.createObject` returns this stream for GCS v2 writes. `ContentHashable` allows higher layers to retrieve a content hash after successful close when available.

### Risks
`write(int)` calls `ByteBuffer.putInt(b)` on a one-byte buffer, which can overflow at runtime and should be tested. For non-empty writes, the computed MD5 digest is never exposed as `mContentHash`, so content hash retrieval is incomplete. Flush is a no-op because GCS write channels do not support it.

### Test Signals
No direct tests are present. High-value tests would cover single-byte writes, byte-array writes, duplicate close, empty object close, StorageException wrapping, and `getContentHash` behavior for non-empty writes.
