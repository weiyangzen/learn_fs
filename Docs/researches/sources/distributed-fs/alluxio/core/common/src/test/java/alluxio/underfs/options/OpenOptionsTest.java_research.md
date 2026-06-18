## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/OpenOptionsTest.java

### Purpose
Tests selected `OpenOptions` behavior.

### Important APIs, Types, And Functions
Uses `OpenOptions.defaults`, `getOffset`, `setOffset`, and equality helper.

### Control Flow
Default offset is asserted as zero. Several offsets are set and verified.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects defaults used by `UnderFileSystem.open`.

### Risks
It does not verify length default, recover-failed-open flag, position-short flag, negative values, or string output.

### Test Signals
Confirms offset defaults and mutation.
