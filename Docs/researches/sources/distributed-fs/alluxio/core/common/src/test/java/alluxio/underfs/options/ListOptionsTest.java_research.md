## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/ListOptionsTest.java

### Purpose
Tests `ListOptions` recursive flag behavior.

### Important APIs, Types, And Functions
Uses `ListOptions.defaults`, `isRecursive`, `setRecursive`, and equality helper.

### Control Flow
Default recursive false is asserted, then the flag is set to false and true and checked.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects listing behavior used by metadata sync and recursive operations.

### Risks
No coverage for interactions with actual listing implementations.

### Test Signals
Confirms non-recursive listing is the default.
