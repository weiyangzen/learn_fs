## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsStatus.java

### Purpose
`UfsStatus` is the abstract base metadata record for UFS files and directories returned by status and listing APIs.

### Important APIs, Types, And Functions
Fields include directory flag, nullable last-modified time, mutable name, owner, group, mode, and nullable xattr map. `copy()` is abstract. `convertToNames` converts a status array to a string array. Accessors expose file/directory flags, owner/group/mode/name/time/xattrs. `setName` mutates and returns `this`. Equality/hash code use name, directory flag, owner, group, mode, and xattr map.

### Control Flow
Subclasses call protected constructors. Copy construction clones the xattr map if present. `toStringHelper` standardizes subclass string output.

### State And Persistence
The status object is mutable through `mName`, and the xattr map and byte-array values are not deeply immutable. It is only an in-memory snapshot of UFS metadata.

### Dependencies And Integration Points
Used throughout UFS APIs, object-store listing conversion, metadata sync, and fingerprint creation. `BaseUnderFileSystem.performListingAsync` mutates names to become full paths.

### Risks
Marked `@NotThreadSafe`. Equality excludes last-modified time and file-specific data in `UfsFileStatus`, so it is not a full metadata comparison. `getXAttr` may return null despite its comment saying empty map when none.

### Test Signals
Directory and file status tests cover basic getters and copy equality. Fingerprint tests cover interactions with metadata fields.
