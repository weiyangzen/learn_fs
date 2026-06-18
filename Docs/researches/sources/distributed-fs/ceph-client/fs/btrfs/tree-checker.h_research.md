# sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.h

## Purpose
`tree-checker.h` declares the Btrfs tree block validation interface and status vocabulary. It is the public boundary for code that reads or verifies Btrfs tree blocks, chunks, owners, and parent expectations.

## Important APIs, Types, And Functions
`struct btrfs_tree_parent_check` packages expected parent-derived facts for a tree block: owner root, expected transid, first key plus a `has_first_key` flag, and expected level. `enum btrfs_tree_block_status` distinguishes clean blocks from invalid item counts, parent keys, key ordering, levels, free-space data, offsets, block pointers, item payloads, owners, and missing WRITTEN flags.

`BTRFS_BLOCK_GROUP_VALID` defines the accepted block group type/profile/remap mask used by chunk validation. Declared functions include `__btrfs_check_leaf()`, `__btrfs_check_node()`, `btrfs_check_leaf()`, `btrfs_check_node()`, `btrfs_check_chunk_valid()`, `btrfs_check_eb_owner()`, and `btrfs_verify_level_key()`.

## Control Flow
Callers that need detailed status use the double-underscore leaf and node functions. Callers that only need errno semantics use `btrfs_check_leaf()` and `btrfs_check_node()`, which return zero or `-EUCLEAN`. Chunk validation can be called for both leaf chunk items and superblock system chunk arrays by passing an optional `extent_buffer`. Parent verification callers fill `btrfs_tree_parent_check` and call `btrfs_verify_level_key()` after reading a block.

## State And Persistence Behavior
The header itself has no state. It defines validation inputs that refer to persistent on-disk facts: root ownership, transid, level, first key, block group flags, and chunk geometry. The `owner_root`, `transid`, and `has_first_key` fields are explicitly skippable for cases such as backref walks where the parent context is incomplete.

## Dependencies And Integration Points
The header includes Linux types and the userspace Btrfs tree format header, then forward-declares `extent_buffer`, `btrfs_fs_info`, `btrfs_chunk`, and `btrfs_key`. It is consumed by disk read paths, tree navigation, backref/qgroup code, btrfs-progs shared code, and any subsystem that must validate chunks or extent-buffer ownership.

## Risks And Edge Cases
The status enum is part of a shared interface with btrfs-progs, so changes should preserve meaning for external users. Parent checks are deliberately optional in several fields; forcing them on incomplete contexts would break valid backref and root-read paths. The block group valid mask must stay aligned with new on-disk block group flags.

## Test Signals
The header enables compile-time integration checks and defines the statuses that tests and callers can assert. Functional signals come from `tree-checker.c` returning detailed enum values or `-EUCLEAN` through this interface.
