# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_export.c

## Purpose
Implements Linux `export_operations` for NFS/export support on ZFS, including file-handle encoding, resolving file handles back to dentries, parent lookup, reverse name lookup, and metadata commit.

## Main APIs and Data
- `zpl_export_operations` exposes `.encode_fh`, `.fh_to_dentry`, `.fh_to_parent`, `.get_name`, `.get_parent`, and `.commit_metadata`.
- `zpl_encode_fh()` packs ZFS `fid_t` data into Linux `struct fid` buffers, optionally appending a parent fid for subtree checking.
- `zpl_fh_to_dentry()` and `zpl_fh_to_parent()` reverse the encoding.
- `zpl_get_name()` and `zpl_get_parent()` provide NFS reverse traversal support.
- `zpl_commit_metadata()` maps NFS metadata commit to `zfs_fsync()`.

## Control Flow
Encoding computes the caller-provided buffer size, prepares an inline `fid_t`, calls either `zfsctl_fid()` or `zfs_fid()`, and updates `max_len` to the required rounded word count. If a parent inode is provided, its fid is packed immediately after the child fid and `FILEID_INO32_GEN_PARENT` is returned.

Decoding validates handle type and embedded lengths before calling `zfs_vget()`. `ENOENT` is translated to `ESTALE` so NFS clients retry lookups when cached file handles no longer point at the current object. Parent decoding slices the second embedded fid and reuses dentry decoding.

Name lookup locks the parent inode shared and calls `zfs_get_name()`. Parent lookup performs `zfs_lookup(..., "..")`. Metadata commit skips synthetic control nodes and fsyncs real ZFS inodes.

## Integration Points
This is NFS glue over ZFS vnode-style operations and ZFS control-directory special nodes. It uses SPL fstrans markers, credentials, inode locking, and Linux `d_obtain_alias()` for disconnected dentries.

## Invariants and Edge Cases
- Handle length validation prevents parsing past provided buffers.
- Control-directory nodes use `zfsctl_*` fid handling.
- Long names beyond Linux’s hardcoded export buffer can lead to `ESTALE`, as noted by the file comment.
- `zpl_commit_metadata()` is a no-op for control nodes.

## Risks and Testing Signals
Test NFS export with and without subtree checking, stale file handles after rename/delete/recreate, snapshot/control-directory exports, long filenames, parent handle decoding, and metadata commit behavior under sync errors.
