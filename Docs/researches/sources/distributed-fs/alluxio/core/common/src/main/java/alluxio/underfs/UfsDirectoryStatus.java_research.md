## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsDirectoryStatus.java

### Purpose
`UfsDirectoryStatus` is the concrete `UfsStatus` variant for directories returned from UFS status and listing operations.

### Important APIs, Types, And Functions
Constructors accept name, owner, group, mode, optional last-modified time, and optional xattrs. The copy constructor delegates to `UfsStatus`. `copy()` returns a deep-ish copy of the status object, and `toString()` uses the inherited `toStringHelper`.

### Control Flow
Construction sets `isDirectory=true`; all field access and equality behavior comes from `UfsStatus`.

### State And Persistence
Instances hold only metadata in memory. The inherited copy constructor clones the xattr map but not the byte-array values inside it.

### Dependencies And Integration Points
Object stores synthesize this type from directory marker objects and common prefixes. Other UFS implementations return it from `getDirectoryStatus`, `getStatus`, and listings.

### Risks
It is annotated `@NotThreadSafe`; `setName` inherited from `UfsStatus` mutates listing results. Mutable xattr byte arrays can leak changes across copies.

### Test Signals
`UfsDirectoryStatusTest` verifies directory/file booleans, owner/group/mode/name getters, and copy equality.
