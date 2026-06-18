# sources/distributed-fs/ceph-client/include/linux/exportfs.h

Purpose: VFS/NFS file-handle encoding and decoding contract for exportable filesystems and `open_by_handle_at()`.

Important APIs/types/functions: `MAX_HANDLE_SZ`, `enum fid_type`, `struct fid`, handle flags, user flags, `struct handle_to_path_ctx`, `struct export_operations`, export operation flags, `exportfs_cannot_lock()`, `exportfs_encode_inode_fh()`, `exportfs_encode_fh()`, capability predicates, `exportfs_encode_fid()`, `exportfs_decode_fh_raw()`, `exportfs_decode_fh()`, and generic inode-number helpers.

Control flow: filesystems implement export ops to encode inode/parent identity and decode handles to dentries. NFSd and handle syscalls validate capabilities, encode connectable or non-decodeable FIDs, decode raw handles, check permissions/subtree constraints, and use filesystem metadata commit/block layout callbacks when provided.

State/persistence: file handles encode persistent filesystem object identity such as inode/generation/subvolume/checkpoint. Runtime state includes dentries/inodes and export op flags.

Dependencies/integration: VFS dentries/inodes/superblocks, NFSd, open-by-handle syscalls, iomap/block layout, filesystem-specific stable identifiers.

Risks/test signals: risks are stale or forgeable handles, missing parent info for subtree checks, custom open/permission ops not respected by NFSd, wrong fid length units, and generation reuse. Test NFS export, `name_to_handle_at`/`open_by_handle_at`, stale inode generation, connectable handles, directory-only decode, and generic helpers on filesystems.
