# sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.h

## Purpose

`delayed-ref.h` defines the Btrfs delayed reference data model and API used by transaction, extent-tree, qgroup, and backref code. It describes delayed ref actions, data and metadata ref identities, per-extent ref heads, the delayed-ref root, generic caller-facing ref descriptors, reservation helpers, and processing/lookup functions.

## Important APIs, Types, and Functions

Important types are `enum btrfs_delayed_ref_action`, `struct btrfs_data_ref`, `struct btrfs_tree_ref`, `struct btrfs_delayed_ref_node`, `struct btrfs_delayed_extent_op`, `struct btrfs_delayed_ref_head`, `struct btrfs_delayed_ref_root`, `enum btrfs_ref_type`, and `struct btrfs_ref`. Inline helpers include delayed ref byte calculations, delayed extent op allocation/free, delayed ref/head put helpers, space flag derivation, owner/offset extraction, and `btrfs_ref_type()`.

The header declares initialization/exit, tree/data ref initialization, delayed tree/data ref add, delayed extent op add, merge/select/delete/lookup helpers, delayed refs reservation helpers, space checks, tree-ref existence lookup, and transaction abort destruction.

## Control Flow

The header has inline allocation, release, and classification helpers, but no major runtime algorithm. The exported API separates caller-side generic refs from transaction-internal delayed ref nodes and heads. Callers initialize a `struct btrfs_ref`, fill data/tree-specific details, then queue it through the C implementation.

## State and Persistence Behavior

All state described here is transaction-local memory until delayed refs are processed. `btrfs_delayed_ref_head` aggregates ref count deltas and extent operation metadata for one bytenr. `btrfs_delayed_ref_root` tracks all heads and dirty qgroup extents in xarrays plus counters protected by its spinlock. Persistent extent-tree, checksum-tree, and qgroup effects are deferred.

## Dependencies and Integration Points

The header depends on Linux refcounts, lists, rbtrees, mutexes, spinlocks, slabs, UAPI Btrfs tree constants, and Btrfs fs/message types. It integrates with extent-tree code that consumes refs, transaction code that owns the delayed-ref root, qgroup tracing, free-space-tree reservation sizing, and tree-mod-log/backref lookup.

## Risks and Edge Cases

The structures have explicit lock ownership expectations that are not enforced by the type system. The same delayed ref action enum is used for additions, drops, extent insertion accounting, and head-only updates. `btrfs_delayed_ref_owner()` returns an inode for data refs but a tree level for metadata refs, so generic callers must understand the context. Reservation helper sizing doubles for free-space-tree updates, making mount-option state part of accounting behavior.

## Test Signals

Compile coverage should include qgroup, free-space-tree, and debug builds. Runtime tests should validate delayed ref selection order, qgroup dirty extent tracking, metadata versus data ref type selection, head lookup/removal, delayed extent op merging, and abort cleanup under allocation failures.
