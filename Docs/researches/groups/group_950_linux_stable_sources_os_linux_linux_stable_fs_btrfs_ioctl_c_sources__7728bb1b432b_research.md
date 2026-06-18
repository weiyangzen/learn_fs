# Group Research: group_950_linux_stable_sources_os_linux_linux_stable_fs_btrfs_ioctl_c_sources__7728bb1b432b

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ioctl.c

## Summary
Implements the Btrfs ioctl surface, including subvolume and snapshot management, device management, tree search, inode/path lookup, qgroups, scrub, balance, feature flags, filesystem labels, encoded I/O, io_uring encoded commands, shutdown, and compatibility handling.

## Main Responsibilities
- Translates VFS file attributes and legacy FS flags to/from Btrfs inode flags.
- Creates, snapshots, deletes, sync-waits, and flags subvolumes.
- Handles filesystem/device operations: resize, add/remove device, default subvolume, filesystem/device info, stats, replace, trim, label, feature bits, and shutdown.
- Exposes privileged metadata queries: tree search, inode lookup, inode-to-path, logical-to-inode, subvolume info/rootrefs, space info.
- Drives long-running exclusive operations: relocation-backed resize/remove, balance, scrub, and device replace.
- Handles qgroup enable/disable, create/remove, assign, limit, rescan, status, and wait.
- Bridges Btrfs encoded read/write APIs to ioctl and io_uring command paths.
- Provides 32-bit compat layouts for selected packed UAPI structs.

## Key APIs
- `btrfs_ioctl()`, `btrfs_compat_ioctl()`.
- `btrfs_fileattr_get()`, `btrfs_fileattr_set()`.
- `btrfs_sync_inode_flags_to_i_flags()`.
- `btrfs_ioctl_get_supported_features()`.
- `btrfs_update_ioctl_balance_args()`.
- `btrfs_uring_cmd()`, `btrfs_uring_read_extent_endio()`.

## Important Behavior
File attribute setting rejects unsupported FSX attributes, validates incompatible compression/NOCOW flag combinations, disallows NOCOW on zoned filesystems, updates compression properties, updates inode version/ctime, and persists inode metadata in a transaction.

Subvolume creation allocates a new root item, tree block, anon device, root UUID item, qgroup inheritance, and subvolume inode under metadata reservation. Snapshot creation forces prior delalloc writeback, toggles `snapshot_force_cow`, waits ordered extents, then commits a pending snapshot. Extent tree v2 currently rejects snapshotting and snapshot deletion.

Subvolume deletion supports legacy name lookup and v2 by-name/by-id deletion. By-id deletion may locate a parent outside the caller’s mount point and restricts idmapped mounts to avoid deleting unrelated subvolumes through idmap privilege differences.

Tree search copies headers/items to user buffers using nofault copies after subpage fault-in to avoid livelock. V1 preserves historical overflow behavior by returning an empty item; v2 reports required buffer size on `-EOVERFLOW`.

Device resize/add/remove, balance, and device replace use Btrfs exclusive-operation state to prevent conflicting mutating operations. Resize and device removal support `"cancel"` paths that signal relocation cancellation and wait for running relocation state.

Encoded reads validate privilege and iovec input, call `btrfs_encoded_read()`, then handle regular encoded extents synchronously if `-EIOCBQUEUED` is returned. Encoded writes require write mode, non-empty encoded transform metadata, valid compression/encryption identifiers, and normal write verification before calling `btrfs_do_write_iter()`.

io_uring encoded read/write support stores command-private data in the io_uring PDU. Encoded reads can return `-EAGAIN` for nonblocking reissue, or retain inode/extent locks until asynchronous fill-pages completion schedules task work that copies pages to the user iterator and releases locks.

## State and Synchronization
Uses `mnt_want_write_file()` / `mnt_drop_write_file()` around write-side ioctls, `subvol_sem` for subvolume/root flag changes, exclusive operation helpers for filesystem-wide operations, qgroup locks, balance mutex/lock, root/inode locks, extent locks, and transaction boundaries.

Subvolume creation/deletion interacts with dentries through `start_creating_killable()`, `end_creating()`, `start_removing_killable()`, and `end_removing()`. Balance transfers ownership of `btrfs_balance_control` and exclusive-op state to `btrfs_balance()` when execution starts.

## Risks
This file is a high-risk UAPI boundary. Correctness depends on strict user-copy sizing, compat layout conversion, capability checks, idmapped mount checks, transaction abort decisions, and exclusive-op lifecycle.

io_uring encoded read intentionally returns to userspace with inode/extent locks held and uses lockdep annotations to model the delayed unlock. Any missed cleanup path could leak locks, pages, iovecs, or command-private data.

Several operations copy progress/state back to userspace even on operation errors. That is intentional for scrub/balance style workflows, but callers must preserve the “operation failed but progress copy succeeded” distinction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ioctl.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ioctl.h

## Summary
Declares the Btrfs ioctl and encoded io_uring command interface used by the VFS-facing Btrfs code.

## Main Contents
- Forward declarations for VFS, io_uring, Btrfs inode, fs-info, and balance argument types.
- Entry points for regular and compat ioctl dispatch.
- File attribute get/set hooks.
- Helpers for supported features, inode flag synchronization, balance argument export, and io_uring encoded I/O completion.

## Key Interfaces
- `btrfs_ioctl()`.
- `btrfs_compat_ioctl()`.
- `btrfs_fileattr_get()`, `btrfs_fileattr_set()`.
- `btrfs_ioctl_get_supported_features()`.
- `btrfs_sync_inode_flags_to_i_flags()`.
- `btrfs_update_ioctl_balance_args()`.
- `btrfs_uring_cmd()`.
- `btrfs_uring_read_extent_endio()`.

## Risks
The header is small but exposes cross-subsystem boundaries: VFS ioctl dispatch, file attributes, balance state reporting, and io_uring encoded read completion. Implementations must keep UAPI and compat behavior stable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/locking.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/locking.c

## Summary
Implements Btrfs tree extent-buffer locking, lockdep class assignment for btree nodes, root-node lock acquisition helpers, and the Btrfs DREW lock.

## Main Responsibilities
- Assigns lockdep classes for extent buffer locks by root objectid and tree level.
- Provides read/write lock wrappers around `extent_buffer->lock`.
- Safely locks current root nodes while handling root-node replacement races.
- Unlocks paths upward from a given btree level.
- Implements DREW, a double-reader-writer-exclusion lock where two classes exclude each other but not themselves.

## Key APIs
- `btrfs_set_buffer_lockdep_class()`.
- `btrfs_maybe_reset_lockdep_class()`.
- `btrfs_tree_read_lock_nested()`, `btrfs_tree_read_unlock()`, `btrfs_try_tree_read_lock()`.
- `btrfs_tree_lock_nested()`, `btrfs_tree_unlock()`.
- `btrfs_unlock_up_safe()`.
- `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, `btrfs_try_read_lock_root_node()`.
- `btrfs_drew_lock_init()`, `btrfs_drew_write_lock()`, `btrfs_drew_try_write_lock()`, `btrfs_drew_write_unlock()`, `btrfs_drew_read_lock()`, `btrfs_drew_read_unlock()`.

## Important Behavior
Lockdep class keys are static and selected by special-purpose root objectid, with per-level names for `BTRFS_MAX_LEVEL == 8`. Unknown roots fall back to a default tree keyset.

Tree lock wrappers trace lock timing and unlock events. Under `CONFIG_BTRFS_DEBUG`, write locks record the owning pid in the extent buffer.

Root-node lock helpers loop: take a ref to the current root node, lock it, verify it is still `root->node`, and retry if the root changed concurrently.

DREW locks use atomic reader/writer counters plus wait queues. Readers have priority: writers yield if readers appear, and pending readers prevent new writers from entering.

## State and Synchronization
Tree locks are rw semaphores embedded in extent buffers. DREW uses atomic counters and memory barriers to order counter visibility against wait queue sleeping/wakeup.

## Risks
Lockdep class coverage is tied to `BTRFS_MAX_LEVEL` and the limited number of lockdep subclasses. DREW correctness depends on the atomic barriers around reader/writer count changes and wait conditions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/locking.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/locking.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/locking.h

## Summary
Defines Btrfs btree lock nesting constants, lockdep annotation helpers, tree-lock APIs, assertion helpers, and the DREW lock structure/API.

## Main Contents
- `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK`.
- `enum btrfs_lock_nesting` subclasses for normal, COW, left/right sibling, split, and new-root locking.
- `enum btrfs_lockdep_trans_states`.
- Lockdep macros for wait events, transaction state waits, and io_uring encoded I/O inode lock release/reacquire modeling.
- Tree lock function declarations and root-node lock helpers.
- Debug-only tree lock assertion helpers.
- `struct btrfs_drew_lock` and DREW lock declarations.
- Debug lockdep class reset declarations.

## Important Details
The nesting enum intentionally consumes the available `MAX_LOCKDEP_SUBCLASSES` budget and has a `static_assert()` to prevent silent overflow.

`btrfs_tree_unlock_rw()` dispatches unlock by stored path lock mode and `BUG()`s on invalid mode.

The io_uring lockdep macros model the fact that Btrfs encoded io_uring reads can return to userspace while the inode rwsem remains held and is later released in task work.

## Risks
Adding new btree lock nesting modes requires revisiting lockdep subclass limits. Callers storing lock modes in paths must keep values restricted to `BTRFS_WRITE_LOCK` or `BTRFS_READ_LOCK`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/locking.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/lru_cache.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/lru_cache.c

## Summary
Implements a small generic Btrfs LRU cache backed by a maple tree and per-key linked lists.

## Main Responsibilities
- Initializes bounded or unbounded cache objects.
- Looks up entries by 64-bit key and generation.
- Stores new entries, rejecting duplicate key/generation pairs.
- Evicts the least recently used entry when `max_size` is reached.
- Removes individual entries and clears the cache.

## Key APIs
- `btrfs_lru_cache_init()`.
- `btrfs_lru_cache_lookup()`.
- `btrfs_lru_cache_store()`.
- `btrfs_lru_cache_remove()`.
- `btrfs_lru_cache_clear()`.

## Important Behavior
The maple tree maps the key to a heap-allocated list head. Each list contains entries with the same maple-tree key value. This supports full `u64` keys even on 32-bit systems, where maple tree keys are only `unsigned long`.

Lookup moves a found entry to the tail of the LRU list. Store inserts a new per-key list head when needed or appends to an existing list. If the cache is full, store removes and frees the current least-recently-used entry before linking the new entry.

Removal deletes the entry from both the per-key list and the LRU list. If the per-key list becomes empty, the list head is erased from the maple tree and freed. Entries are freed with `kfree()`.

## State and Synchronization
No internal locking is provided. Callers must serialize cache access. Cache size is updated after successful store/remove operations.

## Risks
Entries must be kmalloc-backed and embed `struct btrfs_lru_cache_entry` at offset zero, because the cache frees entries directly. Duplicate store returns `-EEXIST` after freeing only the temporary list head, not the caller-supplied entry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/lru_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/lru_cache.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/lru_cache.h

## Summary
Defines the generic Btrfs LRU cache data structures and public API.

## Main Contents
- `struct btrfs_lru_cache_entry`.
- `struct btrfs_lru_cache`.
- Safe reverse LRU iteration macro.
- Helper for retrieving the least-recently-used entry.
- Function declarations for init, lookup, store, remove, and clear.

## Important Details
`btrfs_lru_cache_entry` contains both LRU linkage and per-key list linkage. The header documents that it must be embedded as the first member of a kmalloc-allocated owner structure.

`gen` is an optional secondary discriminator for entries sharing a key. The comments caution that many generations per key are stored as a linked list and should remain small.

## Risks
The offset-zero and kmalloc ownership requirements are part of the ABI between this helper and its users. Violating them causes invalid frees or corrupted container interpretation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/lru_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/lzo.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/lzo.c

## Summary
Implements Btrfs LZO compression and decompression, including workspace allocation, on-disk segment format handling, compressed bio construction, compressed bio decompression, and inline extent decompression.

## Main Responsibilities
- Allocates/frees LZO compression workspaces.
- Compresses filemap data into Btrfs compressed bio folios.
- Emits Btrfs LZO headers, segment headers, payloads, and sector padding.
- Decompresses regular compressed bios into target pages.
- Decompresses inline LZO extents into a destination folio.
- Defines supported LZO compression level metadata.

## Key APIs
- `lzo_alloc_workspace()`.
- `lzo_free_workspace()`.
- `lzo_compress_bio()`.
- `lzo_decompress_bio()`.
- `lzo_decompress()`.
- `btrfs_lzo_compress`.

## Important Behavior
Btrfs LZO extents start with a 4-byte little-endian total compressed length, followed by one or more segments. Each segment has a 4-byte little-endian payload length and at most one sector of uncompressed data. Segment headers must not cross sector boundaries, so compression pads up to 3 zero bytes when needed.

Compression reserves an output folio, writes the total-length header placeholder, compresses at most one sector at a time with `lzo1x_1_compress()`, copies each compressed segment into the output bio, and finally writes total compressed size into the first folio. If compressed output grows beyond allowed limits or grows larger than input after the early threshold, it returns `-E2BIG`.

Decompression validates the total LZO length against compressed bio size and maximum compressed extent size. It walks segment headers/payloads across folios, copies payloads into workspace memory, calls `lzo1x_decompress_safe()`, and forwards decompressed buffers to `btrfs_decompress_buf2page()`.

Inline decompression expects exactly one compressed segment after the total-size and segment-size headers. It validates source length, decompresses into the workspace buffer, copies to the destination folio, and zero-fills plus returns `-EIO` if output is shorter than requested.

## State and Synchronization
Workspace objects contain separate LZO scratch memory, decompressed buffer, compressed buffer, and list linkage. Folios queued into bios are owned by bio endio cleanup; only unqueued output folios are freed directly on error.

## Risks
The format parser is sensitive to corrupted lengths, sector-boundary padding, folio switching, and maximum segment size checks. Error handling relies on precise ownership transfer of folios to bios.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/lzo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/messages.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/messages.c

## Summary
Implements Btrfs logging, error decoding, filesystem error handling, fatal panic handling, and 32-bit logical-address limit warnings.

## Main Responsibilities
- Converts filesystem state bits into compact printable state suffixes.
- Decodes selected negative errno values into human-readable messages.
- Handles filesystem errors by recording the error and forcing the filesystem read-only after mount.
- Provides rate-limited Btrfs printk formatting by log level.
- Emits one-time warnings/errors for 32-bit page-cache address limits.
- Implements fatal panic/BUG policy depending on mount options.

## Key APIs
- `btrfs_decode_error()`.
- `__btrfs_handle_fs_error()`.
- `_btrfs_printk()`.
- `btrfs_warn_32bit_limit()`, `btrfs_err_32bit_limit()` on 32-bit builds.
- `__btrfs_panic()`.

## Important Behavior
`__btrfs_handle_fs_error()` ignores `-EROFS` when the superblock is already read-only, prints a critical message with device, function, line, errno, decoded error, and optional format string, records `fs_error`, and forces the filesystem read-only once the superblock is born.

Before forcing read-only, it stops discard. It intentionally does not cancel device replace to avoid deadlock risk; replacement may continue until completion.

`_btrfs_printk()` uses one ratelimit state per log level so lower-priority floods do not suppress higher-priority messages. It includes filesystem state characters when an `fs_info` is available.

`__btrfs_panic()` panics only when the filesystem has `PANIC_ON_FATAL_ERROR`; otherwise it logs a critical message and relies on the caller macro to `BUG()`.

## State and Synchronization
Filesystem state is read with `READ_ONCE()`. Superblock label/state access in callers may require their own locks. Printing is conditional on `CONFIG_PRINTK`.

## Risks
The error path is intentionally one-way for mounted writable filesystems: after serious errors, the filesystem is forced read-only. Callers must choose error codes carefully because subsequent generic failures caused by prior FS error should use `-EROFS`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/messages.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/messages.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/messages.h

## Summary
Defines Btrfs logging macros, assertion macros, filesystem error/panic helpers, and 32-bit address-limit constants.

## Main Contents
- `btrfs_crit()`, `btrfs_err()`, `btrfs_warn()`, `btrfs_info()`.
- Ratelimited variants for each log level.
- Dynamic-debug and debug-build `btrfs_debug()` variants.
- `ASSERT()` with optional printk-style message under `CONFIG_BTRFS_ASSERT`.
- `DEBUG_WARN()`.
- `btrfs_handle_fs_error()` and `btrfs_panic()` wrappers.
- `btrfs_decode_error()` declaration.
- 32-bit maximum file size and early warning threshold constants.

## Important Details
Logging macros wrap `_btrfs_printk()` in RCU read-side protection so device/fs names can be safely printed.

When `CONFIG_PRINTK` is disabled, logging expands to `btrfs_no_printk()` stubs. When assertions are disabled, `ASSERT()` still compile-checks the condition with `BUILD_BUG_ON_INVALID()`.

The assertion macro supports `ASSERT(cond)`, `ASSERT(cond, "msg")`, and `ASSERT(cond, "fmt %d", value)` by splitting the first variadic token from the rest.

## Risks
The macros form a broad diagnostic contract used across Btrfs. Because many branches compile differently depending on `CONFIG_PRINTK`, `CONFIG_DYNAMIC_DEBUG`, `DEBUG`, and `CONFIG_BTRFS_ASSERT`, build coverage across configurations matters.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/messages.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/misc.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/misc.h

## Summary
Provides miscellaneous Btrfs helper macros and inline functions for cleanup attributes, enum bit definitions, bio iteration, conditional wakeups, percentage math, power-of-two checks, simple bytenr rbtree helpers, and bitmap range tests.

## Main Contents
- `AUTO_KFREE()` and `AUTO_KVFREE()` cleanup helpers.
- `ENUM_BIT()` bit-enum helper.
- Bio physical address and block-iteration helpers.
- `bio_get_size()` and `init_bvec_iter_for_bio()`.
- Conditional wakeup helpers with and without implied memory barriers.
- `mult_perc()`, `is_power_of_two_u64()`, `has_single_bit_set()`.
- `struct rb_simple_node` plus search/insert helpers by `bytenr`.
- `bitmap_test_range_all_set()` and `bitmap_test_range_all_zero()`.

## Important Behavior
`btrfs_bio_for_each_block()` iterates a bio by Btrfs block size and handles large folios/highmem by deriving each iteration’s physical address from the current bvec iterator.

`cond_wake_up()` uses `wq_has_sleeper()`, which includes the barrier needed for `waitqueue_active()` style checks. `cond_wake_up_nomb()` is for call sites where a previous atomic operation or lock/unlock already supplies the barrier.

The simple rbtree helpers assume owner structures begin with `struct rb_simple_node` fields and compare solely by `bytenr`.

## Risks
The conditional wakeup variants must be chosen according to memory-ordering context. Bio iteration helpers assume all folios in the bio cover at least one block.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ordered-data.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ordered-data.c

## Summary
Implements Btrfs ordered extent lifecycle management. Ordered extents track in-flight writes from logical file ranges to final metadata insertion, including COW/NOCOW/prealloc/compressed/direct/encoded variants, checksums, qgroup reservations, writeback completion, waiting, logging support, and splitting.

## Main Responsibilities
- Allocates and inserts ordered extents into per-inode rbtrees and per-root ordered lists.
- Tracks bytes left to write and marks ordered extents done/error/complete.
- Queues ordered extent completion work.
- Removes completed ordered extents and releases metadata/qgroup/accounting state.
- Waits ordered extents by inode range, root, all roots, or block-group disk range.
- Looks up ordered extents by point and range.
- Provides ordered extents to fsync logging.
- Locks file ranges while flushing overlapping ordered extents.
- Splits direct-I/O ordered extents for partial submitted ranges.
- Owns the ordered extent slab cache.

## Key APIs
- `btrfs_alloc_ordered_extent()`.
- `btrfs_add_ordered_sum()`.
- `btrfs_mark_ordered_extent_error()`.
- `btrfs_finish_ordered_extent()`.
- `btrfs_mark_ordered_io_finished()`.
- `btrfs_dec_test_ordered_pending()`.
- `btrfs_put_ordered_extent()`.
- `btrfs_remove_ordered_extent()`.
- `btrfs_wait_ordered_extents()`, `btrfs_wait_ordered_roots()`, `btrfs_wait_ordered_range()`.
- `btrfs_start_ordered_extent_nowriteback()`.
- `btrfs_lookup_ordered_extent()`, `btrfs_lookup_ordered_range()`, `btrfs_lookup_first_ordered_extent()`, `btrfs_lookup_first_ordered_range()`.
- `btrfs_get_ordered_extents_for_logging()`.
- `btrfs_lock_and_flush_ordered_range()`, `btrfs_try_lock_ordered_range()`.
- `btrfs_split_ordered_extent()`.
- `ordered_data_init()`, `ordered_data_exit()`.

## Important Behavior
Ordered extents are indexed in an inode rbtree by non-overlapping file ranges. Insert panics on overlap because overlap implies double allocation or accounting corruption. A cached `ordered_tree_last` accelerates repeated nearby lookups.

Allocation validates type flags, enforces relationships such as DIRECT not with COMPRESSED/ENCODED and ENCODED only with COMPRESSED, transfers or frees qgroup reservations depending on COW versus NOCOW/PREALLOC, grabs an inode reference, increments outstanding extents, initializes checksum/log/root/work lists, and inserts the object.

Finishing I/O decrements `bytes_left` under `ordered_tree_lock`. When it reaches zero, the code sets `BTRFS_ORDERED_IO_DONE`, wakes waiters, takes a completion-work reference, and queues work on either free-space or regular endio write workers. Failed COW writes set `BTRFS_INODE_COW_WRITE_ERROR` so fast fsync waits for ordered completion before logging extent maps that may point at unwritten extents.

Removal releases outstanding extent accounting, delalloc metadata, qgroup-related reservation state through lower layers, global ordered byte counters, rbtree membership, pending transaction wait accounting, root ordered-list membership, and waiters. It sets `BTRFS_ORDERED_COMPLETE` before waking waiters.

Root/all-root waiting splices ordered lists under locks, queues flush work for matching extents, waits for completion, and preserves skipped entries. Block-group filtering is by disk bytenr/disk length.

Range waiting starts writeback, waits page writeback, then walks ordered extents backward from the range end so all overlapping ordered extents complete before returning any saved writeback or ordered error.

Splitting creates a new ordered extent for the first `len` bytes, trims the original extent in place, moves matching checksum sums, preserves done/truncated state as needed, and updates root/inode structures under both root ordered lock and inode ordered-tree lock. Compressed extents and partially completed inconsistent extents cannot be split.

## State and Synchronization
Uses per-inode `ordered_tree_lock`, per-root `ordered_extent_lock` and `ordered_extent_mutex`, filesystem `ordered_root_lock` and `ordered_operations_mutex`, ordered extent wait queues, completions, workqueues, refcounts, and transaction pending ordered counters.

References are held by callers, the rbtree, logging lists, completion work, and wait/flush paths. The final put schedules delayed iput for the inode and frees checksum sums before returning the ordered extent to the slab.

## Risks
This file is concurrency- and accounting-heavy. Bugs can corrupt extent accounting, leak qgroup reservations, race transaction commit pending ordered waits, expose unwritten COW extents to fsync logging, or deadlock extent locking/writeback.

The split path deliberately updates an existing rbtree key range without removing the original node because ordering remains valid. That relies on strict preconditions: split length is within the extent, the extent is not compressed, disk and logical lengths match, and partial completion state is consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ordered-data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ordered-data.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ordered-data.h

## Summary
Defines ordered extent structures, flags, file extent metadata, and public ordered-data APIs.

## Main Contents
- `struct btrfs_ordered_sum`.
- Ordered extent status/type flag enum.
- `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS`.
- `struct btrfs_ordered_extent`.
- `struct btrfs_file_extent`.
- Function declarations for allocation, lookup, finish, wait, split, error marking, and slab lifecycle.

## Important Details
Ordered extent flags include status bits (`IO_DONE`, `COMPLETE`, `IOERR`, `TRUNCATED`, `LOGGED`, `LOGGED_CSUM`, `PENDING`) and mutually exclusive type bits (`REGULAR`, `NOCOW`, `PREALLOC`, `COMPRESSED`). `ENCODED` is an extra compressed-write bit; `DIRECT` is an extra direct-I/O bit for regular/NOCOW/prealloc writes.

`struct btrfs_ordered_extent` mirrors file extent item fields such as file offset, logical length, RAM length, disk bytenr, disk length, and offset. It also stores bytes left, truncation length, compression type, qgroup reservation, inode pointer, checksums, logging linkage, rbtree node, root list node, work items, completion, and bio ordered-csum linkage.

## Risks
Only one exclusive type flag may be set. Mislabeling DIRECT, ENCODED, COMPRESSED, NOCOW, or PREALLOC changes completion, metadata insertion, qgroup release, and split behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ordered-data.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/orphan.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/orphan.c

## Summary
Implements insertion and deletion of Btrfs orphan items in a root.

## Main Responsibilities
- Inserts empty orphan items keyed by orphan objectid and caller-provided offset.
- Deletes existing orphan items by searching and removing the item from the tree.

## Key APIs
- `btrfs_insert_orphan_item()`.
- `btrfs_del_orphan_item()`.

## Important Behavior
Both functions build a key with `objectid = BTRFS_ORPHAN_OBJECTID`, `type = BTRFS_ORPHAN_ITEM_KEY`, and `offset = offset`.

Insertion allocates a path and calls `btrfs_insert_empty_item()` with zero item size.

Deletion searches with modification intent, returns search errors directly, returns `-ENOENT` if the item is absent, and calls `btrfs_del_item()` when found.

## State and Synchronization
The caller supplies the active transaction and root. Path lifetime is handled with `BTRFS_PATH_AUTO_FREE`.

## Risks
The helpers are intentionally thin. Correctness depends on callers choosing the right root/offset and holding a transaction appropriate for modifying the root tree.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/orphan.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/orphan.h

## Summary
Declares Btrfs orphan item insertion and deletion helpers.

## Main Contents
- Forward declarations for `struct btrfs_trans_handle` and `struct btrfs_root`.
- `btrfs_insert_orphan_item()`.
- `btrfs_del_orphan_item()`.

## Risks
The header exposes only transaction-root-offset operations. Callers must enforce orphan lifecycle policy outside this file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/orphan.h -->