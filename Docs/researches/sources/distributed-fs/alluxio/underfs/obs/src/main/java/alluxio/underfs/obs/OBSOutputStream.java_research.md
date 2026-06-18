## sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSOutputStream.java

### Purpose
`OBSOutputStream` buffers OBS writes to a local temporary file and uploads the whole file on close.

### Important APIs, Types, And Functions
The constructor validates bucket/key/client, creates a temp file, and wraps a local output stream in a digest stream when MD5 is available. `write` and `flush` delegate locally. `close` uploads the file with content length and optional content MD5, records the ETag as content hash, and deletes the temp file. `getContentHash` returns the ETag when available.

### Control Flow
All write calls persist locally. `close` is one-shot via `AtomicBoolean`, closes the local stream, opens a `FileInputStream`, builds `ObjectMetadata`, uploads via `ObsClient.putObject`, and cleans up in a `finally` block.

### State, Persistence, And Dependencies
State includes bucket/key, temp file, OBS client, local stream, optional MD5 digest, closed flag, and content hash. Persistent data is the OBS object; temporary local data should be deleted on close.

### Integration Points
`OBSUnderFileSystem.createObject` uses this class when streaming upload is disabled.

### Risks
Large objects require local disk space. The upload input stream is not explicitly closed, relying on upload behavior or GC. Duplicate close only logs a warning and returns. MD5 is Base64-encoded into object metadata.

### Test Signals
No direct OBS output tests are present. Useful tests would mirror Kodo/GCS output stream tests: write delegation, upload metadata, temp cleanup, duplicate close, upload failure propagation, and content hash.
