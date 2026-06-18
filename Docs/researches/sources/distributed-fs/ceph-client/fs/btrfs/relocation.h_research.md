# sources/distributed-fs/ceph-client/fs/btrfs/relocation.h

## Purpose
`relocation.h` declares the public Btrfs relocation interface used outside `relocation.c`. It exposes block-group relocation, relocation-root lookup/update hooks, recovery, data checksum cloning, COW integration, snapshot integration, remap-tree translation/removal, and the eligibility helper for remap-tree relocation.

## Important APIs, Types, and Functions
The inline helper `should_relocate_using_remap_tree` returns true only when the filesystem has the `REMAP_TREE` incompat feature and the target block group is neither system space nor metadata-remap space. Its callers use it to choose the remap-tree path instead of classic relocation.

Primary declarations include `btrfs_relocate_block_group`, `btrfs_recover_relocation`, `btrfs_init_reloc_root`, `btrfs_update_reloc_root`, `find_reloc_root`, `btrfs_should_ignore_reloc_root`, `btrfs_reloc_cow_block`, `btrfs_reloc_clone_csums`, `btrfs_reloc_pre_snapshot`, `btrfs_reloc_post_snapshot`, `btrfs_should_cancel_balance`, `btrfs_get_reloc_bg_bytenr`, `btrfs_translate_remap`, `btrfs_remove_extent_from_remap_tree`, and `btrfs_last_identity_remap_gone`.

The header forward-declares common Btrfs structures used by pointer prototypes, while the inline helper requires the including translation unit to already know `struct btrfs_block_group` fields and relocation feature constants.

## Control Flow
Callers enter relocation through `btrfs_relocate_block_group`. Transaction/COW code calls `btrfs_init_reloc_root` when a shareable root is recorded in a transaction during relocation and `btrfs_update_reloc_root` when committing root item updates. COW of tree blocks calls `btrfs_reloc_cow_block` so relocation can connect newly COWed blocks into its backref cache and optionally rewrite data pointers in leaves. Snapshot creation calls the pre/post hooks to reserve merge metadata and create relocation roots for newly created snapshots. Mount or recovery paths call `btrfs_recover_relocation` to resume interrupted merges. Remap-tree users call `btrfs_translate_remap` to resolve logical ranges and `btrfs_remove_extent_from_remap_tree` when extents are removed from remapped block groups.

## State and Persistence
The header itself stores no state. Its API controls persistent relocation state in the root tree, remap tree, chunk tree, block-group items, orphan relocation inodes, and transaction metadata. The exported functions also coordinate in-memory state under `fs_info->reloc_ctl`, root `reloc_root` pointers, relocation cancellation atomics, and block-group remap flags.

## Dependencies and Integration Points
`relocation.h` is included by core Btrfs modules that need relocation hooks: transaction/root code, COW/block code, snapshot creation, checksum/ordered extent handling, balance/device management, and remap-tree read or extent-removal paths. It depends on Linux integer types and Btrfs declarations/macros available from surrounding headers.

## Risks and Edge Cases
Because `should_relocate_using_remap_tree` dereferences `bg`, include ordering matters for any file using the inline. The remap-tree eligibility check must remain aligned with the implementation; allowing system or metadata-remap block groups into remap relocation would bypass assumptions in chunk and metadata handling. The prototypes expose functions that are valid only under specific locks or transaction contexts, especially `btrfs_get_reloc_bg_bytenr` requiring `reloc_mutex`, root update hooks requiring a transaction, and remap removal requiring a caller-supplied writable path.

## Test Signals
Compile coverage should include every translation unit that includes this header with `REMAP_TREE` enabled and disabled. Behavioral tests should confirm remap-tree eligibility for data block groups only, classic fallback for system and metadata-remap groups, COW hook invocation during relocation, snapshot hook behavior during merge, mount recovery of reloc roots, and remap translation/removal on remapped chunks.
