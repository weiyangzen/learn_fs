# sources/distributed-fs/ceph-client/fs/btrfs/ordered-data.h

## Purpose
`ordered-data.h` defines the ordered-extent state model and public API used by Btrfs writeback, direct I/O, fsync, transaction commit, compression, and range-locking code. The source was read as a complete 232-line header.

## Important APIs, Types, and Functions
`struct btrfs_ordered_sum` stores checksum ranges and variable-length checksum bytes. The flag enum defines status bits (`IO_DONE`, `COMPLETE`, `IOERR`, `TRUNCATED`, `LOGGED`, `LOGGED_CSUM`, `PENDING`) plus mutually exclusive type bits (`REGULAR`, `NOCOW`, `PREALLOC`, `COMPRESSED`) and extra `ENCODED`/`DIRECT` bits. `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS` define valid masks.

`struct btrfs_ordered_extent` records file and disk offsets/lengths, compression, qgroup reservation, refcount, owning inode, checksum/log/root/work/bioc lists, rb-node, waitqueue, work items, and completion. `struct btrfs_file_extent` mirrors the file extent item details needed to allocate an ordered extent.

## Control Flow
The header has no standalone flow. It defines the state transitions used by `ordered-data.c`: allocate and insert, add checksum sums, mark I/O done or errored, queue finish work, remove from trees/lists, wait for completion, collect for logging, lock ranges with ordered extents flushed, and split a leading portion when needed.

## State and Persistence Behavior
The structures are in-memory records for pending on-disk file extent and checksum updates. They persist only until writeback completion metadata is inserted and the final reference is dropped. Flags encode both completion state and the kind of file extent that will be committed.

## Dependencies and Integration Points
It includes list/refcount/completion/rbtree/waitqueue primitives and Btrfs async work support. It forward-declares inode/root/fs/block-group/extent-state types and is consumed by writeback, compression, direct I/O, fsync/tree-log, transaction, and ordered-data implementation code.

## Risks and Edge Cases
Exactly one exclusive type flag must be set by callers. `ENCODED` must pair with `COMPRESSED`, while `DIRECT` must not pair with compressed/encoded. Mismanaging `log_list`, root list, or rb-node membership can leak references or let fsync miss pending extents. `qgroup_rsv` is declared as `int` while reservations are u64 in the implementation context, so value range assumptions should stay visible.

## Test Signals
Compile coverage catches flag and prototype drift. Runtime coverage comes from ordered-data tests for each flag combination, compressed/encoded/direct paths, fsync logging, checksum insertion, truncation, splitting, and transaction waits.
