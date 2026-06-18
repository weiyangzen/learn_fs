# Group Research: group_929_linux_dm_sources_block_storage_linux_dm_drivers_md_md_h_sources_bloc_10d50aab75a9

Scope: `Docs/research_subset_a.md` / `sources/block-storage/linux-dm`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/md.h

## Purpose
Internal header for the Linux MD software RAID driver. It defines the central runtime data structures, state flags, personality interface, sysfs helpers, thread wrappers, and exported MD core entry points used by MD personalities such as raid0/1/5/10, linear, multipath, and clustering code.

## Main Definitions
- `struct md_rdev`: per-component-device state, including data/superblock offsets, block devices, bad-block tracking, pending I/O count, read/write error counters, PPL journal placement, replacement/journal roles, sysfs handles, and raid-disk role fields.
- `enum flag_bits`: per-rdev state bits such as `Faulty`, `In_sync`, `Blocked`, `WriteMostly`, `WantReplacement`, `Replacement`, `Journal`, `FailFast`, and `CollisionCheck`.
- `struct mddev`: array-level state, including personality pointer, disks list, superblock metadata, reshape/recovery state, locking, bitmap information, biosets, flush handling, cluster state, and queue capability state.
- `enum mddev_flags` and `enum mddev_sb_flags`: array runtime and superblock-update flags.
- `enum recovery_flags`: sync/recovery/reshape control flags.
- `struct md_personality`: callback table implemented by each MD layout personality. It covers request handling, run/start/free, status, error handling, hot add/remove, spare activation, sync requests, resize, reshape, quiesce, takeover, and consistency-policy changes.
- `struct md_thread`, `struct md_io_acct`, `struct md_sysfs_entry`: MD-specific wrappers for kernel threads, accounting bios, and sysfs attributes.

## Important Behavior and Contracts
- Per-rdev state is modeled so `Faulty` and `In_sync` should not both be set.
- `MD_FAILFAST` deliberately excludes `REQ_FAILFAST_DRIVER`; the comments explain MD wants minimal retries for device/transport failures but not the driver category.
- `is_badblock()` offsets logical sectors by `rdev->data_offset` before calling the generic badblocks helper, then translates the result back to array-relative sectors.
- `mddev_lock()`, `mddev_lock_nointr()`, and `mddev_trylock()` wrap `reconfig_mutex`; comments document lock ordering with `disk->open_mutex` and `open_mutex`.
- `mddev->lock` protects a specific set of fields and state transitions: flush bio, rdev superblocks/events, `MD_CHANGE_*` clearing, `in_sync`, bitmap pointers, resync min/max, and recovery-running flag transitions.
- Sysfs link helpers skip replacement and journal devices and tolerate missing `kobj.sd`.
- `rdev_dec_pending()` triggers recovery-needed wakeup when the final pending I/O drains on a faulty rdev.
- `is_mddev_broken()` marks `MD_BROKEN` and warns when an rdev’s disk is no longer live.

## Dependencies
Includes block layer, badblocks, kobject/sysfs, mutex/timer/wait/workqueue, and `md-cluster.h`. Exports prototypes implemented in `md.c`, bitmap code, cluster code, and individual RAID personalities.

## Role in Repository
This is the public internal contract for MD code in `drivers/md`. It does not implement the array algorithms itself; it defines the shared state and callback surface that the implementation files depend on.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/md.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/Kconfig -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/Kconfig

## Purpose
Kconfig entry for the device-mapper persistent-data metadata library.

## Main Definition
- `config DM_PERSISTENT_DATA`
  - Type: `tristate`
  - Depends on: `BLK_DEV_DM`
  - Selects: `LIBCRC32C`, `DM_BUFIO`
  - Help text describes it as an immutable on-disk data structure support library for device-mapper targets, especially thin provisioning.

## Role in Repository
This controls whether the persistent-data library is built into the kernel, as a module, or omitted. The selected dependencies match the implementation: checksums use CRC32C, and block caching/locking is built on `dm-bufio`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/Makefile -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/Makefile

## Purpose
Build recipe for the `dm-persistent-data` object.

## Main Definitions
- `obj-$(CONFIG_DM_PERSISTENT_DATA) += dm-persistent-data.o`
- `dm-persistent-data-objs` is composed from:
  - `dm-array.o`
  - `dm-bitset.o`
  - `dm-block-manager.o`
  - `dm-space-map-common.o`
  - `dm-space-map-disk.o`
  - `dm-space-map-metadata.o`
  - `dm-transaction-manager.o`
  - `dm-btree.o`
  - `dm-btree-remove.o`
  - `dm-btree-spine.o`

## Role in Repository
The Makefile assembles the whole persistent metadata library into one module/object selected by `DM_PERSISTENT_DATA`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.c

## Purpose
Implementation of persistent dense arrays on top of the persistent btree and transaction manager. The design packs many fixed-size values into “array blocks” and indexes those blocks from a one-level btree, reducing space overhead versus one btree key per value.

## Main Structures
- `struct array_block`: on-disk block header containing checksum, maximum entries, current entries, value size, and expected block number.
- `struct resize`: helper state for resize operations.

## Important Behavior
- Array blocks are validated by `array_validator`; write preparation stamps the block number and CRC32C-derived checksum, and read validation checks both.
- `calc_max_entries()` computes how many fixed-size values fit after the array header.
- `dm_array_info_init()` embeds the user value type and sets up a btree whose leaf values are `__le64` references to array blocks.
- Btree leaf values use `block_inc`, `block_dec`, and `block_equal` so array-block references are reference counted by the transaction manager.
- `__block_dec()` checks the referenced array block’s refcount. If the block is about to lose its last reference, it decrements all contained values before decrementing the block itself.
- Updates are copy-on-write:
  - `shadow_ablock()` looks up the backing array block, shadows it through `dm_tm_shadow_block()`, increments contained values if required, and reinserts the new block reference into the btree when a real copy occurred.
  - `dm_array_set_value()` decrements the overwritten value unless the value type says old and new are equal, increments the new value if needed, and returns a new root.
- Resize supports both growth and shrink:
  - Growth fills existing tail blocks, inserts full new array blocks, and optionally inserts a final partial block.
  - Shrink removes whole trailing blocks and trims the final block, invoking value decrement callbacks.
- `dm_array_new()` bulk-populates a new array via a callback and is more efficient than repeated resize/set calls.
- `dm_array_walk()` walks the btree, then each packed array block in index order.
- Cursor API wraps a btree cursor and keeps the current array block locked while iterating values.

## Public API Implemented
`dm_array_info_init`, `dm_array_empty`, `dm_array_resize`, `dm_array_new`, `dm_array_del`, `dm_array_get_value`, `dm_array_set_value`, `dm_array_walk`, `dm_array_cursor_begin`, `dm_array_cursor_end`, `dm_array_cursor_next`, `dm_array_cursor_skip`, `dm_array_cursor_get_value`.

## Dependencies
Uses `dm-btree`, `dm-space-map`, and `dm-transaction-manager`. On-disk values are little-endian and use sparse annotations through `__dm_bless_for_disk` / `__dm_unbless_for_disk`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.h

## Purpose
Public interface and documentation for persistent dense arrays.

## Main Definitions
- `struct dm_array_info`: describes array value type and transaction-manager binding. It is reusable across multiple array instances.
- `typedef value_fn`: callback used by `dm_array_new()` to populate initial values.
- `struct dm_array_cursor`: cursor state combining an array info, a btree cursor, current array block, current array-block header, and current entry index.

## API Contract
- Arrays are immutable between transactions. Update operations return a new root.
- Callers must store the logical array size outside the array root.
- Arrays are dense and indexed from zero; out-of-bounds access returns `-ENODATA`.
- Value types reuse `struct dm_btree_value_type` so array values can participate in reference counting.
- Values passed to write APIs must be in on-disk format and marked with the sparse disk annotations.
- Cursors provide efficient ordered iteration and are intended for cases that need lockstep traversal with another structure.

## Exposed Functions
`dm_array_info_init`, `dm_array_empty`, `dm_array_resize`, `dm_array_new`, `dm_array_del`, `dm_array_get_value`, `dm_array_set_value`, `dm_array_walk`, and cursor begin/end/next/skip/get.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-array.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.c

## Purpose
Persistent bitset implementation built as a thin wrapper around `dm_array` of 64-bit little-endian words.

## Main Behavior
- `BITS_PER_ARRAY_ENTRY` is 64.
- `dm_disk_bitset_init()` initializes an embedded `dm_array_info` with a simple 64-bit value type.
- `dm_bitset_new()` packs callback-provided bits into 64-bit words and creates the underlying array in bulk.
- `dm_bitset_resize()` converts bit counts to word counts and grows new words as all-zero or all-one depending on `default_value`.
- A one-word cache is maintained in `struct dm_disk_bitset`:
  - `current_index`
  - `current_bits`
  - `current_index_set`
  - `dirty`
- `get_array_entry()` flushes the cached dirty word when switching to another word. This means even test/read operations can return a new root if a previous mutation was cached.
- `dm_bitset_flush()` writes the dirty cached word to the underlying array and clears cache state.
- `set`, `clear`, and `test` operate on the cached word after loading/flushing as needed.
- Cursor API wraps `dm_array_cursor` and presents bit-by-bit iteration across the packed words.

## Public API Implemented
`dm_disk_bitset_init`, `dm_bitset_empty`, `dm_bitset_new`, `dm_bitset_resize`, `dm_bitset_del`, `dm_bitset_flush`, `dm_bitset_set_bit`, `dm_bitset_clear_bit`, `dm_bitset_test_bit`, `dm_bitset_cursor_begin`, `dm_bitset_cursor_end`, `dm_bitset_cursor_next`, `dm_bitset_cursor_skip`, `dm_bitset_cursor_get_value`.

## Edge Cases
- The underlying array detects out-of-bounds word access, but the final word may contain unused bits; the caller must track the bitset’s true logical size.
- `dm_bitset_cursor_begin()` returns `-ENODATA` for an empty bitset.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.h

## Purpose
Public interface and usage documentation for persistent bitsets.

## Main Definitions
- `struct dm_disk_bitset`: per-bitset object containing embedded `dm_array_info` and a one-word mutable cache.
- `typedef bit_value_fn`: callback used by `dm_bitset_new()` to populate bits.
- `struct dm_bitset_cursor`: bit iterator over the packed array words.

## API Contract
- Bitsets are immutable between transactions; updates return a new root.
- The caller must store the logical number of bits outside the root.
- Reads may flush cached writes and therefore may also return a new root.
- Callers should flush cached changes before using a cursor.
- Final-word unused bits are not bounds checked by the persistent array layer.

## Exposed Functions
Initialization, create/new/resize/delete, set/clear/test/flush, and cursor begin/end/next/skip/get.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-bitset.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.c

## Purpose
Block cache, lock, validation, and checksum layer for persistent metadata. It wraps `dm-bufio` behind `struct dm_block_manager` and exposes `struct dm_block` without leaking bufio internals.

## Main Structures
- Optional debug-only `struct block_lock`: detects recursive metadata lock acquisition and limits concurrent holders.
- `struct buffer_aux`: per-buffer auxiliary state storing the current validator, write-lock flag, and optional debug lock.
- `struct dm_block_manager`: wraps a `dm_bufio_client` and read-only state.

## Important Behavior
- `dm_block_location()` and `dm_block_data()` map an opaque `dm_block` to its bufio block number and data pointer.
- Block validators are sticky per cached buffer. Re-locking a cached block with a different validator returns `-EINVAL`.
- `dm_bm_read_lock()` reads through bufio, optionally takes a debug read lock, validates the buffer, and returns the block.
- `dm_bm_write_lock()` refuses writes in read-only mode, reads the existing block, takes a write lock, validates it, and returns mutable data.
- `dm_bm_write_lock_zero()` creates/zeros a block without reading it and sets the validator directly.
- `dm_bm_unlock()` marks write-locked buffers dirty before releasing them.
- `dm_bm_flush()` writes dirty buffers unless the manager is read-only.
- `dm_bm_checksum()` is CRC32C seeded with all ones and XORed with caller-provided salt.

## Debug Locking
When `CONFIG_DM_DEBUG_BLOCK_MANAGER_LOCKING` is enabled:
- Recursive locking by the same task is detected.
- Optional stack tracing can report the prior acquisition site.
- Writers are prioritized.
- `dm_bm_read_try_lock()` can return `-EWOULDBLOCK`.

## Exports and Module Metadata
Exports the block-manager API and declares GPL module metadata for the immutable metadata library.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.h

## Purpose
Public block-manager interface for persistent metadata users.

## Main Definitions
- `typedef uint64_t dm_block_t`: metadata block number type.
- Opaque `struct dm_block` and `struct dm_block_manager`.
- `struct dm_block_validator`: caller-supplied validator with `prepare_for_write` and `check` callbacks.

## API Contract
- Multiple readers or one writer may hold a block.
- Validators verify read data and stamp/prepare dirty data before writeback.
- Validator changes are only safe when using `dm_bm_write_lock_zero()`.
- `dm_bm_flush()` ensures dirty metadata reaches disk.
- Read-only mode blocks write lock, zero write lock, and flush.
- `dm_bm_prefetch()` requests cached read-ahead for metadata blocks.

## Exposed Functions
Creation/destruction, block size/device size, read/write/try/zero locks, unlock, flush, prefetch, read-only toggles, and checksum helper.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-block-manager.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-internal.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-internal.h

## Purpose
Private header shared by btree implementation files.

## Main Definitions
- `enum node_flags`: `INTERNAL_NODE` and `LEAF_NODE`.
- `struct node_header`: common on-disk btree node header with checksum, flags, block number, entry counts, value size, and padding.
- `struct btree_node`: header followed by flexible key array; values are stored after the maximum key region.
- `struct ro_spine`: rolling two-node read-lock stack.
- `struct shadow_spine`: rolling two-node write/shadow stack plus current root.

## Helper APIs
- Block/node helpers: `bn_read_lock`, `new_block`, `unlock_block`.
- Reference helper: `inc_children`.
- Spine operations: init/exit/step/pop/current/parent/root.
- Layout helpers: `key_ptr`, `value_base`, `value_ptr`, `value64`.
- Search helper: `lower_bound`.
- Shared validator: `btree_node_validator`.
- Internal value type setup for `__le64` child pointers: `init_le64_type`.
- `btree_get_overwrite_leaf()` for single-level overwrite access.

## Role in Repository
This header defines the private on-disk btree node format and copy-on-write traversal helpers used by insertion, removal, cursor, and space-map overflow manipulation.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-remove.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-remove.c

## Purpose
Implements single-key and range leaf removal for persistent btrees, including top-down copy-on-write rebalancing.

## Removal Strategy
The file documents the core invariant: non-root nodes should not drop below a minimum entry threshold. Before descending toward the target, child nodes are rebalanced or merged so the final removal can proceed without violating occupancy constraints while holding only a small rolling lock set.

## Main Helpers
- `node_shift`, `node_copy`, `delete_at`: low-level key/value movement inside nodes.
- `merge_threshold()`: occupancy threshold based on node capacity.
- `struct child`: shadowed child node and its index.
- `init_child()` shadows a child, increments children if required, and patches the parent pointer to the shadow.
- `rebalance2()` / `__rebalance2()`: merge or rebalance two siblings.
- `rebalance3()` / `__rebalance3()`: merge center into siblings or redistribute across three siblings.
- `rebalance_children()`: chooses root collapse, two-way rebalance, or three-way rebalance before descent.
- `remove_raw()`: shadows down the tree and prepares the target leaf for deletion.
- `remove_nearest()` and `remove_one()`: support range leaf removal.

## Public API Implemented
- `dm_btree_remove()`: removes one key path from a possibly multi-level btree and decrements the removed value through the configured value type.
- `dm_btree_remove_leaves()`: removes leaf entries in `[first_key, end_key)` and returns the count removed.

## Important Behavior
- Rebalancing happens on children of the current node, avoiding a special root case except when the root has one child, where child contents can be copied into the root.
- When merging nodes, the removed node’s block refcount is decremented without decrementing children that remain referenced after data movement.
- Parent separator keys are updated after redistribution.
- Removal returns a new root through the shadow spine.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-remove.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-spine.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-spine.c

## Purpose
Btree node validation plus read-only and shadow spine traversal primitives.

## Main Behavior
- `btree_node_validator` validates:
  - Stored block number matches actual block location.
  - Checksum matches the node contents.
  - `max_entries` and `nr_entries` fit in the block.
  - Node is marked internal or leaf.
- `node_prepare_for_write()` stamps block number and checksum before writeback.
- `bn_read_lock()` reads a validated btree node through the transaction manager.
- `bn_shadow()` shadows a node and increments children when shadowing requires copied child references to gain references.
- `new_block()` and `unlock_block()` are small transaction-manager wrappers.

## Spine Behavior
- `ro_spine` keeps up to two read-locked nodes and drops the oldest as traversal advances.
- `shadow_spine` keeps up to two shadowed/writeable nodes and remembers the current shadow root.
- `shadow_step()` shadows a block, records the first shadow as root, and advances the rolling stack.

## Internal Value Type
`init_le64_type()` creates a btree value type for child block pointers:
- `inc` and `dec` operate on adjacent runs through `dm_tm_with_runs()`.
- `equal` compares little-endian 64-bit values.

## Role in Repository
This file isolates node validation and rolling lock mechanics, letting the higher-level btree algorithms express lookup, insertion, and removal in terms of spine steps.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree-spine.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.c

## Purpose
Core implementation of persistent copy-on-write B+ trees with 64-bit keys, arbitrary fixed-size values, optional multi-level nested btrees, walking, lookup, insertion, and cursors.

## Main Concepts
- Node data layout is keys first, then a parallel values area sized by `header.value_size`.
- `calc_max_entries()` chooses a capacity divisible by three, supporting denser two-into-three split behavior.
- Value reference semantics are delegated to `struct dm_btree_value_type`.
- Updates are copy-on-write through `shadow_spine`.

## Major Functional Areas
- Creation/deletion:
  - `dm_btree_empty()` creates an empty leaf node.
  - `dm_btree_del()` deletes a whole tree with an explicit heap stack to avoid recursion in most of the deletion path.
- Lookup:
  - `btree_lookup_raw()` traverses with `ro_spine`.
  - `dm_btree_lookup()` supports nested btrees by iterating levels.
  - `dm_btree_lookup_next()` finds the next key after a supplied key.
- Insertion:
  - `btree_insert_raw()` shadows down to the leaf, ensures space, patches parent child pointers, and returns insertion index.
  - Full nodes may be rebalanced with siblings, split one-into-two, split two-into-three, or split beneath the root.
  - Overwrites decrement old values unless equal, then copy the new on-disk value.
  - `dm_btree_insert_notify()` reports whether the operation inserted or overwrote.
- Key discovery:
  - `dm_btree_find_lowest_key()` and `dm_btree_find_highest_key()` walk down to first/last keys.
- Walking and cursors:
  - `dm_btree_walk()` is single-level only and recursive.
  - `dm_btree_cursor_*` maintains an explicit cursor stack and can prefetch leaf-referenced blocks.

## Public API Implemented
`dm_btree_empty`, `dm_btree_del`, `dm_btree_lookup`, `dm_btree_lookup_next`, `dm_btree_insert`, `dm_btree_insert_notify`, `dm_btree_find_highest_key`, `dm_btree_find_lowest_key`, `dm_btree_walk`, `dm_btree_cursor_begin`, `dm_btree_cursor_end`, `dm_btree_cursor_next`, `dm_btree_cursor_skip`, `dm_btree_cursor_get_value`.

## Important Constraints
- `dm_btree_walk()` asserts `info->levels <= 1`.
- `btree_get_overwrite_leaf()` only works with single-level btrees and existing keys.
- Insert paths require values to be in on-disk little-endian format and annotated with the sparse disk macros.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.h

## Purpose
Public interface for persistent hierarchical B+ trees.

## Main Definitions
- Sparse annotation macros:
  - `__dm_written_to_disk`
  - `__dm_reads_from_disk`
  - `__dm_bless_for_disk`
  - `__dm_unbless_for_disk`
- `struct dm_btree_value_type`: value size plus optional `inc`, `dec`, and `equal` callbacks for reference-counted values.
- `struct dm_btree_info`: transaction-manager binding, number of nested tree levels, and leaf value type.
- `struct dm_btree_cursor`: cursor state with fixed maximum depth.

## API Contract
- Btrees store 64-bit keys and fixed-size values.
- Multi-level support means nested btrees, not the depth of one tree.
- Deletion of an entire tree is O(n) and may block; callers should keep it off I/O paths.
- Insert and remove operations return new roots.
- Value callbacks are responsible for reference-count side effects of copied, overwritten, and deleted values.
- Walk is single-level only, while lookup/insert/remove can use multiple `keys[]` levels.

## Exposed Functions
Create/delete, lookup/lookup-next, insert/insert-notify, remove/remove-leaves, lowest/highest key discovery, walk, and cursor operations.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-persistent-data-internal.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-persistent-data-internal.h

## Purpose
Tiny internal utility header for persistent-data implementation files.

## Main Definition
- `dm_hash_block(dm_block_t b, unsigned hash_mask)`: hashes a metadata block number by multiplying the low unsigned portion by a large prime and applying the provided mask.

## Role in Repository
Used by transaction-manager shadow tables and space-map index-entry cache hashing. It is intentionally private to the persistent-data implementation.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-persistent-data-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.c

## Purpose
Low-level implementation shared by disk and metadata space maps. It stores per-block reference counts using bitmap blocks for small counts and an overflow btree for larger counts.

## On-Disk Format
- Bitmap index:
  - Each `disk_index_entry` points to a bitmap block and stores `nr_free` plus `none_free_before`.
  - Metadata space maps store a fixed array of index entries in one metadata index block.
  - Disk space maps store index entries in a btree and cache them in memory.
- Bitmap block:
  - `disk_bitmap_header` with checksum and block number.
  - Two bits per metadata block:
    - `0`: unused
    - `1`: refcount 1
    - `2`: refcount 2
    - `3`: overflow / many
- Overflow refcount btree:
  - Maps block number to a 32-bit little-endian refcount for counts above 2.

## Validators
- `index_validator` checks metadata index block checksum and block location.
- `dm_sm_bitmap_validator` checks bitmap block checksum and block location.

## Major Functions
- `sm_ll_init()`: initializes common `ll_disk` fields and btree descriptors.
- `sm_ll_extend()`: adds bitmap blocks and index entries for newly addressable blocks.
- `sm_ll_lookup_bitmap()` and `sm_ll_lookup()`: read bitmap and overflow counts.
- `sm_ll_find_free_block()` scans index entries and bitmap blocks for a free block.
- `sm_ll_find_common_free_block()` ensures allocation is free in both old and current transaction views.
- `sm_ll_insert()`: sets an exact refcount, maintaining bitmap, overflow btree, free counts, and allocation delta.
- `sm_ll_inc()` / `sm_ll_dec()`: range refcount mutation with per-bitmap chunking and overflow handling.
- `sm_ll_commit()`: writes changed index state.
- `sm_ll_new_metadata()` / `sm_ll_open_metadata()`: fixed-index metadata-space-map setup.
- `sm_ll_new_disk()` / `sm_ll_open_disk()`: btree-index disk-space-map setup.

## Important Behavior
- `none_free_before` accelerates free scanning inside bitmap blocks.
- `nr_allocated` is updated when refcount transitions between zero and nonzero.
- Overflow manipulation uses `btree_get_overwrite_leaf()` when possible for in-place update of an already-shadowed leaf.
- Bitmap locks may be temporarily dropped while acquiring overflow btree leaves because overflow updates can allocate metadata.
- Disk index-entry cache has 64 direct-mapped entries and writes dirty entries back on eviction/commit.

## Role in Repository
This file is the allocator/refcount engine used by both metadata-block space maps and data-block space maps.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.h

## Purpose
Shared low-level declarations and on-disk structures for space-map implementations.

## Main Definitions
- `struct disk_index_entry`: bitmap block pointer plus free-space summary.
- `struct disk_metadata_index`: checksummed fixed array of metadata index entries.
- `struct ll_disk`: shared low-level space-map state, including transaction manager, bitmap and overflow btree info, block geometry, roots, cached metadata index, callbacks, and index-entry cache.
- `struct disk_sm_root`: compact persistent root containing block count, allocated count, bitmap root, and refcount root.
- `struct disk_bitmap_header`: checksummed bitmap block header.
- Function pointer types for loading/saving/opening/committing index variants.

## Constants
- `MAX_METADATA_BITMAPS = 255`
- `IE_CACHE_SIZE = 64`
- `ENTRIES_PER_BYTE = 4`

## Exposed Internal Functions
Low-level extend, lookup, find-free, insert, inc/dec, commit, and create/open functions for metadata and disk variants.

## Role in Repository
This header separates shared low-level space-map mechanics from the two public wrappers: `dm-space-map-disk.c` and `dm-space-map-metadata.c`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.c

## Purpose
Implements the public `dm_space_map` interface for a general on-disk space map whose bitmap index is btree-backed.

## Main Structure
- `struct sm_disk`:
  - Embedded `struct dm_space_map sm`
  - Current low-level map `ll`
  - Previous committed map `old_ll`
  - Allocation search hint `begin`
  - `nr_allocated_this_transaction`

## Behavior
- Allocation must find a block free in both `old_ll` and current `ll`, preserving rollback safety.
- `get_nr_blocks()` reports the old committed length.
- `get_nr_free()` subtracts allocations made in the current transaction from the old committed free count.
- `set_count`, `inc_blocks`, and `dec_blocks` delegate to common low-level operations and update transaction allocation delta.
- `new_block()` searches from `begin` to the end, then wraps to `[0, begin)` if needed.
- `commit()` commits low-level index changes, snapshots current `ll` into `old_ll`, and resets transaction allocation delta.
- `copy_root()` serializes `disk_sm_root`.

## Public API Implemented
- `dm_sm_disk_create()`
- `dm_sm_disk_open()`

## Role in Repository
This is the space-map implementation suitable for general persistent structures where the index can grow via a btree.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.h

## Purpose
Public constructor interface for disk-backed space maps.

## API
- `dm_sm_disk_create(struct dm_transaction_manager *tm, dm_block_t nr_blocks)`: creates a new disk space map.
- `dm_sm_disk_open(struct dm_transaction_manager *tm, void *root, size_t len)`: opens an existing disk space map from a serialized root.

## Important Note
The header documents two-phase construction because the transaction manager and space map refer to each other.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-disk.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.c

## Purpose
Implements `dm_space_map` for metadata blocks, including bootstrap allocation and recursion handling needed when the space map allocates blocks for its own updates.

## Main Structures
- `struct threshold`: edge-triggered free-space threshold callback state.
- `struct block_op`: queued increment/decrement operation.
- `struct bop_ring_buffer`: fixed-size ring buffer for deferred recursive operations.
- `struct sm_metadata`: metadata space-map state, including current and old low-level maps, allocation hint, recursion count, current transaction allocations, uncommitted block ops, and threshold state.

## Recursion Handling
Metadata updates can allocate metadata blocks, which would recursively update the same space map. The file handles that with:
- `in()` / `out()` recursion-depth tracking.
- `add_bop()` to queue inc/dec operations while recursing.
- `apply_bops()` to apply queued operations when unwinding the outermost recursion.
- `combine_errors()` to preserve the first meaningful error.

## Normal Space-Map Operations
- `get_count()` and `count_is_more_than_one()` account for queued uncommitted operations.
- `set_count()` forbids recursive use.
- `inc_blocks()` and `dec_blocks()` queue when recursing or apply immediately otherwise.
- `new_block()` finds a block free in both old and current maps, increments it, tracks allocation count, and fires threshold callbacks when free space crosses the registered threshold.
- `commit()` commits low-level state, snapshots `ll` into `old_ll`, and resets transaction allocation count.
- `extend()` temporarily switches to bootstrap mode so new blocks are allocated from the extension region, then repeatedly applies bootstrap increments and commits until stable.

## Bootstrap Mode
`bootstrap_ops` is a temporary `dm_space_map` implementation used during initial creation and extension:
- Allocates linearly from `begin`.
- Treats blocks before `begin` as allocated.
- Does not support root copy, set_count, or normal extension.
- Queues inc/dec operations to be applied once the real low-level structures are ready.

## Public API Implemented
- `dm_sm_metadata_init()`
- `dm_sm_metadata_create()`
- `dm_sm_metadata_open()`

## Important Limits
- `MAX_RECURSIVE_ALLOCATIONS = 1024`
- Metadata map size is capped through `DM_SM_METADATA_MAX_BLOCKS` from the header.

## Role in Repository
This is the self-hosting allocator for device-mapper metadata blocks. It is the key piece that lets persistent-data structures allocate blocks transactionally while their allocator metadata is itself stored in persistent-data structures.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.h

## Purpose
Public interface and limits for metadata space maps.

## Main Definitions
- `DM_SM_METADATA_BLOCK_SIZE`: metadata block size in sectors for 4 KiB metadata blocks.
- `DM_SM_METADATA_MAX_BLOCKS`: maximum metadata blocks supported by the fixed metadata index design.
- `DM_SM_METADATA_MAX_SECTORS`: sector limit derived from max blocks.

## API
- `dm_sm_metadata_init()`: allocates an unbound metadata space-map object.
- `dm_sm_metadata_create()`: creates a fresh metadata space map with a transaction manager, block count, and superblock reservation.
- `dm_sm_metadata_open()`: opens an existing metadata space map from a serialized root.

## Important Note
Like the disk variant, construction is two-phase because metadata space maps and transaction managers depend on each other.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-metadata.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map.h

## Purpose
Generic interface for persistent reference-counted space maps.

## Main Definition
`struct dm_space_map` is a function-table object that tracks block reference counts and supports transactional allocation.

## Operations
- Lifecycle: `destroy`
- Capacity: `extend`, `get_nr_blocks`, `get_nr_free`
- Refcounts: `get_count`, `count_is_more_than_one`, `set_count`, `inc_blocks`, `dec_blocks`
- Allocation: `new_block`
- Commit/root: `commit`, `root_size`, `copy_root`
- Notification: `register_threshold_callback`

## Inline Wrappers
The header provides inline wrappers such as `dm_sm_inc_block`, `dm_sm_dec_block`, `dm_sm_new_block`, and `dm_sm_copy_root`.

## Important Contract
- Newly extended space must be committed before allocation.
- Blocks free in the current transaction may not be immediately reusable if they were allocated in the previous transaction; rollback safety affects `get_nr_free()` semantics.
- `new_block()` increments the returned block’s refcount.
- Threshold callback registration is optional; wrappers return `-EINVAL` if unsupported.

## Role in Repository
This is the abstraction consumed by the transaction manager. Concrete implementations are the disk and metadata space maps.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.c

## Purpose
Implements the transaction manager that enforces immutable persistent metadata updates through copy-on-write shadowing, block reference counting, and two-phase commit.

## Main Structures
- `struct prefetch_set`: small hashed set of metadata blocks to prefetch after non-blocking lookup misses.
- `struct shadow_info`: entry in the current transaction’s shadow table.
- `struct dm_transaction_manager`:
  - clone flag and real manager pointer
  - block manager
  - space map
  - shadow hash table
  - prefetch set

## Important Behavior
- Shadow table records blocks already made writable in the current transaction. If a block is already a private shadow and not shared, later shadow requests can become direct write locks.
- `dm_tm_new_block()` allocates through the space map, zero-write-locks the new block, and records it as a shadow.
- `dm_tm_shadow_block()`:
  - checks whether the original is shared.
  - if already shadowed and not shared, returns a write lock on the original.
  - otherwise allocates a new block, decrements the original refcount, reads/copies original contents, write-locks the new block, and records the new block as a shadow.
  - returns `inc_children` to tell callers whether copied child references need reference increments.
- `dm_tm_pre_commit()` commits the space map and flushes dirty metadata.
- `dm_tm_commit()` wipes the shadow table, unlocks the caller’s superblock, and flushes again so the superblock lands after other metadata.
- Non-blocking clones support read-only fast-path lookups via `dm_bm_read_try_lock()`. Misses add blocks to the real manager’s prefetch set and return `-EWOULDBLOCK`; mutating operations reject clones.
- `dm_tm_with_runs()` coalesces adjacent little-endian block-number values into ranges before calling inc/dec range callbacks.

## Public API Implemented
`dm_tm_create_non_blocking_clone`, `dm_tm_destroy`, `dm_tm_pre_commit`, `dm_tm_commit`, `dm_tm_new_block`, `dm_tm_shadow_block`, `dm_tm_read_lock`, `dm_tm_unlock`, `dm_tm_inc`, `dm_tm_inc_range`, `dm_tm_dec`, `dm_tm_dec_range`, `dm_tm_with_runs`, `dm_tm_ref`, `dm_tm_block_is_shared`, `dm_tm_get_bm`, `dm_tm_issue_prefetches`, `dm_tm_create_with_sm`, `dm_tm_open_with_sm`.

## Construction
`dm_tm_create_with_sm()` and `dm_tm_open_with_sm()` tie the recursive knot between transaction manager and metadata space map by first allocating the space map object, then creating the transaction manager, then creating or opening the metadata space map.

## Role in Repository
This is the central coordinator for all persistent-data structures. Btrees, arrays, bitsets, and space maps depend on it for allocation, shadowing, reference counts, locks, and commit ordering.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.h

## Purpose
Public interface and contracts for the persistent-data transaction manager.

## Core Contract
The transaction manager scopes a metadata transaction and enforces immutability of on-disk data structures. Clients should not mutate metadata blocks directly through the block manager.

## Two-Phase Commit
1. Make all non-superblock changes, then call `dm_tm_pre_commit()` to flush them.
2. Lock and update the superblock, then call `dm_tm_commit()`, which unlocks and flushes the superblock. No other blocks should be updated during this second phase.

## Write Access
- `dm_tm_new_block()` returns a zeroed, write-locked new block.
- `dm_tm_shadow_block()` allocates and copies a block for copy-on-write mutation, drops the original reference, and tells callers if copied children need refcount increments.
- `dm_tm_read_lock()` and `dm_tm_unlock()` provide validated read access.

## Refcount Helpers
`dm_tm_inc`, `dm_tm_inc_range`, `dm_tm_dec`, `dm_tm_dec_range`, `dm_tm_ref`, `dm_tm_block_is_shared`, and `dm_tm_with_runs`.

## Non-Blocking Clone
`dm_tm_create_non_blocking_clone()` creates a fast-path read clone where mutating/blocking operations return `-EWOULDBLOCK`; missed blocks can later be prefetched with `dm_tm_issue_prefetches()` on the real manager.

## Construction Helpers
`dm_tm_create_with_sm()` and `dm_tm_open_with_sm()` create/open a transaction manager paired with a metadata space map, reserving the superblock location from allocation.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-transaction-manager.h -->