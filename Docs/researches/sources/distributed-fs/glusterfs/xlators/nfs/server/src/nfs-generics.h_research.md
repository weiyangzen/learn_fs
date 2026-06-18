<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.h

## Purpose

`nfs-generics.h` declares the generic NFS operation facade and directory fd context structures used by protocol handlers and shared NFS code. Source read: complete 160-line file.

## Important APIs, Types, and Functions

Important types are `struct nfs_direntcache` and `nfs_fdctx_t`, which describe cached directory entries and per-fd directory context. Declared APIs mirror `nfs-generics.c`: generic async wrappers for stat, lookup, create, read, write, open, directory, link, rename, attribute, lock, xattr, and access operations. It also declares synchronous stubs `nfs_open_sync`, `nfs_write_sync`, and `nfs_read_sync`.

## Control Flow

No executable flow exists in the header. The declarations define the operation surface that higher-level NFS protocol code calls instead of directly winding Gluster fops.

## State and Persistence Behavior

`nfs_fdctx_t` contains a mutex, directory buffer size, offset, dirent cache pointer, and directory volume pointer. This is in-memory fd context state. The header does not own persistence.

## Dependencies and Integration Points

It includes `nfs.h`, `nfs-fops.h`, and `nfs-inodes.h`. It bridges protocol code to the fop and inode maintenance layers.

## Risks and Edge Cases

The header declares synchronous APIs that are not implemented in `nfs-generics.c`, so callers rely on implementations elsewhere or risk link failures if added incorrectly. Directory cache locking and lifetime must be handled by users of `nfs_fdctx_t`.

## Test Signals

Compile/link tests should verify all declared async and sync wrappers resolve. Directory readdir tests should exercise `nfs_fdctx_t` cache state, offsets, and lock behavior through the implementation that owns those fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.h -->
