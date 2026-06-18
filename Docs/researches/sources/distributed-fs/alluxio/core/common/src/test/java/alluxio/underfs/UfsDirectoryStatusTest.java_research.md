## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsDirectoryStatusTest.java

### Purpose
Tests the basic `UfsDirectoryStatus` metadata contract.

### Important APIs, Types, And Functions
The tests construct `UfsDirectoryStatus`, call name, type, owner, group, and mode getters, and exercise the copy constructor.

### Control Flow
`fields` verifies fixed values. `copy` constructs a copy and asserts equality.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Validates the directory status variant used by UFS listing and status APIs.

### Risks
Does not test last-modified time, xattrs, `copy()`, `toString`, or `setName`.

### Test Signals
Confirms directory instances report `isDirectory=true`, `isFile=false`, and preserve permission metadata.
