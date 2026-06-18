# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_iext_tree.c

Purpose: Implements the in-core extent tree used by `struct xfs_ifork` when inode data, attr, or CoW forks are represented as decoded `xfs_bmbt_irec` records. It stores compact 16-byte records in a small B-tree with linked leaves, optimized for fast cursor walking and sequential append.

Important APIs and types: private `struct xfs_iext_rec`, `struct xfs_iext_node`, and `struct xfs_iext_leaf`; exported operations include `xfs_iext_count`, cursor movement (`xfs_iext_first`, `xfs_iext_last`, `xfs_iext_next`, `xfs_iext_prev`), lookup (`xfs_iext_lookup_extent`, `xfs_iext_lookup_extent_before`, `xfs_iext_get_extent`), mutation (`xfs_iext_insert_raw`, `xfs_iext_insert`, `xfs_iext_remove`, `xfs_iext_update_extent`), and destruction (`xfs_iext_destroy`).

Control flow: extent records are packed/unpacked by `xfs_iext_set` and `xfs_iext_get`. Inserts allocate a root for the first extent, grow the root allocation while height is one, split full leaves, and propagate new separator keys upward with `xfs_iext_insert_node`. Removals shift records out of a leaf, update parent keys when the first record changes, merge underfull leaves or inner nodes when possible, and shrink the root when only one child remains. Lookup descends by file offset to a leaf, then searches records and may advance to the next leaf for hole lookups.

State and persistence: this is purely in-memory state derived from on-disk bmbt records. `if_bytes`, `if_height`, and `if_data` describe the tree. `if_seq` is incremented with `WRITE_ONCE` before mutations so writeback/COW users can detect fork changes. Persistence occurs elsewhere when fork extents are flushed back to disk.

Dependencies and integration: relies on XFS bmap record limits from `xfs_format.h`, inode fork state from `xfs_inode.h`, allocation via kernel memory APIs, and tracepoints. It is consumed heavily by inode fork formatting/flushing and bmap code.

Risks and test signals: high risk areas are separator-key maintenance, leaf merge cursor repair, empty-record detection via `hi == 0`, and overflow assumptions in packed bit fields. Useful tests include bmap fuzzing with many insert/remove/update sequences, sequential append and middle insertion workloads, debug assertions, fsstress with reflink/COW, and mount/recovery after extent-heavy operations.
