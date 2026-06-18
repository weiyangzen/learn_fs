# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.h

## Purpose

`nfs-inodes.h` declares the inode-aware NFS FOP wrapper API implemented by `nfs-inodes.c`. It gives protocol code a stable interface for issuing namespace and open operations while keeping the NFS inode table synchronized with backend results.

## Important APIs, types, and functions

The header exports wrappers for create, mkdir, open, rename, link, unlink, rmdir, symlink, opendir, mknod, and lookup. All wrappers take the NFS xlator, target subvolume, `nfs_user_t`, loc/name inputs, a Gluster FOP callback typedef, and caller-local data. `nfs_link_inode()` is declared as a direct inode link helper, although this implementation file mainly performs link operations internally through callbacks.

## Control flow

There is no runtime control flow in the header. Its signature pattern shows the intended call chain: NFS protocol handlers resolve a file handle to a `loc_t`, initialize an `nfs_user_t` from the RPC request, then call a wrapper. The wrapper submits a `nfs_fop_*` request and later resumes the protocol-specific callback.

## State and persistence behavior

The header owns no state. It defines ownership expectations through callback signatures: the wrappers may allocate transient FOP-local state and fds, while callers retain responsibility for protocol call state passed as `local`.

## Dependencies and integration points

It includes Gluster dict/iobuf types and `nfs-fops.h`, and relies on `nfs_user_t` from `nfs.h` being visible through included dependencies. It is included by NFSv3 helpers and operation handlers that need inode-maintaining wrappers rather than raw FOP calls.

## Risks and edge cases

Prototype drift is the main risk: callback typedefs must match lower-layer FOP callback shapes exactly. The presence of `nfs_inode_lookup()` in the header without an implementation in this file means its definition is elsewhere or stale, which should be checked during build/link validation.

## Test signals

Compile/link coverage is essential. Runtime signals are the same namespace mutation tests used for `nfs-inodes.c`, plus link-time detection for declared but missing APIs.
