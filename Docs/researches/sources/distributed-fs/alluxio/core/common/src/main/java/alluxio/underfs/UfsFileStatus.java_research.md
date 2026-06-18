## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsFileStatus.java

### Purpose
`UfsFileStatus` is the concrete `UfsStatus` variant for files. It adds content hash, content length, and block size metadata used for metadata sync, fingerprints, Web UI display, and block-size planning.

### Important APIs, Types, And Functions
Constants are `INVALID_CONTENT_HASH` as an empty string and `UNKNOWN_BLOCK_SIZE` as `-1`. Main constructors accept name, content hash, length, last-modified time, owner, group, mode, optional xattrs, and block size. Deprecated constructors keep older call sites working by filling `UNKNOWN_BLOCK_SIZE`. Accessors expose content hash, length, and block size.

### Control Flow
Construction sets `isDirectory=false`. `copy()` uses the copy constructor; `toString()` includes content hash and length in addition to base fields.

### State And Persistence
Instances are in-memory metadata snapshots. Copying clones the xattr map via the base copy constructor but shares each xattr byte array.

### Dependencies And Integration Points
`ObjectUnderFileSystem` creates this from `ObjectStatus`, with optional CRC64 xattr. `Fingerprint` uses content hash and permission fields to compare metadata/content. `UnderFileSystem` implementors return it from file status methods.

### Risks
Equality and hash code are inherited from `UfsStatus` and do not include file-specific fields such as content hash, content length, last-modified time, or block size. This is intentional or legacy behavior but risky if callers use equality as full metadata equality.

### Test Signals
`UfsFileStatusTest` verifies getters, file/directory booleans, last-modified time, block size, and copy equality. `FingerprintTest` exercises fingerprint creation with content hash overrides.
