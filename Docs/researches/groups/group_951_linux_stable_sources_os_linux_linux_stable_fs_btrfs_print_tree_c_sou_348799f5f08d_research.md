# Group Research: group_951_linux_stable_sources_os_linux_linux_stable_fs_btrfs_print_tree_c_sou_348799f5f08d

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/print-tree.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/print-tree.c

This file implements Btrfs diagnostic tree/leaf printing helpers. It does not mutate filesystem state; it formats in-memory `extent_buffer` contents into kernel log output with `pr_info()`, `pr_cont()`, `btrfs_info()`, warnings, and debug-only reference/lock details.

Main responsibilities:
- Map well-known root object IDs to readable names through `root_map[]` and `btrfs_root_name()`.
- Print B-tree leaves item-by-item via `btrfs_print_leaf()`.
- Print internal nodes and optionally recurse through children via `btrfs_print_tree()`.
- Decode common item payloads: inode items, directory items, inode refs/extrefs, file extents, checksums, roots, extents/backrefs, block groups, chunks, devices, UUID items, persistent/temporary items, RAID stripe tree items, and remap items.
- Convert item key types to readable strings through `key_type_string()`.

Important functions:
- `btrfs_root_name()` returns symbolic names for core roots like `ROOT_TREE`, `EXTENT_TREE`, `CHUNK_TREE`, `QUOTA_TREE`, `RAID_STRIPE_TREE`, etc.; relocation roots include the offset in the supplied buffer.
- `print_extent_item()` validates extent item size, prints refs/generation/flags, tree block info when present, then walks inline refs and formats each ref type. It warns about shared block/data parent offsets not aligned to sectorsize.
- `print_dir_item()`, `print_inode_ref_item()`, and `print_inode_extref_item()` iterate packed variable-length records inside one item.
- `print_file_extent_item()` distinguishes inline extents from regular/prealloc extents and prints disk bytenr, disk bytes, logical offset, logical bytes, ram bytes, generation, type, and compression.
- `print_raid_stripe_key()` prints each `btrfs_raid_stride` using `btrfs_num_raid_stripes()` from `raid-stripe-tree.h`.
- `btrfs_print_tree()` prints a node header and child keys. If `follow` is true, it reads each child with `read_tree_block()` and a `btrfs_tree_parent_check`, verifies the level relationship, recursively prints it, then frees the child buffer.

Key dependencies:
- Btrfs accessors and item layout definitions from `ctree.h`, `accessors.h`, `file-item.h`, `volumes.h`, and `raid-stripe-tree.h`.
- Tree block validation via `tree-checker.h`.
- Tree block reads via `disk-io.h`.

Notable invariants and edge handling:
- `btrfs_print_leaf()` returns immediately for a null buffer.
- `print_extent_item()` rejects extent items smaller than `struct btrfs_extent_item`.
- UUID items must be `u64` aligned in size.
- Unknown key types print as `UNKNOWN.<type>`.
- Recursive `btrfs_print_tree()` uses `BUG()` if child level relationships are inconsistent after a successful read.
- `print_eb_refs_lock()` only emits refcount/lock owner/current pid under `CONFIG_BTRFS_DEBUG`.

Role in the subsystem:
- This is a debug/inspection aid for Btrfs metadata. It centralizes readable formatting for tree dump paths used during diagnostics, corruption analysis, and development.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/print-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/print-tree.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/print-tree.h

This header exposes the Btrfs tree-printing helpers implemented in `print-tree.c`.

Public API:
- `void btrfs_print_leaf(const struct extent_buffer *l);`
- `void btrfs_print_tree(const struct extent_buffer *c, bool follow);`
- `const char *btrfs_root_name(const struct btrfs_key *key, char *buf);`

Definitions:
- `BTRFS_ROOT_NAME_BUF_LEN` is `48`, sized to hold a root name plus extra detail such as a relocation root offset.

Dependencies and declarations:
- Includes `<linux/types.h>`.
- Forward declares `struct extent_buffer` and `struct btrfs_key`.

Role in the subsystem:
- Provides a small diagnostic interface for tree/leaf logging and root-name stringification without exposing implementation details of the printing logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/print-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/props.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/props.c

This file implements Btrfs inode property handling backed by Btrfs xattrs. The current handler set contains one property, `btrfs.compression`, but the code is structured as a small extensible handler table.

Core structure:
- `struct prop_handler` defines:
  - xattr name
  - validation callback
  - apply callback
  - extract callback for inheritance
  - ignore callback
  - inheritable flag
- `prop_handlers_ht` is a hash table indexed by `btrfs_name_hash()` over the xattr name.
- `prop_handlers[]` currently registers `XATTR_BTRFS_PREFIX "compression"`.

Main public functions:
- `btrfs_props_init()` hashes and registers all property handlers at init time.
- `btrfs_validate_prop()` checks the xattr name has a valid Btrfs prefix, finds a handler, permits zero-length deletion, and otherwise calls the handler validator.
- `btrfs_ignore_prop()` asks the property handler whether this inode should ignore the property.
- `btrfs_set_prop()` writes or removes the backing xattr and applies the in-memory inode state. If applying a non-empty property fails after setting the xattr, it rolls the xattr back.
- `btrfs_load_inode_props()` scans xattr items for an inode and applies known Btrfs properties.
- `btrfs_inode_inherit_props()` copies inheritable properties from a parent directory inode to a new inode.

Property iteration:
- `iterate_object_props()` walks `BTRFS_XATTR_ITEM_KEY` items for an objectid, filters names under `XATTR_BTRFS_PREFIX`, matches known handlers using the hash bucket, copies name/value out of the extent buffer, and invokes a caller-supplied iterator.
- It dynamically resizes name and value buffers using `GFP_NOFS`.
- It releases the Btrfs path and frees buffers on exit.

Compression property behavior:
- `prop_compression_validate()` rejects compression on inodes that cannot compress, accepts valid compression types, and also accepts `no` and `none`.
- `prop_compression_apply()`:
  - zero length resets compression and no-compression flags.
  - `no`/`none` sets `BTRFS_INODE_NOCOMPRESS`, clears `BTRFS_INODE_COMPRESS`, and clears `prop_compress`.
  - `lzo`, `zlib`, and `zstd` set compression state; `lzo` and `zstd` also set their filesystem incompat feature bits.
- `prop_compression_ignore()` ignores compression xattrs for inode types other than regular files and directories.
- `prop_compression_extract()` returns the parent inode’s compression string only for active supported compression types.

Inheritance details:
- Inheritance only runs if the parent has `BTRFS_INODE_HAS_PROPS`.
- Each inheritable property is skipped if ignored for the child, absent on the parent, or invalid for the child.
- The current reservation logic assumes one supported property. If additional properties are added, the code has a reservation path using `btrfs_block_rsv_add()` for subsequent items.
- Successful inheritance writes the xattr, applies the in-memory property, and sets `BTRFS_INODE_HAS_PROPS`.

Role in the subsystem:
- Bridges user-visible Btrfs property xattrs and internal inode behavior, especially compression policy propagation from directories to new children.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/props.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/props.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/props.h

This header declares the Btrfs inode property API implemented in `props.c`.

Public API:
- `btrfs_props_init()` initializes the property handler hash table.
- `btrfs_set_prop()` sets or removes a known property through a transaction.
- `btrfs_validate_prop()` validates a property name/value pair for an inode.
- `btrfs_ignore_prop()` reports whether a validated property should be ignored for an inode.
- `btrfs_load_inode_props()` loads and applies properties from stored xattrs.
- `btrfs_inode_inherit_props()` inherits properties from a directory inode to a new inode.

Dependencies and declarations:
- Includes `<linux/types.h>` and `<linux/compiler_types.h>`.
- Forward declares Btrfs inode, path, and transaction handle types.

Role in the subsystem:
- Defines the narrow interface used by xattr, inode creation, and inode load paths to interact with Btrfs property handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/props.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/qgroup.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/qgroup.c

This file implements Btrfs qgroups: quota groups for referenced/exclusive accounting, reservation enforcement, qgroup hierarchy management, rescan, simple quota support, and relocation-related delayed subtree accounting.

Quota modes:
- `btrfs_qgroup_mode()` returns disabled, full, or simple mode.
- Full mode uses backref walks and dirty extent accounting to maintain referenced/exclusive counters.
- Simple mode uses simpler per-owner deltas and `SIMPLE_QUOTA` enable generation tracking.
- `btrfs_qgroup_enabled()` and `btrfs_qgroup_full_accounting()` are convenience predicates used throughout the file.

In-memory model:
- `fs_info->qgroup_tree` stores `struct btrfs_qgroup` nodes in an rb-tree keyed by qgroupid.
- Each qgroup tracks referenced/exclusive bytes and compressed variants, limit fields, reservation buckets, parent/member relation lists, dirty status, iterator list nodes, temporary refcount fields, and sysfs kobject state.
- Relations are represented by `struct btrfs_qgroup_list` and linked from both member and parent.
- Reservation buckets distinguish data, metadata per-transaction, and metadata preallocation.

Configuration loading and cleanup:
- `btrfs_read_qgroup_config()` reads the quota tree at mount:
  - pass 1 reads status, qgroup info, and qgroup limits.
  - pass 2 reads relation items.
  - it initializes sysfs entries, sets quota-enabled state, resumes queued rescan when needed, and marks full qgroups inconsistent on generation/config mismatches.
- `btrfs_free_qgroup_config()` frees rb-tree entries, relation lists, and sysfs state.
- `btrfs_check_quota_leak()` reports unreleased qgroup reservations at unmount.

Quota enable/disable:
- `btrfs_quota_enable()` creates the quota tree and status item, adds qgroups for existing subvolumes and the default filesystem tree, sets simple/full mode flags, commits the setup transaction, then starts a rescan for full qgroups.
- Simple quota enable sets the incompat feature and records `qgroup_enable_gen` for later delta filtering.
- `btrfs_quota_disable()` stops rescan, flushes outstanding reservations through delalloc/ordered extents/commit, removes the quota root from `fs_info`, frees qgroup config, cleans the quota tree, deletes the root, and frees the root block.

On-disk item helpers:
- `add_qgroup_item()` creates info and limit items for a qgroup.
- `del_qgroup_item()` removes both info and limit items.
- `add_qgroup_relation_item()` and `del_qgroup_relation_item()` maintain mirrored relation items.
- `update_qgroup_info_item()`, `update_qgroup_limit_item()`, and `update_qgroup_status_item()` persist dirty in-memory state to the quota tree.

Qgroup hierarchy operations:
- `btrfs_add_qgroup_relation()` validates qgroup levels, inserts mirrored relation items, links the in-memory relation, and attempts quick accounting if the child is fully exclusive.
- `btrfs_del_qgroup_relation()` removes mirrored relation items and updates in-memory accounting.
- `btrfs_create_qgroup()` creates the on-disk items, in-memory qgroup, and sysfs entry.
- `btrfs_remove_qgroup()` enforces deletion rules:
  - parent qgroups must have no children.
  - level-0 qgroups cannot be removed while the subvolume root still exists.
  - simple quota level-0 qgroups must have no remaining usage because shared extents can outlive deleted subvolumes.
- `btrfs_qgroup_cleanup_dropped_subvolume()` commits current accounting, tries to remove the dropped subvolume qgroup, and ignores expected busy/missing cases.
- `btrfs_limit_qgroup()` updates limit fields, supports `-1` as a clear value, and writes the limit item.

Dirty extent tracing and full accounting:
- Dirty extents are tracked in `trans->transaction->delayed_refs.dirty_extents`, an xarray keyed by `bytenr >> sectorsize_bits`.
- `btrfs_qgroup_trace_extent_nolock()` inserts a preallocated extent record while holding the xarray lock, merging data reservation info into an existing record when needed.
- `btrfs_qgroup_trace_extent_post()` walks commit-root backrefs to populate `old_roots` outside spinlock context.
- `btrfs_qgroup_trace_extent()` is the allocating wrapper.
- `btrfs_qgroup_trace_leaf_items()` traces non-inline file extent items in a leaf.
- `btrfs_qgroup_trace_subtree()` traces metadata and data extents under a subtree, but can mark qgroups inconsistent if the subtree level exceeds the configured threshold.

Accounting update:
- `btrfs_qgroup_account_extents()` runs during transaction commit. For each dirty extent, it finds current roots, optionally removes `qgroup_to_skip`, calls `btrfs_qgroup_account_extent()`, frees any recorded data reservation, removes the xarray entry, and frees the record.
- `btrfs_qgroup_account_extent()` compares old and new root sets, skips non-filesystem roots, respects rescan progress, updates qgroup refcounts, updates referenced/exclusive counters, advances `qgroup_seq`, and frees ulist inputs.
- `qgroup_update_counters()` implements the referenced/exclusive transition matrix for none/shared/exclusive states.
- `btrfs_run_qgroups()` writes dirty qgroups and status state to disk.

Snapshot/inherit behavior:
- `btrfs_qgroup_check_inherit()` validates ioctl inheritance structures and rejects deprecated direct ref/excl copy counts.
- `qgroup_auto_inherit()` creates an inherit structure from the parent qgroups of the inode root for simple quotas.
- `qgroup_snapshot_quick_inherit()` handles a narrow full-accounting fast path when the source has one matching parent that exclusively owns its bytes.
- `btrfs_qgroup_inherit()` creates the new qgroup, inserts inherited relations, copies limits/accounting when appropriate, and marks full qgroups inconsistent when a rescan is needed.

Rescan:
- `qgroup_rescan_init()` initializes rescan state, rejects simple mode, handles mount-time resume vs ioctl-initiated rescan, clears runtime cancel/no-accounting flags, and initializes the rescan work item.
- `btrfs_qgroup_rescan()` initializes rescan, commits current work, zeros current qgroup counters, and queues the worker.
- `btrfs_qgroup_rescan_worker()` repeatedly starts transactions and calls `qgroup_rescan_leaf()` until done, stopped, or failed; it updates status flags and completes waiters.
- `qgroup_rescan_leaf()` walks extent tree leaves from `qgroup_rescan_progress`, clones the leaf, walks extent and metadata items, finds all roots, and accounts each extent as newly referenced.
- `btrfs_qgroup_wait_for_completion()` waits for an active rescan.
- `btrfs_qgroup_rescan_resume()` queues a saved rescan during mount.

Reservation APIs:
- `btrfs_qgroup_reserve_data()` sets `EXTENT_QGROUP_RESERVED` over an inode range, tracks newly reserved bytes with `extent_changeset`, enforces qgroup limits, and retries after `try_flush_qgroup()` on quota exhaustion.
- `btrfs_qgroup_free_data()` clears reserved ranges and frees qgroup data reservation.
- `btrfs_qgroup_release_data()` clears the inode io_tree reservation only after data reaches disk; accounting frees qgroup reservation later at commit.
- `btrfs_qgroup_reserve_meta_prealloc()` reserves metadata prealloc bytes and can retry after flush.
- `btrfs_qgroup_free_meta_prealloc()`, `btrfs_qgroup_free_meta_all_pertrans()`, and `btrfs_qgroup_convert_reserved_meta()` maintain metadata reservation buckets.
- `btrfs_qgroup_check_reserved_leak()` clears and reports leaked inode data reservations.

Relocation and swapped subtree tracking:
- `btrfs_qgroup_init_swapped_blocks()` initializes per-root swapped block rb-trees.
- `btrfs_qgroup_add_swapped_blocks()` records subtree roots involved in balance/relocation swaps so expensive subtree tracing can be delayed.
- `btrfs_qgroup_trace_subtree_after_cow()` checks whether a COWed block matches a recorded swapped subtree, removes the record, reads the reloc counterpart, and traces both subtrees.
- `btrfs_qgroup_clean_swapped_blocks()` frees remaining delayed records at transaction commit.
- `qgroup_trace_subtree_swap()` and helpers walk generation-aware reloc subtrees and trace corresponding source/destination blocks.

Simple quota delta path:
- `btrfs_record_squota_delta()` applies simple quota increments/decrements for a filesystem root when the delta generation is at or after `qgroup_enable_gen`.
- It updates both `excl` and `rfer` equally through parent qgroups and marks touched qgroups dirty.

Error and consistency strategy:
- Full accounting marks qgroups inconsistent and can set runtime no-accounting/cancel-rescan when exact accounting is unsafe or too expensive.
- Many paths prefer preserving filesystem operation progress while forcing later rescan rather than aborting for recoverable accounting uncertainty.
- The file is lock-order sensitive: transaction start/commit, `qgroup_ioctl_lock`, `qgroup_lock`, `qgroup_rescan_lock`, and fs freeze interactions are explicitly managed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/qgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/qgroup.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/qgroup.h

This header defines Btrfs qgroup data structures, reservation types, mode enum, runtime flags, and exported qgroup APIs.

Conceptual overview in comments:
- Qgroups are split into reserve, trace, and account phases.
- Reserve controls quota limit behavior for incoming data/metadata operations.
- Trace records dirty extents that may affect accounting.
- Account updates qgroup counters, normally during transaction commit or rescan.
- A detailed comment describes delayed subtree tracing for balance/relocation swaps, avoiding full subtree scans unless a swapped subtree is later COWed.

Runtime flags:
- `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN`
- `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING`
These share the status item flags field but count down from the high bits to avoid persisted flag collisions.

Core structs:
- `struct btrfs_qgroup_extent_record` records dirty extent length, data reservation info, and old roots for commit-time accounting.
- `struct btrfs_qgroup_swapped_block` records delayed relocation/swap accounting metadata.
- `enum btrfs_qgroup_rsv_type` defines data, metadata per-transaction, and metadata prealloc reservation buckets.
- `struct btrfs_qgroup_rsv` stores reservation bytes per type.
- `struct btrfs_qgroup` stores accounting counters, limits, reservation state, relation lists, dirty/iterator nodes, temporary refcount fields, rb-tree node, and sysfs kobject.
- `struct btrfs_qgroup_list` links member qgroups to parent qgroups.
- `struct btrfs_squota_delta` represents a simple quota usage/free delta.
- `enum btrfs_qgroup_mode` defines disabled, full, and simple modes.

Public API groups:
- Mode and lifecycle: `btrfs_qgroup_mode()`, `btrfs_qgroup_enabled()`, `btrfs_qgroup_full_accounting()`, quota enable/disable, config read/free.
- Rescan: start, resume, wait for completion.
- Hierarchy: add/delete relation, create/remove qgroup, cleanup dropped subvolume, limit qgroup.
- Full accounting trace/account: trace extent, trace leaf items, trace subtree, account extent(s), run dirty qgroups.
- Inheritance: check inherit structure and apply qgroup inheritance.
- Reservations: data reserve/release/free, metadata prealloc reserve/free, per-transaction metadata free, metadata conversion, leak checks.
- Relocation/swap: init/clean/add swapped blocks, trace subtree after COW, destroy extent records.
- Simple quota: `btrfs_record_squota_delta()`.

Role in the subsystem:
- Defines the qgroup contract used across Btrfs transaction, extent, inode, relocation, ioctl, and sysfs paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/qgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.c

This file implements management of Btrfs RAID stripe tree items. The RAID stripe tree stores logical stripe extents as `BTRFS_RAID_STRIPE_KEY` items whose key objectid is logical start and key offset is length; payload strides map each stripe to device id and physical address.

Delete path:
- `btrfs_delete_raid_extent()` removes or trims stripe extents covering a logical range.
- It is a no-op if the RAID stripe tree incompat feature or `stripe_root` is absent.
- Outside tests, it first checks the chunk map and skips deletion if the map type does not require stripe tree updates.
- It searches using `(objectid=start, type=RAID_STRIPE_KEY, offset=-1)` and backs up one slot to find the relevant preceding/overlapping extent.
- It handles all overlap shapes:
  - deletion range in the middle of an item: duplicates a right item, adjusts right physical offsets, then truncates left.
  - deletion range at the end of an item: truncates left.
  - deletion range at the front of an item: recreates the remaining right part with physical offsets advanced by the front padding.
  - full item coverage: deletes the item.
  - multi-item deletion: loops, advancing `start` and `length`.
- `btrfs_partially_delete_raid_extent()` performs delete-and-reinsert for a trimmed item, copying all strides and adding `frontpad` to physical offsets.

Insert/update path:
- `btrfs_insert_one_raid_extent()` builds a `struct btrfs_stripe_extent` sized by the RAID profile factor from a `btrfs_io_context`.
- It fills each stride with device id and physical address from the bioc stripes.
- It inserts a `BTRFS_RAID_STRIPE_KEY` item keyed by logical start and bioc size.
- If the item already exists, it updates the existing payload through `update_raid_extent_item()`.
- On insert/update failure it aborts the transaction.
- `btrfs_insert_raid_extent()` iterates all biocs attached to an ordered extent, inserts each one, then drains the ordered extent’s `bioc_list` and drops references.

Lookup path:
- `btrfs_get_raid_extent_offset()` maps a logical address to the physical address for a target `btrfs_io_stripe`.
- It can search the commit root without locking when `stripe->rst_search_commit_root` is set.
- It locates the containing stripe extent, shortens `*length` if the request crosses a physically non-contiguous stripe extent boundary, and scans strides for the requested device id.
- For DUP profiles, it also requires `stripe_index` to match the stride index.
- On missing data it returns `-ENODATA` and logs debug output unless searching the commit root.

Key dependencies:
- Stripe tree root from `fs_info->stripe_root`.
- Btrfs item insertion/deletion/search helpers.
- `btrfs_io_context`, `btrfs_io_stripe`, ordered extents, and chunk maps from the volume/mapping layer.
- `btrfs_num_raid_stripes()` and update gating from `raid-stripe-tree.h`.

Role in the subsystem:
- Maintains the persistent logical-to-physical stripe mapping needed by the RAID stripe tree feature for supported data RAID profiles.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.h

This header declares the RAID stripe tree API and inline helpers.

Definitions:
- `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` lists supported profiles for RAID stripe tree updates:
  - DUP
  - RAID1 variants
  - RAID0
  - RAID10

Public API:
- `btrfs_delete_raid_extent()` deletes a logical range from the stripe tree.
- `btrfs_get_raid_extent_offset()` looks up the physical offset for a logical address, stripe index, and target device stripe.
- `btrfs_insert_raid_extent()` inserts stripe extents associated with an ordered extent.
- Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, `btrfs_insert_one_raid_extent()` is exposed for tests.

Inline helpers:
- `btrfs_need_stripe_tree_update()` returns true only when:
  - the filesystem has the `RAID_STRIPE_TREE` incompat feature,
  - the block group type is data,
  - the profile is in the supported RAID stripe tree mask.
- `btrfs_num_raid_stripes()` derives stride count from item size by dividing by `sizeof(struct btrfs_raid_stride)`.

Dependencies:
- Includes UAPI tree definitions plus Btrfs filesystem and accessor headers because inline helpers inspect block group flags and on-disk stride sizing.

Role in the subsystem:
- Provides the gatekeeping and exported operation surface for RAID stripe tree maintenance and lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.h -->