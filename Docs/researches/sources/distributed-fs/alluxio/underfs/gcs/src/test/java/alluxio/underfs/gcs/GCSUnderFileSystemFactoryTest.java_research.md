## sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemFactoryTest.java

### Purpose
This JUnit test verifies that the GCS UFS module registers a factory for `gs://` paths.

### Important APIs, Types, And Functions
The single `factory()` test calls `UnderFileSystemFactoryRegistry.find("gs://test-bucket/path", Configuration.global())` and asserts that a non-null `UnderFileSystemFactory` is returned.

### Control Flow
The test relies on module service discovery and global configuration. It does not instantiate an actual GCS client or validate credentials.

### State, Persistence, And Dependencies
No persistent state is modified. Dependencies are JUnit, Alluxio configuration, and UFS factory registry metadata.

### Integration Points
This is a smoke test for `GCSUnderFileSystemFactory.supportsPath` and service registration.

### Risks
It does not verify the version switch between legacy and v2 implementations, error propagation, unsupported paths, or required credential checks.

### Test Signals
A failure indicates the module is not visible to the registry or does not recognize `gs://` paths.
