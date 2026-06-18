<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.h

## Purpose

`nfs-common.h` declares shared constants and helper APIs for GlusterFS NFS server path, inode, gfid, xlator, and generation handling. Source read: complete 72-line file.

## Important APIs, Types, and Functions

Important constants are `NFS_PATH_MAX`, `NFS_NAME_MAX`, `NFS_DEFAULT_CREATE_MODE`, `NFS_RESOLVE_EXIST`, and `NFS_RESOLVE_CREATE`. Declared APIs cover xlator mapping, loc lifecycle, inode/gfid/entry/root loc construction, gfid hashing, and generation fix-up.

## Control Flow

The header has no executable flow; it defines the helper surface used by MOUNT, NFSv3 helpers, inode wrappers, and fop wrappers.

## State and Persistence Behavior

The APIs declared here manipulate transient `loc_t`, inode references, and inode ctx state. No persistent storage is declared.

## Dependencies and Integration Points

The header depends on `unistd.h`, Gluster xlator/iatt/uuid types, and standard NAME_MAX. It integrates with `mount3.c`, `nfs-fops.c`, `nfs-generics.c`, and NFS inode/filehandle code.

## Risks and Edge Cases

`NFS_PATH_MAX` is hard-coded to 4096 as a crash workaround for long paths, so callers must preserve length checks. Declarations must stay synchronized with `nfs-common.c`; currently `nfs_parent_inode_loc_fill` is implemented but not exposed here.

## Test Signals

Compile all NFS server files with this header and exercise path/gfid loc construction through MOUNT and NFSv3 lookup/read/write tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.h -->
