# sources/distributed-fs/openafs/src/afs/LINUX/osi_export.c

## Purpose
This file implements Linux `export_operations` for exporting AFS through NFS translator support. It encodes AFS FIDs into Linux file handles, decodes file handles back to vcaches/dentries, resolves parent/name relationships for exported dentries, and handles dynroot/fakestat special cases.

## Important APIs, types, and functions
- File-handle type constants such as `AFSFH_NET_VENUSFID`, `AFSFH_NET_CELLFID`, `AFSFH_DYN_RO_CELL`, `AFSFH_DYN_MOUNT`, and related dynroot link/cell variants.
- `afs_encode_fh` serializes normal and dynroot vcache FIDs into Linux export file handles.
- `afs_fh_to_dentry` or legacy `afs_decode_fh` decodes file handles to AFS `VenusFid` values and calls dentry construction.
- `update_dir_parent` reads the `..` entry from a directory dcache and updates `adp->f.parent`.
- `UnEvalFakeStat` maps a fakestat volume-root directory back to its mount point when required.
- `get_dentry_from_fid` creates an AFS request, obtains a vcache, fills inode attributes, and creates an anonymous dentry.
- `afs_export_get_dentry`, `afs_export_get_name`, and `afs_export_get_parent` implement the Linux export callbacks.
- `afs_export_ops` registers the callback table.

## Control flow and behavior
Encoding starts from the dentry inode's vcache. Dynroot FIDs are encoded by dynroot vnode type: cell/alias handles store a cell handle, mount handles also store the unique field, and unsupported dynroot symlinks fail. Normal file handles prefer a migratable cell-handle format when there is enough space; otherwise they emit a four-word network-order VenusFid.

Decoding switches on file-handle type, validates length, maps cell handles back to local cell numbers, synthesizes dynroot FIDs where needed, then calls the modern or legacy dentry lookup path. `get_dentry_from_fid` builds request/attribute objects, calls `afs_GetVCache`, updates missing directory parents, optionally unevaluates fakestat volume roots, refreshes inode attributes with `afs_getattr`/`afs_fill_inode`, drops `AFS_GLOCK` around `d_alloc_anon`, attaches AFS dentry operations, and returns the dentry or an encoded error.

`afs_export_get_name` resolves a child's name in a parent directory. It handles the dynamic mount directory, volume-root mount point FID translation, fake-stat evaluation, parent cell/volume mismatch rejection, dcache freshness/fetching waits, and `afs_dir_EnumerateDir` with `get_name_hook`. `afs_export_get_parent` handles dynmount roots, dynroot mount children, volume-root mount parent FIDs, and ordinary parent FID fields, using `update_dir_parent` if a directory parent is not yet cached.

## State and persistence
The file updates runtime vcache metadata such as directory parent vnode/unique fields and may force vcache/inode attribute refresh. It does not persist data itself, but it uses cached directory contents and volume/cell metadata to reconstruct exported object identity. File handles include cell handles to remain stable across local cell-number changes.

## Dependencies and integration points
The code integrates Linux exportfs with OpenAFS vcache, dcache, dynroot, fakestat, cell, volume, request, inode, dentry, and NFS translator layers. It is compiled only when `AFS_NONFSTRANS` is not defined. It depends on `afs_dentry_operations`, `afs_fill_inode`, `afs_GetCellByHandle`, `afs_GetDCache`, `afs_dir_Lookup`, and `afs_dir_EnumerateDir`.

## Risks
Export correctness is sensitive to stale directory caches, missing parent FIDs, cell-handle lookup failures, fakestat policy, and dynroot edge cases. `afs_export_get_name` includes an unconditional success `printk`, which may be noisy for exported workloads. `d_alloc_anon` requires careful lock dropping; vcache/inode references must remain valid across that window. NFS export semantics rely on stable handles; fallback four-word local cell-number handles are less migratable. Unsupported dynroot symlink handles return failure.

## Test signals
NFS export tests should cover normal file and directory handle encode/decode, reconnect after cell-number changes using cell handles, dynroot cell/link/mount cases, volume roots with fakestat enabled/disabled, parent lookup for newly materialized directories, stale directory cache refresh/retry, negative dentries, and missing cells/volumes. Lockdep and reference-count leak checks are high value around anonymous dentry construction.
