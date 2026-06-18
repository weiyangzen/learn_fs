# sources/distributed-fs/lustre-release/lustre/llite/llite_nfs.c

## Purpose

`llite_nfs.c` implements NFS export support for Lustre llite. It encodes Lustre FIDs into export file handles, decodes file handles back into dentries, resolves parent handles, finds names for child dentries by scanning directories, assigns a stable clustered-NFS device id from the MDT UUID, and handles special `.lustre` and `.lustre/fid` objects used for FID-based access.

The file provides `lustre_export_operations`, which is installed on the superblock during mount when the kernel stack is large enough.

## Important APIs, Types, And Functions

- `get_uuid2int()`: hashes an MDT UUID string into a 32-bit value used by `llite_lib.c` to set a stable `s_dev` for clustered NFS exports.
- `search_inode_for_lustre()`: looks up an inode by Lustre FID. It first tries `ilookup5()` with `ll_test_inode_by_fid()`, then issues an MDT getattr by FID and builds/updates an inode with `ll_prep_inode()`.
- `ll_iget_for_nfs()`: converts a FID to a dentry for exportfs. It validates FID sanity, handles root FID, resolves normal objects through `search_inode_for_lustre()`, creates aliases with `d_obtain_alias()`, and special-cases `.lustre` and `.lustre/fid` dentries for `LU_DOT_LUSTRE_FID` and `LU_OBF_FID`. It also adjusts regular-file operations for `nfsd` kthreads to disable splice.
- `ll_encode_fh()`: encodes a `struct lustre_file_handle` containing child FID and optional parent FID into the NFS file-handle buffer and returns `FILEID_LUSTRE`.
- `do_nfs_get_name_filldir()` and `ll_nfs_get_name_filldir()`: directory fill callbacks that compare each `lu_dirent` FID to the target child FID and copy the matching name.
- `ll_get_name()`: implements exportfs `.get_name` by preparing metadata op data, reading the parent directory with `ll_dir_read()`, and returning the name matching the child inode FID.
- `ll_fh_to_dentry()` and `ll_fh_to_parent()`: decode Lustre export file handles into child or parent dentries.
- `ll_dir_get_parent_fid()`: asks the MDT for `".."` on a directory and extracts the returned parent FID.
- `ll_get_parent()`: exportfs `.get_parent` implementation using `ll_dir_get_parent_fid()` and `ll_iget_for_nfs()`.
- `lustre_export_operations`: exportfs operation table with `.get_parent`, `.encode_fh`, `.get_name`, `.fh_to_dentry`, and `.fh_to_parent`.

## Control Flow

NFS file-handle creation starts in `ll_encode_fh()`. It verifies the caller's buffer is large enough for `struct lustre_file_handle`, stores the child FID and optional parent FID, updates the word count, and returns Lustre's file-handle type. If the buffer is too small it returns `FILEID_INVALID` after reporting the needed size.

File-handle decode enters `ll_fh_to_dentry()` or `ll_fh_to_parent()`, validates the handle type, and calls `ll_iget_for_nfs()` with the relevant FID. Normal FIDs go through `search_inode_for_lustre()`: the local inode cache is checked first, then MDT getattr-by-FID retrieves metadata, and `ll_prep_inode()` constructs the inode. The resulting inode is wrapped with `d_obtain_alias()`.

Special FIDs need explicit dcache construction. For `.lustre`, `ll_iget_for_nfs()` looks up or allocates the `.lustre` child under the root and attaches the resolved inode. For the object-by-FID pseudo-directory, it ensures `.lustre` exists, then looks up or allocates the `fid` child and attaches the OBF inode. Locks on the root or `.lustre` inode serialize dentry construction.

Name lookup for exportfs uses `ll_get_name()`. It verifies the parent is a directory with file operations, builds `md_op_data`, locks the directory inode, calls `ll_dir_read()` with a filldir callback, unlocks, and returns `-ENOENT` if no directory entry FID matched the child.

Parent lookup uses `ll_dir_get_parent_fid()`, which prepares metadata op data for `".."`, calls `md_getattr_name()`, reads `RMF_MDT_BODY`, copies `mbo_fid1` if valid, and lets `ll_iget_for_nfs()` resolve that parent FID.

## State And Persistence Behavior

This file does not write persistent filesystem state. It creates and reuses VFS dentries/inodes to represent server-backed Lustre FIDs to exportfs and NFS. It can populate the local inode cache by fetching attributes from the MDT and can create dcache aliases for `.lustre` and `.lustre/fid` pseudo-objects. `get_uuid2int()` contributes to persistent export identity at the mount level by making `s_dev` stable across clients using the same MDT UUID.

The code also modifies in-memory regular-file operations for `nfsd` kthreads to select a no-splice file operations table, avoiding a kernel NFS/splice interaction. On older kernels it forces the open-lock caching threshold for NFS lookups.

## Dependencies And Integration Points

`llite_nfs.c` integrates Linux exportfs with Lustre FIDs, MDT getattr operations, llite inode preparation, directory reading, LDLM/name lookup helpers, dcache aliasing, and special Lustre FID constants such as root, `.lustre`, and OBF. It depends on `ll_get_default_mdsize()`, `md_getattr()`, `md_getattr_name()`, `ll_prep_inode()`, `ll_prep_md_op_data()`, `ll_finish_md_op_data()`, `ll_dir_read()`, `ll_select_file_operations()`, `cl_fid_build_ino()`, and `ll_need_32bit_api()`.

The export operation table is installed by `client_common_fill_super()` in `llite_lib.c`, and the stable `s_dev` hash is also used there for clustered NFS behavior.

## Risks And Edge Cases

- Stale NFS handles commonly refer to deleted or moved objects. The code suppresses noisy logs for failed getattr-by-FID and returns stale-style errors through exportfs.
- Special `.lustre` and OBF dentry construction manually allocates dentries and attaches inodes. Error paths must avoid leaking inode references or dentries.
- `ll_dir_get_parent_fid()` may receive replies without a valid parent FID; the comment notes MDTs may lose parent FID information, so callers must tolerate unresolved parents.
- `ll_get_name()` depends on directory entries carrying `lu_dirent` FIDs and uses container-style access to recover the enclosing record from the name pointer.
- File-handle buffer sizing is in 32-bit words and must match `struct lustre_file_handle`.
- Disabling splice for `nfsd` changes file operation selection for regular inodes resolved through NFS.

## Test Signals

Useful tests include NFS export handle encode/decode for regular files, directories, root, `.lustre`, and `.lustre/fid`; stale FID handling after unlink or MDT lookup failure; parent lookup for normal and remote/striped directories; `.get_name` over large and striped directories; small file-handle buffer behavior; clustered NFS clients producing the same `s_dev` from the same MDT UUID; nfsd regular-file operation selection with splice disabled; and error cleanup for failed dentry allocation or `.lustre` inode lookup.
