## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/ListOptions.java

### Purpose
`ListOptions` carries directory listing semantics, currently whether listing should be recursive.

### Important APIs, Types, And Functions
`defaults()` returns recursive false. `isRecursive` and `setRecursive` expose the flag. Equality, hash code, and `toString` include it.

### Control Flow
`BaseUnderFileSystem.listStatus(path, options)` implements recursive traversal when true. `ObjectUnderFileSystem` passes the flag down to object listing and synthetic directory population.

### State And Persistence
Mutable in-memory option only.

### Dependencies And Integration Points
Used by UFS listing, metadata sync, recursive delete, and recursive rename logic.

### Risks
Recursive listing can be expensive and memory-heavy, especially for non-object UFS fallback which collects full arrays. Object-store recursive listings must correctly infer pseudo-directories.

### Test Signals
`ListOptionsTest` verifies default false, setter behavior, and equality.
