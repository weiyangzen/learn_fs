## sources/distributed-fs/alluxio/underfs/local/pom.xml

### Purpose
This Maven module builds the local filesystem UFS extension.

### Important APIs, Types, And Functions
The artifact is `alluxio-underfs-local`. It depends on `alluxio-core-common` as provided and its test jar for tests. Build plugins include Maven shade and copy/rename.

### Control Flow
There are no feature profiles. The module inherits versioning and plugin configuration from `alluxio-underfs`.

### State, Persistence, And Dependencies
The build emits the local UFS extension artifact. Runtime dependencies are limited to Alluxio common and Java filesystem APIs.

### Integration Points
The module contributes `LocalUnderFileSystemFactory`, `LocalUnderFileSystem`, and local UFS tests.

### Risks
Because this module is often used for tests and single-node deployments, packaging changes can break many contract tests. It depends on parent plugin behavior for extension layout.

### Test Signals
Tests cover factory recognition, local file operations, symlink handling, status, locations, and async listing behavior.
