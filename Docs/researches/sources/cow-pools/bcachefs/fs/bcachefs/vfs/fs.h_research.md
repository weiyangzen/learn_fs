# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fs.h

Defines the bcachefs VFS inode wrapper and the public VFS-layer inode helpers used by namespace, I/O, ioctl, pagecache, quota, and lifecycle code.

Key declarations:
- `struct bch_inode_info` embeds `struct inode` and adds bcachefs identity, hash nodes, list membership, flags, update/quota/pagecache locks, quota reservation state, qid, devices needing nocow flush, cached unpacked inode, and delayed writeback work.
- Pagecache locking helpers expose two-state lock modes: add-pagecache users (`bch2_pagecache_add_*`) and block-pagecache users (`bch2_pagecache_block_*`).
- `bch2_lock_inodes()` / `bch2_unlock_inodes()` sort inode pointers and acquire requested update/pagecache locks in stable order.
- `inode_attr_changing()` / `inode_attrs_changing()` detect inherited inode option changes, especially for project quota inheritance.
- Public entry points include inode creation, lookup/import, inode writeback/update, quota transfer, setattr, unlink, subvolume inode eviction, fiemap, and VFS init/exit.

Core mechanics:
- `inode_inum()` returns the bcachefs `(subvol, inum)` identity cached in `ei_inum`.
- `to_bch_ei()` and `file_bch_inode()` provide container conversions from VFS inode/file to bcachefs inode wrapper.
- `bch2_set_projid()` is a small project-id helper over `bch2_fs_quota_transfer()`, updating `QTYP_PRJ`.
- `bch2_dirty_inode()` queues delayed VFS writeback work when the mount has a nonzero writeback timeout.

Important invariants:
- `EI_INODE_ERROR` means VFS and btree inode state may no longer be consistent after an error.
- `EI_INODE_SNAPSHOT` marks snapshot-subvolume inodes where quota accounting is skipped.
- `EI_INODE_HASHED` protects inode hash-table membership and is tested under the VFS inode lock.
- Multi-inode lock macros intentionally de-duplicate equal inode pointers after sorting.

Filesystem relevance:
- This header defines the state that lets bcachefs pair Linux VFS inode semantics with transactional btree inode metadata and per-folio allocation state.

Notable risks:
- `ei_devs_need_flush` tracks nocow flush needs coarsely by device mask; comments note that per-device flush sequence tracking would be more precise.
