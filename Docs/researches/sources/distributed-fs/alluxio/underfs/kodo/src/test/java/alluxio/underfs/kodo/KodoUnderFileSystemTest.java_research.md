## sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoUnderFileSystemTest.java

### Purpose
`KodoUnderFileSystemTest` validates failure behavior for Kodo operations that depend on object listings.

### Important APIs, Types, And Functions
Setup injects a mocked `KodoClient` into `KodoUnderFileSystem`. Tests cover nonrecursive directory delete, recursive directory delete, and file rename.

### Control Flow
Each test configures `KodoClient.listFiles` to throw `QiniuException`, invokes the high-level operation, and asserts false.

### State, Persistence, And Dependencies
No external object-store state is used. Dependencies include Mockito, JUnit, and Alluxio UFS options.

### Integration Points
The tests exercise `KodoUnderFileSystem.getObjectListingChunk` through inherited `ObjectUnderFileSystem` logic.

### Risks
They do not cover successful listings, pagination markers, object status, stream behavior, or credential validation.

### Test Signals
Passing tests indicate listing failures are contained and surfaced as failed high-level operations.
