# sources/distributed-fs/ceph-client/fs/hfs/string.c

Purpose: implements classic HFS filename hashing and comparison using Macintosh lexical case ordering.

Important APIs and control flow: the file-local `caseorder[256]` table folds case and imposes Mac ordering. `hfs_hash_dentry()` caps names at `HFS_NAMELEN`, hashes each byte through `caseorder`, and stores the dentry hash. `hfs_strcmp()` compares two Mac-encoded names byte-by-byte through `caseorder`, returning the ordering difference or length difference. `hfs_compare_dentry()` implements dcache equality, enforcing HFS name length behavior and comparing folded bytes. The functions are exported for KUnit visibility.

State and persistence: no on-disk state is written. The comparison order determines catalog B-tree key ordering and dentry cache behavior, so it indirectly controls persistent catalog record placement and lookup correctness.

Dependencies and integration: used by `hfs_cat_keycmp()` and installed as dentry operations through `hfs_dentry_operations` in `sysdep.c`. Name conversion to/from disk encoding is handled separately in `trans.c`.

Risks and test signals: any mismatch between hashing and comparison can cause negative dentry aliasing or lookup misses. Truncation at `HFS_NAMELEN` is a compatibility edge. Tests should include case-equivalent names, punctuation/space ordering, high-bit Mac characters, exactly/over-limit lengths, and catalog lookup order.
