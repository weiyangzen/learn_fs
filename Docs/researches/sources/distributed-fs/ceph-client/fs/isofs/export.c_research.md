## sources/distributed-fs/ceph-client/fs/isofs/export.c

Purpose: implements NFS export operations for ISOFS because ISOFS uses `iget5_locked` with block/offset inode identity instead of default iget-compatible inode numbers.

Important APIs/types: `isofs_export_ops` supplies `.encode_fh`, `.fh_to_dentry`, `.fh_to_parent`, and `.get_parent`. `struct isofs_fid` stores block, offset, parent offset, generation, parent block, and parent generation. `isofs_export_iget` validates block bounds, reconstitutes an inode with `isofs_iget`, checks generation if supplied, and returns an alias dentry.

Control flow: file handles encode the normalized directory-entry block and offset, plus optional parent identity. Parent lookup relies on the invariant that directory inode identity points to the `.` entry at offset zero; it reads the directory block, steps to the second entry (`..`), validates it, normalizes it, and igets the parent.

State and persistence: no writes. Exported file handles persist identity externally in NFS clients; correctness depends on stable block/offset mapping and generation checks.

Dependencies and integration points: integrates with VFS exportfs, ISOFS inode normalization in `isofs.h`, and NFS file-handle size constraints, including an NFSv2-friendly packed offset layout.

Risks and test signals: risks include stale handles, non-normalized directory inodes, invalid parent records, block bounds, and 16-bit offset packing limitations. Test NFS export of directories/files, reconnect after dcache eviction, parent lookup from child directories, generation mismatch, and malformed media with bad `..` entries.
