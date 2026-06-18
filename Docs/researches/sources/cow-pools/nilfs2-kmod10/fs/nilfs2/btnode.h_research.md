# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/btnode.h

Header for B-tree node cache operations. It declares cache initialization/clear, node block create/read/delete, and prepare/commit/abort APIs for changing a node block key.

The central type is `struct nilfs_btnode_chkey_ctxt`, which carries old key, new key, old buffer, and optional new buffer through rekey operations.

Integration: consumed by `btree.c`, `gcinode.c`, and any path that must move B-tree node buffers when virtual or physical block addresses are reassigned.

Risk/notes: callers must use the change-key context transactionally; abort and commit have different cleanup semantics depending on whether a full folio move or copy-mode move was prepared.
