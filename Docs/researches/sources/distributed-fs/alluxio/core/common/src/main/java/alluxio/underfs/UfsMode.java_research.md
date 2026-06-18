## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsMode.java

### Purpose
`UfsMode` enumerates the effective operation mode for under storage during normal operation or maintenance.

### Important APIs, Types, And Functions
The enum values are `NO_ACCESS`, `READ_ONLY`, and `READ_WRITE`.

### Control Flow
No behavior is defined. `BaseUnderFileSystem.getOperationMode` maps a physical-store state to one of these modes and defaults to `READ_WRITE`.

### State And Persistence
No state beyond enum constants.

### Dependencies And Integration Points
Used by mount and physical-UFS state logic to gate reads/writes or disable access.

### Risks
Consumers must consistently enforce the mode; the enum by itself has no policy.

### Test Signals
No direct tests in this subset.
