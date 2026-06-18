# sources/distributed-fs/ceph-client/fs/gfs2/dir.h

## Purpose
Declares GFS2 directory APIs, directory-add preflight state, hash helpers, and qstr-to-dirent initialization.

## Important APIs, Types, And Functions
`struct gfs2_diradd` carries allocation preflight results: number of blocks required, saved dirent, saved buffer, and whether to save location. Public declarations cover search, check, add, no-add cleanup, delete, read, move-inode update, exhash deallocation, allocation-required preflight, new directory buffer allocation, and hash-cache invalidation. `gfs2_disk_hash()` computes CRC32-based directory hashes. `gfs2_str2qstr()` fills qstr fields. `gfs2_qstr2dirent()` initializes an empty dirent with hash, record length, name length, type zero, and copied name. `gfs2_qdot` and `gfs2_qdotdot` are exported qstrs.

## Control Flow
Inline helpers compute hashes and initialize on-disk dirent fields. `gfs2_dir_no_add()` releases a preflight buffer when insertion is abandoned.

## State And Persistence
No header-owned state except exported qstr declarations. Inline dirent initialization sets on-disk fields before callers fill inode/type.

## Dependencies And Integration Points
Includes dcache and CRC32 APIs. Used by directory implementation, dentry hashing, export parent lookup, inode operations, and rename/link paths.

## Risks
Hash function must remain compatible with on-disk directory hashes. `gfs2_qstr2dirent()` leaves inode/type empty by design; callers must fill them before exposing the entry. Saved `gfs2_diradd` buffers must be released if not consumed.

## Test Signals
Compile all users, verify hash consistency with `dentry.c`, test abandoned add preflight cleanup, and inspect created dirents for correct hash/name/record fields.
