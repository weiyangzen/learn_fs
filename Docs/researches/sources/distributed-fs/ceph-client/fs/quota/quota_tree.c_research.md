# sources/distributed-fs/ceph-client/fs/quota/quota_tree.c

Purpose: Provides the shared radix-tree-like on-disk storage engine used by VFS v2 quota formats to locate, allocate, update, delete, and enumerate dquot records in quota files.

Important APIs, types, and functions: Exports `qtree_entry_unused()`, `qtree_write_dquot()`, `qtree_delete_dquot()`, `qtree_read_dquot()`, `qtree_release_dquot()`, and `qtree_get_next_id()`. Internal helpers manage tree indexes, quota blocks, free block lists, free-entry lists, block-header validation, insertion recursion, removal recursion, and next-id scans.

Control flow: Reads and writes go through filesystem `quota_read` and `quota_write` at block offsets derived from `qtree_mem_dqinfo`. Writing inserts a missing dquot by walking or allocating tree blocks, finding a leaf data slot, converting memory data to disk format, and writing the entry. Releasing fake zero-usage dquots deletes their entry. Deletion clears the leaf entry, updates data-block entry counts and free lists, then recursively removes empty tree blocks except the root. Reads locate the leaf via tree indexes; missing entries become fake zeroed dquots.

State and persistence: Persistent state is the quota file tree rooted at `QT_TREEOFF`, data-block headers (`qt_disk_dqdbheader`), free-block chain, free-entry chain, and disk dquot entries. In-memory `qtree_mem_dqinfo` mirrors block counts, free list heads, block size, tree depth, entry size, and format operations. Metadata changes call `mark_info_dirty()`.

Dependencies and integration points: Used by `quota_v2.c` under `dqio_sem`. Depends on `qtree_fmt_operations` for format-specific disk conversion and id tests, generic dquot counters, and quota error reporting.

Risks and test signals: Risks include corrupt free-list links, cycles in tree blocks, out-of-range block references, full-block accounting mistakes, partial write handling, and id enumeration skipping entries. Test with dense and sparse ids, free/reallocate cycles, corrupted headers, tree depth limits, fake dquot deletion, full block transitions, and `Q_GETNEXTQUOTA`.
