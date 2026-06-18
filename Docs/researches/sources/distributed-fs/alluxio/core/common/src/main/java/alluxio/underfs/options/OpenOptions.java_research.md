## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/OpenOptions.java

### Purpose
`OpenOptions` carries read-open parameters for UFS files.

### Important APIs, Types, And Functions
Defaults are offset zero, length `Long.MAX_VALUE`, recover-failed-open false, and position-short false. Getters and fluent setters expose offset, maximum length, recovery behavior, and small positioned-read hint. Equality, hash code, and `toString` include all fields.

### Control Flow
`BaseUnderFileSystem.open(path)` uses defaults. `ObjectUnderFileSystem.open` passes the options plus a one-attempt retry policy to `openObject`; `openExistingFile` passes the full eventual-consistency retry policy.

### State And Persistence
Mutable in-memory option only. No persistence.

### Dependencies And Integration Points
Used by UFS implementations to select range reads, retry open behavior, and optimize positioned reads.

### Risks
No local validation for negative offsets or lengths. The `positionShort` hint must not alter correctness for normal reads.

### Test Signals
`OpenOptionsTest` verifies default offset, setter behavior for offset, and equality. It does not test length, recovery, or position-short flags.
