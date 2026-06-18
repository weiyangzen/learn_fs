# sources/distributed-fs/ceph-client/fs/btrfs/delayed-inode.h

## Purpose

`delayed-inode.h` defines the in-memory data structures and public internal API for Btrfs delayed inode and delayed directory-index processing. It is the contract between directory operations, inode update paths, readdir, tree logging, transaction commit, delayed worker scheduling, and delayed node cleanup.

## Important APIs, Types, and Functions

Key types are `enum btrfs_delayed_item_type`, `struct btrfs_delayed_node`, and `struct btrfs_delayed_item`. A delayed node identifies an inode, owns insertion/deletion rbtrees, tracks pending item count, delayed inode item snapshot, reservation bytes, directory index counters, prepared/list membership flags, leaf-reservation counters, and optional debug ref trackers. A delayed item stores an index key offset, list nodes for tree/readdir/log use, reserved bytes, parent node pointer, refcount, insertion/deletion type, logged state, data length, and flexible item payload.

The header declares APIs for delayed dir index insert/delete/count, running delayed items, balancing, committing inode-specific delayed state, removing or killing delayed nodes, filling an inode from delayed state, delayed inode ref deletion, readdir integration, logging integration, init/exit, and debugging assertions. It also defines debug ref-tracker wrappers that compile to no-ops without `CONFIG_BTRFS_DEBUG`.

## Control Flow

There is little executable logic beyond debug inline helpers. The type layout shows the expected flow: callers create delayed nodes, queue insertion/deletion items under a mutex, global delayed-root lists expose nodes to commit/worker code, readdir and logging temporarily pin item references, and cleanup drops items plus reservations.

## State and Persistence Behavior

All structures are in-memory staging state. Durability is achieved only when implementation code flushes the delayed items into the Btrfs tree inside a transaction. The header highlights which fields are protected by node mutexes, delayed-root spinlocks, and refcounts, and which list nodes are used by specific consumers.

## Dependencies and Integration Points

Dependencies include Linux rbtrees, spinlocks, mutexes, lists, wait queues, VFS fs types, atomic/refcount/ref-tracker facilities, and Btrfs ctree types. Integration points are Btrfs directory item operations, inode item update/read paths, transaction commit, async delayed workers, readdir, fsync tree logging, root teardown, and debugging leak detection.

## Risks and Edge Cases

The same delayed item has several list nodes with different ownership rules; using the wrong list or failing to take a reference can cause use-after-free. The delayed node flags encode list membership, dirty inode state, and delayed inode-ref deletion, so they must remain synchronized with `count` and `delayed_root.items`. Debug ref tracker wrappers are conditional, so production builds rely only on normal refcounts.

## Test Signals

Compile tests should cover both debug and non-debug configurations. Runtime signals include no delayed-root leaks after unmount, correct readdir/logging behavior with pending delayed items, balanced item counters after insert/delete cancellation, and no refcount warnings under inode eviction and dead-root cleanup.
