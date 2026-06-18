## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/DeleteOptionsTest.java

### Purpose
Tests `DeleteOptions` default and setter behavior.

### Important APIs, Types, And Functions
Uses `DeleteOptions.defaults`, `isRecursive`, `setRecursive`, and `CommonUtils.testEquals`.

### Control Flow
The default test expects recursive false. The fields test toggles false and true and checks each value.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects delete-directory semantics for UFS operations.

### Risks
No negative or concurrency concerns; coverage is intentionally narrow.

### Test Signals
Confirms non-recursive delete is the default.
