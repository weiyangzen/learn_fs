# sources/distributed-fs/ceph-client/fs/btrfs/tree-checker.c

## Purpose
`tree-checker.c` validates Btrfs tree blocks after read and before higher-level code trusts their contents. It detects corrupt leaves, nodes, malformed item payloads, invalid owners, invalid chunk geometry, and parent/first-key mismatches. The goal is to centralize defensive validation so normal tree users can assume basic on-disk invariants.

## Important APIs, Types, And Functions
The main exported validators are `btrfs_check_leaf()`, `btrfs_check_node()`, `btrfs_check_chunk_valid()`, `btrfs_check_eb_owner()`, and `btrfs_verify_level_key()`. `__btrfs_check_leaf()` and `__btrfs_check_node()` return detailed `enum btrfs_tree_block_status` values for btrfs-progs and internal callers.

Static item validators include checks for file extents, checksum items, directory items, inode refs/extrefs, block group items, chunk items, device items and extents, inode items, root items, extent items and refs, RAID stripe extents, remap keys, and free-space tree items. Error reporters such as `generic_err()`, `file_extent_err()`, `dir_item_err()`, `block_group_err()`, `chunk_err()`, `dev_item_err()`, and `extent_err()` produce structured corruption messages and dump the first extent-buffer page.

## Control Flow
`__btrfs_check_leaf()` first verifies the block is level 0, has the WRITTEN flag, and is not an invalid empty critical tree. It then walks every slot in key order, checks key ordering, verifies item data offsets are packed backwards without holes or overlap, ensures item data stays inside the leaf and does not overlap item metadata, and dispatches by key type through `check_leaf_item()`.

`__btrfs_check_node()` verifies WRITTEN, internal level range, nritems bounds, nonzero and aligned child pointers, and increasing node keys. `btrfs_check_leaf()` and `btrfs_check_node()` convert any non-clean detailed status to `-EUCLEAN`.

`btrfs_check_chunk_valid()` is shared by leaf chunk items and superblock sys chunk array validation. It decodes either leaf-backed or stack-backed chunk fields, validates stripe counts against RAID profile, logical and length alignment, sector size, stripe length, length overflow, recognized type/profile flags, mixed group rules, remap feature gates, and RAID parity/copy constraints.

## State And Persistence Behavior
The checker does not persist state. It reads on-disk structures from `extent_buffer` memory and reports corruption through Btrfs logging. It uses `fs_info` for sectorsize, nodesize, csum size, feature flags, super generation, readonly state, and last committed transaction. Some validation is intentionally feature-gated, for example remap tree, extent tree v2, skinny metadata, simple quotas, mixed block groups, and RAID stripe tree.

## Dependencies And Integration Points
This file integrates with Btrfs accessors, on-disk format definitions, compression constants, volumes and RAID metadata, file/inode/dir item helpers, extent tree helpers, and error injection. It is invoked by disk IO and tree read paths before tree blocks are accepted. `btrfs_check_eb_owner()` supports callers that know the expected root owner, while `btrfs_verify_level_key()` validates parent-driven expectations after a block is read.

## Risks And Edge Cases
The leading risk is false positives: overly strict validation can prevent mounting valid historical filesystems. The file explicitly avoids checks when fields are unreliable or not yet initialized, such as superblock sys chunks without reliable `fs_info->sectorsize`, extent tree v2 global root counts during early mount, dummy fs selftests, tree log and relocation owner semantics, and live tree blocks newer than the last committed transaction. Validation must also avoid unsafe item reads by checking sizes and boundaries before dereferencing variable-length structures.

## Test Signals
Failures return `-EUCLEAN` or detailed `BTRFS_TREE_BLOCK_*` statuses and emit corruption logs naming root, block, slot, and decoded keys. Error injection is enabled for `btrfs_check_leaf()` and `btrfs_check_node()`. The checks provide strong regression signals for fuzzed images, malformed chunks, invalid free-space tree items, overlap in extent or checksum ranges, and feature-incompatible item types.
