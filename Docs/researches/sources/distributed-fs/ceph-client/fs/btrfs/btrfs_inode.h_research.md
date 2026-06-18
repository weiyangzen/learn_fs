# sources/distributed-fs/ceph-client/fs/btrfs/btrfs_inode.h

## Purpose
`btrfs_inode.h` defines the in-memory Btrfs inode extension and the public inode-level APIs used by lookup, directory operations, delalloc, checksumming, NOCOW, fsync logging, orphan cleanup, preallocation, encoded I/O, and inode lifecycle code. It embeds a VFS inode while adding Btrfs-specific roots, extent maps, range state, ordered extents, metadata reservation, logging generation state, compression/defrag properties, and accounting fields.

## Important APIs, types, and functions
- `BTRFS_DIR_START_INDEX` sets the first real directory index after `.` and `..`.
- The anonymous inode runtime flag enum includes fsync/delalloc/defrag/logging/verity/free-space/root-stub state such as `BTRFS_INODE_NEEDS_FULL_SYNC`, `BTRFS_INODE_NO_DELALLOC_FLUSH`, `BTRFS_INODE_FREE_SPACE_INODE`, and `BTRFS_INODE_ROOT_STUB`.
- `struct btrfs_inode` is the core inode container, embedding `struct inode vfs_inode` and Btrfs fields for root ownership, objectid handling, compression, locks, extent maps, range state, log state, delalloc/csum/defrag accounting, inode item flags, a per-inode `btrfs_block_rsv`, delayed nodes, delayed iput linkage, mmap locking, and VFS integration.
- `BTRFS_I()` converts `struct inode *` or `const struct inode *` to the containing Btrfs inode with type-preserving `_Generic`.
- Inline helpers cover inode hashing, inode number handling on 32-bit vs 64-bit systems, inode key construction, size/disk size updates, free-space/data inode tests, outstanding extent tracing, fsync generation state, full-sync marking, compression eligibility, lock assertions, mapping stable-write flags, and experimental folio order setup.
- Function declarations cover checksum calculation/verification, NOCOW checks, delalloc inode lists, lookup/link/unlink/subvolume deletion, truncate, delalloc start/set/clear/merge/split, new inode creation, inode allocation/destruction/drop, iget/get-extent/update/orphan cleanup, delayed iput, preallocation, writeback, encoded read/write, inode search, lock/unlock, inode byte accounting, range-clean assertions, allocation hints, and I/O extent map creation.

## Control flow
The header defines the state that inode implementation files operate on. Lookup/iget code allocates a `struct btrfs_inode`, initializes its root, objectid, VFS inode, extent map tree, range state, block reserve, and counters, then exposes it through the VFS inode. File writes mark delalloc ranges in `io_tree`, update `delalloc_bytes`/`new_delalloc_bytes`/`outstanding_extents`, possibly use the inode’s block reserve, and later run writeback through `btrfs_run_delalloc_range()`. Ordered extents are tracked in the inode’s ordered tree so completion can update metadata, checksums, and logged state.

Fsync and tree logging use `last_trans`, `logged_trans`, `last_sub_trans`, `last_log_commit`, `first_dir_index_to_log`, `last_dir_index_offset`, `last_unlink_trans`, and `last_reflink_trans` to decide whether a fast log is valid or a full inode sync is required. `btrfs_set_inode_last_sub_trans()` records writes after a prior fsync in the same transaction. `btrfs_set_inode_full_sync()` sets the full-sync bit and pessimistically updates reflink tracking while holding appropriate inode or mmap serialization.

Directory operations use `index_cnt`, `dir_index`, `BTRFS_DIR_START_INDEX`, link/unlink declarations, fscrypt names in `btrfs_new_inode_args`, and directory-specific logging offsets. Regular files instead use the union alternatives for delalloc, csum, defrag, reflink, and encoded I/O state. Special free-space inodes are identified by runtime flag and suppress normal outstanding-extent tracing.

## State and persistence behavior
Some fields mirror persisted inode item state: inode number/objectid, generation, `disk_i_size`, inode flags/ro_flags, creation time, and root ownership. Many fields are runtime-only caches or synchronization state: extent maps, `io_tree` state bits, optional `file_extent_tree` for accurate i_size updates when holes are explicit, ordered extent rb-tree, delayed inode list linkage, log mutex, runtime flags, delayed node pointer, delayed iput node, and mmap lock.

Counter fields are carefully protected. The main spinlock protects transaction/log generation counters, delalloc bytes, new delalloc bytes, defrag bytes, disk size, outstanding extents, csum bytes, and file private data setup. `log_mutex` protects directory logging fields. The VFS inode lock or `i_mmap_lock` is required for full-sync transitions and reflink-related state updates. The embedded `btrfs_block_rsv` persists only as in-memory reservation accounting tied to inode operations.

On 32-bit platforms, `struct inode::i_ino` cannot hold the full Btrfs objectid, so `struct btrfs_inode::objectid` stores it separately. Root stub inodes are an exception: `btrfs_ino()` returns the VFS inode number for stubs that represent inaccessible subvolume roots.

## Dependencies and integration points
The header depends on Linux VFS/MM/fscrypt/lockdep primitives, Btrfs tracepoints, `ctree.h`, block reserves, extent maps, and extent I/O trees. It is included by inode implementation, file I/O, tree-log, delayed inode, extent allocation, checksumming, ordered extent, ioctl/encoded I/O, and free-space cache code. It integrates Btrfs root/subvolume identity with the VFS inode model and provides the shared declarations other subsystems need to mutate inode metadata safely.

## Risks and test signals
Risks include stale or incorrectly locked fsync generation state causing missing log replay data, delalloc accounting mismatches leading to ENOSPC or incorrect stat blocks, 32-bit inode number truncation mistakes, root-stub confusion for subvolume snapshots, compression eligibility ignoring NODATACOW/NODATASUM, races between mmap writes and full-sync marking, and failure to clear or merge delalloc/extent state correctly.

Useful tests include fsync after buffered/direct/mmap writes, reflink and dedupe followed by fsync with checksums, directory unlink/relink logging, subvolume root-stub lookup cases, 32-bit build coverage, free-space inode behavior, verity enable serialization, qgroup/delalloc ENOSPC stress, encoded I/O, NOCOW extent checks, preallocation/truncate/contiguous expansion, delayed iput draining, and lockdep/KCSAN runs around inode lock, `i_mmap_lock`, `log_mutex`, and the inode spinlock.
