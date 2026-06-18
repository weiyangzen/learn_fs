## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileOutputStream.java

### Purpose
`HdfsUnderFileOutputStream` wraps `FSDataOutputStream` for HDFS writes and maps Alluxio flush semantics to HDFS sync semantics.

### Important APIs, Types, And Functions
It extends `OutputStream` and implements `ContentHashable`. `write` methods delegate to `FSDataOutputStream`. `flush()` calls `hsync()`. `getContentHash()` fetches file status and returns an approximate hash from length and modification time.

### Control Flow
Writes are synchronous delegation to the Hadoop stream. Close closes the underlying stream. Hash lookup happens after writing by querying the file system path.

### State, Persistence, And Dependencies
State includes the HDFS `FileSystem`, target path, and output stream. Persistent data is the HDFS file. Dependencies include Hadoop FS classes and `UnderFileSystemUtils.approximateContentHash`.

### Integration Points
`HdfsUnderFileSystem.createDirect` constructs this stream after `FileSystem.create`. Higher layers can call `supportsFlush()` and rely on flush-to-HDFS behavior.

### Risks
Calling `hsync()` on every flush can be expensive. The content hash is approximate and may not identify same-size same-mtime changes. Hash lookup after close can fail if the file was moved or not yet visible.

### Test Signals
No direct test in this subset covers output stream sync or hash behavior. Useful tests would mock `FSDataOutputStream.hsync`, close propagation, and content hash generation.
