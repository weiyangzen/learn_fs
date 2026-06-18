# Group Research: group_647_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_ioctl_c_sources_lo_6072aa22210f

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/kdave-linux` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ioctl.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ioctl.c

## Purpose

`ioctl.c` is the main Btrfs user-space control-plane dispatcher. It implements `btrfs_ioctl()`, compat handling, and the backing logic for filesystem attributes, subvolume and snapshot lifecycle, device management, tree/search inspection APIs, sync/scrub/balance/quota operations, feature bits, labels, encoded I/O, io_uring encoded I/O, subvolume deletion waits, and forced shutdown.

## Public Interfaces

Exports or header-declared functions include:

- `btrfs_ioctl()`: primary ioctl switch for Btrfs files.
- `btrfs_compat_ioctl()`: compat wrapper for 32-bit callers.
- `btrfs_fileattr_get()` / `btrfs_fileattr_set()`: VFS fileattr integration.
- `btrfs_sync_inode_flags_to_i_flags()`: maps Btrfs inode flags to VFS inode flags.
- `btrfs_ioctl_get_supported_features()`: exposes supported/safe feature masks.
- `btrfs_update_ioctl_balance_args()`: snapshots live balance status into UAPI args.
- `btrfs_uring_cmd()` / `btrfs_uring_read_extent_endio()`: io_uring encoded I/O entry and completion.

## Major Behavior

File attribute handling translates between `FS_*_FL` flags and Btrfs inode flags, rejects unsupported or incompatible combinations, disallows NOCOW on zoned filesystems, manages compression properties, updates inode ctime/iversion, and persists inode changes in a transaction.

Subvolume creation and snapshot creation are transaction-heavy paths. `create_subvol()` allocates a new root objectid, anon block device, root tree block, root item, UUID tree entry, qgroup inheritance, and subvolume inode/dentry. `create_snapshot()` builds a pending snapshot and commits the transaction to materialize it. Snapshot creation coordinates with `snapshot_lock`, `snapshot_force_cow`, delalloc writeback, and ordered extent waits to prevent NOCOW races.

Subvolume deletion supports old name-based and v2 name/id-based deletion. It handles mount write counts, idmapped mount restrictions, parent dentry lookup for deletion by id, user deletion policy via `USER_SUBVOL_RM_ALLOWED`, VFS permission checks, and calls `btrfs_delete_subvolume()` under inode locking.

Tree/search ioctls implement privileged key-range iteration with bounded user buffer copying. The v1 API preserves historical overflow behavior by returning an empty item; v2 reports required size up to a 16 MiB limit. Path lookup APIs include privileged inode lookup and unprivileged lookup with read/execute permission checks while walking parent refs.

Device operations cover resize, add, remove v1/v2, device info, filesystem info, stats, and device replace. Most mutating device paths require `CAP_SYS_ADMIN`, mount write access, and Btrfs exclusive-operation coordination. Extent-tree-v2 support is explicitly rejected for several device/scrub/snapshot operations.

Space, sync, scrub, balance, and quota ioctls bridge UAPI structs to internal subsystem entry points. Balance paths distinguish new, running, paused, resumed, canceled, and progress states under `balance_mutex` plus exclusive-operation state. Quota paths serialize against `subvol_sem`, `cleaner_mutex`, and `qgroup_ioctl_lock` as needed.

Received-subvolume metadata updates modify `received_uuid`, send/receive transids and timestamps, update root items, and maintain UUID tree entries. The code prechecks UUID-tree item overflow to avoid transaction aborts from malicious input.

Feature and label ioctls read or mutate superblock fields under `super_lock`, after capability and safe-set/safe-clear validation. Feature mutations are committed through a transaction.

Encoded I/O ioctls import user iovecs, validate encoded arguments, call `btrfs_encoded_read()` or `btrfs_do_write_iter()`, and update task I/O accounting. The io_uring encoded read path can return `-EIOCBQUEUED`, retain inode/extent locks across userspace return, and complete later through task work while using lockdep annotations from `locking.h`.

`btrfs_ioctl_subvol_sync()` provides waiting and peeking over `dead_roots`, with modes for count, first/last queued deletion, one specific subvolume, and queued deletion waits. `btrfs_ioctl_shutdown()` validates flags, optionally freezes/thaws the superblock, and calls `btrfs_force_shutdown()`.

## Dependencies and Integration

This file is tightly integrated with Btrfs root/tree management, transactions, qgroups, UUID tree, volume/device code, scrub, balance, send, backrefs, defrag, fsverity, encoded I/O, and VFS permission/write-count APIs. It also depends on locking helpers from `locking.c/.h`, ordered extent waiting from `ordered-data.c`, and diagnostics from `messages.h`.

## Concurrency and Safety Notes

The file is security-sensitive: it copies many UAPI structs, validates reserved fields and flags, checks capabilities, and carefully pairs `mnt_want_write_file()` / `mnt_drop_write_file()`. Important locks include `subvol_sem`, `balance_mutex`, `ordered_extent`/snapshot DREW locks, `super_lock`, `trans_lock`, `fs_roots_radix_lock`, and VFS inode locks. Main risk areas are UAPI compatibility, lock ordering, exclusive-operation lifetime, transaction abort vs graceful error returns, and async io_uring cleanup paths.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ioctl.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ioctl.h

## Purpose

`ioctl.h` declares the Btrfs ioctl and file attribute interfaces implemented by `ioctl.c`. It is a narrow internal header for connecting VFS operation tables, compat ioctl support, feature reporting, balance-status formatting, inode flag synchronization, and io_uring encoded I/O support.

## Interfaces

Declared functions:

- `btrfs_ioctl()`
- `btrfs_compat_ioctl()`
- `btrfs_fileattr_get()`
- `btrfs_fileattr_set()`
- `btrfs_ioctl_get_supported_features()`
- `btrfs_sync_inode_flags_to_i_flags()`
- `btrfs_update_ioctl_balance_args()`
- `btrfs_uring_cmd()`
- `btrfs_uring_read_extent_endio()`

## Dependencies

The header forward-declares VFS and Btrfs types instead of including broader subsystem headers. It includes only `<linux/types.h>`, keeping compile dependencies low.

## Integration Notes

This header forms the contract between Btrfs file operations and the ioctl implementation. Any changes here affect mount/file operation wiring and io_uring command dispatch.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/locking.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/locking.c

## Purpose

`locking.c` implements Btrfs tree-lock helpers for `extent_buffer` objects and the Btrfs DREW lock, a double-reader-writer-exclusion primitive used where two classes of users must exclude each other without excluding same-class users.

## Major Behavior

Under `CONFIG_DEBUG_LOCK_ALLOC`, the file defines lockdep class keysets for Btrfs tree block locks. Lock classes are selected by root objectid and tree level, with named classes for root, extent, chunk, device, checksum, quota, log, relocation, free-space, block-group, raid-stripe, remap, and default tree roots. `btrfs_set_buffer_lockdep_class()` assigns an extent buffer lock class by objectid and level, and `btrfs_maybe_reset_lockdep_class()` reapplies it when a root requests reset.

Extent-buffer locking wraps the underlying `rw_semaphore` in traceable helpers:

- `btrfs_tree_read_lock_nested()`
- `btrfs_try_tree_read_lock()`
- `btrfs_tree_read_unlock()`
- `btrfs_tree_lock_nested()`
- `btrfs_tree_unlock()`

Write locking records `lock_owner` under debug builds. Tracepoints measure lock acquisition and release.

Root node helpers loop until the locked extent buffer is still the current root node, because the root can change between grabbing and locking it:

- `btrfs_lock_root_node()`
- `btrfs_read_lock_root_node()`
- `btrfs_try_read_lock_root_node()`

`btrfs_unlock_up_safe()` unlocks a `btrfs_path` from a given level upward unless `keep_locks` is set.

The DREW lock uses atomic reader/writer counters and two waitqueues. Readers increment `readers` and wait until no writers remain. Writers fail or wait while readers exist, and readers are intentionally favored when pending.

## Dependencies and Integration

This file uses `extent_io.h`, `ctree.h`, trace events, lockdep, waitqueues, and atomic memory barriers. It underpins Btrfs tree traversal, COW, split/balance operations, snapshot coordination, and debug lock checking.

## Concurrency Notes

The code is lock-ordering infrastructure. Correctness depends on nesting subclasses, memory barriers after atomic counter changes, and root-node retry loops. The DREW implementation favors readers, which is intentional but can affect writer latency under sustained read pressure.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/locking.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/locking.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/locking.h

## Purpose

`locking.h` declares Btrfs tree locking APIs, lockdep annotations, lock nesting classes, and the DREW lock structure/API.

## Key Definitions

The header defines `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` path lock markers, plus `enum btrfs_lock_nesting`. Nesting classes cover normal locks, COW blocks, left/right adjacent nodes, COW of adjacent nodes, split allocations, and new-root promotion. A `static_assert` enforces that the number of classes stays within `MAX_LOCKDEP_SUBCLASSES`.

It also defines transaction wait-state lockdep indices:

- `BTRFS_LOCKDEP_TRANS_COMMIT_PREP`
- `BTRFS_LOCKDEP_TRANS_UNBLOCKED`
- `BTRFS_LOCKDEP_TRANS_SUPER_COMMITTED`
- `BTRFS_LOCKDEP_TRANS_COMPLETED`

## Lockdep Annotation Macros

The header provides helper macros for wait-event lockdep modeling:

- `btrfs_might_wait_for_event()`
- `btrfs_lockdep_acquire()`
- `btrfs_lockdep_release()`
- `btrfs_lockdep_inode_acquire()`
- `btrfs_lockdep_inode_release()`
- transaction-state variants
- lockdep map initialization macros

The inode lockdep helpers are specifically used by io_uring encoded I/O, where Btrfs can return to userspace with an inode lock held until async completion.

## APIs

Tree lock functions include read/write nested locks, try read lock, root-node lock helpers, unlock helpers, and debug assertions. `btrfs_tree_unlock_rw()` dispatches based on stored path lock mode.

The DREW lock structure contains atomic `readers` and `writers` plus waitqueues for pending readers and writers. APIs include init, read lock/unlock, write lock/unlock, and try-write-lock.

## Integration Notes

This header is shared by tree manipulation, transaction wait code, ordered extent waits, io_uring lockdep annotations, and snapshot code. Its enum values and lockdep classes are part of Btrfs’s internal deadlock-prevention discipline.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/locking.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.c

## Purpose

`lru_cache.c` implements a small generic Btrfs LRU cache using a maple tree for key lookup and a list for LRU ordering. It is designed for embedded cache-entry structs whose first field is `struct btrfs_lru_cache_entry`.

## Major Behavior

`btrfs_lru_cache_init()` initializes the LRU list, maple tree, current size, and max size. `max_size == 0` means unlimited size, leaving trimming to the caller.

Lookup uses `mtree_load()` by key, then `match_entry()` scans the per-key list for exact `key` and `gen`. A hit moves the entry to the tail of the LRU list.

Store allocates a list head for a new maple-tree bucket. If the key is new, it inserts the bucket and adds the entry. If the key exists, it frees the unused bucket, loads the existing list, rejects duplicate `(key, gen)` pairs with `-EEXIST`, and appends the new entry. If the cache is full, it evicts the first LRU entry before adding the new one.

Remove deletes the entry from both its per-key list and global LRU list. If the per-key list becomes empty, it erases and frees the maple-tree bucket. Removal frees the entry itself and decrements size.

Clear iterates the LRU list and removes every entry, then asserts an empty cache and maple tree.

## Dependencies and Integration

Depends on Linux maple tree, list APIs, `kmalloc_obj`, `kfree`, and Btrfs `ASSERT()`. The caller is responsible for synchronization; no internal lock protects the cache.

## Risk Notes

The cache assumes entries are kmalloc-backed and that `struct btrfs_lru_cache_entry` is at offset 0 in the embedding allocation. Violating either assumption would make eviction/freeing unsafe. The per-key list handles 32-bit maple key truncation scenarios and same-key generations.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.h

## Purpose

`lru_cache.h` defines the data structures and API for Btrfs’s generic LRU cache helper.

## Structures

`struct btrfs_lru_cache_entry` contains:

- `lru_list` for global LRU order.
- `key` as full `u64` logical key.
- `gen` as optional generation discriminator.
- `list` for the per-maple-tree-key bucket.

The header documents two important ownership/layout constraints: the entry must be embedded as the first member of its containing struct, and the allocation must be compatible with `kfree()`.

`struct btrfs_lru_cache` contains the global LRU list, maple tree, current size, and max size.

## APIs

Declared operations:

- `btrfs_lru_cache_init()`
- `btrfs_lru_cache_lookup()`
- `btrfs_lru_cache_store()`
- `btrfs_lru_cache_remove()`
- `btrfs_lru_cache_clear()`

It also provides `btrfs_lru_cache_for_each_entry_safe()` and `btrfs_lru_cache_lru_entry()` helpers.

## Integration Notes

The header abstracts away 32-bit maple-tree key limitations by storing full `u64` keys in entries and allowing bucket lists under a maple-tree slot. Callers must provide external locking if cache access is concurrent.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/lzo.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/lzo.c

## Purpose

`lzo.c` implements Btrfs’s LZO compression backend. It allocates compression workspaces, compresses file data into Btrfs’s on-disk LZO segment format, and decompresses both regular compressed extents and inline compressed extents.

## Format

The file documents the Btrfs LZO format:

- A 4-byte little-endian total compressed length header.
- One or more segments.
- Each segment has a 4-byte little-endian payload length followed by compressed data.
- Each segment represents at most one uncompressed sector.
- Segment headers must not cross sector boundaries; padding zeros may be inserted near sector ends.
- Inline LZO extents allow only one segment.

## Workspace

`struct workspace` owns:

- LZO compression memory.
- A decompressed buffer.
- A compressed buffer.
- A list node for workspace pooling.

`lzo_alloc_workspace()` allocates these buffers based on `lzo1x_worst_compress(sectorsize)`. `lzo_free_workspace()` frees them.

## Compression Flow

`lzo_compress_bio()` creates a compressed bio for a file range. It reserves the initial total-size header, then iterates input file folios sector by sector. Each sector is compressed with `lzo1x_1_compress()`, then `copy_compressed_data_to_bio()` writes the segment header, payload, and any required padding into compressed folios queued on the bio.

The code gives up with `-E2BIG` if compression expands beyond acceptable limits, including an early check after more than two sectors. Folio ownership is carefully split: queued folios are released by bio completion, while unqueued output folios are freed locally on failure.

## Decompression Flow

`lzo_decompress_bio()` reads the total compressed length header, validates it against the compressed bio size and maximum compressed extent size, then iterates segment headers and payloads. It copies segment payloads into the workspace, calls `lzo1x_decompress_safe()`, and writes output into target pages through `btrfs_decompress_buf2page()`.

`lzo_decompress()` handles inline compressed data: it validates the total length and single-segment length headers, decompresses into the workspace buffer, copies into the destination folio, and zeros/report-errors on short output.

## Dependencies and Integration

Depends on Linux LZO APIs, Btrfs compression helpers, folio/bio helpers, inode/root diagnostics, and `messages.h`. It exports `btrfs_lzo_compress` with max/default level 1.

## Risk Notes

Important correctness boundaries are segment header validation, sector-boundary padding, compressed length limits, folio offset math, and ownership transfer of compressed folios into bios. Corruption paths return `-EUCLEAN` or `-EIO` with Btrfs error logs.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/lzo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/messages.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/messages.c

## Purpose

`messages.c` implements Btrfs logging, error decoding, filesystem error handling, panic handling, and 32-bit address-limit warnings.

## Major Behavior

When `CONFIG_PRINTK` is enabled, `btrfs_state_to_string()` appends compact filesystem state characters to log messages. It reports error and notable states such as remounting, transaction aborted, log replay aborted, device replacing, skipped checksums, log cleanup error, and emergency shutdown. Read-only state is intentionally not printed as an error state.

`btrfs_decode_error()` maps selected negative errno values to stable human-readable strings, including I/O failure, no space, read-only filesystem, unsupported operation, filesystem corruption, and quota exceeded.

`__btrfs_handle_fs_error()` is the central expected-error path. It ignores `-EROFS` when the superblock is already read-only, logs a critical message with function/line/context, stores `fs_error`, skips full handling before mount completion, stops discard, sets the superblock read-only, and logs forced read-only. It deliberately does not cancel device replace to avoid deadlock risk.

`_btrfs_printk()` formats Btrfs log messages with log-level names and device id, uses per-level ratelimit states, and disables rate limiting under `CONFIG_BTRFS_DEBUG`.

On 32-bit builds, `btrfs_warn_32bit_limit()` and `btrfs_err_32bit_limit()` emit one-time warnings/errors for logical address limits.

`__btrfs_panic()` logs or panics depending on the mount option `PANIC_ON_FATAL_ERROR`; callers then execute `BUG()` through the macro in `messages.h`.

## Dependencies and Integration

The file depends on `fs.h`, `messages.h`, `discard.h`, and `super.h`. It is used across Btrfs for consistent diagnostics and fatal error policy.

## Risk Notes

This is safety-critical because error handling changes filesystem writability. The code avoids repeated noise via ratelimits and one-time flags, but preserves critical errors and forced-readonly transitions.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/messages.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/messages.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/messages.h

## Purpose

`messages.h` defines Btrfs logging macros, assertion behavior, filesystem error/panic interfaces, and 32-bit address-limit constants.

## Logging API

The header defines severity wrappers:

- `btrfs_crit()`
- `btrfs_err()`
- `btrfs_warn()`
- `btrfs_info()`

and ratelimited variants. With dynamic debug, `btrfs_debug()` and `btrfs_debug_rl()` route through `_dynamic_func_call_no_desc()`. Without debug support, debug macros compile to no-ops while still consuming `fs_info`.

When `CONFIG_PRINTK` is disabled, print macros use `btrfs_no_printk()`.

## Assertions

Under `CONFIG_BTRFS_ASSERT`, `ASSERT()` verifies a condition and supports optional printk-style messages. It prints the failed condition, file, line, and optional format text, then calls `BUG()`. Without assertions, it uses `BUILD_BUG_ON_INVALID(cond)` to type-check expressions without generating runtime code.

`DEBUG_WARN()` maps to `WARN()` only under `CONFIG_BTRFS_DEBUG`.

## Error/Panic Interfaces

The header declares:

- `__btrfs_handle_fs_error()`
- `btrfs_decode_error()`
- `__btrfs_panic()`

and wraps them with `btrfs_handle_fs_error()` and `btrfs_panic()` macros that inject `__func__` and `__LINE__`.

## 32-bit Limits

On 32-bit builds, it defines `BTRFS_32BIT_MAX_FILE_SIZE`, an early warning threshold, and declarations for warning/error emitters.

## Integration Notes

This header is widely included by Btrfs code and controls how assertions and diagnostics behave across debug, printk, and production configurations. Format-string validation in `ASSERT()` reduces risk of broken assertion messages.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/messages.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/misc.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/misc.h

## Purpose

`misc.h` provides small shared utility macros and inline helpers for Btrfs code: cleanup pointer helpers, enum bit construction, bio iteration, conditional wakeups, percentage math, 64-bit power-of-two checks, simple rb-tree helpers, and bitmap range tests.

## Key Utilities

`AUTO_KFREE()` and `AUTO_KVFREE()` define cleanup-at-scope-exit pointers initialized to `NULL`.

`ENUM_BIT()` creates enum-backed bit values with an auto-incremented internal sequence.

Bio helpers include:

- `bio_iter_phys()`
- `btrfs_bio_for_each_block()`
- `bio_get_size()`
- `init_bvec_iter_for_bio()`
- `btrfs_bio_for_each_block_all()`

These support block-sized iteration across bios, including large folios and highmem.

Waitqueue helpers:

- `cond_wake_up()` uses `wq_has_sleeper()` and carries the implied barrier.
- `cond_wake_up_nomb()` uses `waitqueue_active()` when a preceding barrier already exists.

Math/helpers:

- `mult_perc()`
- `is_power_of_two_u64()`
- `has_single_bit_set()`

The simple rb-tree helpers assume embedded structs begin with `struct rb_simple_node`, containing an rb node and `bytenr`. They implement exact search, first-at-or-after search, compare, and insert.

Bitmap helpers test whether a range is all set or all zero.

## Dependencies and Integration

This file pulls in common kernel headers for bios, rbtree, bitmap, waitqueues, pagemap, and math. It is used by ordered-data allocation flag validation and many lower-level Btrfs routines.

## Risk Notes

The rb-tree helpers depend on strict struct layout conventions. `cond_wake_up_nomb()` must only be used when callers truly provide the required memory barrier elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.c

## Purpose

`ordered-data.c` manages Btrfs ordered extents: the in-memory records that track outstanding writes from allocation/writeback through I/O completion, checksum insertion, metadata completion, fsync logging, transaction waiting, and cleanup.

## Data Structures and Storage

Ordered extents are stored per inode in an rb-tree keyed by file offset, with `ordered_tree_last` as a lookup cache. Each extent is also linked into a per-root ordered extent list, and roots with pending extents are linked into `fs_info->ordered_roots`. Objects are allocated from the `btrfs_ordered_extent_cache` slab.

`entry_end()`, `tree_insert()`, `__tree_search()`, `ordered_tree_search()`, and range-overlap helpers implement non-overlapping rb-tree storage and lookup.

## Allocation and Insertion

`btrfs_alloc_ordered_extent()` validates type flags, handles regular/COW/NOCOW/PREALLOC/COMPRESSED/ENCODED/DIRECT combinations, releases or transfers qgroup reservations, initializes refs/lists/waits/completion/work, increments outstanding extents, and inserts the extent into both inode and root/global tracking structures.

`btrfs_add_ordered_sum()` appends checksum records to an ordered extent.

## I/O Completion

`can_finish_ordered_extent()` decrements `bytes_left`, records I/O errors, sets `BTRFS_ORDERED_IO_DONE` when all data is done, wakes waiters, traces completion, and takes a ref for queued finish work.

`btrfs_finish_ordered_extent()` and `btrfs_mark_ordered_io_finished()` are endio-facing helpers. The range version can walk multiple ordered extents in a finished I/O range. On COW write error, the inode gets `BTRFS_INODE_COW_WRITE_ERROR` so fast fsync will wait for completion before logging possibly stale extent maps.

`btrfs_dec_test_ordered_pending()` supports callers that complete one ordered extent range and optionally cache the finished extent.

## Removal and Lifetime

`btrfs_remove_ordered_extent()` removes an extent from the inode rb-tree and root list, updates outstanding extent/delalloc/ordered-byte accounting, marks completion, handles transaction `pending_ordered` wakeups, releases lockdep maps, and wakes waiters. It does not drop refs itself.

`btrfs_put_ordered_extent()` frees an extent when refs reach zero, after asserting it is no longer linked in root/log/rb-tree structures. It schedules delayed iput and frees checksum sums.

## Waiting and Flushing

`btrfs_wait_ordered_extents()` splices a root’s ordered list, selects extents optionally intersecting a block group range, queues flush work, waits for each completion, and restores skipped/spliced entries. `btrfs_wait_ordered_roots()` iterates roots in the global ordered-root list.

`btrfs_start_ordered_extent_nowriteback()` starts writeback for dirty pages in the ordered extent range unless direct I/O, then waits for `BTRFS_ORDERED_COMPLETE`. A no-writeback subrange can be excluded.

`btrfs_wait_ordered_range()` starts writeback, waits for page writeback, then walks ordered extents backward through the requested range until all relevant extents complete, preserving writeback errors.

Range lock helpers `btrfs_lock_and_flush_ordered_range()` and `btrfs_try_lock_ordered_range()` coordinate extent locking with pending ordered extents.

## Lookup and Logging

Lookup helpers include exact-offset, first-before/around-offset, first-overlapping-range, and any-overlapping-range variants. `btrfs_get_ordered_extents_for_logging()` collects not-yet-logged ordered extents in file-offset order for fsync logging and takes refs.

## Splitting

`btrfs_split_ordered_extent()` splits the first `len` bytes from a non-compressed ordered extent into a new ordered extent. It rejects errors, compressed extents, invalid lengths, and partially completed inconsistent extents. It adjusts offsets, disk ranges, lengths, bytes-left, truncation state, checksum sums, and inserts the new extent while holding both root ordered extent lock and inode ordered tree lock.

## Dependencies and Risk Notes

The file integrates with transactions, qgroups, delalloc space, compression, extent I/O, file writeback, block groups, and Btrfs workqueues. Correctness depends on rb-tree non-overlap, refcount ownership, lock ordering, delayed metadata completion, and exact accounting of `bytes_left`, qgroup reservations, delalloc metadata, and root ordered lists.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.h

## Purpose

`ordered-data.h` defines the ordered extent data model and declares the APIs implemented by `ordered-data.c`.

## Structures

`struct btrfs_ordered_sum` records checksum data for a logical range, with a variable-length `sums[]` tail.

`struct btrfs_ordered_extent` tracks one pending write extent. Key fields include file offset, logical length, on-disk bytenr/length, encoded extent metadata, remaining bytes, truncation length, flags, compression type, qgroup reservation, refcount, inode owner, checksum list, fsync log list, waitqueue, rb-tree node, root list node, work/completion state, and bio-context list.

`struct btrfs_file_extent` represents the file extent item target for a write, including disk range, logical length, ram length, offset, and compression.

## Flags

The ordered extent flag enum includes completion/error/logging state bits and mutually exclusive type bits:

- `BTRFS_ORDERED_REGULAR`
- `BTRFS_ORDERED_NOCOW`
- `BTRFS_ORDERED_PREALLOC`
- `BTRFS_ORDERED_COMPRESSED`

Additional modifiers include `BTRFS_ORDERED_ENCODED` and `BTRFS_ORDERED_DIRECT`. Static assertions ensure flags fit in `unsigned long`, and masks define exclusive/type flag groups.

## APIs

The header declares allocation, finish, wait, lookup, logging, range lock, split, error marking, and slab init/exit functions. `btrfs_start_ordered_extent()` is an inline wrapper around the no-writeback variant.

## Integration Notes

This header is central to Btrfs writeback, direct I/O, compression, fsync, transaction commit, qgroup accounting, and subvolume snapshot consistency. Flag invariants are important: only one exclusive type flag is valid, encoded implies compressed, and direct excludes compressed/encoded.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ordered-data.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/orphan.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/orphan.c

## Purpose

`orphan.c` provides small helpers to insert and delete orphan items in a Btrfs root tree.

## Behavior

`btrfs_insert_orphan_item()` builds a key with:

- `objectid = BTRFS_ORPHAN_OBJECTID`
- `type = BTRFS_ORPHAN_ITEM_KEY`
- `offset = caller-supplied offset`

It allocates a path and inserts an empty item with zero payload into the given root.

`btrfs_del_orphan_item()` builds the same key, searches for it with a deletion intent, returns `-ENOENT` if missing, and calls `btrfs_del_item()` if found.

Both functions use `BTRFS_PATH_AUTO_FREE(path)` for cleanup and return `-ENOMEM` on path allocation failure.

## Dependencies and Integration

The file depends on `ctree.h` and `orphan.h`. Orphan items are used by higher-level inode/subvolume cleanup paths to record objects requiring cleanup across transaction boundaries or mount recovery.

## Risk Notes

The helper is intentionally thin. Correctness is delegated to transaction callers and B-tree insertion/deletion primitives.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/orphan.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/orphan.h

## Purpose

`orphan.h` declares Btrfs orphan item insertion and deletion helpers.

## Interfaces

Declared functions:

- `btrfs_insert_orphan_item(struct btrfs_trans_handle *trans, struct btrfs_root *root, u64 offset)`
- `btrfs_del_orphan_item(struct btrfs_trans_handle *trans, struct btrfs_root *root, u64 offset)`

## Integration Notes

The header forward-declares transaction and root types and includes only `<linux/types.h>`. It is consumed by cleanup/recovery and metadata mutation code that needs to record or remove orphan items in a root.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/orphan.h -->