# sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.c

Purpose: maintains the RAID stripe tree, which records logical data extents and their per-stripe device/physical locations for supported RAID profiles. It supports insert/update on write completion, deletion/truncation on extent removal, and lookup during IO mapping.

Important APIs/types/functions: public functions are `btrfs_delete_raid_extent()`, `btrfs_insert_raid_extent()`, `btrfs_insert_one_raid_extent()` for tests and ordered-extent bioc insertion, and `btrfs_get_raid_extent_offset()`. Internal helpers partially delete an item by reinserting adjusted stride physical offsets and update an existing item after `-EEXIST`.

Control flow: deletion first skips unsupported filesystems or profiles, then searches for the stripe item overlapping the removal range. It handles four cases: hole punching inside one item, trimming the left side, trimming the right side, or deleting whole items while advancing through the range. Insertion builds a variable-sized `btrfs_stripe_extent` from each `btrfs_io_context`, inserts it by logical start/length, and updates existing entries when necessary. Lookup finds the containing stripe extent, shortens the caller length if the mapping crosses a recorded extent boundary, then selects the matching devid and DUP stripe index.

State and persistence: persistent state is `BTRFS_RAID_STRIPE_KEY` items in `fs_info->stripe_root`, keyed by logical start and length with an array of strides. Ordered extents temporarily own bioc list entries until insertion consumes and releases them.

Dependencies and integration: depends on the RAID stripe tree incompat bit, chunk maps/profile checks, ordered extents, volume mapping, B-tree item insertion/deletion/duplication, tracepoints, and committed-root lookup for some read paths.

Risks and test signals: range deletion is branch-heavy and sensitive to off-by-one length updates, leaf splits after duplicate item, and physical offset adjustments after front trimming. Lookup must handle logically contiguous but physically split extents by shortening length. Tests should cover full delete, left/right trim, middle punch, multi-item delete, duplicate insert update, unsupported profiles, DUP stripe-index selection, committed-root lookup, and missing stripe entries returning `-ENODATA`.
