## sources/distributed-fs/alluxio/underfs/gcs/src/test/java/alluxio/underfs/gcs/GCSUnderFileSystemTest.java

### Purpose
`GCSUnderFileSystemTest` validates legacy GCS UFS failure behavior for operations implemented through object listings.

### Important APIs, Types, And Functions
The setup creates a mocked `GoogleStorageService` and injects it into a `GCSUnderFileSystem`. Tests cover `deleteDirectory` in recursive and nonrecursive modes and `renameFile`.

### Control Flow
Each test configures `listObjectsChunked` to throw `ServiceException`. It then calls the high-level `ObjectUnderFileSystem` operation and asserts the result is false.

### State, Persistence, And Dependencies
No external GCS state is used. The test depends on Mockito, JUnit, Alluxio `DeleteOptions`, and default UFS configuration.

### Integration Points
The tests indirectly exercise `GCSUnderFileSystem.getObjectListingChunk` and the inherited object-store delete/rename logic.

### Risks
Coverage is limited to listing exceptions. It does not test successful listing, pagination, object status, copy retries, delete failures, permission inheritance, or stream creation.

### Test Signals
Passing tests indicate service listing errors are converted into non-successful high-level operations rather than uncaught exceptions for these paths.
