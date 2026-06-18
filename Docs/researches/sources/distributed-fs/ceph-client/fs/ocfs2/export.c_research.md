# sources/distributed-fs/ceph-client/fs/ocfs2/export.c

Purpose: implements `export_operations` so OCFS2 can be exported through NFS. It encodes inode and parent file handles, decodes file handles back to dentries, validates stale handles, and obtains parent dentries for reconnectable exports.

Important APIs and functions: defines the on-wire-ish `struct ocfs2_inode_handle` containing block number and generation. Main routines are `ocfs2_get_dentry`, `ocfs2_get_parent`, `ocfs2_encode_fh`, `ocfs2_fh_to_dentry`, `ocfs2_fh_to_parent`, and the exported `ocfs2_export_ops`.

Control flow: handle decode validates a nonzero block number, first checks the inode cache with `ocfs2_ilookup`, and otherwise takes the NFS sync lock in EX mode before testing the inode allocator bit and reading the inode with `ocfs2_iget`. Generation mismatch returns `-ESTALE`. Parent lookup takes the NFS sync lock and a metadata lock on the child directory, resolves `".."`, validates the allocator bit, and obtains the parent alias. Encoding requires three 32-bit words for the target and six when a parent is supplied; insufficient buffers return `FILEID_INVALID` and the required size.

State and persistence behavior: file handles persist only the inode block number and generation, plus optional parent block/generation. The NFS sync DLM lock serializes handle decode against cross-node inode deletion so stale handles cannot race allocator reuse. No persistent state is stored by this file itself.

Dependencies and integration points: integrates VFS exportfs callbacks with OCFS2 inode lookup, allocator bitmap validation, metadata locking, dentry aliasing, tracing, and `ocfs2_nfs_sync_lock` from `dlmglue.c`. It is used when the superblock installs `ocfs2_export_ops`.

Risks: stale-handle detection depends on both allocator-bit validation and generation comparison. Missing the NFS sync lock would race remote inode deletion and reuse. Parent lookup returns `-ENOENT` for failed `".."` lookup but `-ESTALE` for invalid allocator state; NFS clients can observe these as different recovery behaviors. File-handle endianness is explicitly little-endian in the raw fid words.

Test signals: NFS export mount, lookup by file handle after inode eviction, stale handle after unlink/reuse, parent reconnect of disconnected dentries, insufficient file-handle buffer lengths, generation mismatch, invalid block number zero, allocator-bit clear, and multi-node deletion while NFS decode is in progress.
