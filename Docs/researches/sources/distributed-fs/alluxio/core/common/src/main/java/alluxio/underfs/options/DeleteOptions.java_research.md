## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/DeleteOptions.java

### Purpose
`DeleteOptions` carries delete-directory semantics, currently just recursive deletion.

### Important APIs, Types, And Functions
`defaults()` returns a new option with recursive false. `isRecursive` and fluent `setRecursive` expose the flag. Equality, hash code, and `toString` include the flag.

### Control Flow
The private constructor initializes non-recursive behavior. `ObjectUnderFileSystem.deleteDirectory` uses the flag to reject non-empty directories or to recursively list and batch delete descendants.

### State And Persistence
Mutable in-memory option object only.

### Dependencies And Integration Points
Used by `UnderFileSystem.deleteDirectory` and eventual-consistency variants.

### Risks
Non-recursive is the safe default. Accidentally setting recursive true can delete a tree; provider implementations must honor the flag.

### Test Signals
`DeleteOptionsTest` verifies default false, setter behavior, and equality.
