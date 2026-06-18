# subset-b-004041 Research

Grouped research for Linux MD core header and device-mapper persistent-data library files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/md.h -->
# sources/distributed-fs/ceph-client/drivers/md/md.h

## Purpose
Defines the internal contract for the Linux MD RAID core. It is the shared header used by MD personalities, bitmap/cluster helpers, sysfs/control paths, and device-mapper RAID integration to describe component devices, arrays, recovery state, metadata persistence, and request handling entry points.

## Important APIs, Types, And Functions
The key device structure is `struct md_rdev`, which records a member block device, metadata location, data offsets, role numbers, bad-block log, pending I/O counters, read/write error state, replacement/journal/PPL metadata, and flags from `enum flag_bits`. Inline helpers such as `is_badblock()`, `rdev_has_badblock()`, `is_rdev_broken()`, `rdev_dec_pending()`, and `rdev_blocked()` centralize bad-block and failed-device state checks.

The central array structure is `struct mddev`. It contains the active personality, gendisk and optional dm gendisk, disk list, superblock versions, event counters, reshape geometry, sync-thread state, recovery flags, sysfs nodes, bitmap configuration, bio sets, cluster hooks, suspend and reconfiguration locks, safemode timer state, and metadata update accounting. `enum sync_action`, `enum recovery_flags`, `enum mddev_flags`, and `enum md_ro_state` define the state machines used by recovery, reshape, degraded operation, clean/dirty metadata transitions, and read-only behavior.

`struct md_personality` is the personality vtable: `make_request`, `run`, `start`, `free`, `status`, error handling, hot add/remove, sync/reshape callbacks, resize/size methods, quiesce, takeover, consistency policy changes, and bitmap-sector translation. Public prototypes expose core operations such as `md_run()`, `md_start()`, `md_stop()`, `md_handle_request()`, `md_update_sb()`, `md_do_sync()`, `md_check_recovery()`, `md_error()`, `md_flush_request()`, and stacking-limit helpers.

## Control Flow
Array setup flows through `md_alloc()`, `mddev_init()`, metadata import via ioctl/sysfs helpers, and `md_run()`/`md_start()` invoking the selected personality callbacks. Normal I/O enters through `md_handle_request()` and then the personality `make_request` method. Writes are bracketed by `md_write_start()`, `md_write_inc()`, and `md_write_end()` so safemode, bitmap, superblock, and pending-write state can remain coherent.

Recovery control is represented by `mddev->recovery`, `last_sync_action`, `curr_resync`, `sync_thread`, and helpers such as `md_sync_action()`, `md_check_recovery()`, `md_reap_sync_thread()`, `md_idle_sync_thread()`, and freeze/unfreeze wrappers. Reconfiguration paths should suspend I/O, take `reconfig_mutex` through helpers such as `mddev_suspend_and_lock()`, update array/member state, then unlock and resume.

## State And Persistence
Persistent MD state includes superblock format fields, event counters, clean/dirty transitions, reshape position, member role and data offsets, bad-block logs, bitmaps, PPL/journal state, and cluster metadata. The header documents lock responsibilities: `reconfig_mutex` protects configuration, `open_mutex` protects stop/open races, `lock` protects superblock and bitmap transition fields, and `active_io`/`writes_pending` gate suspend and safemode behavior.

## Dependencies And Integration Points
The header depends on block-layer, kobject/sysfs, badblocks, workqueue/timer, percpu-ref, bio-set, trace, and RAID userspace ABI headers. It integrates MD personalities (`linear`, `raid0`, `raid1`, `raid4/5/6`, `raid10`), clustered MD, bitmap implementations, device-mapper RAID, sysfs controls, ioctl/autostart paths, and queue-limit stacking.

## Risks
The major risk is state-machine drift: flags in `md_rdev`, `mddev->flags`, `sb_flags`, and `recovery` are tightly coupled to metadata writes, sysfs state, and personality callbacks. Lock-order violations can deadlock with block-device open paths or recovery threads. Incorrect event or reshape fields can make arrays assemble stale data after a crash. Bad-block and `Blocked`/`FaultRecorded` handling are data-integrity sensitive because writes may be blocked until metadata records a failure.

## Test Signals
Useful signals include MD personality build coverage, mdadm assemble/create/stop/grow tests, degraded and replacement disk tests, bad-block injection, check/repair/resync sysfs exercises, suspend/resume and safemode clean/dirty transitions, dm-raid stacking tests, and lockdep/KASAN/KCSAN coverage around reconfiguration and recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/md.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/Kconfig

## Purpose
Adds the `DM_PERSISTENT_DATA` kernel configuration symbol for the device-mapper persistent-data library. The library provides immutable on-disk metadata structures used by targets such as thin provisioning, cache metadata, and other dm components that need transactional btrees, space maps, arrays, and bitsets.

## Important APIs, Types, And Functions
This file defines one `tristate` config item. It depends on `BLK_DEV_DM`, selects `CRC32`, and selects `DM_BUFIO`. There are no C APIs here; the config symbol controls compilation of the object set listed by the companion Makefile.

## Control Flow
During Kconfig resolution, enabling a dependent dm target can select or require `DM_PERSISTENT_DATA`. When enabled built-in or as a module, the Makefile builds `dm-persistent-data.o` from the persistent-data source files. The selected dependencies ensure checksum helpers and dm-bufio cache infrastructure are present.

## State And Persistence
The Kconfig entry has no runtime state. Its persistence impact is indirect: enabling it compiles the code that reads and writes persistent metadata formats, and disabling it removes those helpers and any targets that depend on them.

## Dependencies And Integration Points
Integration points are the kernel configuration system, device-mapper block-device support, CRC helpers, and dm-bufio. Device-mapper targets that use these library APIs rely on this symbol being available in their build dependency chain.

## Risks
Incorrect dependency declarations would fail at link time or allow targets to build without required checksum/bufio support. Because the symbol is `tristate`, module/built-in ordering must be compatible with dm targets that consume exported symbols from the library.

## Test Signals
Build tests should cover `DM_PERSISTENT_DATA=y`, `m`, and disabled configurations where dependent targets are also disabled. Link checks should confirm all exported persistent-data symbols resolve for dm-thin/cache-style users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Makefile -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/Makefile

## Purpose
Defines how the persistent-data library is built into `dm-persistent-data.o` when `CONFIG_DM_PERSISTENT_DATA` is enabled.

## Important APIs, Types, And Functions
The object list includes `dm-array.o`, `dm-bitset.o`, `dm-block-manager.o`, `dm-space-map-common.o`, `dm-space-map-disk.o`, `dm-space-map-metadata.o`, `dm-transaction-manager.o`, `dm-btree.o`, `dm-btree-remove.o`, and `dm-btree-spine.o`. This ordering records the library components that collectively expose the persistent metadata API.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_DM_PERSISTENT_DATA)` and links the listed implementation objects into one module or built-in object. Consumers see a single persistent-data library even though functionality is split across block manager, transaction manager, btree, array/bitset, and space-map layers.

## State And Persistence
The Makefile has no runtime state. It is significant for persistence because omitting one object would remove part of the transactional metadata stack and could leave exported APIs unresolved.

## Dependencies And Integration Points
The file integrates with the Linux Kbuild system and the Kconfig symbol in the same directory. It also documents layering: common structures and transaction/block management are linked with higher-level containers and allocation maps.

## Risks
The main risk is object list drift. A new source file that provides exported symbols must be added here, and deleting or renaming a source must be reflected here. Build-only validation catches most errors, but subtle module layout changes can affect symbol export availability for dm targets.

## Test Signals
Compile with the persistent-data library built-in and modular. Run `modpost`/link checks for unresolved symbols and build the dm targets that use this library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.c

## Purpose
Implements a persistent, immutable array abstraction on top of a single-level dm btree. Instead of storing one btree entry per logical array element, the btree maps packed array-block indexes to blocks containing many fixed-size values, reducing metadata space and lookup overhead for dense arrays.

## Important APIs, Types, And Functions
The on-disk leaf payload is `struct array_block`, containing checksum, max entry count, current entry count, value size, and expected block number. `array_validator` verifies checksum and block-location identity on read and refreshes both on write.

Public APIs are `dm_array_info_init()`, `dm_array_empty()`, `dm_array_resize()`, `dm_array_new()`, `dm_array_del()`, `dm_array_get_value()`, `dm_array_set_value()`, `dm_array_walk()`, and cursor functions. Internal helpers include `element_at()`, `fill_ablock()`, `trim_ablock()`, `lookup_ablock()`, `shadow_ablock()`, `insert_ablock()`, `insert_new_ablock()`, and resize helpers for grow/shrink operations.

The array btree stores `__le64` block pointers. Its value type uses `block_inc()`, `block_dec()`, and `block_equal()` so array block reference counts are managed through the transaction manager. When an array block's refcount drops to one and is about to be deleted, `__block_dec()` reads the block and decrements every contained value through the caller-supplied value type.

## Control Flow
Creation starts with an empty btree root. Resizing computes the number of full array blocks and tail entries before and after the operation. Growth shadows or adds tail blocks, fills new entries with the default value, increments value references, and inserts new array blocks into the btree. Shrink removes trailing btree entries and trims the new tail block, decrementing removed values.

Lookups compute `array_index = logical_index / max_entries`, resolve the array block through the btree, verify the entry is within `nr_entries`, copy the on-disk value, and unlock. Updates shadow the array block via the transaction manager, reinsert the shadow into the btree when the block location changes, compare/decrement/increment values as needed, and return a new root. Walking and cursors iterate the btree in order, loading each packed block and exposing values in index order.

## State And Persistence
The array is immutable between transactions: mutating calls return a new root, and callers may keep the old root alive by incrementing its reference. Array length is intentionally not stored in the array root; callers must persist the logical size elsewhere. Checksums and block numbers protect array-block reads from corruption or misplaced blocks.

## Dependencies And Integration Points
This file depends on `dm-btree`, `dm-transaction-manager`, `dm-space-map` semantics through refcounts, dm-bufio block validation via the block manager, and device-mapper logging. It is used by higher-level metadata such as bitsets and dm target metadata arrays.

## Risks
The array depends on correct caller-supplied value-type callbacks. Missing `inc`/`dec` callbacks for values that contain block references can leak or prematurely free metadata blocks. The size is external, so callers can read or write semantically out of bounds if they lose the stored length. Cache/transaction correctness depends on reinserting shadowed array blocks whenever the physical block changes. `trim_ablock()` and growth paths are sensitive to off-by-one errors in tail-block calculations.

## Test Signals
Focused tests should create, grow, shrink, delete, walk, and cursor-iterate arrays across empty, one-block, exact-block, and multi-block sizes. Reference-count tests should use value types that count `inc`/`dec` calls. Fault tests should corrupt checksums/block numbers and expect validator failures. Snapshot-style tests should retain an old root while updating a new root and verify both views remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.h

## Purpose
Declares the dm persistent array API. The array provides dense, fixed-size, on-disk values with btree-like immutable update semantics and more compact storage than a plain one-entry-per-value btree.

## Important APIs, Types, And Functions
`struct dm_array_info` binds an array type to a transaction manager and a `struct dm_btree_value_type`. The same info object can describe many arrays with identical value semantics. `dm_array_info_init()` fills this structure and wires array-block pointer reference counting into an internal btree info.

The main lifecycle APIs are `dm_array_empty()`, `dm_array_new()`, `dm_array_resize()`, and `dm_array_del()`. Access APIs are `dm_array_get_value()`, `dm_array_set_value()`, and `dm_array_walk()`. `value_fn` lets callers populate a new array efficiently through callbacks. The cursor API (`struct dm_array_cursor`, `dm_array_cursor_begin()`, `dm_array_cursor_next()`, `dm_array_cursor_skip()`, `dm_array_cursor_get_value()`, `dm_array_cursor_end()`) supports efficient ordered iteration without repeated lookup calls.

## Control Flow
Callers initialize `dm_array_info`, create or open a root saved in their own metadata, resize as needed, and then get/set values by zero-based index. Mutations return a `new_root`, preserving immutable update behavior. Walking and cursors traverse index order over packed array blocks.

## State And Persistence
The header explicitly states that the array does not expose or store its logical length in a standalone place; the caller must persist the size next to the root. Values passed into mutating APIs must be in on-disk little-endian format, and the Sparse annotations inherited from `dm-btree.h` express that contract. Old roots can remain valid if callers increment them through the transaction manager before update.

## Dependencies And Integration Points
The API is built on `dm-btree.h` and the transaction manager. It is a lower-level dependency for `dm-bitset` and can be used by dm target metadata that needs dense arrays such as mappings, hints, or compact counters.

## Risks
Misremembering the external size is the main API risk. The final partial array block will not independently know the total logical length beyond its stored entries. Callers must also pair values with correct value-type callbacks to keep referenced metadata blocks alive. Cursor users must not keep `value_le` pointers after moving or ending the cursor.

## Test Signals
Header-level contract tests should cover external size tracking, immutable root behavior, little-endian value handling, cursor lifetime rules, and value-type callback invocation during resize, overwrite, and delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.c

## Purpose
Implements a persistent bitset as a thin wrapper over `dm_array` storing 64-bit little-endian words. It adds bit-level set, clear, test, resize, creation, deletion, flush, and cursor operations while using a one-word cache to reduce repeated array updates.

## Important APIs, Types, And Functions
The fixed value type `bitset_bvt` stores `__le64` words and has no reference-count callbacks because words do not reference blocks. `dm_disk_bitset_init()` initializes the embedded array info and resets cache state. `dm_bitset_new()` packs bit callback results into array words through `pack_bits()`. `dm_bitset_resize()` grows or shrinks the underlying array in units of 64-bit words, filling new words with all-zero or all-one defaults.

The cache is managed by `read_bits()`, `get_array_entry()`, and `dm_bitset_flush()`. Set, clear, and test operations compute the array word and bit offset; changing to a different word flushes a dirty cached word back through `dm_array_set_value()`. Cursor functions wrap `dm_array_cursor` and expose bit-by-bit iteration with skip support.

## Control Flow
A caller initializes one `dm_disk_bitset` per bitset instance, creates or opens a root, and resizes to the desired bit count. `dm_bitset_set_bit()` and `dm_bitset_clear_bit()` call `get_array_entry()`, possibly flushing the old cached word and reading the new word, then mutate `current_bits` and mark it dirty. `dm_bitset_test_bit()` may also flush if it must switch words, so even read-like operations can return a new root. `dm_bitset_flush()` writes the cached word and clears dirty state.

## State And Persistence
Persistent state is the underlying array of 64-bit words. Runtime state is the cached `current_index`, `current_bits`, and dirty flag in `struct dm_disk_bitset`. Like `dm_array`, the logical bit count is external; the implementation cannot detect out-of-range bits inside the final stored word. Dirty cached changes are not persisted until flushed or until an operation switches array entries and flushes implicitly.

## Dependencies And Integration Points
This file depends on `dm-array`, `dm-transaction-manager`, Linux bitops, and device-mapper logging. It is suitable for metadata that needs compact persistent booleans, with caller-managed transaction commits.

## Risks
The cache makes root handling subtle: a test or set that flushes a previous word may update the root even if the requested bit is read-only. Callers must pass and store returned roots consistently. Forgetting `dm_bitset_flush()` before committing, walking, or using a cursor can lose cached updates. Bounds are only checked at the array-word level, so caller-maintained bit counts remain critical.

## Test Signals
Tests should toggle multiple bits in the same word and across word boundaries, verify root changes on implicit flush, resize to non-64-bit-aligned sizes, create from a callback, iterate with cursors and skips, and confirm unflushed updates are not visible to cursor reads until flushed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.h

## Purpose
Declares the persistent bitset API built on `dm_array`. It exposes bit-indexed operations with immutable root updates while documenting the one-word cache and caller-managed size contract.

## Important APIs, Types, And Functions
`struct dm_disk_bitset` embeds `struct dm_array_info` and stores cache fields `current_index`, `current_bits`, `current_index_set`, and `dirty`. `dm_disk_bitset_init()` prepares the instance. Lifecycle and construction APIs are `dm_bitset_empty()`, `dm_bitset_new()`, `dm_bitset_resize()`, and `dm_bitset_del()`. Access APIs are `dm_bitset_set_bit()`, `dm_bitset_clear_bit()`, `dm_bitset_test_bit()`, and `dm_bitset_flush()`.

`struct dm_bitset_cursor` wraps `struct dm_array_cursor` and tracks remaining entries, array index, bit index, and current word. Cursor APIs begin, end, advance, skip, and read the current boolean.

## Control Flow
The caller initializes a bitset object, obtains a root, resizes or creates contents, uses set/clear/test operations while updating any returned root, flushes cached updates, and then commits through the surrounding transaction manager. Cursor users should flush first, then begin iteration with the logical bit count.

## State And Persistence
The bitset stores words on disk, but the logical bit count is external. The final word may contain unused bits that are not automatically bounded by the library. Runtime cache state is part of `struct dm_disk_bitset`, so unlike `dm_array_info`, the object is not purely type-level metadata and should not be shared across independent bitset instances.

## Dependencies And Integration Points
The header depends on `dm-array.h` and indirectly on btree/transaction-manager APIs. It integrates with metadata users that need persistent boolean maps and ordered scans.

## Risks
The most important risk is failing to flush dirty cache state or failing to preserve `new_root` returned from operations. Sharing a `dm_disk_bitset` instance across roots would mix cache state. Callers must guard against out-of-range bits within the final word.

## Test Signals
Test signals include root update handling on set/clear/test, explicit flush before commit, cursor iteration after flush, boundary behavior at 63/64/65 bits, and independent cache state for multiple bitset instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-bitset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.c

## Purpose
Implements the persistent-data block manager using dm-bufio. It provides cached block reads, write locks, dirty tracking, validation callbacks, read-only mode, prefetch, flush, and optional debug locking for metadata blocks.

## Important APIs, Types, And Functions
`struct dm_block_manager` wraps a `dm_bufio_client` and a read-only flag. `struct dm_block` is intentionally opaque and cast internally to `struct dm_buffer`. `struct buffer_aux` records the validator associated with a cached block and whether the current lock is write-owned; in debug builds it also contains a custom `block_lock`.

Public APIs include `dm_block_manager_create()`, `dm_block_manager_destroy()`, `dm_block_manager_reset()`, `dm_bm_block_size()`, `dm_bm_nr_blocks()`, `dm_bm_read_lock()`, `dm_bm_write_lock()`, `dm_bm_read_try_lock()`, `dm_bm_write_lock_zero()`, `dm_bm_unlock()`, `dm_bm_flush()`, `dm_bm_prefetch()`, read-only toggles, `dm_block_location()`, `dm_block_data()`, and `dm_bm_checksum()`.

Validators are central. `dm_block_manager_write_callback()` calls `prepare_for_write()` before a dirty buffer is written. `dm_bm_validate_buffer()` calls `check()` when a cached buffer first receives a validator and rejects validator mismatches on later use, except that zero-write locks can intentionally set the validator for overwritten blocks.

## Control Flow
Creation allocates the manager and creates a dm-bufio client with auxiliary data callbacks. Read locks call `dm_bufio_read()`, acquire a read block lock in debug builds, validate, and return the block. Write locks are similar but check read-only mode and acquire an exclusive lock. `dm_bm_write_lock_zero()` obtains a new/zeroed buffer with no disk read and sets its validator. Unlock marks write-locked buffers dirty before releasing them. Flush writes dirty buffers through dm-bufio.

The debug `block_lock` implementation detects recursive acquisitions by the same task, limits concurrent readers, gives write waiters priority, and can print stack traces when enabled.

## State And Persistence
Runtime state lives in dm-bufio cache buffers and `buffer_aux` metadata. Persistent behavior comes from validator write callbacks, checksum preparation, block-number stamping by higher layers, dirty marking, and `dm_bm_flush()` forcing dirty metadata to the device. Read-only mode blocks write locks and flushes.

## Dependencies And Integration Points
The file depends on dm-bufio, crc32c, device-mapper logging, Linux slab/module/rwsem/task APIs, and optional stacktrace support. All higher persistent-data structures use this layer through the transaction manager or direct prefetch calls.

## Risks
Validator mismatch is a serious integrity issue because the same block cannot safely be interpreted as two metadata formats. Failing to unlock write blocks leaves dirty buffers unflushed and locks held. Recursive locks can deadlock without debug detection. Read-only mode must be respected by all mutating callers. The checksum helper uses a specific crc32c initialization/xor convention that must match validator implementations.

## Test Signals
Tests should cover checksum validation failures, block-number mismatch failures, write-lock dirty marking, zero-write lock without prior read, read-only `-EPERM`, read try-lock `-EWOULDBLOCK`, recursive-lock debug behavior, prefetch smoke tests, and flush ordering through transaction-manager tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.h

## Purpose
Declares the block manager API used by the persistent-data library. It abstracts cached metadata block access, validation, locking, flushing, and checksum support over a block device.

## Important APIs, Types, And Functions
`dm_block_t` is a 64-bit metadata block number. `struct dm_block` and `struct dm_block_manager` are opaque. `dm_block_location()` and `dm_block_data()` expose a locked block's location and memory.

`struct dm_block_validator` names a metadata format and supplies `prepare_for_write()` plus `check()` callbacks. Lock APIs include `dm_bm_read_lock()`, `dm_bm_write_lock()`, `dm_bm_read_try_lock()`, `dm_bm_write_lock_zero()`, and `dm_bm_unlock()`. Lifecycle and state APIs include create/destroy/reset, block-size/device-size queries, flush, prefetch, read-only toggles, and `dm_bm_checksum()`.

## Control Flow
Callers create a manager for a block device and metadata block size, lock blocks with a validator, inspect or modify the returned memory, unlock, then flush at transaction boundaries. `dm_bm_write_lock_zero()` is the preferred path when a caller will overwrite a whole block and wants to avoid a disk read.

## State And Persistence
The API contract states that write-locked memory will be written back sometime after unlock and that superblock-style callers can flush dirty metadata before committing a final root block. Validator consistency persists through cached block lifetime.

## Dependencies And Integration Points
The header depends on Linux types and block-device structures. It is the base layer for the transaction manager, btree, arrays, and space maps.

## Risks
The most common API risks are forgetting to unlock, using inconsistent validators, relying on data in a block after unlock, and writing partially initialized data after `dm_bm_write_lock_zero()`. Read-only mode prevents writes and flushes but cannot prevent misuse of already-returned pointers.

## Test Signals
Header-contract tests should ensure every lock path unlocks correctly, validator failures propagate, write-zero blocks are fully initialized by callers, and flush is called in transaction commit sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-block-manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-internal.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-internal.h

## Purpose
Declares internal btree structures and helpers shared by insertion, deletion, removal, and spine implementations. It captures the on-disk node layout and the rolling-lock abstractions used by the persistent btree implementation.

## Important APIs, Types, And Functions
`enum node_flags` distinguishes `INTERNAL_NODE` and `LEAF_NODE`. `struct node_header` stores checksum, flags, expected block number, entry count, max entries, and value size. `struct btree_node` starts with that header followed by sorted little-endian 64-bit keys and a separate value area.

Accessors `key_ptr()`, `value_base()`, `value_ptr()`, and `value64()` compute key/value locations inside a node. Shared helpers include `bn_read_lock()`, `new_block()`, `unlock_block()`, `inc_children()`, `lower_bound()`, `init_le64_type()`, and `btree_get_overwrite_leaf()`.

`struct ro_spine` and `struct shadow_spine` hold at most two rolling locks while descending a btree. Read-only spine APIs handle lookup traversal; shadow spine APIs perform copy-on-write traversal and track the new root.

## Control Flow
Btree readers descend with `ro_step()` and release old ancestors as they move down. Mutators descend with `shadow_step()`, which shadows blocks through the transaction manager and lets the caller update parent pointers to new shadow locations. Removal and insertion code use the same node layout and accessor helpers to split, rebalance, merge, and overwrite nodes.

## State And Persistence
The node layout is persistent and little-endian. Checksums and block-number stamping are validated by `btree_node_validator` in the spine implementation. Internal values of multi-level btrees are `__le64` block references whose reference counts are managed by the `le64` value type.

## Dependencies And Integration Points
This header depends on `dm-btree.h` and the transaction manager abstractions. It is private to the persistent-data btree implementation and should not be used by external dm targets.

## Risks
The risks are layout and arithmetic sensitive: `value_base()` assumes `max_entries` and `value_size` were validated, and all callers must preserve sorted keys and correct parent boundary keys. Misusing ro versus shadow spine APIs can break lock ordering or mutate shared nodes without copy-on-write.

## Test Signals
Structural tests should validate node checksum/block-number errors, lower-bound behavior, sorted-key invariants after insert/remove, shadow-root updates, and correct child reference increments when shared nodes are shadowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-remove.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-remove.c

## Purpose
Implements key removal and leaf-range removal for dm persistent btrees. It maintains btree occupancy constraints while preserving copy-on-write semantics and limiting held locks through shadow spines.

## Important APIs, Types, And Functions
The exported functions are `dm_btree_remove()` and `dm_btree_remove_leaves()`. Internal node-mutation helpers include `node_shift()`, `node_copy()`, `delete_at()`, `shift()`, `__rebalance2()`, `rebalance2()`, `delete_center_node()`, `redistribute3()`, `__rebalance3()`, `rebalance3()`, `rebalance_children()`, `remove_raw()`, `remove_nearest()`, and `remove_one()`.

`struct child` packages a shadowed child block, node pointer, and parent index. `init_child()` shadows a child and updates the parent to point at the new block, incrementing descendants if the shadow operation broke sharing.

## Control Flow
Removal descends from root to leaf using `remove_raw()`. Before stepping into a child, `rebalance_children()` ensures the child has enough entries to tolerate deletion. If the parent has one entry, the root can collapse by copying the child contents into the root. Otherwise the code rebalances two siblings when one side exists, or three siblings when both sides exist. Small combined sibling populations merge nodes and decrement removed block references; larger populations redistribute entries and update parent separator keys.

For a full key remove, `dm_btree_remove()` iterates nested btree levels, then decrements the old leaf value through the value type and deletes the key/value entry. `dm_btree_remove_leaves()` repeatedly removes the nearest leaf entry starting from `first_key` until it reaches `end_key`, updating `first_key` and counting removals.

## State And Persistence
All mutations occur on shadowed blocks returned by the transaction manager. Parent pointers are patched to new block locations after shadowing. Deleting a leaf invokes the value type's `dec` callback so referenced metadata can be freed. Merging nodes decrements metadata block references without decrementing children that remain referenced by another node.

## Dependencies And Integration Points
This file depends on internal btree helpers, transaction-manager copy-on-write and refcounts, little-endian node layout, and device-mapper error logging. Higher-level APIs in `dm-btree.h`, `dm-array`, and space-map overflow trees rely on these removal paths.

## Risks
Removal is high risk because it changes multiple siblings and parent separator keys. Off-by-one errors in shifts, merges, or `lower_bound()` handling can orphan subtrees or make keys unreachable. The code intentionally changes only top-down with limited locks; violating that convention can deadlock. `dm_btree_remove_leaves()` assumes contiguous bottom-level key semantics and callers must preserve updated `first_key`/root values.

## Test Signals
Tests should remove first, middle, last, missing, and repeated keys; force two-node and three-node rebalances; collapse root levels; remove ranges crossing leaf boundaries; use shared old roots to verify copy-on-write; and check value `dec` callbacks and metadata block refcounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-remove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-spine.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-spine.c

## Purpose
Implements btree node validation, read-only rolling spines, copy-on-write shadow spines, and the internal `__le64` value type used for btree child block references.

## Important APIs, Types, And Functions
`btree_node_validator` prepares and checks btree nodes. `node_prepare_for_write()` stamps the block number and checksum. `node_check()` verifies expected block location, checksum, node capacity, entry count, and that the node is either internal or leaf.

Lock helpers are `bn_read_lock()`, `new_block()`, and `unlock_block()`. `bn_shadow()` calls `dm_tm_shadow_block()` and invokes `inc_children()` when a shared node is copied. Read-only spine APIs are `init_ro_spine()`, `exit_ro_spine()`, `ro_step()`, `ro_pop()`, and `ro_node()`. Shadow spine APIs are `init_shadow_spine()`, `exit_shadow_spine()`, `shadow_step()`, `shadow_current()`, `shadow_parent()`, `shadow_has_parent()`, and `shadow_root()`.

`init_le64_type()` creates a btree value type for child block pointers; its callbacks increment/decrement contiguous runs of child references through the transaction manager and compare little-endian block values.

## Control Flow
Readers use `ro_step()` to acquire a child and drop the grandparent when two nodes are already held. Mutators use `shadow_step()` similarly, except each step returns a writable shadow. The first shadowed block's location becomes the new root. Insertion/removal code later patches parent values to point to each new shadow.

## State And Persistence
Persistent state is the btree node header checksum and block-number stamp plus sorted key/value payload. Runtime spine state is just a small rolling array of held blocks. The `le64` value type ensures child metadata references stay correct when internal nodes are copied or deleted.

## Dependencies And Integration Points
This file integrates the btree layer with the transaction manager and block-manager validator interface. It is used by `dm-btree.c` and `dm-btree-remove.c`, and indirectly by array and space-map implementations.

## Risks
Validator correctness is critical because every btree metadata block depends on it. `node_check()` cannot validate full key ordering, so higher-level insert/remove paths must maintain sorted keys and separator semantics. Shadow spines require callers to patch parents; forgetting that produces valid blocks that are not reachable from the returned root.

## Test Signals
Signals include checksum/block-number corruption tests, lockdep coverage for rolling traversal, copy-on-write tests with shared nodes, internal-child refcount tests, and btree insert/remove stress that exercises parent patching after every shadow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree-spine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.c

## Purpose
Implements creation, deletion, lookup, insertion, walking, key discovery, and cursor iteration for immutable persistent B+ trees with 64-bit keys and fixed-size values. It supports nested btrees where each level indexes the next root.

## Important APIs, Types, And Functions
Exported APIs include `dm_btree_empty()`, `dm_btree_del()`, `dm_btree_lookup()`, `dm_btree_lookup_next()`, `dm_btree_insert()`, `dm_btree_insert_notify()`, `dm_btree_find_lowest_key()`, `dm_btree_find_highest_key()`, `dm_btree_walk()`, and cursor functions. Internal array/node helpers include `array_insert()`, `lower_bound()`, `upper_bound()`, `insert_at()`, `calc_max_entries()`, `copy_entries()`, `move_entries()`, `redistribute2()`, `redistribute3()`, `split_one_into_two()`, `split_two_into_three()`, `btree_split_beneath()`, `rebalance_left()`, `rebalance_right()`, and `rebalance_or_split()`.

The deletion of whole trees uses an explicit heap-allocated `del_stack` to avoid recursive kernel stack growth. `btree_insert_raw()` performs copy-on-write descent and preemptive space creation. `btree_get_overwrite_leaf()` exposes a shadowed leaf for overwrite-only users such as space-map overflow counts.

## Control Flow
`dm_btree_empty()` allocates a leaf node with capacity based on block size and value size. Lookup descends through read-only spines, requiring exact key matches at each nested level. `lookup_next` resolves upper levels exactly and then finds the next leaf key at the bottom level.

Insertion descends one level at a time. For missing intermediate keys it creates a new empty subtree and inserts its root. Along the descent, full nodes are split or rebalanced before insertion. When overwriting an existing leaf value, the old value's `dec` callback is called unless an `equal` callback says old and new values are equivalent; new insertions assume the caller already owns the value reference. Whole-tree deletion walks all nodes, skips children of shared nodes by decrementing the shared node reference, and decrements leaf values for unshared leaves.

Cursor iteration pushes btree nodes to the leftmost leaf, optionally prefetches leaf values that are block numbers, and advances/backtracks in sorted order.

## State And Persistence
Btree state is persisted in checksummed nodes managed by the transaction manager. Mutations return a new root and never modify shared blocks in place. Value-type callbacks are the bridge between btree structure changes and external reference-counted objects. Internal-node values are child block pointers with `le64` callbacks that maintain child refs.

## Dependencies And Integration Points
This file depends on btree internal/spine helpers, transaction manager refcount and shadowing, block-manager block size, and dm logging. It underpins arrays, bitsets, space-map bitmap indexes, and overflow refcount trees.

## Risks
Btree correctness is highly sensitive to separator-key updates, split/rebalance decisions, and value callback usage. Monotonic insertion paths use different split heuristics than middle insertions. `dm_btree_walk()` is recursive and restricted to single-level trees, so stack use matters. Cursor depth is capped by `DM_BTREE_CURSOR_MAX_DEPTH`; malformed or unexpectedly deep trees can fail traversal.

## Test Signals
Tests should cover empty trees, exact and next lookup, overwrite versus insert-notify, nested btrees, monotonically increasing/decreasing insert streams, random insert/remove churn, tree deletion with shared roots, cursor skip/next behavior, value callback counts, and corruption tests that trip validators before logic sees bad nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.h

## Purpose
Declares the public persistent btree API for device-mapper metadata. It provides immutable B+ trees with 64-bit keys, arbitrary fixed-size little-endian values, nested tree support, and ordered cursors.

## Important APIs, Types, And Functions
`struct dm_btree_value_type` defines value size and optional callbacks: `inc` for duplicated values, `dec` for deleted values, and `equal` for overwrite comparisons. `struct dm_btree_info` binds a transaction manager, number of nested levels, and value type.

Lifecycle and mutation APIs are `dm_btree_empty()`, `dm_btree_del()`, `dm_btree_insert()`, `dm_btree_insert_notify()`, `dm_btree_remove()`, and `dm_btree_remove_leaves()`. Lookup and traversal APIs are `dm_btree_lookup()`, `dm_btree_lookup_next()`, `dm_btree_find_lowest_key()`, `dm_btree_find_highest_key()`, and `dm_btree_walk()`. The cursor API uses `struct dm_btree_cursor` and supports begin, end, next, skip, and current-value access.

Sparse annotations such as `__dm_written_to_disk()` document that callers pass on-disk-format data to insert/update APIs.

## Control Flow
Callers initialize `dm_btree_info`, create or load a root, and perform lookups/mutations through the transaction manager. Mutations return new roots. Multi-level btrees use one key per level, where non-leaf values point to subtrees and the final value comes from the caller's value type.

## State And Persistence
The btree is persistent and immutable across transactions. Old roots can coexist with updated roots when their reference counts are preserved. Value callbacks are required for correct persistence of referenced blocks and external resource counts.

## Dependencies And Integration Points
The API depends on `dm-block-manager.h` and an external transaction manager. It is the core index type for the persistent-data library and is consumed by arrays, bitsets, and space maps.

## Risks
The public contract places reference-count responsibility on value callbacks and caller behavior. Passing CPU-endian values where little-endian disk values are expected corrupts persisted metadata. `dm_btree_walk()` is limited to single-level trees and is recursive. `remove_leaves()` only removes a contiguous bottom-level range and does not imply full subtree deletion.

## Test Signals
API tests should validate value callbacks, nested key arrays, old/new root immutability, lookup missing-key `-ENODATA`, cursor depth limits, and removal/range-removal semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-persistent-data-internal.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-persistent-data-internal.h

## Purpose
Provides a tiny internal helper shared by persistent-data components.

## Important APIs, Types, And Functions
`dm_hash_block(dm_block_t b, unsigned int hash_mask)` multiplies the low 32 bits of a metadata block number by a large prime and masks the result. It is used for fixed-size hash tables/caches such as transaction-manager shadow tracking and space-map index-entry caches.

## Control Flow
Callers pass a block number and a mask, usually one less than a power-of-two table size. The helper returns the bucket index.

## State And Persistence
There is no state or persistent format in this header. It affects runtime distribution of block numbers across small hash tables.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` for `dm_block_t`. It is internal to the persistent-data implementation and not a public dm target API.

## Risks
The helper intentionally casts to `unsigned int`, so high bits of very large block numbers do not affect the hash. That is acceptable for small caches but could create clustering if reused for larger or adversarial tables. The caller must pass a mask appropriate for the table size.

## Test Signals
Basic tests should verify bucket values stay within mask bounds and that caches using this helper handle collisions correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-persistent-data-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.c

## Purpose
Implements the low-level on-disk space-map engine shared by disk and metadata space maps. It tracks per-block reference counts using compact bitmap blocks for counts 0, 1, 2, and overflow, plus a btree for counts greater than 2.

## Important APIs, Types, And Functions
Validators `index_validator` and `dm_sm_bitmap_validator` protect metadata-index and bitmap blocks with checksum and expected block-number checks. Bitmap helpers `sm_lookup_bitmap()`, `sm_set_bitmap()`, `sm_find_free()`, and `dm_bitmap_word_used()` manage two-bit entries inside bitmap blocks.

The main shared state is `struct ll_disk`, declared in the header. Exported low-level functions include `sm_ll_extend()`, `sm_ll_lookup_bitmap()`, `sm_ll_lookup()`, `sm_ll_find_free_block()`, `sm_ll_find_common_free_block()`, `sm_ll_insert()`, `sm_ll_inc()`, `sm_ll_dec()`, `sm_ll_commit()`, `sm_ll_new_metadata()`, `sm_ll_open_metadata()`, `sm_ll_new_disk()`, and `sm_ll_open_disk()`.

Range updates use `struct inc_context` to hold a shadowed bitmap block and optional overflow-tree leaf. Overflow helpers update the refcount btree in place through `btree_get_overwrite_leaf()` when possible. The disk-index variant uses a 64-entry cache of btree index entries; the metadata-index variant keeps a fixed `disk_metadata_index` block in memory.

## Control Flow
Initialization sets up two btree infos: one for bitmap index entries and one for overflow refcounts. `sm_ll_extend()` increases logical blocks, allocates new bitmap blocks through the transaction manager, initializes index entries, and saves them through the configured index backend.

Lookups locate the bitmap index entry, read the bitmap block, and return the two-bit count. Count value `3` means the true count is in the overflow btree. Inserts shadow the relevant bitmap, update the two-bit entry, insert/remove overflow entries as needed, adjust `nr_allocated`, `nr_free`, and `none_free_before`, and save the index entry. Range inc/dec loops operate bitmap by bitmap, shadowing once per bitmap and reopening write locks when overflow tree operations temporarily release the bitmap.

`sm_ll_commit()` flushes dirty index-entry state through the backend. Metadata mode commits the fixed metadata index by shadowing its index block. Disk mode writes back dirty cached index entries into the bitmap-index btree.

## State And Persistence
Persistent state consists of `disk_sm_root`, bitmap index entries, bitmap blocks, and overflow refcount btree roots. `nr_blocks` and `nr_allocated` describe total and allocated blocks. `none_free_before` accelerates free searches within a bitmap. All metadata updates are copy-on-write through the transaction manager.

## Dependencies And Integration Points
This file depends on btree internals, transaction-manager shadowing/refcounts, block-manager validators, device-mapper logging, and Linux bitops. It is wrapped by `dm-space-map-disk.c` for general data blocks and `dm-space-map-metadata.c` for metadata self-allocation.

## Risks
Reference-count transitions around 2/3 are delicate because they move counts between the bitmap and overflow btree. Any missed overflow insert/remove corrupts sharing semantics. `nr_allocated`, `nr_free`, and `none_free_before` must stay synchronized with bitmap mutations or allocation can leak blocks or report false free space. Disk index cache writeback must not lose dirty entries. Allocating a block that was free only in the current transaction is prevented by higher wrappers comparing old and current maps.

## Test Signals
Tests should exercise count transitions 0->1->2->3->4 and back to 0, range inc/dec across bitmap boundaries, overflow btree leaf reuse, free-block searches with `none_free_before`, metadata and disk index commit paths, index cache collisions/writeback, checksum/blocknr corruption, and extension near backend max-entry limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.h

## Purpose
Declares the shared low-level space-map disk format and helper interface used by both disk and metadata space-map wrappers.

## Important APIs, Types, And Functions
`struct disk_index_entry` maps a bitmap index to a bitmap block and stores `nr_free` plus `none_free_before`. `struct disk_metadata_index` is the compact fixed metadata-index block containing up to `MAX_METADATA_BITMAPS` entries. `struct disk_sm_root` is the root persisted by wrappers and stores total blocks, allocated blocks, bitmap root, and overflow refcount root. `struct disk_bitmap_header` is the header for bitmap blocks.

`struct ll_disk` contains the transaction manager, bitmap and refcount btree infos, block geometry, current roots, backend function pointers, index cache, and changed flags. Backend callbacks abstract whether bitmap index entries live in a fixed metadata-index block or a btree/cache.

Declared low-level APIs initialize/open metadata or disk variants, extend space, lookup counts, find free blocks, insert counts, increment/decrement ranges, and commit cached/index state.

## Control Flow
Wrappers initialize `ll_disk` through either metadata or disk constructors, then call shared operations for all count and allocation changes. Backend function pointers route index-entry load/save/commit operations to the correct persistence shape.

## State And Persistence
The header describes the persistent encoding: two bits per block in bitmap blocks, overflow counts in a separate btree, and roots summarized in `disk_sm_root`. It also defines runtime caching state for disk index entries.

## Dependencies And Integration Points
The header depends on `dm-btree.h` and is consumed by `dm-space-map-common.c`, `dm-space-map-disk.c`, and `dm-space-map-metadata.c`.

## Risks
Changing these structures changes on-disk metadata compatibility. Alignment, packing, and little-endian fields are part of the disk format. `MAX_METADATA_BITMAPS` bounds metadata-space size, and wrappers must enforce it.

## Test Signals
Tests should validate serialized root sizes, endian conversions, metadata max-block limits, disk and metadata backend equivalence for count operations, and index cache behavior around dirty entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.c

## Purpose
Implements the public `dm_space_map` wrapper for general disk/data space. It builds on the shared low-level space-map engine and preserves rollback safety by allocating only blocks that are free in both the previous committed map and the current transaction map.

## Important APIs, Types, And Functions
`struct sm_disk` embeds `struct dm_space_map`, current `ll`, committed snapshot `old_ll`, allocation search cursor `begin`, and `nr_allocated_this_transaction`. Its operation table implements destroy, extend, count lookup, set/inc/dec, new block, commit, root size/copy, and no threshold callback.

Public constructors are `dm_sm_disk_create()` and `dm_sm_disk_open()`. Internal operation methods include `sm_disk_get_nr_blocks()`, `sm_disk_get_nr_free()`, `sm_disk_set_count()`, `sm_disk_inc_blocks()`, `sm_disk_dec_blocks()`, `sm_disk_new_block()`, and `sm_disk_commit()`.

## Control Flow
Create initializes an empty low-level disk map, extends it to the requested block count, then commits to seed `old_ll`. Open loads a root and commits the current state into `old_ll`. Increment, decrement, and set operations delegate to low-level functions and accumulate net allocations in `nr_allocated_this_transaction`.

`sm_disk_new_block()` searches from `begin` to the end, then wraps to the beginning, using `sm_ll_find_common_free_block()` so a block must be free in both `old_ll` and `ll`. Once found, it advances `begin`, increments the block's count in the current map, and tracks the allocation. Commit writes low-level index state, copies `ll` into `old_ll`, and resets transaction allocation accounting.

## State And Persistence
Persistent root data is `disk_sm_root`. Runtime state maintains both current and committed snapshots so free space semantics exclude blocks freed only in the current transaction. `get_nr_blocks()` reports committed block count, while extensions are not visible there until commit, matching the `dm_space_map` contract.

## Dependencies And Integration Points
This file depends on `dm-space-map-common`, `dm-space-map`, transaction manager, Linux slab/list/export helpers, and device-mapper logging. It is used by metadata formats that need a space map for provisioned data blocks or other non-self-hosted allocation domains.

## Risks
The rollback-safety rule is critical. Allocating a block freed earlier in the same transaction could make rollback impossible or expose stale metadata/data. `nr_allocated_this_transaction` must be updated for all set/inc/dec/new paths or free-space reporting becomes wrong. `memcpy(&old_ll, &ll, sizeof(...))` copies cache state, so low-level structures must remain safe for value copying.

## Test Signals
Tests should allocate after freeing within the same transaction and verify the freed block is not reused until commit. Other signals include wraparound search behavior, root copy/open round trips, extend visibility only after commit, free-space accounting, and overflow count transitions through the common layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.h

## Purpose
Declares constructors for the disk/data `dm_space_map` implementation.

## Important APIs, Types, And Functions
`dm_sm_disk_create(struct dm_transaction_manager *tm, dm_block_t nr_blocks)` creates a new disk space map and initializes it to manage `nr_blocks`. `dm_sm_disk_open(struct dm_transaction_manager *tm, void *root, size_t len)` opens a previously persisted root. The header forward-declares `struct dm_space_map` and `struct dm_transaction_manager`.

## Control Flow
Callers create or open the space map after they have a transaction manager. The returned `struct dm_space_map` is then used through the generic inline wrappers in `dm-space-map.h`.

## State And Persistence
The root buffer passed to open must contain the serialized root produced by `copy_root()` from this implementation. Create performs an initial commit internally so its old/current map snapshots start synchronized.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` for `dm_block_t` and integrates with transaction-manager-managed metadata users.

## Risks
The file notes two-phase construction pressure caused by the transaction-manager/space-map cycle. Callers must not mix disk-space roots with metadata-space roots unless the surrounding format explicitly permits the same `disk_sm_root` layout and semantics.

## Test Signals
Tests should create/open roots, verify `root_size()` matches expected serialized size, and exercise the returned object only through generic `dm_space_map` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.c

## Purpose
Implements the self-hosting metadata `dm_space_map`. This map manages the metadata blocks used by the transaction manager and low-level space-map structures themselves, so it must handle recursive allocation safely while preserving copy-on-write transaction semantics.

## Important APIs, Types, And Functions
`struct sm_metadata` embeds `struct dm_space_map`, current and committed low-level maps, allocation cursor `begin`, recursion depth, per-transaction allocation count, a ring buffer of deferred block operations, and an edge-triggered free-space threshold callback.

Recursive operation support is built from `struct bop_ring_buffer`, `add_bop()`, `apply_bops()`, `in()`, `out()`, `recursing()`, and `combine_errors()`. Normal operations implement count lookup, `count_is_more_than_one`, set/inc/dec, new block, commit, root size/copy, threshold registration, and extend. Bootstrap mode uses `bootstrap_ops` to allocate linearly while creating or extending the self-hosted structures.

Public functions are `dm_sm_metadata_init()`, `dm_sm_metadata_create()`, and `dm_sm_metadata_open()`. The implementation also enforces `DM_SM_METADATA_MAX_BLOCKS` from the header during create.

## Control Flow
Create allocates `sm_metadata`, switches temporarily to bootstrap operations, creates the low-level metadata index and overflow btree, extends the map, then switches to normal ops. It records all blocks consumed by the superblock and initial metadata structures as pending increments, applies those operations, and commits.

Normal inc/dec operations either defer into `uncommitted` when already recursing or enter the recursion guard, perform the low-level update, and on the outermost exit apply deferred operations. `new_block` finds a block free in both old and current maps, advances the cursor, increments it immediately or defers the increment if recursive, tracks `allocated_this_transaction`, and checks the threshold callback after allocation.

Extend switches back to bootstrap mode and starts allocation at the old end. It extends low-level bitmap coverage, then repeatedly records and applies increments for newly consumed metadata blocks and commits until no additional blocks are allocated by the commit itself. Open loads the low-level root, initializes runtime counters and threshold state, and snapshots `old_ll`.

## State And Persistence
Persistent state is the shared `disk_sm_root`, fixed metadata index, bitmap blocks, and overflow refcount btree. Runtime-only state includes recursion depth, deferred operation ring, allocation cursor, per-transaction allocation count, and threshold edge state. Free-space reporting subtracts blocks allocated in the current transaction from the committed free count.

## Dependencies And Integration Points
This file depends on the generic `dm_space_map` API, common low-level space-map code, transaction manager, device-mapper logging, and Linux allocation helpers. It is tied into `dm_tm_create_with_sm()`/`dm_tm_open_with_sm()` to solve the cyclic dependency between transaction manager and metadata allocator.

## Risks
Recursive allocation is the central risk. If the deferred operation ring overflows or operations are applied at the wrong recursion depth, refcounts for metadata blocks can become wrong. `set_count()` is explicitly rejected while recursing because arbitrary overwrite semantics are unsafe there. Threshold callbacks are edge-triggered and must not assume repeated calls while below threshold. Extend must account for metadata allocated by its own commit loop or new metadata blocks could be left marked free.

## Test Signals
Tests should create and open metadata maps, allocate blocks during operations that themselves allocate metadata, force overflow of counts into the refcount btree, extend near and beyond current coverage, verify threshold callback edge behavior, ensure current-transaction freed blocks are not reallocated early, and check root copy/open after commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.h

## Purpose
Declares the metadata-space-map API and constants for the self-hosting metadata allocator used by the persistent-data transaction manager.

## Important APIs, Types, And Functions
`DM_SM_METADATA_BLOCK_SIZE` fixes the metadata block size in sectors for this implementation. `DM_SM_METADATA_MAX_BLOCKS` and `DM_SM_METADATA_MAX_SECTORS` describe the current limit imposed by one metadata index block with 255 entries, each covering roughly 16k metadata blocks.

`dm_sm_metadata_init()` allocates an uninitialized space-map object. `dm_sm_metadata_create()` initializes it for a fresh metadata device, given a transaction manager, block count, and superblock location. `dm_sm_metadata_open()` loads an existing root.

## Control Flow
The header documents the two-phase construction caused by the transaction-manager/space-map cycle: callers first allocate/init the space-map object, then create/open it once the transaction manager can refer back to it.

## State And Persistence
The metadata map persists the same root shape as common space maps but has stricter size limits and self-allocation semantics. The superblock location is excluded/reserved during create so metadata allocation does not overwrite it.

## Dependencies And Integration Points
The header depends on `dm-transaction-manager.h` and is used by the transaction-manager constructors that create/open a transaction manager with its metadata space map.

## Risks
The hard maximum metadata size is part of the API. Callers that expose larger metadata devices must clamp or reject sizes consistently. Incorrect superblock location handling can mark the superblock as free. Two-phase construction requires correct cleanup on errors.

## Test Signals
Signals include create/open root round trips, size clamping at `DM_SM_METADATA_MAX_BLOCKS`, superblock reservation, and transaction-manager create/open integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map.h

## Purpose
Defines the generic `dm_space_map` interface for persistent reference-count maps. A space map records how many times each metadata or data block is referenced and is committed as part of the transaction.

## Important APIs, Types, And Functions
`struct dm_space_map` is a vtable with operations for destroy, extend, block/free counts, count lookup, count comparison, count set, commit, range inc/dec, new-block allocation, root serialization, and optional threshold callback registration. Inline wrappers such as `dm_sm_inc_block()`, `dm_sm_dec_block()`, `dm_sm_new_block()`, `dm_sm_copy_root()`, and `dm_sm_register_threshold_callback()` provide the common call surface.

`dm_sm_threshold_fn` is an edge callback type for implementations that support low-free-space notification.

## Control Flow
Callers use a concrete constructor from disk or metadata implementations, then manipulate it through the generic wrappers. Mutations occur inside transaction-manager operations. `extend()` adds capacity but the interface states newly added space must not be allocated until after commit. `new_block()` returns a block with its reference count already incremented.

## State And Persistence
The interface defines important transactional semantics: `get_nr_blocks()` excludes uncommitted extensions, `get_nr_free()` reports blocks available for allocation now, and space maps must avoid allocating blocks from the previous transaction so rollback remains safe. `root_size()` and `copy_root()` serialize enough information to reopen the map.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` for `dm_block_t`. It is consumed by the transaction manager and by disk/metadata space-map implementations.

## Risks
Implementations must uphold rollback-safe allocation semantics or metadata transactions can become unrecoverable. Callers must not assume a block with zero count in the current map is immediately allocatable if it was allocated in the previous committed map. Threshold callbacks are optional and registration can fail with `-EINVAL`.

## Test Signals
Generic tests should run the same allocation/count/commit/root-copy scenarios against both disk and metadata implementations, including extension visibility, free-space accounting, and current-transaction free/reallocate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.c

## Purpose
Implements the transaction manager that enforces immutable persistent metadata updates. It coordinates block allocation, copy-on-write shadowing, reference-count changes through a space map, prefetching for non-blocking clones, and the two-phase commit protocol used by dm metadata formats.

## Important APIs, Types, And Functions
`struct dm_transaction_manager` stores whether it is a clone, a pointer to the real manager, the block manager, the space map, a shadow table of blocks already copied in this transaction, and a prefetch set. `struct shadow_info` and the hash/rbtree buckets record shadowed block locations so repeated shadow requests can be optimized.

Public APIs include `dm_tm_create_non_blocking_clone()`, `dm_tm_destroy()`, `dm_tm_pre_commit()`, `dm_tm_commit()`, `dm_tm_new_block()`, `dm_tm_shadow_block()`, `dm_tm_read_lock()`, `dm_tm_unlock()`, `dm_tm_inc()`, `dm_tm_inc_range()`, `dm_tm_dec()`, `dm_tm_dec_range()`, `dm_tm_with_runs()`, `dm_tm_ref()`, `dm_tm_block_is_shared()`, `dm_tm_get_bm()`, `dm_tm_issue_prefetches()`, `dm_tm_create_with_sm()`, and `dm_tm_open_with_sm()`.

`__shadow_block()` allocates a new block, decrements the original, reads the original, allocates a zeroed writable destination, copies data, and returns the new writable block. `dm_tm_shadow_block()` first asks the space map whether children need ref increments and avoids re-shadowing blocks already shadowed in the same transaction when safe.

## Control Flow
Normal creation/open uses `dm_sm_metadata_init()` plus `dm_tm_create()` to form the cyclic transaction-manager/metadata-space-map pair. New blocks are allocated from the space map, write-locked zeroed through the block manager, and recorded as shadows. Shadowing checks whether the original is shared. If the block is already shadowed and child increments are not needed, it write-locks the existing block; otherwise it copies to a new block and records the new location.

Commit is two-phase. `dm_tm_pre_commit()` commits the space map and flushes all dirty metadata except the caller's superblock. The caller then write-locks and updates the superblock. `dm_tm_commit()` wipes the shadow table, unlocks the superblock, and flushes again, making the root update durable after all dependent metadata.

Non-blocking clones support fast-path reads by using `dm_bm_read_try_lock()` against the real manager and queueing prefetch requests on `-EWOULDBLOCK`; mutating operations on clones return `-EWOULDBLOCK` or BUG for void mutators.

## State And Persistence
The shadow table is per-transaction runtime state and is cleared only at commit or destroy. Persistent state changes are mediated by the space map and dirty block-manager buffers. `dm_tm_with_runs()` coalesces adjacent block references for efficient range inc/dec. The manager's correctness depends on the space map's committed/current snapshots.

## Dependencies And Integration Points
This file depends on block manager, generic and concrete space maps, internal hash helper, Linux mutex/hash/rbtree/slab/export APIs, and device-mapper logging. Btrees, arrays, and space maps all call into this manager for copy-on-write and refcounts.

## Risks
Commit ordering is data-integrity critical: the superblock/root must not be made durable before the metadata it references. Shadowing implicitly decrements the original, so callers must not keep using the original writable path afterward. If child references are not incremented when a shared internal node is copied, later deletion can free live children. The shadow table can silently fail insertion under memory pressure, which is safe but may cause redundant shadows and extra space use.

## Test Signals
Tests should verify two-phase commit ordering under simulated write failures, repeated shadow requests in one transaction, shared-block child increment behavior, new-block allocation rollback on write-lock failure, non-blocking clone prefetch behavior, range coalescing with `dm_tm_with_runs()`, and open/create integration with metadata space maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.h

## Purpose
Declares the persistent-data transaction manager API. It is the main coordination layer that clients use to allocate, read, shadow, reference-count, and commit metadata blocks safely.

## Important APIs, Types, And Functions
The opaque `struct dm_transaction_manager` owns transaction scope. Lifecycle and construction APIs are `dm_tm_destroy()`, `dm_tm_create_non_blocking_clone()`, `dm_tm_create_with_sm()`, and `dm_tm_open_with_sm()`. Commit APIs are `dm_tm_pre_commit()` and `dm_tm_commit()`, with comments specifying the two-phase protocol.

Writable block APIs are `dm_tm_new_block()` and `dm_tm_shadow_block()`. Read APIs are `dm_tm_read_lock()` and `dm_tm_unlock()`. Refcount APIs are `dm_tm_inc()`, `dm_tm_inc_range()`, `dm_tm_dec()`, `dm_tm_dec_range()`, `dm_tm_with_runs()`, `dm_tm_ref()`, and `dm_tm_block_is_shared()`. `dm_tm_get_bm()` exposes the underlying block manager, and `dm_tm_issue_prefetches()` flushes queued prefetches from non-blocking clone reads.

## Control Flow
Clients make all metadata mutations through new/shadow block calls, update structures in returned write locks, unlock through the transaction manager, and commit using pre-commit followed by a final superblock update and `dm_tm_commit()`. Fast-path clients can create a non-blocking clone that performs try-lock reads and returns `-EWOULDBLOCK` instead of sleeping.

## State And Persistence
The header documents immutable metadata semantics: shadowing copies a block and drops the original reference; `inc_children` tells callers whether copied child references need adjustment. The two-phase commit comments define the persistence ordering expected by all on-disk metadata users.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` and forward-declares `dm_space_map`. It is consumed by btree, array, bitset, and space-map implementations plus dm targets that own superblocks.

## Risks
The API is easy to misuse if callers directly access the block manager for writable metadata or unlock a partially updated superblock. Void refcount mutators must not be called on non-blocking clones. `dm_tm_new_block()` returns zeroed blocks and callers must fully initialize them before unlock to avoid stale or invalid metadata.

## Test Signals
Contract tests should cover clone behavior, commit protocol sequencing, shadow-block `inc_children` handling, read/write locking via validators, direct refcount operations, root serialization with metadata-space maps, and failure paths around allocation and flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-transaction-manager.h -->
