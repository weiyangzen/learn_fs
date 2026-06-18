## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsUnderFileInputStream.java

### Purpose
`HdfsUnderFileInputStream` is the simple seekable wrapper over `FSDataInputStream` for local/sequential HDFS reads.

### Important APIs, Types, And Functions
It extends `SeekableUnderFileInputStream` and implements `seek(long)` and `getPos()` by delegating to the wrapped `FSDataInputStream`.

### Control Flow
All read behavior is inherited from the base filter stream. The only special control path is direct HDFS seek for repositioning.

### State, Persistence, And Dependencies
State is the wrapped input stream held by the superclass. It depends on Hadoop `FSDataInputStream`.

### Integration Points
`HdfsUnderFileSystem.open` returns this stream after seeking to the requested offset when the read is considered local/sequential.

### Risks
It provides no additional retry or recovery around reads after open. Seek errors propagate as checked IOExceptions.

### Test Signals
This class is indirectly exercised by local-style HDFS open paths; the positioned stream has stronger explicit tests in this subset.
