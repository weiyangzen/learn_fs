## sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemFactoryTest.java

### Purpose
This test verifies Kodo factory registration for `kodo://` paths.

### Important APIs, Types, And Functions
`factory()` calls `UnderFileSystemFactoryRegistry.find("kodo://test-bucket/path", Configuration.global())` and asserts non-null.

### Control Flow
The test performs registry lookup only; it does not create the UFS or validate credentials.

### State, Persistence, And Dependencies
No persistent state is modified. It depends on Alluxio configuration and factory registry.

### Integration Points
The test protects service discovery and `KodoUnderFileSystemFactory.supportsPath`.

### Risks
It does not reject non-Kodo schemes or test create-time configuration requirements.

### Test Signals
Failure suggests missing module service metadata or broken scheme-prefix support.
