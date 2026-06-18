## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTest.java

### Purpose
Tests UFS factory discovery boundaries in the core module.

### Important APIs, Types, And Functions
Calls `UnderFileSystemFactoryRegistry.find` for local and external-module schemes. Uses JUnit `Assume` to run external-factory checks only when the core classpath has exactly one available implementation.

### Control Flow
`coreFactory` asserts local paths and `file://` paths do not resolve to a core UFS factory. `externalFactory` asserts HDFS, OSS, S3, S3A, and GlusterFS paths do not resolve without their separate modules.

### State And Persistence
Reads static registry state only.

### Dependencies And Integration Points
Guards extension split behavior: core common should not accidentally provide factories for schemes owned by external modules.

### Risks
Classpaths with additional factories skip the external test via `Assume`, reducing coverage in integrated builds.

### Test Signals
Useful signal for service-loader packaging and module boundary regressions.
