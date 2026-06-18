# sources/distributed-fs/ceph-client/fs/gfs2/export.c

## Purpose
Implements GFS2 export operations for NFS/exportfs file handles, including encoding inode identities, resolving handles back to dentries, finding parents, and deriving a child's name within a parent directory.

## Important APIs, Types, And Functions
`gfs2_encode_fh()` writes small or large file handles containing child and optional parent formal inode numbers and block addresses. `get_name_filldir()` is a `dir_context` actor that finds a matching inode number during directory scan. `gfs2_get_name()` locks the parent directory and uses `gfs2_dir_read()` to discover the child name. `gfs2_get_parent()` looks up `..`. `gfs2_get_dentry()` resolves an inum via `gfs2_lookup_by_inum()` and wraps it with `d_obtain_alias()`. `gfs2_fh_to_dentry()` and `gfs2_fh_to_parent()` decode handle variants. `gfs2_export_ops` registers the callbacks.

## Control Flow
Encoding validates caller buffer length, writes child identity, and optionally appends parent identity unless the inode is the root. Decode accepts current small/large and old handle sizes, reconstructs big-endian 64-bit identifiers, rejects malformed short handles or zero formal inode numbers, and obtains aliases. Name lookup scans the parent directory under shared glock until a matching inode number is emitted.

## State And Persistence
File handles persist GFS2 inode identity externally for NFS clients. The file itself does not change disk state. Directory scanning observes current directory entries under glock protection.

## Dependencies And Integration Points
Depends on exportfs, GFS2 directory reading, lookup by inum, glocks, qdotdot, and inode identity fields. Used when GFS2 is exported over NFS or other exportfs consumers.

## Risks
Stale handles must return `ESTALE`/NULL behavior rather than aliasing wrong inodes. `gfs2_get_name()` matches only `no_addr` in the filldir callback even though it stores formal inode too; uniqueness assumptions rely on block address identity. Parent handles require larger buffers. Directory scan cost can be high for large directories.

## Test Signals
Test NFS export encode/decode for root and non-root, parent handle decode, stale/deleted inode handles, rename after handle creation, large directory get_name scans, and old handle size compatibility.
