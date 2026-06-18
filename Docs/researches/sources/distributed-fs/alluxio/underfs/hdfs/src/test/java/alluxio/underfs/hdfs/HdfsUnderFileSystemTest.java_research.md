## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemTest.java

### Purpose
`HdfsUnderFileSystemTest` covers basic HDFS UFS identity/configuration behavior and the positioned-read heuristic.

### Important APIs, Types, And Functions
Setup creates a temporary local-root HDFS UFS using mount-specific Hadoop configuration. Tests cover `getUnderFSType`, `createConfiguration`, and `verifyPread`. The helper `checkDataValid` validates byte values despite signed conversion.

### Control Flow
`verifyPread` writes a local file, opens it with `OpenOptions.setPositionShort(true)`, replaces the wrapped stream with a spy `PreadSeekableStream`, performs reads/skips/seeks, and verifies counts for positioned and normal read methods.

### State, Persistence, And Dependencies
The test uses a JUnit `TemporaryFolder`. It depends on Mockito/PowerMock Whitebox, Hadoop `FSDataInputStream`, and Alluxio UFS options.

### Integration Points
It indirectly tests `HdfsUnderFileSystem.open` choosing `HdfsPositionedUnderFileInputStream` and the stream's switching behavior.

### Risks
The tests use a local filesystem path rather than a real HDFS cluster, so they do not cover block locations, Kerberos, lease recovery, space reporting, or distributed semantics.

### Test Signals
Passing tests confirm the configured implementation class is propagated, HDFS client cache disabling is set, and the pread heuristic transitions at the expected thresholds.
