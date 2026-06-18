## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/HdfsUnderFileSystemFactoryTest.java

### Purpose
This JUnit test verifies HDFS factory discovery and rejection of non-HDFS schemes.

### Important APIs, Types, And Functions
`factory()` calls `UnderFileSystemFactoryRegistry.find` for `hdfs://`, `s3://`, `s3n://`, and `alluxio://` paths.

### Control Flow
The test asserts a factory is found for HDFS and not found for the other schemes under global configuration.

### State, Persistence, And Dependencies
No filesystem state is touched. It depends on the UFS registry and Alluxio global configuration.

### Integration Points
This protects service registration and `HdfsUnderFileSystemFactory.supportsPath` for default prefixes.

### Risks
It does not exercise mount-specific `UNDERFS_VERSION` matching or custom HDFS prefixes.

### Test Signals
Failure usually indicates broken service discovery, missing module metadata, or changed default HDFS prefix configuration.
