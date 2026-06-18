# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-inodes.c

## Purpose

`nfs-inodes.c` wraps generic NFS FOP submission with NFS-specific inode table maintenance. It is the bridge between protocol handlers that issue create/open/link/unlink style operations and Gluster's inode/fd bookkeeping, so successful namespace mutations are reflected in the NFS xlator's inode cache before the original protocol callback is resumed.

## Important APIs, types, and functions

- `nfl_inodes_init()` stores inode, parent, newparent, name, and newname references into `struct nfs_fop_local`.
- `inodes_nfl_to_prog_data` restores the upper-layer callback/local state from the FOP-local wrapper and wipes the wrapper.
- `nfs_inode_create()`, `nfs_inode_mkdir()`, `nfs_inode_mknod()`, and `nfs_inode_symlink()` call the matching `nfs_fop_*` operation and link the returned inode into the parent on success.
- `nfs_inode_unlink()` and `nfs_inode_rmdir()` unlink and forget cached inodes after successful removal.
- `nfs_inode_rename()` updates the inode table using `inode_rename()`.
- `nfs_inode_link()` links an existing inode into a new parent.
- `nfs_inode_open()` and `nfs_inode_opendir()` allocate fds and forward open callbacks; `opendir` binds the fd on success while file opens leave binding to the higher fd-cache layer.

## Control flow

Each public wrapper validates its NFS xlator, target subvolume, loc/user inputs, allocates a `nfs_fop_local` via `nfs_fop_handle_local_init`, stores the protocol callback/local value, and submits the underlying FOP. Completion callbacks first inspect `op_ret`; on success they mutate the inode table with `inode_link()`, `inode_rename()`, `inode_unlink()`, or `inode_forget()`. The wrapper local is then converted back into the protocol callback context and the saved callback is invoked with the original FOP result. Link-like callbacks call `inode_lookup()` then `inode_unref()` on linked inodes to keep lookup counts coherent.

## State and persistence behavior

The file maintains only in-memory inode and fd state. It does not persist metadata itself; backend xlators perform the durable operation. Its state changes are references stored in `nfs_fop_local`, inode table links, lookup counts, and fd refs. Error paths wipe the local wrapper and unref newly created fds to avoid leaks.

## Dependencies and integration points

This file depends on `nfs-fops.h` for asynchronous FOP helpers, `nfs.h` for `nfs_user_t`, Gluster inode/fd APIs, `loc_t`, callback typedefs, and NFS message IDs. It is consumed by NFSv3 operation code that wants one call to perform both the backend FOP and NFS inode-cache repair.

## Risks and edge cases

- A few wipe calls pass `xl` instead of `nfsx`; if the wipe routine assumes the NFS xlator for mempool ownership, that is worth auditing.
- `nfs_inode_link_cbk()` stores `newloc->name` in `nfl->path` while using `nfl->newparent`; the naming works but is easy to misread.
- File `open` intentionally does not bind the fd, so callers must preserve the fd-cache invariant.
- Callback sequencing invokes the upper callback before the final linked-inode lookup/unref pair in create-like operations.

## Test signals

Useful tests cover successful and failed create/mkdir/mknod/symlink, rename across parents, hard link creation, unlink/rmdir cache removal, open/opendir fd lifetime on success and failure, and namespace operation callbacks receiving original FOP return values after cache repair.
