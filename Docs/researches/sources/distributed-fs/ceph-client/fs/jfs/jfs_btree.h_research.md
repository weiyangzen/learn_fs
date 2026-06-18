# sources/distributed-fs/ceph-client/fs/jfs/jfs_btree.h

## Purpose
Provides common B+tree flags, metapage/root access macros, dirty/release helpers, and traversal stack structures for JFS dtree and xtree code.

## Important APIs, types, and functions
Defines `BT_ROOT`, `BT_LEAF`, `BT_INTERNAL`, right/left-most flags, operation-order bits, `BT_IS_ROOT()`, `BT_PAGE()`, `BT_GETPAGE()`, `BT_MARK_DIRTY()`, `BT_PUTPAGE()`, `struct btframe`, `struct btstack`, and stack macros.

## Control flow
Dtree/xtree algorithms use these macros to fetch inline root pages or child metapages, track search paths to leaves, dirty the right backing store, and release non-root pages.

## State and persistence behavior
Traversal stack state is transient. Tree pages persist either inside the inode root or metapage-backed blocks.

## Dependencies and integration points
Depends on JFS inode-private roots, metapage cache, assert/printk diagnostics, and tree implementation files.

## Risks and test signals
Test deep directories/extents, root splits, deletes, insertions, root versus child dirtying, stack depth, and `read_metapage()` failures.
