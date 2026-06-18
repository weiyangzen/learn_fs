# Group Research: group_252_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_print_tree_c_sourc_6e23adc4768f

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/btrfs-linux` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.c

This file implements debug/diagnostic printing for Btrfs tree blocks, leaves, keys, and selected item payloads. It is not filesystem mutation logic; it is used to inspect on-disk metadata structures through `pr_info()`, `pr_cont()`, and `btrfs_info()` logging.

Primary exported functions:
- `btrfs_root_name()` maps root object IDs to readable names, with special formatting for tree relocation roots.
- `btrfs_print_leaf()` prints one leaf extent buffer and decodes many item types.
- `btrfs_print_tree()` prints a node or leaf and can recursively follow child block pointers.

Important internal helpers:
- `print_chunk()` prints chunk length, owner, type, and stripe device/offset records.
- `print_dev_item()` prints device item ID, total bytes, and bytes used.
- `print_extent_item()` decodes extent items, including tree block info and inline refs.
- `print_extent_data_ref()` and `print_extent_owner_ref()` print data and simple-quota owner refs.
- `print_uuid_item()` decodes UUID-tree payloads as subvolume IDs and validates `u64` alignment.
- `print_raid_stripe_key()` prints RAID stripe tree stride device/physical pairs.
- `print_inode_item()`, `print_dir_item()`, `print_inode_ref_item()`, and `print_inode_extref_item()` decode common fs-tree records.
- `print_extent_csum()` reports checksum item logical range based on checksum and sector sizes.
- `print_file_extent_item()` distinguishes inline file extents from regular/prealloc extent mappings.
- `key_type_string()` maps Btrfs item key types to readable strings, including qgroup, RAID stripe, and remap keys.

Behavior and control flow:
- `btrfs_print_leaf()` prints the leaf header, optional debug extent-buffer ref/lock state, then iterates every item slot and dispatches by key type.
- For known item types it prints enough structured fields to correlate logical keys with payload metadata.
- It intentionally prints directory/xattr item records without dumping names or values.
- `btrfs_print_tree()` prints node headers and child pointers. If `follow` is true, it reads each child with a `btrfs_tree_parent_check`, validates level consistency, recurses, and frees the child extent buffer.

Safety and validation:
- `print_extent_item()` validates item size before dereferencing `struct btrfs_extent_item`.
- Shared block/data refs warn if parent bytenr is not sector-size aligned.
- `print_uuid_item()` rejects UUID items whose payload size is not `u64` aligned.
- Recursive tree following uses `read_tree_block()` with expected level, transid, owner root, and first-key checks.
- The code uses `BUG()` for impossible child level mismatches during diagnostic traversal.

Dependencies:
- Relies heavily on accessor helpers from `accessors.h`.
- Uses metadata definitions from `ctree.h`, `file-item.h`, `volumes.h`, and `raid-stripe-tree.h`.
- Uses `read_tree_block()` and extent-buffer lifetime helpers from tree/disk IO code.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.h

This header exposes Btrfs metadata printing helpers used by diagnostic code.

Definitions:
- `BTRFS_ROOT_NAME_BUF_LEN` is `48`, sized for root names plus extra relocation-root offset text.
- Forward declares `struct extent_buffer` and `struct btrfs_key`.

Public interface:
- `void btrfs_print_leaf(const struct extent_buffer *l);`
- `void btrfs_print_tree(const struct extent_buffer *c, bool follow);`
- `const char *btrfs_root_name(const struct btrfs_key *key, char *buf);`

Role in the module:
- Keeps print-tree callers independent from the implementation details in `print-tree.c`.
- Provides the buffer-size contract required by `btrfs_root_name()`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/props.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/props.c

This file implements Btrfs inode property handling through Btrfs xattrs, currently centered on the `btrfs.compression` property. It validates property names/values, applies properties to in-memory inode state, loads persisted properties from xattr items, and inherits selected properties from parent directories.

Core data model:
- `struct prop_handler` describes one property:
  - xattr name
  - validation callback
  - apply callback
  - extract callback for inheritance
  - ignore callback
  - inheritable flag
- `prop_handlers_ht` is a hash table keyed by Btrfs name hash for quick xattr-property lookup.

Primary exported functions:
- `btrfs_props_init()` registers static property handlers in the hash table.
- `btrfs_validate_prop()` validates that a named property exists and that the value is accepted.
- `btrfs_ignore_prop()` asks whether a valid property should be skipped for a target inode.
- `btrfs_set_prop()` writes/removes the xattr and applies the resulting in-memory state.
- `btrfs_load_inode_props()` scans an inode’s xattr items and applies recognized properties.
- `btrfs_inode_inherit_props()` copies inheritable properties from parent to newly created inode.

Property lookup and scanning:
- `find_prop_handlers_by_hash()` selects the handler bucket from `prop_handlers_ht`.
- `find_prop_handler()` matches exact xattr names inside a bucket.
- `iterate_object_props()` walks xattr items for an object ID, filters names with `XATTR_BTRFS_PREFIX`, copies name/value data out of extent buffers, and invokes an iterator callback for recognized properties.
- `inode_prop_iterator()` applies properties during inode load and sets `BTRFS_INODE_HAS_PROPS` on success.

Compression property:
- Registered xattr name is `XATTR_BTRFS_PREFIX "compression"`.
- `prop_compression_validate()` requires a compressible inode and accepts known compression types plus `"no"` and `"none"`.
- `prop_compression_apply()` updates inode flags:
  - zero-length value resets compression/nocompression state.
  - `"no"`/`"none"` sets `BTRFS_INODE_NOCOMPRESS`.
  - `"lzo"`, `"zlib"`, and `"zstd"` set `BTRFS_INODE_COMPRESS` and `prop_compress`.
  - LZO and ZSTD also set the corresponding incompat feature flags.
- `prop_compression_ignore()` skips non-regular and non-directory inodes.
- `prop_compression_extract()` converts the parent’s compression enum back to a property string for inheritance.

Error handling and consistency:
- `btrfs_set_prop()` rolls back the xattr if applying a non-empty property fails.
- Removing a property applies the handler with `NULL, 0` and asserts success.
- Inheritance validates extracted parent values before propagation.
- `btrfs_inode_inherit_props()` accounts for the current single-property reservation assumption and reserves extra metadata only after the first property if more are added later.

Dependencies:
- Uses xattr helpers from `xattr.h`.
- Uses compression helpers from `compression.h`.
- Uses Btrfs dir-item accessors to parse packed xattr items from leaves.
- Uses inode runtime flags from `btrfs_inode.h`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/props.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/props.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/props.h

This header declares the Btrfs property API implemented by `props.c`.

Public interface:
- `btrfs_props_init()` initializes the property handler table.
- `btrfs_set_prop()` sets or removes a property xattr and applies it to an inode.
- `btrfs_validate_prop()` validates property name and value.
- `btrfs_ignore_prop()` reports whether a valid property should be skipped for an inode.
- `btrfs_load_inode_props()` loads persisted inode properties using a supplied path.
- `btrfs_inode_inherit_props()` inherits parent directory properties into a child inode.

Role:
- Provides the property layer entry points to inode creation, xattr, and inode-load paths.
- Forward declares Btrfs transaction, inode, and path structures to avoid pulling full implementation headers into callers.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/props.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.c

This file implements Btrfs quota groups, including full qgroup accounting, simple quota accounting, qgroup configuration loading, qgroup relation management, quota enable/disable, rescan workers, reservation enforcement, delayed extent accounting, and relocation swap handling.

Modes and global state:
- `btrfs_qgroup_mode()` returns disabled, full, or simple mode from fs flags and qgroup status flags.
- `btrfs_qgroup_enabled()` and `btrfs_qgroup_full_accounting()` are mode predicates.
- Full accounting tracks referenced/exclusive bytes through backref walks.
- Simple quota mode tracks ownership deltas against root ownership and propagates through qgroup parents.

In-memory qgroup management:
- Qgroups are stored in `fs_info->qgroup_tree`, an rb-tree keyed by qgroup ID.
- `find_qgroup_rb()`, `add_qgroup_rb()`, `del_qgroup_rb()`, and relation helpers manage qgroup and parent/member graph state.
- `qgroup_dirty()` adds changed qgroups to `fs_info->dirty_qgroups` for later disk updates.
- Iterator lists prevent duplicate traversal while propagating updates through parent qgroups.

On-disk config loading and writing:
- `btrfs_read_qgroup_config()` reads the quota tree during mount:
  - pass 1 reads status, info, and limit items;
  - pass 2 reads bidirectional qgroup relation items;
  - inconsistent generation/config marks full qgroups inconsistent;
  - simple mode reads `qgroup_enable_gen`.
- `add_qgroup_item()`, `del_qgroup_item()`, `update_qgroup_info_item()`, `update_qgroup_limit_item()`, and `update_qgroup_status_item()` maintain quota-tree items.
- `btrfs_run_qgroups()` writes dirty qgroup info/limit items and updates the status item during transaction commit or qgroup assignment.

Quota enable/disable:
- `btrfs_quota_enable()` creates the quota tree, status item, qgroup records for existing roots, and the fs tree qgroup.
- Full mode starts inconsistent and queues a rescan; simple mode sets the simple-quota incompat flag and an enable generation.
- `btrfs_quota_disable()` stops rescans, flushes outstanding reservations, clears quota state, deletes quota-tree contents, deletes the quota root, and frees config.
- `flush_reservations()` drains delalloc, ordered extents, and commits so stale qgroup reservations do not reappear after re-enable.

Qgroup relation and lifecycle operations:
- `btrfs_add_qgroup_relation()` validates levels, creates both relation items, adds the in-memory relation, and attempts quick accounting propagation.
- `btrfs_del_qgroup_relation()` removes both relation directions and updates accounting if possible.
- `btrfs_create_qgroup()` creates a new qgroup item and sysfs entry.
- `btrfs_remove_qgroup()` verifies deletability, removes relation/item state, warns on non-zero reservations, and marks full qgroups inconsistent if non-zero usage is being deleted.
- `btrfs_qgroup_cleanup_dropped_subvolume()` removes a dropped subvolume’s qgroup after committing current accounting, ignoring expected busy/absent cases.
- `btrfs_limit_qgroup()` updates max referenced/exclusive and reservation limits, with `-1` used as a clear sentinel.

Delayed extent tracing and full accounting:
- `btrfs_qgroup_trace_extent_nolock()` records dirty extents in delayed refs’ xarray by sectorsize-shifted bytenr.
- `btrfs_qgroup_trace_extent_post()` populates old roots using commit-root backref walks after dropping spinlock context.
- `btrfs_qgroup_trace_extent()` wraps allocation, xarray reservation, insert, and post-processing.
- `btrfs_qgroup_trace_leaf_items()` scans file extent items in a leaf and traces non-inline disk-backed extents.
- `btrfs_qgroup_account_extents()` walks dirty extent records at commit time, computes new roots, optionally skips one qgroup, calls `btrfs_qgroup_account_extent()`, frees associated data reservations, and erases records.
- `btrfs_qgroup_account_extent()` compares old/new root sets, filters non-fstree roots, coordinates with rescan progress, updates refcounts and counters, and frees root ulist resources.

Counter logic:
- `qgroup_update_refcnt()` walks root qgroups and parents, accumulating old or new reference counts under a sequence number.
- `qgroup_update_counters()` updates referenced and exclusive byte counters based on old/new refcount transitions.
- `quick_update_accounting()` handles relation changes cheaply when child referenced bytes are entirely exclusive; otherwise it marks full qgroups inconsistent.
- `btrfs_record_squota_delta()` handles simple quota byte deltas, skips extents older than the simple-quota enable generation, propagates to parent qgroups, and guards against underflow.

Snapshot/subvolume inheritance:
- `btrfs_qgroup_check_inherit()` validates inherit payload size, flags, and referenced parent qgroups; old ref/excl copy behavior is rejected.
- `qgroup_auto_inherit()` derives simple-quota inherited parents from the containing root’s parent qgroups.
- `qgroup_snapshot_quick_inherit()` can avoid a rescan when a snapshot parent relationship is simple enough to update by nodesize.
- `btrfs_qgroup_inherit()` creates the destination qgroup, adds inherited relations, copies selected limits/accounting from the source, and marks inconsistent if manual or unsafe inheritance needs rescan.

Rescan:
- `qgroup_rescan_init()` validates state, sets rescan flags/progress, clears runtime cancel/no-accounting flags, and initializes work.
- `qgroup_rescan_zero_tracking()` clears all current qgroup rfer/excl counters and marks qgroups dirty.
- `btrfs_qgroup_rescan()` commits current work, zeros tracking, and queues the worker for full accounting.
- `qgroup_rescan_leaf()` scans extent-tree leaves from progress, clones a scratch leaf, walks extent/metadata items, finds all roots, and accounts them as new roots.
- `btrfs_qgroup_rescan_worker()` repeatedly scans leaves in transactions, updates inconsistent/rescan flags, completes waiters, and logs paused/cancelled/completed/failed outcomes.
- `btrfs_qgroup_wait_for_completion()` waits for the rescan completion, optionally interruptibly.
- `btrfs_qgroup_rescan_resume()` queues an interrupted mount-time rescan.

Reservation enforcement:
- `qgroup_reserve()` checks limits across a root qgroup and its parents, honoring quota override for capable users, then records reservations.
- `btrfs_qgroup_free_refroot()` releases reservations for a root and all parent qgroups; `(u64)-1` frees all per-transaction metadata reservation.
- `btrfs_qgroup_reserve_data()` reserves data ranges by setting `EXTENT_QGROUP_RESERVED`, enforcing limits, and retrying after flushing qgroup space on `-EDQUOT`.
- `btrfs_qgroup_free_data()` clears reserved ranges and frees qgroup data reservation.
- `btrfs_qgroup_release_data()` clears the io-tree reservation bit without freeing qgroup bytes, for data that reached disk and will be accounted at commit.
- Metadata APIs reserve, free, and convert prealloc/per-transaction metadata reservations, mirrored in root-local reservation counters to avoid underflow across quota mode transitions.
- `try_flush_qgroup()` flushes delalloc, waits ordered extents, runs delayed iputs, and commits to recover qgroup space.

Relocation swapped-block accounting:
- `btrfs_qgroup_init_swapped_blocks()` initializes per-level rb-trees used to remember swapped subtree roots.
- `btrfs_qgroup_add_swapped_blocks()` records subvolume/reloc subtree roots before balance swaps them, including level, generations, first key, last snapshot, and whether leaves need tracing.
- `btrfs_qgroup_trace_subtree_after_cow()` detects later COW of a swapped subtree root, removes the record, reads the reloc counterpart, and traces both subtrees.
- `qgroup_trace_subtree_swap()` and helpers do generation-aware traversal so only new relocation blocks and corresponding subvolume blocks are traced.
- `btrfs_qgroup_clean_swapped_blocks()` drops remaining swap records at transaction commit when no delayed trace was needed.

Cleanup and diagnostics:
- `btrfs_check_quota_leak()` reports unreleased qgroup reservations at unmount.
- `btrfs_free_qgroup_config()` frees in-memory qgroup trees and sysfs state.
- `btrfs_qgroup_check_reserved_leak()` clears and reports leaked inode data reservation bits at inode destruction.
- `btrfs_qgroup_destroy_extent_records()` frees delayed-ref dirty extent records and destroys the xarray.

Concurrency:
- `qgroup_ioctl_lock` serializes ioctl/config operations.
- `qgroup_lock` protects in-memory qgroup rb-tree/list/counter state.
- `qgroup_rescan_lock` protects rescan state and progress.
- The code deliberately drops locks before starting/committing transactions in several paths to avoid lock inversions with freeze, rescan, and qgroup ioctl paths.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.h

This header defines Btrfs qgroup data structures, reservation types, runtime flags, mode enum, simple-quota delta structure, and the public API implemented by `qgroup.c`.

Conceptual overview:
- The header documents qgroups in three phases:
  - reserve: pre-account metadata/data space for limit enforcement;
  - trace: record dirty extents whose ownership/reference state may change;
  - account: update qgroup numbers during rescan or transaction commit.
- It also documents the balance relocation optimization using delayed subtree tracing through swapped block records.

Runtime flags:
- `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN` cancels a running rescan.
- `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING` suppresses live accounting when qgroups are inconsistent or disabled for accounting.
- These share the status-item flags field but count down from the MSB to avoid collision with persisted flags.

Core structures:
- `struct btrfs_qgroup_extent_record` records a dirty extent’s length, old roots, and data reservation bytes/refroot to free at commit.
- `struct btrfs_qgroup_swapped_block` records delayed tracing state for a swapped relocation/subvolume subtree pair.
- `enum btrfs_qgroup_rsv_type` distinguishes data, per-transaction metadata, and preallocated metadata reservations.
- `struct btrfs_qgroup_rsv` stores per-type reserved byte counters.
- `struct btrfs_qgroup` stores usage counters, limits, reservation counters, relation lists, dirty/iterator lists, temporary old/new refcounts, rb-tree node, and sysfs kobject.
- `struct btrfs_qgroup_list` links a member qgroup to a parent qgroup.
- `struct btrfs_squota_delta` describes a simple-quota byte delta by root, length, generation, direction, and data/metadata kind.

Helpers and enums:
- `btrfs_qgroup_subvolid()` extracts the low bits of a qgroup ID.
- Event trace enum values identify reserve, release, and free operations.
- `enum btrfs_qgroup_mode` exposes disabled, full, and simple modes.

Public API groups:
- Mode/status: `btrfs_qgroup_mode()`, `btrfs_qgroup_enabled()`, `btrfs_qgroup_full_accounting()`.
- Quota lifecycle: enable, disable, rescan, resume, wait, read/free config.
- Qgroup graph: add/delete relation, create/remove qgroup, cleanup dropped subvolume, limit qgroup.
- Full accounting trace/account: trace extents, leaves, subtrees, account extents, run qgroups.
- Inherit validation/application: `btrfs_qgroup_check_inherit()` and `btrfs_qgroup_inherit()`.
- Reservation API: data reserve/release/free, metadata prealloc reserve/free, pertrans free, meta conversion, leak check.
- Relocation swap API: init/clean swapped blocks, add swapped records, trace after COW.
- Cleanup/simple quota: destroy extent records and record simple-quota deltas.

Role:
- Serves as the cross-subsystem contract for inode IO, transaction commit, relocation, subvolume creation/deletion, ioctl quota control, and sysfs qgroup exposure.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/qgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.c

This file implements the Btrfs RAID stripe tree operations. The stripe tree maps logical data extents to per-stripe device IDs and physical offsets for supported RAID profiles when the `RAID_STRIPE_TREE` incompat feature is enabled.

Primary functions:
- `btrfs_delete_raid_extent()` deletes or trims RAID stripe tree entries covering a logical range.
- `btrfs_insert_one_raid_extent()` inserts or updates one RAID stripe extent from a `btrfs_io_context`.
- `btrfs_insert_raid_extent()` inserts all stripe extents attached to an ordered extent and releases their bioc references.
- `btrfs_get_raid_extent_offset()` resolves a logical address and device stripe to the physical offset stored in the stripe tree.

Deletion behavior:
- `btrfs_delete_raid_extent()` first skips work if the feature/root is absent or the target chunk profile does not need stripe-tree updates.
- It searches by logical start and handles overlap cases:
  - deletion range punches a hole inside one stripe extent;
  - deletion trims the tail of an existing extent;
  - deletion trims the front of an existing extent;
  - deletion removes whole stripe extent items.
- `btrfs_partially_delete_raid_extent()` deletes an old item and reinserts a shortened item, adjusting each stride’s physical offset by `frontpad`.
- Hole punching duplicates the right-side item, adjusts right-side physical offsets, then truncates/reinserts the left-side item.
- The search uses `offset = (u64)-1` to land correctly even when the target is the first item on a leaf.

Insertion behavior:
- `btrfs_insert_one_raid_extent()` allocates a variable-sized `struct btrfs_stripe_extent` based on the RAID profile factor.
- It fills each `btrfs_raid_stride` with device ID and physical address from `bioc->stripes`.
- The key is `(logical, BTRFS_RAID_STRIPE_KEY, size)`.
- If insertion returns `-EEXIST`, `update_raid_extent_item()` overwrites the existing item payload.
- Non-recoverable insert/update failures abort the transaction.

Ordered extent integration:
- `btrfs_insert_raid_extent()` is feature-gated on `RAID_STRIPE_TREE`.
- It iterates `ordered_extent->bioc_list`, inserts each recorded stripe extent, then removes and drops each bioc.

Lookup behavior:
- `btrfs_get_raid_extent_offset()` searches the stripe root for an item containing the requested logical address.
- It supports commit-root lookup through `stripe->rst_search_commit_root`, using skip-locking/search-commit-root path flags.
- If the requested logical range crosses the found stripe extent boundary, it shortens `*length` so upper layers split IO at the stripe-tree boundary.
- It selects the stride matching `stripe->dev->devid`; for DUP it also requires the requested stripe index.
- On success it sets `stripe->physical = stride physical + logical offset`.
- On miss it returns `-ENODATA` and emits a debug message outside commit-root search and non-EIO cases.

Dependencies:
- Uses Btrfs item insertion/deletion/search helpers.
- Uses chunk map/profile helpers from `volumes.h`.
- Uses `btrfs_need_stripe_tree_update()` and `btrfs_num_raid_stripes()` from `raid-stripe-tree.h`.
- Uses tracepoints for insert/delete/lookup observability.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.h

This header declares the RAID stripe tree API and small helpers for deciding when stripe-tree metadata is needed.

Definitions:
- `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` lists supported RAID/profile bits:
  - DUP
  - RAID1 mask
  - RAID0
  - RAID10

Public API:
- `btrfs_delete_raid_extent()` removes stripe-tree mappings for a logical range.
- `btrfs_get_raid_extent_offset()` resolves logical IO to a stored per-device physical offset and may shorten IO length at stripe extent boundaries.
- `btrfs_insert_raid_extent()` records stripe extents from an ordered extent.
- Under sanity tests, `btrfs_insert_one_raid_extent()` is exported for direct testing.

Inline helpers:
- `btrfs_need_stripe_tree_update()` returns true only when:
  - the filesystem has `RAID_STRIPE_TREE`;
  - the block group type is data;
  - the profile is one of the supported RAID stripe tree profiles.
- `btrfs_num_raid_stripes()` derives the number of strides from the item size.

Role:
- Provides the interface between ordered extent completion, extent deletion, IO mapping, and the stripe-tree implementation.
- Encapsulates feature/profile gating so callers can cheaply skip stripe-tree work when unsupported or unnecessary.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.h -->