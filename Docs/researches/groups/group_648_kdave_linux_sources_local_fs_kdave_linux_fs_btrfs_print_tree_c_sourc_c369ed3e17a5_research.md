# Group Research: group_648_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_print_tree_c_sourc_c369ed3e17a5

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/kdave-linux` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/print-tree.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/print-tree.c

## Purpose

Diagnostic Btrfs tree printer for kernel logs. It formats root names, key types, leaves, internal nodes, and selected item payloads so developers can inspect B-tree metadata during debugging.

## Main Interfaces

- `btrfs_root_name(const struct btrfs_key *key, char *buf)`: returns a symbolic root name for known root objectids, formats tree reloc roots with offset, otherwise returns numeric objectid text.
- `btrfs_print_leaf(const struct extent_buffer *l)`: logs a leaf header and each item’s key, offset, size, and type-specific payload.
- `btrfs_print_tree(const struct extent_buffer *c, bool follow)`: logs an internal node or leaf. If `follow` is true, recursively reads and prints children.

## Internal Behavior

- Maintains `root_map[]` for well-known roots including root, extent, chunk, device, checksum, quota, UUID, free-space, block-group, raid-stripe, and remap trees.
- `key_type_string()` maps Btrfs item key types to readable labels, including newer entries such as:
  - `BTRFS_EXTENT_OWNER_REF_KEY`
  - `BTRFS_RAID_STRIPE_KEY`
  - `BTRFS_REMAP_KEY`
  - `BTRFS_REMAP_BACKREF_KEY`
- Leaf printing handles many item classes:
  - inode items and timestamps
  - inode refs and extrefs
  - dir items, dir indexes, xattrs
  - root items
  - extent and metadata items with inline refs
  - file extents, including inline extents
  - block group, chunk, device, and device extent items
  - UUID items
  - raid stripe items
  - remap items
- Extent item printing validates minimum item size, prints tree block info when present, iterates inline refs, and warns about misaligned shared parents.
- Simple quota owner refs are printed through `print_extent_owner_ref()` and assert the `SIMPLE_QUOTA` incompat feature.
- `print_eb_refs_lock()` logs extent-buffer reference and lock-owner state only under `CONFIG_BTRFS_DEBUG`.
- Recursive tree following uses `read_tree_block()` with `btrfs_tree_parent_check` populated from the parent pointer generation, owner root, and first key.

## Dependencies

Uses Btrfs accessor helpers and tree structures from `ctree.h`, `accessors.h`, `file-item.h`, `tree-checker.h`, `volumes.h`, and `raid-stripe-tree.h`.

## Error Handling and Safety Notes

- Null extent buffers are ignored.
- Unexpected extent item sizes are logged and skipped.
- UUID item sizes must be aligned to `sizeof(u64)`.
- Recursive tree traversal uses `BUG()` if a child has an impossible level relationship after read.
- Unknown item key types are still printed as `UNKNOWN.<type>`.

## Role in the System

This file is not part of normal filesystem semantics; it is a debugging aid used to inspect on-disk metadata in kernel logs.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/print-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/print-tree.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/print-tree.h

## Purpose

Public declarations for Btrfs tree-printing diagnostics.

## Exports

- `BTRFS_ROOT_NAME_BUF_LEN`: fixed buffer length for formatted root names, including tree relocation offset text.
- `btrfs_print_leaf(const struct extent_buffer *l)`
- `btrfs_print_tree(const struct extent_buffer *c, bool follow)`
- `btrfs_root_name(const struct btrfs_key *key, char *buf)`

## Dependencies

Forward declares `struct extent_buffer` and `struct btrfs_key`, and includes Linux type definitions.

## Role in the System

Allows other Btrfs code to invoke tree/leaf debug dumping without exposing implementation details from `print-tree.c`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/print-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/props.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/props.c

## Purpose

Implements Btrfs inode property handling backed by Btrfs xattrs. The current property table supports `btrfs.compression`.

## Core Structures

- `struct prop_handler`: handler record for a property:
  - xattr name
  - validation callback
  - apply callback
  - extraction callback for inheritance
  - ignore callback
  - inheritable flag
- `prop_handlers_ht`: hash table keyed by `btrfs_name_hash()` of the xattr name.

## Main Interfaces

- `btrfs_props_init()`: registers property handlers in the hash table.
- `btrfs_validate_prop()`: validates a property name and optional value.
- `btrfs_ignore_prop()`: asks the handler whether the property should be skipped for an inode.
- `btrfs_set_prop()`: writes/removes the xattr and applies the in-memory inode state.
- `btrfs_load_inode_props()`: scans an inode’s xattr items and applies known Btrfs properties.
- `btrfs_inode_inherit_props()`: propagates inheritable properties from parent to new inode.

## Property Scanning

`iterate_object_props()` walks `BTRFS_XATTR_ITEM_KEY` items for an objectid, filters for `XATTR_BTRFS_PREFIX`, matches registered handlers, reads values from the leaf into temporary buffers, and invokes a supplied iterator callback.

## Compression Property

The only registered handler is `btrfs.compression`.

Validation:
- Rejects inodes that cannot be compressed.
- Accepts valid compression strings from `btrfs_compress_is_valid_type()`.
- Also accepts `no` and `none`.

Apply behavior:
- Empty value clears compression and no-compression flags.
- `no` or `none` sets `BTRFS_INODE_NOCOMPRESS`.
- `lzo`, `zlib`, and `zstd` set `BTRFS_INODE_COMPRESS` and `inode->prop_compress`.
- LZO and ZSTD set corresponding filesystem incompat feature bits.

Ignore behavior:
- Compression xattr is ignored for non-regular-file and non-directory inodes.

Inheritance:
- Only inheritable handlers are considered.
- Parent value is extracted from in-memory inode state.
- The child is validated before xattr insertion.
- The code assumes one currently supported property for reservation purposes, with a note that more properties would require revisiting metadata reservation.

## Error Handling

- Unknown or malformed property names return `-EINVAL`.
- Allocation failures while scanning xattrs return `-ENOMEM`.
- If applying a just-written xattr fails, `btrfs_set_prop()` removes the xattr again.
- Load-time apply failures are warned but do not abort the whole load.

## Role in the System

This file bridges persistent Btrfs property xattrs and runtime inode flags, especially for compression policy and inheritance.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/props.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/props.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/props.h

## Purpose

Header for Btrfs property operations.

## Exports

- `btrfs_props_init()`
- `btrfs_set_prop()`
- `btrfs_validate_prop()`
- `btrfs_ignore_prop()`
- `btrfs_load_inode_props()`
- `btrfs_inode_inherit_props()`

## Dependencies

Forward declares Btrfs inode, path, and transaction-handle types. Includes Linux type and compiler-type headers.

## Role in the System

Provides the property subsystem API used by xattr/inode creation paths without exposing the internal handler table.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/props.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/qgroup.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/qgroup.c

## Purpose

Implements Btrfs quota groups, including full qgroup accounting, simple quotas, reservation tracking, qgroup relations, qgroup rescan, snapshot inheritance, delayed extent tracing, and balance subtree-swap accounting.

## Modes

- `BTRFS_QGROUP_MODE_DISABLED`: quotas off.
- `BTRFS_QGROUP_MODE_FULL`: classic qgroups with referenced/exclusive accounting from backrefs.
- `BTRFS_QGROUP_MODE_SIMPLE`: simple quota mode using owner-generation deltas and no full rescan worker.

Mode helpers:
- `btrfs_qgroup_mode()`
- `btrfs_qgroup_enabled()`
- `btrfs_qgroup_full_accounting()`

## In-Memory Model

Qgroups are stored in `fs_info->qgroup_tree` by qgroup id. Relations are stored as `struct btrfs_qgroup_list` links:
- `groups`: parents a qgroup belongs to.
- `members`: children of a parent qgroup.
- `dirty`: qgroups needing on-disk info/limit updates.
- iterator lists support breadth-style parent traversal during accounting.

Reservation categories:
- data
- metadata per-transaction
- metadata preallocation

Reservation helpers add/release per-type byte counts and propagate changes through parent qgroups.

## Config Load and Free

`btrfs_read_qgroup_config()` reads the quota tree during mount:
- Reads status, qgroup info, and limit items.
- Builds qgroup rb-tree entries.
- Reads relation items in a second pass.
- Sets quota enabled state and resumes pending rescans.
- Marks full qgroups inconsistent on generation/config mismatch.
- Reads simple quota enable generation when `SIMPLE_QUOTA` is active.

`btrfs_free_qgroup_config()` removes sysfs entries and frees qgroups/relations.

`btrfs_check_quota_leak()` reports unreleased reservation values at unmount.

## Enable and Disable

`btrfs_quota_enable()`:
- Requires `subvol_sem` write lock.
- Rejects extent tree v2.
- Creates quota tree and status item.
- Creates qgroup info/limit items for existing subvolumes and fs tree.
- Supports simple quota enable, setting `SIMPLE_QUOTA`, `qgroup_enable_gen`, and `BTRFS_FS_SQUOTA_ENABLING`.
- For full qgroups, marks initial state inconsistent and queues a rescan.

`btrfs_quota_disable()`:
- Requires `subvol_sem` write lock and `cleaner_mutex`.
- Stops rescan, flushes delayed allocation/ordered extents, commits outstanding reservations, removes quota root, clears mode flags, frees config, and commits.

## Qgroup CRUD and Relations

- `btrfs_create_qgroup()`: creates on-disk info/limit items, adds rb-tree and sysfs entry.
- `btrfs_remove_qgroup()`: verifies the qgroup can be deleted, removes relation/item state, warns on nonzero counters or reservations, removes sysfs entry.
- `btrfs_add_qgroup_relation()`: creates bidirectional relation items and in-memory link.
- `btrfs_del_qgroup_relation()`: removes bidirectional relation items and in-memory link.
- `btrfs_limit_qgroup()`: updates limit fields, with `-1` meaning clear the selected limit.

Fast relation accounting is attempted when a child has only exclusive references. Otherwise full qgroups are marked inconsistent.

Simple quota parent usage is checked by summing member usage and warning on mismatch.

## Dirty Extent Tracing and Full Accounting

Full qgroups account by tracing extents whose ownership/reference set changes.

Key entry points:
- `btrfs_qgroup_trace_extent_nolock()`: stores a dirty extent record in the delayed-ref xarray.
- `btrfs_qgroup_trace_extent_post()`: after lock release, finds old roots from commit roots.
- `btrfs_qgroup_trace_extent()`: allocates and inserts the record, then does post-processing.
- `btrfs_qgroup_trace_leaf_items()`: traces file extents referenced from a leaf.
- `btrfs_qgroup_account_extents()`: at transaction commit, finds new roots for each dirty extent and updates qgroups.
- `btrfs_qgroup_account_extent()`: updates rfer/excl counters from old/new root sets.

Accounting logic:
- `qgroup_update_refcnt()` walks root qgroups and parents to accumulate old/new reference counts.
- `qgroup_update_counters()` adjusts referenced and exclusive counters based on transitions between no refs, shared refs, and exclusive refs.
- Non-filesystem roots are ignored by `maybe_fs_roots()`.
- `qgroup_to_skip` can remove a root from old/new root sets before accounting.

## Subtree and Balance Swap Handling

Subtree tracing is used for snapshot deletion and relocation/balance cases:
- `btrfs_qgroup_trace_subtree()` walks a subtree, traces metadata blocks and file extents, and may mark qgroups inconsistent if the subtree level exceeds the configured threshold.
- `qgroup_trace_subtree_swap()` and helpers compare old/new swapped subtrees and trace corresponding blocks.
- `btrfs_qgroup_add_swapped_blocks()` records delayed subtree-swap accounting entries during relocation.
- `btrfs_qgroup_trace_subtree_after_cow()` detects COW of a swapped subtree root and performs deferred accounting.
- `btrfs_qgroup_clean_swapped_blocks()` drops deferred records at transaction commit.

This is an optimization for balance: if swapped subtrees remain structurally unchanged, the expensive scan can be skipped.

## Snapshot/Subvolume Inheritance

- `btrfs_qgroup_check_inherit()` validates inherit structures and rejects legacy ref/excl copy modes.
- `btrfs_qgroup_inherit()` creates the destination qgroup, applies inherited limits/relations, copies source accounting for snapshots in full mode, and may mark qgroups inconsistent if a rescan is required.
- Simple quota mode can auto-inherit parent qgroups from the inode root with `qgroup_auto_inherit()`.
- `qgroup_snapshot_quick_inherit()` can avoid rescan for a narrow full-qgroup case where parent ownership remains exclusive.

## Reservations

Data reservation:
- `btrfs_qgroup_reserve_data()` marks inode io_tree ranges with `EXTENT_QGROUP_RESERVED` and reserves quota bytes.
- On `-EDQUOT`, it tries flushing delalloc, ordered extents, delayed iputs, and a transaction commit, then retries.
- `btrfs_qgroup_release_data()` clears io_tree reservation bits after data reaches disk but does not free qgroup reservation bytes.
- `btrfs_qgroup_free_data()` clears bits and frees reservation bytes.

Metadata reservation:
- `btrfs_qgroup_reserve_meta_prealloc()`
- `btrfs_qgroup_free_meta_prealloc()`
- `btrfs_qgroup_convert_reserved_meta()`
- `btrfs_qgroup_free_meta_all_pertrans()`

Root-local metadata reservation counters prevent underflow when quotas are toggled around outstanding reservations.

`btrfs_qgroup_check_reserved_leak()` detects and frees leaked inode data reservations at inode destruction.

## Rescan

Full qgroup rescan:
- `btrfs_qgroup_rescan()` initializes rescan, commits current transaction, zeroes existing counters, and queues worker.
- `btrfs_qgroup_rescan_worker()` scans extent tree leaves through commit roots and accounts each extent.
- `qgroup_rescan_leaf()` clones a leaf under the rescan lock, then performs backref walking outside the lock.
- Rescan stops on filesystem closing, remounting, quota disable, or cancel flag.
- Completion can be waited through `btrfs_qgroup_wait_for_completion()`.
- `btrfs_qgroup_rescan_resume()` queues pending mount-time rescan.

Simple quota mode rejects rescan initialization.

## Simple Quota Deltas

`btrfs_record_squota_delta()` handles simple quota accounting:
- Ignores non-fs trees.
- Ignores extents older than `qgroup_enable_gen`.
- Updates level-0 qgroup and parent qgroups directly.
- Assumes simple quota `excl == rfer`.
- Warns and clamps on underflow.

## Error Handling and Consistency

`qgroup_mark_inconsistent()` marks full qgroups inconsistent, cancels rescan, and disables accounting through runtime flags. It is intentionally a no-op for simple quota mode.

Common consistency triggers:
- quota status generation mismatch
- qgroup config inconsistencies
- xarray insertion failure
- backref walk/accounting failure
- qgroup item update errors
- subtree threshold exceeded
- impossible/mismatched swapped-block records

## Role in the System

This is the central implementation of Btrfs quota behavior. It ties together on-disk quota-tree metadata, transaction commit accounting, delayed refs, backref walking, reservation enforcement, snapshot inheritance, sysfs qgroup visibility, and simple quota updates.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/qgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/qgroup.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/qgroup.h

## Purpose

Defines Btrfs qgroup data structures, mode enums, reservation types, runtime flags, and public quota-group APIs.

## Conceptual Model

The header documents qgroups as three main systems:
- Reserve: pre-charge data/metadata space and enforce limits.
- Trace: record dirty extents whose ownership/reference state may change.
- Account: update qgroup counters, usually during rescan or transaction commit.

It also documents the balance subtree-swap optimization, where swapped subtrees are recorded and only fully traced later if COW modifies a swapped subtree before transaction commit.

## Key Definitions

Runtime-only status flags:
- `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN`
- `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING`

Reservation types:
- `BTRFS_QGROUP_RSV_DATA`
- `BTRFS_QGROUP_RSV_META_PERTRANS`
- `BTRFS_QGROUP_RSV_META_PREALLOC`

Modes:
- disabled
- full
- simple

Main structs:
- `btrfs_qgroup_extent_record`: dirty extent record, including length, optional data reservation to free at commit, refroot, and old roots.
- `btrfs_qgroup_swapped_block`: delayed subtree-swap record used by relocation/balance.
- `btrfs_qgroup_rsv`: per-type reserved byte counters.
- `btrfs_qgroup`: qgroup counters, limits, reservations, relation lists, iterator nodes, rb-tree node, temp ref counts, and sysfs kobject.
- `btrfs_qgroup_list`: parent/member relation glue.
- `btrfs_squota_delta`: simple quota delta event.

## Public APIs

The header exposes:
- mode helpers
- quota enable/disable/rescan/wait/resume
- qgroup relation create/delete
- qgroup create/remove/limit
- dropped subvolume cleanup
- config read/free
- dirty extent trace/account functions
- snapshot inheritance validation/application
- reservation APIs for data and metadata
- swapped-block lifecycle and delayed subtree accounting
- simple quota delta recording
- sanity-test count verification under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`

## Role in the System

This is the public contract for quota code used across Btrfs transaction, inode, extent, relocation, and ioctl paths.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/qgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.c

## Purpose

Implements the Btrfs RAID stripe tree, which maps logical data ranges to per-device physical stripe locations for supported RAID profiles.

## Main Interfaces

- `btrfs_delete_raid_extent(struct btrfs_trans_handle *trans, u64 start, u64 length)`: removes or trims RAID stripe extents overlapping a logical range.
- `btrfs_insert_one_raid_extent(struct btrfs_trans_handle *trans, struct btrfs_io_context *bioc)`: creates one RAID stripe extent item from an IO context.
- `btrfs_insert_raid_extent(struct btrfs_trans_handle *trans, struct btrfs_ordered_extent *ordered_extent)`: inserts all stripe extents attached to an ordered extent and releases their `bioc` references.
- `btrfs_get_raid_extent_offset(...)`: resolves a logical address to a device physical address using the stripe tree.

## Delete Logic

`btrfs_delete_raid_extent()` handles overlap cases carefully:
- No stripe tree feature or no stripe root: no-op.
- Non-testing mode checks the chunk map and skips profiles that do not need stripe tree updates.
- Searches by `objectid=start`, `offset=(u64)-1`, then backs up one slot to find the relevant item.
- Handles:
  - complete item deletion
  - truncating left side
  - truncating right side with physical offset adjustment
  - punching a middle hole by duplicating the item for the right range and truncating the left range
  - ranges spanning multiple stripe extents

`btrfs_partially_delete_raid_extent()` deletes the old item and reinserts a trimmed copy, adjusting each stride’s physical address by `frontpad`.

## Insert Logic

`btrfs_insert_one_raid_extent()`:
- Allocates a variable-sized `btrfs_stripe_extent` based on profile factor.
- Copies devid and physical offsets from `bioc->stripes[]`.
- Inserts key `(logical, BTRFS_RAID_STRIPE_KEY, size)`.
- If the item already exists, overwrites it via `update_raid_extent_item()`.
- Aborts the transaction on insertion/update failures.

`btrfs_insert_raid_extent()` processes all `bioc` records linked to an ordered extent and releases them afterward.

## Lookup Logic

`btrfs_get_raid_extent_offset()`:
- Searches the stripe tree for the stripe extent containing `logical`.
- Supports commit-root lookup through `stripe->rst_search_commit_root`.
- Reduces `*length` if the requested range crosses a stripe extent boundary, forcing higher layers to split the bio.
- Finds the stride matching the requested device id.
- For DUP profiles, also matches the requested stripe index.
- Returns `-ENODATA` when no suitable stripe mapping exists.

## Dependencies

Uses Btrfs tree search/update helpers, transaction APIs, chunk maps, ordered extent IO contexts, tracepoints, and `raid-stripe-tree.h`.

## Error Handling

- Allocation failures return `-ENOMEM`.
- Missing chunk map returns `-EINVAL`.
- Missing stripe mapping returns `-ENODATA`.
- Insert/update failures abort the transaction where appropriate.
- Lookup logs debug diagnostics except for expected commit-root/EIO cases.

## Role in the System

This file maintains the persistent logical-to-physical stripe mapping required by the RAID stripe tree incompat feature for supported data block group profiles.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.h

## Purpose

Header for RAID stripe tree helpers and supported-profile checks.

## Key Definitions

`BTRFS_RST_SUPP_BLOCK_GROUP_MASK` includes supported data profiles:
- DUP
- RAID1 variants
- RAID0
- RAID10

## Exports

- `btrfs_delete_raid_extent()`
- `btrfs_get_raid_extent_offset()`
- `btrfs_insert_raid_extent()`
- `btrfs_insert_one_raid_extent()` under sanity-test builds

## Inline Helpers

- `btrfs_need_stripe_tree_update(fs_info, map_type)`:
  - Requires `RAID_STRIPE_TREE` incompat feature.
  - Only applies to data block groups.
  - Returns true for supported profiles in `BTRFS_RST_SUPP_BLOCK_GROUP_MASK`.
- `btrfs_num_raid_stripes(item_size)`:
  - Derives stride count from item size divided by `sizeof(struct btrfs_raid_stride)`.

## Role in the System

Provides the small public API and profile gating used by write, delete, and logical-to-physical mapping paths for the RAID stripe tree feature.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.h -->