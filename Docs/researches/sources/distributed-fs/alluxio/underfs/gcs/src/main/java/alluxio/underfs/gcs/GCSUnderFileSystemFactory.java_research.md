## sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSUnderFileSystemFactory.java

### Purpose
`GCSUnderFileSystemFactory` creates the GCS UFS implementation and decides whether to instantiate the legacy jets3t implementation or the Google Cloud Storage v2 implementation.

### Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create(String, UnderFileSystemConfiguration)` checks `UNDERFS_GCS_VERSION`; version `2` creates `GCSV2UnderFileSystem`, otherwise it creates `GCSUnderFileSystem`. `supportsPath(String)` accepts paths starting with `Constants.HEADER_GCS`.

### Control Flow
Creation validates that the path is non-null, constructs an `AlluxioURI`, and delegates to the chosen implementation's static create method. `IOException` and jets3t `ServiceException` are logged and propagated through Guava `Throwables.propagate`.

### State, Persistence, And Dependencies
The factory is stateless and thread-safe. It depends on Alluxio configuration keys, GCS UFS classes, Guava preconditions/throwables, and the UFS factory SPI.

### Integration Points
The service registry discovers this factory so `gs://` paths can mount through the GCS module. It is the only switch point between legacy and v2 GCS clients.

### Risks
The v2 choice is a strict integer comparison; unexpected version values silently choose the legacy implementation. Propagating checked creation failures as runtime exceptions can surface later than a direct checked error path.

### Test Signals
`GCSUnderFileSystemFactoryTest` verifies that the registry finds a factory for a `gs://` path.
