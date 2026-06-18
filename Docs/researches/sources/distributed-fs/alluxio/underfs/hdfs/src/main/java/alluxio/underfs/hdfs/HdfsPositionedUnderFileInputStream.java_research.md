## sources/distributed-fs/alluxio/underfs/hdfs/src/main/java/alluxio/underfs/hdfs/HdfsPositionedUnderFileInputStream.java

### Purpose
`HdfsPositionedUnderFileInputStream` is a seekable HDFS input stream optimized for remote/random reads. It switches between positioned reads and normal buffered reads based on recent access patterns.

### Important APIs, Types, And Functions
It extends `SeekableUnderFileInputStream`. Constants `SEQUENTIAL_READ_LIMIT` and `MOVEMENT_LIMIT` drive the heuristic. Overrides include `read`, `read(byte[], int, int)`, `seek`, `skip`, `available`, `getPos`, and `markSupported`.

### Control Flow
Reads use normal `InputStream.read` when the logical position matches the underlying `Seekable` position, or positioned reads otherwise. After enough sequential reads, it seeks the underlying stream to `mPos` and uses buffered reads. Large skips or backward/far seeks reset the sequential counter.

### State, Persistence, And Dependencies
State is in-memory: logical position and sequential-read count. It wraps `FSDataInputStream` and relies on Hadoop `Seekable` and `PositionedReadable`.

### Integration Points
`HdfsUnderFileSystem.open` returns this stream when reads are remote, position-short is requested, or block locality is not satisfied.

### Risks
IOExceptions in read paths are converted to runtime `AlluxioHdfsException`, unlike many Java input streams that throw checked IOExceptions. The heuristic constants are fixed and may not fit all workloads. `skip` can advance beyond EOF before reads detect it.

### Test Signals
`HdfsUnderFileSystemTest.verifyPread` spies on a stream and verifies transitions between buffered reads and positioned reads after small skips, large skips, and far seeks.
