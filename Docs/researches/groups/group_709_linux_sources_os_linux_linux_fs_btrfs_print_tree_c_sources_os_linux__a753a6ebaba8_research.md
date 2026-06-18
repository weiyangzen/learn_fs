# Group Research: group_709_linux_sources_os_linux_linux_fs_btrfs_print_tree_c_sources_os_linux__a753a6ebaba8

Scope checked against `Docs/research_subset_a.md`: `sources/os/linux/linux` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/print-tree.c -->
# File Research: sources/os/linux/linux/fs/btrfs/print-tree.c

This file implements diagnostic printing for Btrfs tree blocks, leaves, keys, and selected item payloads. It is debug/inspection code, not metadata mutation logic.

Primary exported functions:
- `btrfs_root_name()` maps known root object IDs to readable names, with special formatting for tree relocation roots.
- `btrfs_print_leaf()` prints a leaf header and decodes each item by key type.
- `btrfs_print_tree()` prints node/leaf structure and can recursively follow child pointers.

Important helpers:
- `print_chunk()` and `print_dev_item()` decode chunk/device metadata.
- `print_extent_item()` decodes extent items, tree block info, and inline backrefs.
- `print_extent_data_ref()` and `print_extent_owner_ref()` print full/simple quota backref ownership data.
- `print_uuid_item()` validates and prints UUID-tree payload subvolume IDs.
- `print_raid_stripe_key()` prints RAID stripe tree stride device/physical pairs.
- `print_inode_item()`, `print_dir_item()`, `print_inode_ref_item()`, and `print_inode_extref_item()` decode common fs-tree records.
- `print_extent_csum()` derives checksum coverage from checksum size and sectorsize.
- `print_file_extent_item()` distinguishes inline file extents from regular/prealloc mappings.
- `key_type_string()` maps many Btrfs key types to readable strings, including qgroup, RAID stripe, and remap keys.

Behavior:
- `btrfs_print_leaf()` emits header metadata, optional debug extent-buffer ref/lock state, then dispatches each item slot by key type.
- Known payload types are decoded enough to correlate logical keys with on-disk fields.
- Directory/xattr records print structural metadata but not names or values.
- `btrfs_print_tree()` prints node keys and child block pointers; with `follow=true`, it reads child blocks using `btrfs_tree_parent_check`, validates levels, recurses, and releases child buffers.

Safety and validation:
- Extent item size is checked before dereferencing.
- Shared refs warn on parent bytenrs not aligned to sectorsize.
- UUID items reject payloads not aligned to `u64`.
- Recursive traversal validates expected child level, transid, owner root, and first key.
- Uses `BUG()` for impossible child level mismatches during diagnostic traversal.

Dependencies:
- Uses Btrfs accessors from `accessors.h`.
- Uses metadata definitions from `ctree.h`, `file-item.h`, `volumes.h`, and `raid-stripe-tree.h`.
- Uses tree IO helpers from `disk-io.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/print-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/print-tree.h -->
# File Research: sources/os/linux/linux/fs/btrfs/print-tree.h

This header exposes the Btrfs metadata printing interface.

Definitions:
- `BTRFS_ROOT_NAME_BUF_LEN` is `48`, sized for readable root names and relocation-root offset text.
- Forward declares `struct extent_buffer` and `struct btrfs_key`.

Public API:
- `btrfs_print_leaf()` prints a Btrfs leaf extent buffer.
- `btrfs_print_tree()` prints a node/leaf tree, optionally following children.
- `btrfs_root_name()` formats a root key object ID into a readable name.

Role:
- Keeps diagnostic callers independent from `print-tree.c` internals.
- Provides the buffer-size contract used by `btrfs_root_name()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/print-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/props.c -->
# File Research: sources/os/linux/linux/fs/btrfs/props.c

This file implements Btrfs inode properties backed by Btrfs xattrs. The current registered property is `btrfs.compression`.

Core model:
- `struct prop_handler` describes one property: xattr name, validate/apply/extract/ignore callbacks, and inheritance flag.
- `prop_handlers_ht` is a hash table keyed by Btrfs name hash for xattr-property lookup.

Primary exported functions:
- `btrfs_props_init()` registers static handlers.
- `btrfs_validate_prop()` checks property name and value.
- `btrfs_ignore_prop()` asks whether a valid property should be skipped for an inode.
- `btrfs_set_prop()` writes/removes the xattr and applies the in-memory inode state.
- `btrfs_load_inode_props()` scans an inode’s xattr items and applies known properties.
- `btrfs_inode_inherit_props()` copies inheritable properties from a parent directory to a new inode.

Property scanning:
- `iterate_object_props()` walks xattr items for an object ID, filters names under `XATTR_BTRFS_PREFIX`, copies name/value data from extent buffers, finds matching handlers, and invokes a callback.
- `inode_prop_iterator()` applies persisted properties and sets `BTRFS_INODE_HAS_PROPS` on success.

Compression property:
- `prop_compression_validate()` requires a compressible inode and accepts known compression types plus `no` and `none`.
- `prop_compression_apply()` clears state for zero-length values, sets `BTRFS_INODE_NOCOMPRESS` for `no`/`none`, or sets `BTRFS_INODE_COMPRESS` and `prop_compress` for `lzo`, `zlib`, or `zstd`.
- LZO and ZSTD set their filesystem incompat feature bits.
- `prop_compression_ignore()` skips non-regular and non-directory inodes.
- `prop_compression_extract()` converts parent compression state back to a string for inheritance.

Consistency notes:
- `btrfs_set_prop()` rolls back the xattr if applying a non-empty property fails.
- Property removal applies the handler with `NULL, 0` and asserts success.
- Inheritance validates extracted parent values before propagation.
- Current metadata reservation comments assume only one supported property.

Dependencies:
- Uses xattr helpers, dir-item accessors, compression helpers, transaction metadata reservations, and inode runtime flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/props.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/props.h -->
# File Research: sources/os/linux/linux/fs/btrfs/props.h

This header declares the Btrfs property API implemented by `props.c`.

Public API:
- `btrfs_props_init()`
- `btrfs_set_prop()`
- `btrfs_validate_prop()`
- `btrfs_ignore_prop()`
- `btrfs_load_inode_props()`
- `btrfs_inode_inherit_props()`

Role:
- Provides entry points used by inode creation, inode load, and xattr/property paths.
- Uses forward declarations for Btrfs inode, path, and transaction structures to keep callers decoupled from implementation headers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/props.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/qgroup.c -->
# File Research: sources/os/linux/linux/fs/btrfs/qgroup.c

This file implements Btrfs quota groups, including full qgroup accounting, simple quota accounting, config loading, qgroup relations, quota enable/disable, rescans, reservations, delayed extent accounting, and relocation swap handling.

Modes:
- `btrfs_qgroup_mode()` returns disabled, full, or simple mode.
- `btrfs_qgroup_enabled()` and `btrfs_qgroup_full_accounting()` are mode predicates.
- Full accounting tracks referenced/exclusive bytes through backref walks.
- Simple quota mode tracks ownership deltas against root ownership and propagates through parent qgroups.

In-memory state:
- Qgroups live in `fs_info->qgroup_tree`, keyed by qgroup ID.
- Relation lists model parent/member links between qgroups.
- Dirty qgroups are queued on `fs_info->dirty_qgroups` and written by `btrfs_run_qgroups()`.
- Iterator lists prevent duplicate propagation through parent graphs.

On-disk config:
- `btrfs_read_qgroup_config()` reads the quota tree at mount in two passes: status/info/limit items first, relation items second.
- Generation or config mismatches mark full qgroups inconsistent.
- Simple mode reads `qgroup_enable_gen`.
- `add_qgroup_item()`, `del_qgroup_item()`, relation item helpers, and update helpers maintain quota-tree records.

Enable/disable:
- `btrfs_quota_enable()` creates the quota tree, status item, qgroup records for existing roots, and the fs tree qgroup.
- Full mode starts inconsistent and queues a rescan; simple mode sets the simple-quota incompat flag and enable generation.
- `btrfs_quota_disable()` cancels/waits for rescans, flushes outstanding reservations, clears runtime state, deletes quota-tree contents, deletes the quota root, and frees qgroup config.
- Several paths deliberately drop `qgroup_ioctl_lock` around transaction start/commit to avoid lock inversions.

Relation and lifecycle operations:
- `btrfs_add_qgroup_relation()` validates qgroup levels, creates both relation items, adds in-memory relation state, and attempts quick accounting propagation.
- `btrfs_del_qgroup_relation()` removes relation items and in-memory links.
- `btrfs_create_qgroup()` creates a qgroup item and sysfs entry.
- `btrfs_remove_qgroup()` verifies deletability, removes relations/items, warns on non-zero reservations, and may mark full qgroups inconsistent.
- `btrfs_qgroup_cleanup_dropped_subvolume()` removes dropped subvolume qgroups after committing current accounting.
- `btrfs_limit_qgroup()` updates referenced/exclusive and reservation limits; `(u64)-1` clears a limit.

Delayed extent tracing and accounting:
- `btrfs_qgroup_trace_extent_nolock()` records dirty extents in delayed refs’ xarray by sectorsize-shifted bytenr.
- `btrfs_qgroup_trace_extent_post()` populates old roots using commit-root backref walks outside spinlock context.
- `btrfs_qgroup_trace_extent()` wraps allocation, xarray reservation, insert, and post-processing.
- `btrfs_qgroup_trace_leaf_items()` traces non-inline file extents in a leaf.
- `btrfs_qgroup_account_extents()` walks dirty extent records at transaction commit, finds new roots, accounts deltas, frees old root lists, releases data reservations, erases xarray records, and frees memory.
- `btrfs_qgroup_destroy_extent_records()` cleans dirty extent records when a transaction is destroyed.

Full accounting counters:
- `qgroup_update_refcnt()` propagates old/new root reference counts through parent qgroups.
- `qgroup_update_counters()` updates referenced and exclusive counters from old/new root cardinality.
- `btrfs_qgroup_account_extent()` coordinates refcount updates, skips non-fs-tree roots, handles rescan overlap, bumps `qgroup_seq`, and frees root lists.

Subtree tracing:
- `btrfs_qgroup_trace_subtree()` traces a subtree for snapshot drop or relocation unless the configured drop-subtree threshold would make it too expensive, in which case full qgroups are marked inconsistent.
- `qgroup_trace_subtree_swap()` and helpers trace swapped relocation/subvolume subtrees using generation-aware traversal.
- Leaf tracing also records file extent items when requested.

Rescan:
- `btrfs_qgroup_rescan()` initializes a full qgroup rescan, commits current work, zeroes counters, and queues the worker.
- `qgroup_rescan_leaf()` scans extent-tree leaves from progress, clones the leaf before accounting, and accounts each extent against current roots.
- `btrfs_qgroup_rescan_worker()` loops transactions until complete, stopped, cancelled, or errored, then updates status and completion state.
- `btrfs_qgroup_rescan_resume()` restarts queued rescans at mount.
- `btrfs_qgroup_wait_for_completion()` waits for the worker.

Inheritance:
- `btrfs_qgroup_check_inherit()` validates ioctl inheritance structures and rejects legacy ref/excl copy behavior.
- `qgroup_auto_inherit()` builds simple-quota inheritance from the source root’s parent qgroups.
- `qgroup_snapshot_quick_inherit()` avoids full rescans for a narrow full-accounting snapshot case.
- `btrfs_qgroup_inherit()` creates destination qgroups, relation items, inherited limits, and initial counters for subvolume/snapshot creation.

Reservation handling:
- `qgroup_reserve()` enforces limits and records reservations through all parent qgroups.
- `btrfs_qgroup_reserve_data()` marks inode `io_tree` ranges with `EXTENT_QGROUP_RESERVED`, reserves qgroup data bytes, and retries after flushing on quota exhaustion.
- `btrfs_qgroup_release_data()` clears range reservation bits after data reaches disk without freeing qgroup reservation counters.
- `btrfs_qgroup_free_data()` clears range reservation bits and frees qgroup counters for invalidation/error paths.
- Metadata reservation APIs manage `META_PREALLOC` and `META_PERTRANS` reservations and root-side counters to avoid disable/enable underflows.
- `btrfs_qgroup_check_reserved_leak()` detects and releases leaked per-inode data reservation bits.

Simple quota:
- `btrfs_record_squota_delta()` applies simple quota deltas for extents whose generation is after `qgroup_enable_gen`, propagating referenced/exclusive changes through parent qgroups.
- Simple quota parent usage consistency is checked by `squota_check_parent_usage()`.

Relocation swapped blocks:
- `btrfs_qgroup_init_swapped_blocks()` initializes per-root swapped-block rb-trees.
- `btrfs_qgroup_add_swapped_blocks()` records delayed subtree tracing metadata during balance relocation swaps.
- `btrfs_qgroup_trace_subtree_after_cow()` detects COW of a recorded swapped subtree, reads the relocation counterpart, traces the swap, and removes the record.
- `btrfs_qgroup_clean_swapped_blocks()` drops stale records at transaction commit.

Risk areas:
- Lock ordering around `qgroup_ioctl_lock`, transaction handles, rescan locks, and extent-buffer locks is central to correctness.
- Full accounting depends on expensive backref walks and marks qgroups inconsistent when accounting cannot be trusted.
- Reservation underflow is guarded with warnings and root-side metadata reservation tracking.
- Rescan/live accounting overlap is handled through progress checks and runtime flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/qgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/qgroup.h -->
# File Research: sources/os/linux/linux/fs/btrfs/qgroup.h

This header defines Btrfs quota group public structures, enums, runtime flags, and function prototypes.

Conceptual overview:
- Comments split qgroup behavior into reserve, trace, and account phases.
- A long balance optimization comment explains delayed subtree tracing for relocation swaps.

Important definitions:
- Runtime-only qgroup status flags:
  - `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN`
  - `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING`
- `BTRFS_QGROUP_DROP_SUBTREE_THRES_DEFAULT` defaults subtree-drop inconsistency threshold to `3`.
- `enum btrfs_qgroup_rsv_type` defines data, per-transaction metadata, and preallocated metadata reservations.
- `enum btrfs_qgroup_mode` defines disabled, full, and simple modes.
- Trace event operation enum covers reserve, release, and free.

Core structs:
- `struct btrfs_qgroup_extent_record` records dirty extent size, old roots, and deferred data-reservation release info.
- `struct btrfs_qgroup_swapped_block` records relocation/subvolume subtree swap metadata for delayed tracing after COW.
- `struct btrfs_qgroup_rsv` stores reservation counters by reservation type.
- `struct btrfs_qgroup` stores qgroup ID, referenced/exclusive counters, compressed counters, limit fields, reservations, relation lists, dirty/iterator links, temporary accounting refcounts, rb-tree node, and sysfs kobject.
- `struct btrfs_qgroup_list` links member and parent qgroups.
- `struct btrfs_squota_delta` describes simple-quota ownership deltas.

Public API categories:
- Mode and lifecycle: `btrfs_qgroup_mode()`, `btrfs_qgroup_enabled()`, `btrfs_quota_enable()`, `btrfs_quota_disable()`.
- Rescan: `btrfs_qgroup_rescan()`, resume, wait, and config loading/freeing.
- Relations and qgroups: add/delete relation, create/remove qgroup, dropped-subvolume cleanup, limit updates.
- Full accounting: trace extents/leaves/subtrees, account extents, run qgroups.
- Inheritance: check and apply qgroup inheritance.
- Reservations: data reserve/release/free, metadata reserve/free/convert, leak checks.
- Relocation swaps: init/clean/add swapped blocks and trace after COW.
- Simple quota: `btrfs_record_squota_delta()`.

Role:
- Shared contract for qgroup code used by transaction, inode, extent, relocation, ioctl, and sysfs paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/qgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.c -->
# File Research: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.c

This file implements Btrfs RAID stripe tree operations. The stripe tree maps logical file extents to per-stripe physical device offsets for supported RAID profiles.

Primary functions:
- `btrfs_delete_raid_extent()` deletes a logical range from the RAID stripe tree.
- `btrfs_insert_one_raid_extent()` inserts or updates one stripe extent from a `btrfs_io_context`.
- `btrfs_insert_raid_extent()` inserts all stripe extents attached to an ordered extent and releases their `bioc` references.
- `btrfs_get_raid_extent_offset()` looks up the physical offset for a logical range, device, profile, and stripe index.

Deletion behavior:
- `btrfs_delete_raid_extent()` no-ops when the RAID stripe tree feature/root is absent or the chunk profile does not require stripe-tree updates.
- It searches for stripe extents overlapping `[start, start + length)`.
- It handles all overlap shapes:
  - whole-item deletion,
  - deleting the right tail of an item,
  - deleting the left head of an item,
  - punching a hole by duplicating the item for the right side and truncating the left side.
- `btrfs_partially_delete_raid_extent()` rebuilds an item with adjusted logical start/length and physical stride offsets.

Insertion behavior:
- `btrfs_insert_one_raid_extent()` builds a variable-sized `struct btrfs_stripe_extent` with one stride per RAID factor.
- The key is `(logical, BTRFS_RAID_STRIPE_KEY, size)`.
- If insertion finds an existing item, it updates the item payload.
- Insert/update failures abort the transaction where appropriate.
- `btrfs_insert_raid_extent()` iterates `ordered_extent->bioc_list`, inserts each mapping, then removes and puts all `bioc` entries.

Lookup behavior:
- `btrfs_get_raid_extent_offset()` searches the stripe root, optionally through the commit root with skipped locking.
- It backs up one slot when exact search misses so a containing extent can be found.
- If the requested logical range crosses a stripe extent boundary, it shortens `*length` so the caller can split IO.
- It selects the stride matching the requested device ID, and for DUP profiles also matches `stripe_index`.
- Returns `-ENODATA` when no matching stripe extent/device is found.

Dependencies:
- Uses Btrfs tree search/insert/delete helpers.
- Uses `btrfs_io_context`, ordered extents, chunk maps, and volume/profile helpers.
- Emits tracepoints for insert, delete, and lookup.

Risk notes:
- Range deletion is sensitive to off-by-one and item-split behavior.
- Physical stride offsets must be adjusted consistently when logical ranges are truncated or split.
- Lookup may mutate requested length to enforce physically continuous IO boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.h -->
# File Research: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.h

This header declares the Btrfs RAID stripe tree API and small inline helpers.

Definitions:
- `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` lists supported profiles: DUP, RAID1 variants, RAID0, and RAID10.

Public API:
- `btrfs_delete_raid_extent()` removes logical ranges from the stripe tree.
- `btrfs_get_raid_extent_offset()` maps logical IO to stripe physical offsets and may shorten length for split IO.
- `btrfs_insert_raid_extent()` inserts stripe records for an ordered extent.
- Under sanity tests, `btrfs_insert_one_raid_extent()` is exported for direct testing.

Inline helpers:
- `btrfs_need_stripe_tree_update()` returns true only when the RAID stripe tree incompat feature is enabled, the block group is data, and the profile is supported.
- `btrfs_num_raid_stripes()` derives stride count from item size.

Role:
- Provides the stripe-tree contract to IO completion, deletion/truncation, mapping, and tests.
- Centralizes feature/profile gating so callers can avoid unnecessary stripe-tree work.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.h -->