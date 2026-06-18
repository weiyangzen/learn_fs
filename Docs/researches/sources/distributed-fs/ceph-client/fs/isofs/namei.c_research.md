## sources/distributed-fs/ceph-client/fs/isofs/namei.c

Purpose: implements directory entry lookup for ISOFS.

Important APIs: `isofs_lookup` allocates a page-sized scratch buffer, calls `isofs_find_entry`, igets the matching inode, and returns `d_splice_alias`. `isofs_cmp` delegates to dentry custom compare operations when present, allowing case-insensitive and Joliet-specific comparisons. `isofs_find_entry` mirrors readdir name resolution for matching.

Control flow: lookup scans the directory from offset zero, reads blocks with `isofs_bread`, handles zero-length sector padding, copies split records, validates name lengths, derives candidate names through Rock Ridge, Joliet, Acorn, normal translation, or raw ISO names, applies hide/showassoc filters, compares against the dentry, normalizes matched block/offset, and returns the identity.

State and persistence: no writes. Lookup populates dcache through returned aliases and depends on stable block/offset inode identity. Temporary page memory carries translated names and split directory records.

Dependencies and integration points: integrates with VFS dcache, dentry operations selected in `inode.c`, Rock Ridge/Joliet/Acorn helpers, `isofs_iget`, and directory-record normalization.

Risks and test signals: lookup and readdir must agree on visible names. Risks include mismatched case folding, hidden/associated option handling, malformed split entries, Rock Ridge ignored entries (`RE`), and scratch-buffer offsets. Test lookup of every name style emitted by readdir, case-insensitive modes, hidden/associated entries, corrupt records, and directories with split entries.
