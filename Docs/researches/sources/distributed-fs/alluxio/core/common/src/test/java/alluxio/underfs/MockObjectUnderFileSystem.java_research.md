## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/MockObjectUnderFileSystem.java

### Purpose
`MockObjectUnderFileSystem` is a minimal concrete subclass of `ObjectUnderFileSystem` for unit tests.

### Important APIs, Types, And Functions
It implements all abstract object-store hooks with inert return values: false, null, or no-op. `setMode` and `setOwner` are no-ops.

### Control Flow
The class does not model storage. Tests subclass or Mockito selected methods when they need behavior.

### State And Persistence
Only inherited state exists. No object data is persisted.

### Dependencies And Integration Points
Used by `ObjectUnderFileSystemTest` to access protected retry behavior and to override listing/status methods for async listing tests.

### Risks
Because many methods return null, using it without overriding required hooks can produce null pointer failures unrelated to production behavior.

### Test Signals
It is a fixture, not an assertion-bearing test. Its usefulness is enabling focused tests of superclass logic.
