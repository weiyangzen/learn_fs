## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsFileStatusTest.java

### Purpose
Tests the basic `UfsFileStatus` metadata contract.

### Important APIs, Types, And Functions
The tests construct `UfsFileStatus`, call content hash, content length, type, last-modified, owner, group, mode, block-size, and name getters, and exercise the copy constructor.

### Control Flow
`fields` verifies a randomly generated status. `copy` creates a copy and asserts equality.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Validates the file status variant used by file status APIs, listings, and fingerprint tests.

### Risks
Random inputs are unseeded. Equality assertions do not detect missing content fields because base equality excludes them.

### Test Signals
Confirms file instances report `isDirectory=false`, `isFile=true`, and preserve primary file metadata.
