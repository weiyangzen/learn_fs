# Group Research: group_215_bcachefs_sources_cow_pools_bcachefs_fs_bcachefs_sb_members_h_sources_09b961b77e49

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/bcachefs`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.h

This header is the central inline/API surface for bcachefs superblock member devices. It covers on-disk member record access, live device iteration, refcount acquisition, missing-device handling, member property conversion, btree allocation bitmap helpers, and member-management declarations.

Key responsibilities:
- Provides v1/v2 superblock member accessors:
  - `__bch2_members_v2_get_mut()`
  - `bch2_members_v2_get()`
  - `members_v1_get_mut()`
  - `bch2_members_v1_get()`
- Exposes conversion and formatting APIs:
  - `bch2_member_to_text()`
  - `bch2_member_to_text_short*()`
  - `bch2_devs_mask_to_text_locked()`
- Defines online/member iteration macros:
  - RCU-only: `for_each_member_device_rcu`, `for_each_online_member_rcu`, `for_each_rw_member_rcu`
  - Refcounted: `for_each_member_device`, `for_each_online_member`, `for_each_rw_member`, `for_each_readable_member`
- Wraps device lifetime and I/O references:
  - `bch2_dev_get()`, `bch2_dev_put()`
  - `bch2_dev_get_ioref()`
  - `enumerated_ref_tryget()`/`put()` on per-device read/write I/O refs
- Implements device lookup variants:
  - no-error RCU lookup
  - checked lookup with missing-device accounting
  - refcounted tryget
  - bkey-aware and bucket-aware tryget
- Converts on-disk `struct bch_member` into CPU-side `struct bch_member_cpu` through `bch2_mi_to_cpu()`.
- Provides inline btree allocation bitmap sector tests and declares mutation/GC helpers.

Important invariants:
- Device masks are fixed to `BCH_SB_MEMBERS_MAX`, currently 64.
- `bucket_valid()` checks bucket offset against `first_bucket` and `nbuckets_minus_first`; bucket-based lookups release refs and fail on invalid buckets.
- Debug builds use explicit atomic device refs and underflow panic diagnostics; non-debug builds use `percpu_ref`.
- I/O refs distinguish READ/WRITE and caller-supplied reference categories.
- `bch2_member_alive()` treats zero UUID and `BCH_SB_MEMBER_DELETED_UUID` as non-live.
- Btree bitmap helpers assume a 64-bit bitmap plus `btree_bitmap_shift`; sectors outside representable range are not marked.

Dependencies:
- Uses `util/enumerated_ref.h` for I/O reference accounting.
- Uses `util/darray.h` for fixed small device lists.
- Depends on bcachefs btree key and superblock types.

Research notes:
- This file is heavily inline because device lookup and iteration are hot paths.
- Error-reporting lookup variants are intentionally distinct from no-error paths, allowing callers to avoid noisy accounting during speculative or validation probes.
- `bch2_prt_member_name()` is safe for invalid IDs and handles `BCH_SB_MEMBER_INVALID` specially.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_format.h

This header defines the persistent/on-disk superblock member format and member-related constants/enums.

Key definitions:
- `BCH_SB_MEMBERS_MAX` is 64, due to current use of device bitmasks.
- `BCH_SB_MEMBER_INVALID` is 255, a sentinel for no device.
- `BCH_SB_MEMBER_DELETED_UUID` marks a deleted member slot.
- `BCH_MIN_NR_NBUCKETS` sets the minimum bucket count.
- IOPS measurement enum:
  - sequential read/write
  - random read/write
- Member error enum:
  - read
  - write
  - checksum
- `struct bch_member` is the on-disk member record, including:
  - UUID
  - bucket geometry
  - flags
  - IOPS estimates
  - persistent error counters
  - sequence number
  - btree allocation bitmap
  - journal restart hints
  - fixed-width device name/model/serial fields
  - flush error counter
- `BCH_MEMBER_V1_BYTES` preserves older fixed member size compatibility.
- `struct bch_sb_field_members_v1` stores fixed-size member records.
- `struct bch_sb_field_members_v2` adds `member_bytes` for extensible member records.

Important bitfields:
- State, discard, data-allowed mask, group, durability.
- Freespace initialized, resize-on-mount, rotational, rotational-set.
- Member states: `rw`, `ro`, `evacuating`, `spare`.

Important invariants:
- New fields can be appended to `struct bch_member` because v2 stores per-record byte size.
- `BCH_MEMBER_NBUCKETS_MAX` is constrained by large kernel allocation limits for bucket-generation arrays.
- `BCH_MI_BTREE_BITMAP_SHIFT_MAX` derives from 64 bitmap entries and u64 sector addressability.

Research notes:
- This file is pure format ABI. Changes here affect compatibility and recovery.
- The v1/v2 split explains the padded copy logic in `members.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_types.h

This header defines `struct bch_member_cpu`, the in-memory CPU-endian projection of an on-disk member record.

Fields include:
- Bucket geometry:
  - `nbuckets`
  - `nbuckets_minus_first`
  - `first_bucket`
  - `bucket_size`
- Placement/availability metadata:
  - `group`
  - `state`
  - `discard`
  - `data_allowed`
  - `durability`
- Operational flags:
  - `freespace_initialized`
  - `resize_on_mount`
  - `rotational`
  - `valid`
- Btree allocation bitmap state:
  - `btree_bitmap_shift`
  - `btree_allocated_bitmap`

Research notes:
- This is intentionally compact and mirrors the decoded fields produced by `bch2_mi_to_cpu()` in `members.h`.
- The include-guard closing comment appears to name `_BCACHEFS_SB_MEMBERS_H` rather than `_BCACHEFS_SB_MEMBERS_TYPES_H`; functionally harmless but notable.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/check_snapshots.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/check_snapshots.c

This file implements snapshot and snapshot-tree fsck/recovery validation. It repairs links among snapshot nodes, snapshot tree records, subvolumes, skiplist/depth fields, and snapshot-tagged btree keys.

Major operations:
- Ensures in-memory snapshot table capacity with `bch2_snapshot_table_make_room()`.
- Creates replacement snapshot-tree records via `bch2_snapshot_tree_create()`.
- Finds a usable master subvolume for a snapshot tree with:
  - `bch2_snapshot_oldest_subvol()`
  - `bch2_snapshot_tree_master_subvol()`
- Validates each `snapshot_tree` key in `check_snapshot_tree()`:
  - root snapshot must exist
  - root snapshot must be the actual root
  - snapshot must point back to the tree
  - master subvolume must exist, be in the same snapshot tree, and not itself be a snapshot subvolume
  - invalid tree records can be deleted or repaired
- Public pass `bch2_check_snapshot_trees()` scans `BTREE_ID_snapshot_trees`.
- Validates each snapshot key in `check_snapshot()`:
  - parent exists and points back to child
  - children exist and point back to parent
  - `BCH_SNAPSHOT_SUBVOL` flag matches subvolume linkage
  - snapshot-tree pointer is valid or repairable
  - depth field matches parent depth
  - skiplist entries are valid ancestors and sorted after repair
- Public passes:
  - `bch2_check_snapshots_trans()`
  - `bch2_check_snapshots()`
- Reconstructs missing snapshot nodes from snapshot-bearing keys:
  - groups snapshot IDs by affected btree object
  - only reconstructs singleton missing nodes
  - creates missing `snapshot_tree` records as needed
- Validates snapshot IDs on arbitrary keys with `__bch2_check_key_has_snapshot()`:
  - keys in deleted snapshots are auto-fixable deletion candidates
  - keys in missing snapshots may require additional recovery passes before deletion is offered

Important invariants:
- Snapshot IDs decrease from parent to child; validation relies on this ordering.
- Snapshot depth repair iterates snapshots in reverse so parent depths are already correct.
- Tree pointer repair anchors on the computed root snapshot.
- Missing snapshot deletion is conservative and gated by required recovery passes.

Dependencies:
- Btree iteration/update APIs.
- Snapshot and subvolume lookup helpers.
- Fsck error framework and recovery pass scheduling.
- `snapshot_id_list` darrays.

Research notes:
- This file is the consistency safety net for the snapshot subsystem.
- It distinguishes “missing because deleted” from “missing and unknown,” preventing aggressive key deletion before reconstruction/check passes run.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/check_snapshots.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/delete.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/delete.c

This file implements asynchronous snapshot cleanup and deferred deletion of dead snapshot nodes.

Conceptual model:
- Dead leaf snapshot: no children and no subvolume points to it.
- Redundant interior snapshot: one live child, no subvolume, and keys can be moved to the child.
- Interior node physical removal is deferred because depth/skiplist updates across a subtree are not safely atomic during normal runtime.

Major APIs:
- `bch2_snapshot_delete_status_to_text()` prints running deletion status and worker backtrace.
- `bch2_snapshot_node_set_deleted()` marks a snapshot leaf for cleanup:
  - sets `WILL_DELETE`
  - clears `SUBVOL`
  - clears `subvol`
- `bch2_snapshot_node_set_no_keys()` marks interior nodes whose keys have been removed/moved.
- `bch2_snapshot_node_delete()` physically removes a snapshot node or marks it deleted depending on metadata-version support.
- `__bch2_delete_dead_snapshots()` runs the deletion worker under `snapshot_delete.lock`.
- `bch2_delete_dead_snapshots()` respects `auto_snapshot_deletion`.
- `bch2_delete_dead_snapshots_async()` queues background work with write-reference protection.
- `bch2_delete_dead_interior_snapshots()` removes `NO_KEYS` interior nodes during recovery.
- `bch2_check_snapshot_needs_deletion()` marks the filesystem as needing cleanup when it sees `WILL_DELETE`, redundant interior nodes, or `NO_KEYS`.

Deletion flow:
- `check_should_delete_snapshot()` builds deletion sets:
  - `deleting_from_trees`
  - `delete_leaves`
  - `delete_interior`
  - `no_keys`
- `eytzinger_delete_list` is built from leaves and interior deletes for fast repeated membership checks.
- Snapshot-aware btrees are scanned and keys in dying snapshots are processed:
  - leaf snapshot keys are deleted
  - interior snapshot keys may be copied to the surviving child if not already overwritten
- Runtime deletion physically deletes leaves.
- Runtime deletion marks interior nodes `NO_KEYS`.
- Recovery later adjusts child depths/skiplists and physically deletes empty interior nodes.

Important paths:
- `delete_dead_snapshot_keys_v1()` scans all snapshot-aware btrees.
- `delete_dead_snapshot_keys_v2()` accelerates cleanup by scanning inodes first and then scanning extents/dirents/xattrs only for affected inode ranges.
- `skip_unrelated_snapshot_tree()` avoids scanning unrelated snapshot trees.
- `bch2_fix_child_of_deleted_snapshot()` repairs depth and skiplist fields before recovery-time interior deletion.

Important invariants:
- A snapshot node with two children cannot be deleted directly.
- Runtime physical deletion of interior nodes is rejected.
- Parent child pointers are normalized after mutation.
- Deleting the root updates or deletes the corresponding `snapshot_tree`.
- Delete progress state is protected separately from the main delete lock.

Research notes:
- This is one of the highest-risk paths in the group because it can delete large amounts of data-bearing metadata.
- The implementation is conservative: runtime handles key removal, recovery handles structural tree surgery.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/delete.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/format.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/format.h

This header defines persistent snapshot and subvolume key formats.

Subvolume format:
- `SUBVOL_POS_MIN`, `SUBVOL_POS_MAX` define valid key range.
- `BCACHEFS_ROOT_SUBVOL` is subvolume ID 1.
- `struct bch_subvolume` contains:
  - flags
  - snapshot ID
  - root inode
  - snapshot creation parent
  - filesystem path parent
  - creation time
- Subvolume flags:
  - read-only
  - is snapshot
  - unlinked

Snapshot format:
- `struct bch_snapshot` contains:
  - flags
  - parent
  - two child slots
  - associated subvolume
  - snapshot tree ID
  - depth
  - three skiplist entries
  - birth time
- Snapshot flags:
  - `WILL_DELETE`
  - `SUBVOL`
  - `DELETED`
  - `NO_KEYS`

Snapshot tree format:
- `struct bch_snapshot_tree` records:
  - master subvolume
  - root snapshot

Important design notes embedded in comments:
- Snapshot trees and subvolume creation trees are separate.
- Deleted snapshot keys may remain as explicit deleted markers to distinguish known-deleted IDs from unknown missing IDs.
- `NO_KEYS` exists because runtime interior-node removal cannot update tree metadata atomically.
- Comments explicitly warn that snapshot deletion should be cross-checked with subvolume state because incorrect deletion has high blast radius.

Research notes:
- This file is the on-disk ABI for snapshot/subvolume metadata.
- The flags here directly control recovery and deletion behavior in `check_snapshots.c`, `snapshot.c`, `subvolume.c`, and `delete.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/format.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.c

This file implements snapshot-tree formatting, validation, in-memory snapshot-table maintenance, ancestor queries, snapshot node creation, snapshot-aware overwrite checks, initialization, and diagnostic tree printing.

High-level snapshot design:
- Subvolumes point to snapshot IDs.
- Snapshot-aware btrees store snapshot IDs in `bpos.snapshot`.
- Snapshot visibility is ancestor-based: keys from ancestors are visible unless overwritten closer to the target snapshot.
- Snapshot creation is O(1): two child nodes are created under the current source snapshot, one for the new snapshot and one replacing the source subvolume snapshot.
- Snapshot deletion is deferred and batched.

Snapshot tree APIs:
- `bch2_snapshot_tree_to_text()`
- `bch2_snapshot_tree_validate()`
- `bch2_snapshot_tree_lookup()`
- `__bch2_snapshot_tree_create()`

Ancestor lookup:
- Early/recovery path: parent walk via `bch2_snapshot_is_ancestor_early()`.
- Fast path:
  - skiplist jumps for far ancestors
  - 128-bit in-memory ancestor bitmap for nearby ancestors
- Debug mode compares fast and slow paths and panics on mismatch with detailed traces.

In-memory table:
- `bch2_snapshot_t_mut()` grows `c->snapshots.table` with RCU replacement.
- Table index is `U32_MAX - id`, matching the design where newer/deeper IDs descend downward.
- `__bch2_mark_snapshot()` populates `snapshot_t` fields from btree keys and updates ancestor bitmap.
- `WILL_DELETE` marks the filesystem as needing snapshot deletion and may queue async cleanup.

Validation:
- `bch2_snapshot_validate()` checks:
  - key position range
  - parent ID ordering
  - normalized children
  - duplicate children
  - child ID ordering
  - normalized skiplist
  - skiplist entries not below parent

Traversal:
- `__bch2_snapshot_tree_next()` performs depth-first traversal using parent/child links.
- `bch2_snapshot_tree_next()` wraps it under RCU.

Overwrite queries:
- `__bch2_get_snapshot_overwrites()` collects ancestor snapshot IDs that overwrite a key.
- `__bch2_key_has_snapshot_overwrites()` checks whether any ancestor key exists for a position.

Creation:
- `create_snapids()` allocates new snapshot keys, initializes depth/skiplists, sets `SUBVOL`, and marks the in-memory table.
- `bch2_snapshot_node_create_children()` converts a leaf parent into an interior node with two children.
- `bch2_snapshot_node_create_tree()` creates a new snapshot tree root.
- `bch2_snapshot_node_create()` dispatches based on whether a parent exists.

Initialization and diagnostics:
- `bch2_snapshots_read()` builds the in-memory table in reverse order and schedules deletion passes if needed.
- `bch2_fs_snapshots_init_early()` initializes locks and deletion work.
- `bch2_snapshot_tree_keys_to_text()` prints a full snapshot tree with path and accounting info.

Important invariants:
- Parent IDs are greater than child IDs.
- A parent that gains children ceases to be a subvolume snapshot node.
- Snapshot table updates are RCU-visible and protected by `table_lock` during mutation.
- Ancestor bitmap updates tolerate readers observing partially updated state because slow paths remain valid.

Research notes:
- This is the core snapshot implementation file.
- The embedded documentation is unusually complete and explains the architectural difference from btrfs: bcachefs shares individual btree keys rather than cloning COW btrees.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.h

This header exposes snapshot and snapshot-tree bkey operations, in-memory lookup helpers, traversal macros, list helpers, fsck/recovery entry points, overwrite queries, deletion entry points, and subsystem init/exit APIs.

Key exported bkey operation structures:
- `bch2_bkey_ops_snapshot_tree`
- `bch2_bkey_ops_snapshot`

Core inline helpers:
- `__snapshot_t()` maps snapshot ID to table slot with `U32_MAX - id`.
- `snapshot_t()` RCU-loads from `c->snapshots.table`.
- `bch2_snapshot_tree()` returns tree ID.
- `bch2_snapshots_same_tree()` compares table tree IDs.
- `bch2_snapshot_parent*()` returns parent ID, with debug depth sanity checks.
- `bch2_snapshot_nth_parent()` walks ancestors.
- `bch2_snapshot_root()` finds root.
- `bch2_snapshot_id_state()` distinguishes empty/live/deleted.
- `bch2_snapshot_exists()` checks live state.
- `bch2_snapshot_is_leaf()` and `bch2_snapshot_is_internal_node()` classify nodes.
- `bch2_snapshot_live_descendent()` follows `NO_KEYS` interior nodes to the surviving live descendant.

Traversal and list utilities:
- `__for_each_snapshot_child`
- `for_each_snapshot_child`
- `snapshot_list_has_id()`
- `snapshot_list_has_ancestor()`
- `snapshot_list_add()`
- `snapshot_list_add_nodup()`
- `snapshot_list_merge()`

Public operations:
- Lookup:
  - `bch2_snapshot_lookup()`
  - `bch2_snapshot_get_subvol()`
- Creation:
  - `bch2_snapshot_node_create()`
- Checking/reconstruction:
  - `bch2_check_snapshot_trees()`
  - `bch2_check_snapshots_trans()`
  - `bch2_check_snapshots()`
  - `bch2_reconstruct_snapshots()`
- Snapshot-aware key validation:
  - `bch2_check_key_has_snapshot()`
- Overwrite tracking:
  - `bch2_get_snapshot_overwrites()`
  - `bch2_key_has_snapshot_overwrites()`
- Deletion:
  - `bch2_snapshot_node_set_deleted()`
  - `bch2_delete_dead_snapshots*()`
  - `bch2_delete_dead_interior_snapshots()`
- Lifecycle:
  - `bch2_snapshots_read()`
  - `bch2_fs_snapshots_exit()`
  - `bch2_fs_snapshots_init_early()`

Important invariants:
- `bch2_snapshot_is_ancestor()` rejects zero IDs with `EBUG_ON`.
- Fast overwrite checks skip non-snapshot-aware btrees and leaf snapshots.
- `SNAPSHOT_ID_deleted` is distinct from missing/empty, which is important for fsck decisions.

Research notes:
- This header forms the main contract used by snapshot, subvolume, fsck, and btree iterator code.
- Many helpers are inline because snapshot ancestry checks are on hot lookup paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/snapshot.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.c

This file implements subvolume bkey validation, fsck repair, lookup, read-only checks, unlink/delete, creation, initial root-subvolume creation, and upgrade support.

Fsck/checking:
- `bch2_subvolume_missing()` schedules `check_inodes` recovery for missing subvolumes.
- `check_subvol()` validates:
  - referenced snapshot exists
  - unlinked subvolumes are deleted
  - root subvolume has no filesystem path parent
  - `subvolume_children` index contains required parent-child entries
  - root inode exists and has correct `bi_subvol` and `bi_snapshot`
  - missing roots can be recreated as directories for lost+found reattachment
  - non-snapshot subvolumes must be the master subvolume of their snapshot tree
- `bch2_check_subvols()` scans `BTREE_ID_subvolumes`.
- `check_subvol_child()` validates reverse child-index entries.
- `bch2_check_subvol_children()` scans `BTREE_ID_subvolume_children`.

Bkey operations:
- `bch2_subvolume_validate()` checks key position, nonzero snapshot, and nonzero inode.
- `bch2_subvolume_to_text()` prints root inode, snapshot ID, parents, and flags.
- `bch2_subvolume_trigger()` maintains the `subvolume_children` btree when `fs_path_parent` changes.

Lookup and access:
- `bch2_subvol_has_children()` reports non-empty subvolume-child state.
- `bch2_subvolume_get()` fetches cached subvolume keys.
- `bch2_subvol_is_ro_trans()` returns `-EROFS` for read-only or unlinked subvolumes.
- `bch2_snapshot_get_subvol()` maps snapshot ID to its subvolume.
- `bch2_subvolume_get_snapshot()` maps subvolume ID to snapshot ID.

Deletion/unlink:
- `bch2_subvolumes_reparent()` reparents creation-tree children before deletion.
- `__bch2_subvolume_delete()`:
  - clears snapshot-tree master if deleting the master subvolume
  - deletes the subvolume key
  - marks the snapshot node deleted
- `bch2_subvolume_unlink()`:
  - sets `UNLINKED`
  - clears `fs_path_parent`
  - registers a commit hook to evict pagecache and queue actual deletion
- `bch2_subvolume_wait_for_pagecache_and_delete()` drains unlinked subvolumes after inode eviction.

Creation:
- `bch2_subvolume_create()` allocates a new subvolume ID, creates one or two snapshot nodes, updates the source subvolume snapshot when making a snapshot, initializes the new subvolume, and sets read-only/snapshot flags.
- For normal subvolume creation, one root snapshot node is created.
- For snapshot creation, two child snapshot nodes are created under the source snapshot.

Initialization/upgrade:
- `bch2_initialize_subvolumes()` creates:
  - root snapshot tree ID 1
  - root snapshot ID `U32_MAX`
  - root subvolume ID 1
- `bch2_fs_upgrade_for_subvolumes()` sets `bi_subvol` on the root inode.
- `bch2_fs_subvolumes_init_early()` initializes delayed pagecache deletion work.

Important invariants:
- Root subvolume is ID 1 and root snapshot starts at `U32_MAX`.
- Subvolume deletion is delayed until pagecache eviction prevents stale inode references.
- `creation_parent` records snapshot creation ancestry, separate from filesystem path parent and snapshot tree parentage.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.h

This header exposes the subvolume API and bkey ops.

Main exports:
- Fsck/checks:
  - `bch2_check_subvols()`
  - `bch2_check_subvol_children()`
- Bkey operations:
  - `bch2_subvolume_validate()`
  - `bch2_subvolume_to_text()`
  - `bch2_subvolume_trigger()`
  - `bch2_bkey_ops_subvolume`
- Lookup:
  - `bch2_subvol_has_children()`
  - `bch2_subvolume_get()`
  - `bch2_subvolume_get_snapshot()`
- Read-only checks:
  - `bch2_subvol_is_ro_trans()`
  - `bch2_subvol_is_ro()`
- Iteration helpers:
  - `bch2_btree_iter_peek_in_subvolume_max_type()`
  - `for_each_btree_key_in_subvolume_max_continue`
  - `for_each_btree_key_in_subvolume_max`
- Lifecycle:
  - `bch2_subvolume_unlink()`
  - `bch2_subvolume_create()`
  - `bch2_initialize_subvolumes()`
  - `bch2_fs_upgrade_for_subvolumes()`
  - `bch2_fs_subvolumes_init_early()`

Important behavior:
- Subvolume iteration helpers translate subvolume ID to snapshot ID and then set the btree iterator snapshot.
- `bch2_bkey_ops_subvolume` uses a minimum value size of 16 bytes for backward-compatible decoding.

Research notes:
- This header is the bridge between VFS-facing subvolume operations and snapshot-aware btree iteration.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/subvolume.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/types.h

This header defines in-memory snapshot subsystem data structures.

Key types:
- `snapshot_id_list`: darray of `u32` snapshot IDs.
- `IS_ANCESTOR_BITMAP`: 128 nearby ancestor bits.
- `struct snapshot_t`:
  - snapshot ID state: empty/live/deleted
  - parent
  - three skiplist entries
  - depth
  - two normalized children
  - associated subvolume ID
  - snapshot tree ID
  - nearby ancestor bitmap
- `struct snapshot_table`:
  - RCU header
  - flexible array of `snapshot_t`
- `struct snapshot_interior_delete`:
  - interior snapshot ID
  - surviving live child
- `interior_delete_list`: darray of interior delete records.
- `struct snapshot_delete`:
  - delete worker locks/state
  - running thread pointer
  - progress tracking
  - delete worklists
  - eytzinger delete list
- `struct bch_fs_snapshots`:
  - RCU snapshot table
  - table lock
  - create semaphore
  - deletion state
  - pagecache deletion work
  - unlinked-subvolume list and lock
- `subvol_inum`: packed pair of subvolume ID and inode number.

Important invariants:
- Snapshot IDs decrease down the tree.
- `children[0] >= children[1]` is the normalized form.
- RCU readers may tolerate partial ancestor-bitmap updates because they can fall back to skiplist/parent traversal.
- `subvol_inum` explicitly must not contain padding.

Research notes:
- This file captures the performance strategy for ancestry checks: skiplist, bitmap, parent walk.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/snapshots/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.c

This file implements bcachefs I/O clocks: approximate clocks advanced in sectors of I/O, plus timers that fire when the I/O clock reaches a sector count.

Main components:
- Timer ordering uses Linux `min_heap` over `struct io_timer *`, sorted by `expire`.
- `bch2_io_timer_add()`:
  - immediately fires timers already expired
  - avoids duplicate timer insertion
  - pushes future timers into the heap
- `bch2_io_timer_del()` removes a timer from the heap.
- `bch2_io_clock_schedule_timeout()` blocks the current task until an I/O-clock deadline.
- `bch2_kthread_io_clock_wait_once()` and `bch2_kthread_io_clock_wait()` combine I/O-clock waits with CPU-time `schedule_timeout()`, freezer handling, and kthread stop checks.
- `__bch2_increment_clock()` advances the atomic clock and fires all expired timers.
- `bch2_io_timers_to_text()` prints current clock and pending timers.
- `bch2_io_clock_init()` allocates per-CPU buffers and initializes the timer heap.
- `bch2_io_clock_exit()` frees timer heap and per-CPU buffers.

Important invariants:
- Timer heap is protected by `timer_lock`.
- Timers are fired while holding `timer_lock` in `__bch2_increment_clock()`; callbacks must be suitable for that context.
- Clock units are sectors, not wall-clock time.
- Per-CPU batching makes the clock approximate.

Research notes:
- The API is useful for throttling or scheduling based on I/O progress rather than time.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.h

This header declares I/O clock APIs and defines the inline fast path for clock advancement.

Exports:
- Timer operations:
  - `bch2_io_timer_add()`
  - `bch2_io_timer_del()`
- Wait operations:
  - `bch2_kthread_io_clock_wait_once()`
  - `bch2_kthread_io_clock_wait()`
  - `bch2_io_clock_schedule_timeout()`
- Clock advancement:
  - `__bch2_increment_clock()`
  - inline `bch2_increment_clock()`
- Diagnostics/lifecycle:
  - `bch2_io_timers_to_text()`
  - `bch2_io_clock_exit()`
  - `bch2_io_clock_init()`

Important behavior:
- `bch2_increment_clock()` accumulates sectors in a per-CPU buffer and only calls the global increment path when the per-CPU threshold is reached.
- It chooses read/write clock by indexing `c->io_clock[rw]`.

Research notes:
- The header keeps the high-frequency per-I/O path inline and defers heap/timer work to `clock.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/clock_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/clock_types.h

This header defines I/O clock and timer data structures.

Key definitions:
- `NR_IO_TIMERS` is `BCH_SB_MEMBERS_MAX * 3`.
- `IO_CLOCK_PCPU_SECTORS` is 128, the per-CPU batching threshold.
- `struct io_timer`:
  - callback function
  - secondary function/debug pointer
  - expiration sector
- `io_timer_heap`: min-heap of `struct io_timer *`.
- `struct io_clock`:
  - atomic sector clock
  - per-CPU sector buffer
  - max slop
  - spinlock
  - timer heap

Important behavior:
- Clocks and timers are expressed in sectors of I/O.
- Per-CPU buffering means the clock has bounded imprecision.

Research notes:
- This type header depends on the vendored min-heap implementation and the member-device limit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/clock_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.c

This file implements dynamic-array resize backing for the macro API in `darray.h`.

Core function:
- `__bch2_darray_resize_noprof()`:
  - grows only when `new_size > d->size`
  - rounds capacity to a power of two
  - checks multiplication overflow for `new_size * element_size`
  - uses `kvmalloc` for allocations below kernel limits and `vmalloc` for larger allocations
  - copies old elements
  - publishes new data pointer with `rcu_assign_pointer()`
  - frees old allocation normally or via RCU depending on caller
  - preserves embedded preallocated storage when present

Important behavior:
- The implementation supports arrays with inline preallocated storage.
- `have_prealloc` prevents freeing embedded storage.
- RCU resize mode delays freeing old backing storage.

Research notes:
- This file is the only non-macro implementation point for darrays.
- The version check handles Linux allocation API differences around 6.18.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.h

This header provides typed dynamic-array macros used widely throughout bcachefs.

Core abstractions:
- `DARRAY(type)` and `DARRAY_PREALLOCATED(type, nr)`.
- Named type generation:
  - `DEFINE_DARRAY_NAMED`
  - `DEFINE_DARRAY`
  - free-item variants
- Built-in darray typedefs for integer types and string arrays.

Operations:
- Initialization and cleanup:
  - `darray_init()`
  - `darray_exit()`
  - `darray_exit_free_item()`
- Iteration:
  - forward
  - reverse
  - from pointer
  - bounded max
- Resize:
  - `darray_resize_gfp()`
  - `darray_resize()`
  - `darray_resize_rcu()`
  - make-room variants
- Mutation:
  - `darray_push_gfp()`
  - `darray_push()`
  - `darray_pop()`
  - insert/remove helpers
- Search:
  - `darray_find_p()`
  - `darray_find()`
- Sorting/search layout:
  - normal sort
  - Eytzinger sort/find with one-based layout

Important invariants:
- Arrays track `nr`, `size`, `data`, and optional inline storage.
- Capacity is managed in element counts, not bytes.
- RCU resize requires callers to use the RCU-specific resize path.
- Eytzinger one-based helpers assume element 0 is reserved by caller; users push an empty sentinel before sorting.

Research notes:
- This macro library underpins snapshot ID lists, deletion lists, printbuf alignment scratch arrays, and many other bcachefs internals.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.c

This file implements enumerated references: a refcount abstraction that collapses to `percpu_ref` in normal builds and tracks refs per named user in debug builds.

Debug-mode behavior:
- `enumerated_ref_get()` increments a specific indexed ref.
- `__enumerated_ref_tryget()` increments if nonzero.
- `enumerated_ref_tryget()` also rejects dying refs.
- `enumerated_ref_put()` decrements a specific index, checks underflow, and completes shutdown only when all indexed refs are zero.
- Debug refs are allocated as an array of `atomic_long_t`.

Normal-mode behavior:
- Uses a single `percpu_ref`.
- `enumerated_ref_kill_cb()` invokes optional stop callback and completes shutdown.

Lifecycle:
- `enumerated_ref_init()` initializes completion, stop callback, and backend storage/refcount.
- `enumerated_ref_start()` reinitializes live refs.
- `enumerated_ref_stop_async()` begins shutdown.
- `enumerated_ref_stop()` waits for completion, printing outstanding refs every 10 seconds.
- `enumerated_ref_exit()` frees backend resources.
- `enumerated_ref_to_text()` prints indexed refs only in debug mode.

Important invariants:
- Debug mode requires `idx < ref->nr`.
- Stop completion is reinitialized on every stop.
- Debug start expects all indexed refs are zero before seeding each index.

Research notes:
- This is used where bcachefs wants production-fast refs but debug builds need attribution for leaks or stuck shutdowns.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.h

This header defines the public enumerated-ref API and inline production implementation.

Main API:
- `enumerated_ref_get()`
- `__enumerated_ref_tryget()`
- `enumerated_ref_tryget()`
- `enumerated_ref_put()`
- `enumerated_ref_is_zero()`
- `enumerated_ref_stop_async()`
- `enumerated_ref_stop()`
- `enumerated_ref_start()`
- `enumerated_ref_exit()`
- `enumerated_ref_init()`
- `enumerated_ref_to_text()`

Production-mode behavior:
- `get`/`tryget`/`put` call `percpu_ref_*`.
- `enumerated_ref_tryget()` uses `percpu_ref_tryget_live()`.
- `enumerated_ref_is_zero()` uses `percpu_ref_is_zero()`.

Debug-mode behavior:
- Function declarations are used so `enumerated_ref.c` can track refs per caller category.
- `enumerated_ref_is_zero()` scans all indexed debug refs.

Research notes:
- The API accepts an index even in production mode, giving callers stable attribution points with no production overhead beyond ignored parameters.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref_types.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref_types.h

This header defines `struct enumerated_ref`.

Fields:
- Debug mode:
  - number of categories
  - dying flag
  - per-category `atomic_long_t` refs
- Normal mode:
  - one `struct percpu_ref`
- Shared:
  - optional stop callback
  - shutdown completion

Research notes:
- The structure is intentionally dual-mode: detailed attribution for debug builds, minimal production refcounting otherwise.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/enumerated_ref_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.c

This file implements sorting into Eytzinger array layout, with generic compare/swap support and optimized swap routines.

Major components:
- Alignment detection for choosing word-sized swap paths.
- Swap implementations:
  - 64-bit word swaps
  - 32-bit word swaps
  - byte swaps
  - caller-provided wrapper swap
- Compare wrapper support for both `cmp_func_t` and `cmp_r_func_t`.
- `eytzinger1_sort_r()`:
  - converts array into one-based Eytzinger layout using heap-sort-like operations
  - supports private compare context
  - picks optimized swap mode when no swap function is supplied
  - calls `cond_resched()` during long operations
- `eytzinger1_sort()` wraps non-private compare/swap functions.
- `eytzinger0_sort_r()` and `eytzinger0_sort()` adapt zero-based arrays by shifting base pointer.

Important invariants:
- One-based layout assumes the caller has reserved index 0.
- Sorting uses `inorder_to_eytzinger1()` to map logical sorted positions to tree-layout positions.
- The code is generic over element size and comparison function.

Research notes:
- Snapshot deletion uses one-based Eytzinger darray helpers for fast membership checks.
- This implementation is performance-focused and mirrors kernel sort-style callback conventions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.h

This header defines traversal, index conversion, search, and sort declarations for arrays in Eytzinger layout.

Concept:
- Eytzinger layout stores a binary search tree in array order.
- It improves branch prediction and prefetching relative to classic binary search over sorted arrays.
- Both one-based and zero-based variants are provided.

One-based helpers:
- Child/left/right child calculation.
- First/last inorder node.
- Next/previous inorder traversal.
- Conversion between inorder index and Eytzinger index.
- `eytzinger1_for_each`.
- Exact find with `eytzinger1_find()` and `_find_r()`.

Zero-based helpers:
- Equivalent child/traversal/conversion wrappers.
- `eytzinger0_for_each` and reverse iteration.
- Range-style searches:
  - find greatest `<=`
  - find smallest `>`
  - find smallest `>=`
- Exact find with `eytzinger0_find()` and `_find_r()`.

Sort declarations:
- `eytzinger1_sort_r()`
- `eytzinger1_sort()`
- `eytzinger0_sort_r()`
- `eytzinger0_sort()`

Important invariants:
- Debug checks are active only under `EYTZINGER_DEBUG`.
- One-based find returns `0` for not found.
- Zero-based find returns `-1` for not found.
- One-based layout can have better cacheline alignment because levels start at powers of two.

Research notes:
- This is a reusable low-level performance utility, not bcachefs-specific in concept.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.c

This file implements fast unordered lists backed by a generic radix tree, an ID allocator, and per-CPU slot buffers.

Design:
- Items live in a `genradix` indexed by allocated integer slots.
- Slot numbers are allocated by `ida`.
- Per-CPU buffers cache free slot IDs to reduce contention.
- Adding/removing/iterating is mostly lockless except when refilling or draining per-CPU slot buffers.

Main functions:
- `fast_list_get_idx()` reserves a slot:
  - consumes a per-CPU cached slot if available
  - otherwise allocates a batch of slots with `ida`
  - preallocates the radix-tree pointer slot
- `fast_list_add()` reserves a slot and stores the item pointer.
- `fast_list_put_idx()` returns a reserved but unused slot to per-CPU cache or `ida`.
- `fast_list_remove()` clears the radix-tree item and frees the slot.
- `fast_list_exit()` frees per-CPU cached slots, warns if objects remain, destroys `ida`, and frees radix tree.
- `fast_list_init()` initializes storage and allocates per-CPU buffers.

Important invariants:
- Slot index 0 is treated as invalid/no slot.
- `fast_list_remove()` must be passed the index returned by add/get.
- Exit warns if allocated slots remain live.
- Per-CPU buffer manipulation disables local IRQs.

Research notes:
- This structure optimizes unordered membership/iteration where stable slot IDs are enough and ordering is irrelevant.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.h

This header defines `struct fast_list` and its public API.

Key structures:
- `struct fast_list`:
  - `GENRADIX(void *) items`
  - `ida slots_allocated`
  - per-CPU slot buffer

Iteration:
- `fast_list_iter_peek()` skips empty radix slots.
- `fast_list_for_each_from()` iterates from a starting index.
- `fast_list_for_each()` iterates from zero.

Mutation/API:
- `fast_list_set()` stores an item at an existing slot.
- `fast_list_get_idx()`
- `fast_list_put_idx()`
- `fast_list_add()`
- `fast_list_remove()`
- `fast_list_exit()`
- `fast_list_init()`

Important behavior:
- Iteration skips NULL entries.
- Callers can reserve slots early with `fast_list_get_idx()` to handle allocation failure before entering non-failing contexts.

Research notes:
- The header is intentionally small; most policy is in `fast_list.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/fifo.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/fifo.h

This header defines generic macro-based ring buffers/FIFOs with selectable index type.

Core types:
- `FIFO(type)`
- `FIFO_U16_IDX(type)`
- `FIFO_U32_IDX(type)`
- `FIFO_U64_IDX(type)`

Lifecycle:
- `init_fifo()` initializes indices, size, mask, and allocates power-of-two backing storage.
- `free_fifo()` frees backing storage.
- `fifo_swap()` swaps two FIFO objects.

Capacity/state:
- `fifo_used()`
- `fifo_free()`
- `fifo_empty()`
- `fifo_full()`

Element operations:
- `fifo_push_back_ref()`
- `fifo_push_front_ref()`
- `fifo_push_back()`
- `fifo_push_front()`
- `fifo_pop_front()`
- `fifo_pop_back()`
- aliases: `fifo_push`, `fifo_pop`, `fifo_peek`

Growth:
- `fifo_grow()` doubles backing storage.
- Growth preserves absolute front/back indices by copying old data into both halves of the new buffer.

Index helpers:
- Convert pointer to absolute or relative FIFO index.
- Access by relative FIFO index.

Iteration:
- forward entry iteration
- pointer iteration
- reverse pointer iteration

Important invariants:
- Backing size is rounded to a power of two and accessed by mask.
- Front/back are monotonic modulo the index type.
- Callers must handle allocation failure from `init_fifo()` and `fifo_grow()`.

Research notes:
- This is a generic low-level utility suitable for queues/deques where callers manage locking externally.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/fifo.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.c

This file implements incremental mean/variance helpers and exponentially weighted variants.

Core arithmetic:
- `u128_div()` divides a 128-bit value by a 64-bit divisor using staged 64/32-bit division.
- Exported for GPL use.

Unweighted stats:
- `mean_and_variance_get_mean()` returns `sum / n`, or zero for no samples.
- `mean_and_variance_get_variance()` computes `E[x^2] - mean^2` using 128-bit arithmetic.
- `mean_and_variance_get_stddev()` returns integer square root of variance.

Weighted stats:
- `mean_and_variance_weighted_update()` updates exponentially weighted mean and variance.
- Mean is stored shifted by `weight` for precision.
- Variance is also stored shifted and unshifted at readout.
- First update is special-cased by caller-supplied `initted`.
- Getters return weighted mean, variance, and stddev.

Important constraints:
- Caller must not change weight after updates.
- Caller must not directly inspect weighted fields as final values.
- Signed division by powers of two uses the helper from the header for round-toward-zero behavior.

Research notes:
- Comments cite an external statistical derivation paper and KUnit tests in this group verify expected behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.h

This header defines 128-bit helper arithmetic and mean/variance data structures.

128-bit abstraction:
- Uses native `unsigned __int128` in kernel builds when available and not PA-RISC.
- Falls back to `{ hi, lo }` representation otherwise.
- Provides:
  - `u64_to_u128()`
  - `u128_lo()`
  - `u128_hi()`
  - `u128_add()`
  - `u128_sub()`
  - `u128_shl()`
  - `u128_square()`
  - `u64s_to_u128()`
  - external `u128_div()`

Stats structures:
- `struct mean_and_variance`:
  - sample count
  - sum
  - sum of squares
- `struct mean_and_variance_weighted`:
  - shifted weighted mean
  - shifted weighted variance

Helpers:
- `fast_divpow2()` divides signed values by `2^d` rounding toward zero.
- `mean_and_variance_update()` increments count, sum, and 128-bit sum of squares.
- Declarations for unweighted and weighted getters/update.

Important behavior:
- Squaring uses `abs(v)`, so sample square magnitude is tracked without sign.
- `SQRT_U64_MAX` defines maximum integer square-root input scale.

Research notes:
- The header is portable across kernel architectures lacking native 128-bit integer support.
- The closing comment has a spelling typo: `MEAN_AND_VAIRANCE_H_`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance_test.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance_test.c

This file provides KUnit coverage for mean/variance and 128-bit helper arithmetic.

Test coverage:
- `mean_and_variance_basic_test()`:
  - verifies mean/variance over small repeated samples.
- `mean_and_variance_weighted_test()`:
  - checks weighted mean/variance for positive and negative sequences.
- `mean_and_variance_weighted_advanced_test()`:
  - checks longer positive and negative weighted sequences with weight 8.
- `do_mean_and_variance_test()`:
  - common harness comparing unweighted and weighted expected mean/stddev arrays.
- `mean_and_variance_test_1()`:
  - steady state, outlier, return to steady state.
- `mean_and_variance_test_2()`:
  - transition from one steady state to another.
- `mean_and_variance_fast_divpow2()`:
  - verifies signed power-of-two division behavior for positive and negative values.
- `mean_and_variance_u128_basic_test()`:
  - verifies 128-bit add, subtract, shift, square, and division.

KUnit registration:
- Test suite name: `"mean and variance tests"`.
- Module metadata describes bcachefs mean/variance unit tests.

Research notes:
- Expected values are hard-coded, making this a regression suite for integer rounding behavior.
- The tests cover negative weighted samples, which is important because signed right shift behavior is normalized through `fast_divpow2()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/mean_and_variance_test.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.c

This file implements `printbuf`, bcachefs’s reusable diagnostic string builder with best-effort allocation, indentation, tabstop alignment, and unit formatting.

Buffer growth:
- `bch2_printbuf_make_room_gfp()` ensures capacity including NUL.
- Fixed external buffers set overflow on insufficient room.
- Heap buffers grow to the next power of two.
- Allocation respects `atomic` mode and optional `may_vmalloc`.
- Allocation failures set flags rather than forcing callers to unwind.
- `bch2_printbuf_make_room()` uses `GFP_KERNEL`.

Printing:
- `bch2_prt_vprintf()` and `bch2_prt_printf()` retry after growth when formatted output does not fit.
- `bch2_printbuf_str()` returns `""` for empty/unallocated buffers.
- `bch2_printbuf_exit()` frees owned memory and poisons the pointer.

Indent/tabstops:
- Tracks current line, last field, indent, and tabstop index.
- `bch2_printbuf_tabstop_push/pop/reset()` manage preset tabstops.
- `bch2_printbuf_indent_add*()` and `bch2_printbuf_indent_sub()` manage indentation.
- `bch2_prt_newline()` emits newline plus current indentation.
- `bch2_prt_tab()` left-aligns to next tabstop.
- `bch2_prt_tab_rjust()` right-aligns previous field to next tabstop.
- `bch2_prt_bytes_indented()` post-processes embedded `\n`, `\t`, and `\r`.
- `bch2_printbuf_tabstop_align()` performs a two-pass elastic alignment over raw tab characters.

Formatting helpers:
- Human-readable unsigned/signed integers.
- Raw or human-readable units based on printbuf flags.
- String option list with selected item bracketed.
- Bitflag formatting from string tables.
- Bitflag vector formatting.

Important invariants:
- `printbuf_remaining()` reserves one byte for NUL.
- Printbuf functions favor partial output over hard errors.
- Atomic mode avoids sleeping allocations.
- Alignment post-processing may replace the owned buffer.

Research notes:
- Most files in this group use `printbuf` for fsck, status, and debug rendering.
- The design intentionally supports both kernel-space and userspace portability.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.h

This header defines the `printbuf` structure, initialization macros, inline primitive append helpers, and public formatting API.

Core structure:
- Buffer pointer, size, write position.
- Line/field/indent tracking.
- Atomic allocation nesting count.
- Flags:
  - allocation failure
  - heap allocated
  - overflow
  - suppressed
  - SI unit mode
  - human-readable units
  - has indent/tabstops
  - may vmalloc
- Inline tabstop array of 8 entries.

Initialization:
- `PRINTBUF` creates heap-allocated printbuf state.
- `PRINTBUF_EXTERN(buf, size)` uses caller-provided storage.
- `bch2_printbuf_init()` returns `PRINTBUF`.
- `DEFINE_CLASS(printbuf, ...)` adds cleanup support.

State helpers:
- Save/restore printbuf position, line, field, indent, tabstop.
- Reset with or without keeping tabstops.
- Remaining capacity and NUL termination helpers.

Primitive append helpers:
- reserved and checked char append
- repeated chars
- raw bytes
- strings
- lowercase/uppercase hex bytes

Guards:
- `printbuf_atomic` increments/decrements atomic allocation mode.
- `printbuf_indent`
- `printbuf_indent_nextline`

Public declarations:
- buffer growth
- printf/vprintf
- tabstop/indent management
- newline/tab/rjust tab
- tabstop alignment
- bytes with indentation
- unit/human-readable formatting
- options and bitflags

Important behavior:
- Callers can check `allocation_failure` if they need to return `-ENOMEM`.
- Otherwise, printbuf is designed for best-effort diagnostics.
- External buffers do not allocate and can overflow.

Research notes:
- This header is used broadly enough that its inline functions are effectively part of bcachefs’s diagnostic ABI.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/printbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.c

This file implements deferred processing of objects after RCU or SRCU grace periods, using per-CPU queues, radix-backed batches, linked-list fallback, and a workqueue drain path.

Core design:
- Each CPU has `struct rcu_pending_pcpu`.
- Pending objects are grouped by grace-period poll state.
- Objects normally go into a `genradix` vector for cache-efficient batch processing.
- If allocation fails or vmalloc-backed kvfree is involved, objects fall back to linked lists.
- A single RCU callback per CPU schedules work and rearms itself while pending objects remain.

Grace-period abstraction:
- Supports normal RCU or SRCU through wrapper helpers:
  - get current state
  - start poll
  - poll completion
  - barrier
  - call RCU/SRCU

Internal data structures:
- `struct rcu_pending_seq`:
  - genradix object vector
  - count
  - cursor
  - grace-period sequence
- `struct rcu_pending_list`:
  - linked-list head/tail
  - grace-period sequence
- `struct rcu_pending_pcpu`:
  - parent pointer
  - lock
  - CPU number
  - darray of radix batches
  - fixed oldstate lists plus one expired list
  - RCU callback
  - work item

Processing:
- `merge_expired_lists()` moves completed lists into the expired list.
- `__process_finished_items()` drains completed radix batches and expired lists outside the spinlock.
- Supported processing modes include:
  - kvfree-style freeing
  - call-rcu-style callback invocation
  - caller-provided `pending->process()` callback
- `rcu_pending_work()` loops until no finished items remain.

Enqueue:
- `__rcu_pending_enqueue()`:
  - picks current CPU pending queue
  - gets current grace-period state
  - optionally processes expired items when sleeping is allowed
  - inserts into radix batch when possible
  - falls back to linked list when allocation fails
  - arms/rearms RCU callback or starts a grace period if callback is already armed
- `rcu_pending_enqueue()` is the public generic enqueue wrapper.

Dequeue:
- `rcu_pending_dequeue()` scans current CPU.
- `rcu_pending_dequeue_from_all()` scans current CPU then all CPUs.
- `rcu_pending_dequeue_where()` and `_from_all_where()` remove the first object accepted by a non-sleeping claim predicate.

Exit/init:
- `rcu_pending_exit()` waits for callbacks/work to drain, checks queues are empty, frees per-CPU state.
- `rcu_pending_init()` allocates per-CPU state, initializes locks/work, stores SRCU pointer and process callback.

Important invariants:
- Per-CPU queue state is protected by `p->lock`.
- Queue draining happens outside the lock.
- Predicate dequeue functions call `try_claim` under lock and require it not to sleep.
- Exit loops through RCU/SRCU barriers and work flushing until no queue is pending or callback is armed.

Research notes:
- This is a sophisticated batching replacement for many individual RCU callbacks.
- The code has explicit kernel/userspace compatibility branches for RCU head linkage.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.h

This header exposes the `rcu_pending` deferred-processing API.

Types:
- `rcu_pending_process_fn`: callback invoked with the pending object and an `rcu_head`.
- `struct rcu_pending`:
  - per-CPU state pointer
  - optional SRCU struct
  - process callback

Public functions:
- Enqueue:
  - `rcu_pending_enqueue()`
- Dequeue:
  - `rcu_pending_dequeue()`
  - `rcu_pending_dequeue_from_all()`
  - `rcu_pending_dequeue_where()`
  - `rcu_pending_dequeue_from_all_where()`
- Lifecycle:
  - `rcu_pending_exit()`
  - `rcu_pending_init()`

Important behavior:
- Passing an SRCU pointer switches the implementation from RCU to SRCU grace periods.
- Dequeue-where predicates are used to claim only selected pending objects.

Research notes:
- The header hides batching and grace-period mechanics from users; callers see a deferred-processing queue keyed by RCU completion.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/rcu_pending.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/seqmutex.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/seqmutex.h

This header defines a small mutex plus sequence counter utility.

Structure:
- `struct seqmutex`:
  - `struct mutex lock`
  - `u32 seq`

API:
- `seqmutex_init()` initializes the mutex.
- `seqmutex_trylock()` attempts to lock without incrementing sequence.
- `seqmutex_lock()` locks and increments `seq`.
- `seqmutex_unlock()` unlocks and returns the sequence observed while locked.
- `seqmutex_relock()` tries to reacquire only if `seq` still matches the supplied value.

Important behavior:
- `seqmutex_relock()` double-checks sequence before and after `mutex_trylock()`.
- A caller can unlock, perform work, and later relock only if no intervening full lock acquisition changed the sequence.

Research notes:
- This is a compact optimistic-relock helper for code that needs to drop a mutex and detect intervening mutation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/seqmutex.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.c -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.c

This file implements SipHash with configurable compression/finalization rounds. It is BSD-3-Clause licensed and derived from OpenBSD/FreeBSD lineage.

Core functions:
- `SipHash_Rounds()` executes SipRound for a requested number of rounds.
- `SipHash_CRounds()` mixes one 8-byte little-endian message block.
- `SipHash_Init()` initializes state from a 128-bit key and fixed SipHash constants.
- `SipHash_Update()` streams arbitrary-length input:
  - tracks buffered bytes
  - completes partial blocks
  - processes full 8-byte blocks
  - stores trailing bytes
- `SipHash_Final()` writes little-endian 64-bit digest.
- `SipHash_End()` pads the final block with total byte count, runs finalization, zeroes context, and returns digest.
- `SipHash()` is the one-shot helper.

Important behavior:
- Uses unaligned little-endian loads for message blocks.
- The context is cleared on `SipHash_End()`.
- Round counts are caller-selected, enabling SipHash-2-4 and SipHash-4-8 through macros in the header.

Research notes:
- This is standalone cryptographic/hash utility code rather than bcachefs-specific logic.
- The implementation returns a 64-bit keyed PRF suitable for short inputs.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.h -->
# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.h

This header declares the SipHash API and convenience macros.

Constants:
- Block length: 8 bytes.
- Key length: 16 bytes.
- Digest length: 8 bytes.

Types:
- `SIPHASH_CTX`:
  - four 64-bit state words
  - 8-byte partial block buffer
  - byte count
- `SIPHASH_KEY`:
  - two little-endian 64-bit key halves

API:
- `SipHash_Init()`
- `SipHash_Update()`
- `SipHash_End()`
- `SipHash_Final()`
- `SipHash()`

Convenience macros:
- SipHash-2-4:
  - `SipHash24_Init`
  - `SipHash24_Update`
  - `SipHash24_End`
  - `SipHash24_Final`
  - `SipHash24`
- SipHash-4-8:
  - `SipHash48_Init`
  - `SipHash48_Update`
  - `SipHash48_End`
  - `SipHash48_Final`
  - `SipHash48`

Research notes:
- License is BSD-3-Clause, unlike the GPL/LGPL bcachefs utility files around it.
- The API exposes round counts through generic functions and safer named macros for common variants.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.h -->