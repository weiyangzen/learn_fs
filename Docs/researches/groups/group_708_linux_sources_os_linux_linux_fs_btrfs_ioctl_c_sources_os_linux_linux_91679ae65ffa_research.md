# Group Research: group_708_linux_sources_os_linux_linux_fs_btrfs_ioctl_c_sources_os_linux_linux_91679ae65ffa

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ioctl.c -->
# File Research: sources/os/linux/linux/fs/btrfs/ioctl.c

This file implements the Btrfs ioctl control plane, VFS file attribute integration, and Btrfs-specific io_uring encoded I/O commands. It is the primary userspace entry point for subvolume/snapshot operations, device management, balance/scrub/quota controls, tree and inode lookup queries, feature flags, labels, send metadata, encoded reads/writes, transaction sync, and forced shutdown.

Core responsibilities:
- Map Btrfs inode flags to/from VFS `FS_IOC_GETFLAGS`/fileattr flags, including compression, no-COW, immutable, append, sync, noatime, dirsync, and verity state.
- Create, snapshot, delete, query, and sync subvolumes.
- Expose tree-search, inode-to-path, logical-to-inode, subvolume-info, and rootref lookup ioctls.
- Manage filesystem devices: resize, add, remove, device info, filesystem info, dev stats, and device replace.
- Coordinate exclusive operations for resize, device removal, device replace, device add, and balance.
- Run defrag, trim, scrub, balance, quota/qgroup, quota rescan, and transaction sync operations.
- Get/set filesystem label and supported/active feature flags.
- Bridge `BTRFS_IOC_SEND`, received-subvolume metadata updates, and 32-bit compat UAPI layouts.
- Implement encoded read/write via traditional ioctl and io_uring command paths.
- Dispatch all Btrfs-specific ioctl commands through `btrfs_ioctl()` and compat remapping through `btrfs_compat_ioctl()`.

Important behavior:
- UAPI structs are copied with `memdup_user()`/`copy_from_user()` and path/name buffers are explicitly NUL-checked.
- Mutating operations generally require `CAP_SYS_ADMIN` or owner checks, `mnt_want_write_file()`, root readonly checks, and transaction handling.
- File flag changes reject unsupported or conflicting combinations such as compression plus NOCOW; zoned filesystems reject `FS_NOCOW_FL`.
- Compression fileattr changes update the `btrfs.compression` property inside the same transaction as inode flag updates.
- Subvolume creation reserves metadata/qgroup space before transaction work and carefully transfers anon device ownership to the new root.
- Snapshot creation forces future writes to COW, waits ordered extents, and commits through a pending snapshot transaction path.
- Subvolume deletion supports name-based v1/v2 and id-based v2 deletion; idmapped mount deletion by subvolid is deliberately restricted.
- Tree search copies results incrementally, faults user buffers before copying to avoid livelock, and preserves v1 overflow behavior.
- Received-subvolume UUID updates check UUID-tree item overflow before starting a transaction to avoid user-triggered transaction aborts.
- Scrub copies progress back to userspace even on selected errors so userspace can resume.
- Encoded I/O requires `CAP_SYS_ADMIN`; encoded writes require write mode and reject invalid reserved fields, unsupported compression/encryption ids, and inconsistent unencoded ranges.
- io_uring encoded reads may return to userspace with the inode lock held; lockdep annotations transfer cleanup to task-work completion.

Major internal areas:
- `btrfs_fileattr_get()` / `btrfs_fileattr_set()` implement VFS file attribute support.
- `create_subvol()`, `create_snapshot()`, `btrfs_mksubvol()`, and `btrfs_mksnapshot()` implement subvolume and snapshot creation.
- `btrfs_ioctl_snap_destroy()` implements subvolume deletion policy and dispatch.
- `search_ioctl()` plus `copy_to_sk()` implement tree-search ioctls.
- `btrfs_search_path_in_tree*()` implement privileged and permission-checked inode path lookup.
- Device operations call into `volumes.c`, `dev-replace.c`, scrub, and exclusive-operation helpers.
- Balance and quota ioctls call into the balance and qgroup subsystems while preserving mount write and locking order.
- Encoded ioctl/io_uring paths call `btrfs_encoded_read()`, `btrfs_encoded_read_regular*()`, and `btrfs_do_write_iter()`.

Cross-file relationships:
- Public prototypes are declared in `ioctl.h`.
- Uses locking helpers from `locking.h`, ordered extent waiting from ordered-data paths, qgroup metadata/data reservation APIs, transaction APIs, root-tree APIs, send support, scrub, device replacement, compression, defrag, uuid-tree, and fsverity.
- The io_uring encoded read endio callback is exported for compressed/encoded read completion integration.

Risk notes:
- This is a high-risk integration hub. Correctness depends on ordering among permission checks, mount write acquisition, exclusive-op state, transaction lifetime, root references, qgroup reservation conversion/freeing, user copy-back semantics, and inode/extent locking.
- Compat UAPI layouts are hand-translated and must stay byte-compatible with userspace structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ioctl.h -->
# File Research: sources/os/linux/linux/fs/btrfs/ioctl.h

This header exposes the Btrfs ioctl/fileattr/io_uring entry points implemented in `ioctl.c`.

Exports:
- `btrfs_ioctl()` and `btrfs_compat_ioctl()` for VFS ioctl dispatch.
- `btrfs_fileattr_get()` and `btrfs_fileattr_set()` for VFS file attribute integration.
- `btrfs_ioctl_get_supported_features()` for feature-flag UAPI support.
- `btrfs_sync_inode_flags_to_i_flags()` to synchronize internal Btrfs inode flags into VFS inode flags.
- `btrfs_update_ioctl_balance_args()` to populate userspace balance status structs from live balance state.
- `btrfs_uring_cmd()` and `btrfs_uring_read_extent_endio()` for Btrfs io_uring encoded I/O commands and async read completion.

Design notes:
- The header uses forward declarations to avoid pulling large Btrfs and VFS structure definitions into callers.
- It is intentionally small and acts as the public boundary for ioctl-facing helpers used elsewhere in the filesystem.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/locking.c -->
# File Research: sources/os/linux/linux/fs/btrfs/locking.c

This file implements extent-buffer tree locking wrappers, Btrfs lockdep class assignment, and the DREW double-reader/writer-exclusion lock used by snapshot coordination.

Core responsibilities:
- Assign lockdep classes to extent-buffer locks based on root objectid and tree level.
- Provide read/write lock wrappers around `extent_buffer->lock`, with tracing and lockdep nesting.
- Lock the current root node safely even if the root pointer changes while taking references.
- Unlock Btrfs path nodes above a given level.
- Implement `btrfs_drew_lock`, a lock that excludes readers from writers but allows reader-reader and writer-writer sharing.

Key mechanisms:
- Under `CONFIG_DEBUG_LOCK_ALLOC`, static keysets are defined for special roots such as root, extent, chunk, dev, csum, quota, log, reloc, uuid, free-space, block-group, raid-stripe, remap, and generic tree roots.
- `btrfs_set_buffer_lockdep_class()` maps an extent buffer to a root/level lock class.
- `btrfs_maybe_reset_lockdep_class()` reapplies classes for roots marked with `BTRFS_ROOT_RESET_LOCKDEP_CLASS`.
- `btrfs_tree_read_lock_nested()`, `btrfs_try_tree_read_lock()`, `btrfs_tree_read_unlock()`, `btrfs_tree_lock_nested()`, and `btrfs_tree_unlock()` wrap rwsem operations with tracepoints.
- `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, and `btrfs_try_read_lock_root_node()` loop until the locked buffer still matches `root->node`.
- `btrfs_unlock_up_safe()` releases held path locks from a level upward unless `path->keep_locks` is set.
- DREW lock read/write paths use atomic counters, waitqueues, and memory barriers to ensure pending readers prevent new writers and waiters observe counter transitions.

Important invariants:
- Lockdep setup assumes `BTRFS_MAX_LEVEL == 8`.
- Tree locks preserve standard rwsem semantics: writer excludes all, readers share.
- DREW locks prefer readers when readers and writers race.
- Root-node locking must validate the locked buffer against the current root node before returning it.

Cross-file relationships:
- Declarations and inline helpers live in `locking.h`.
- Used throughout btree search/update, snapshot creation, relocation, encoded I/O lockdep handoff, and transaction wait annotations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/locking.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/locking.h -->
# File Research: sources/os/linux/linux/fs/btrfs/locking.h

This header defines Btrfs lock nesting classes, lockdep helper macros, tree-lock APIs, and the DREW lock type.

Key definitions:
- `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` encode path lock state.
- `enum btrfs_lock_nesting` defines lockdep subclasses for normal, COW, left/right sibling, left/right COW, split, and new-root locking.
- `enum btrfs_lockdep_trans_states` defines transaction state wait-event lockdep maps.
- `struct btrfs_drew_lock` stores reader/writer counters and waitqueues.

Exported APIs:
- Tree lock wrappers: `btrfs_tree_lock_nested()`, `btrfs_tree_lock()`, `btrfs_tree_unlock()`, `btrfs_tree_read_lock_nested()`, `btrfs_tree_read_lock()`, `btrfs_tree_read_unlock()`, and `btrfs_try_tree_read_lock()`.
- Root-node locking: `btrfs_lock_root_node()`, `btrfs_read_lock_root_node()`, and `btrfs_try_read_lock_root_node()`.
- Path unlocking: `btrfs_unlock_up_safe()` and `btrfs_tree_unlock_rw()`.
- DREW lock lifecycle and operations.
- Lockdep class hooks for extent buffers when debug lock allocation is enabled.

Lockdep helpers:
- `btrfs_might_wait_for_event()`, `btrfs_lockdep_acquire()`, and `btrfs_lockdep_release()` annotate wait-event conditions.
- `btrfs_lockdep_inode_acquire()` and `btrfs_lockdep_inode_release()` model io_uring encoded I/O returning with an inode lock held.
- Transaction state helpers annotate transaction wait-state transitions.
- Static assertion prevents adding more nesting classes than lockdep supports.

Design notes:
- This header centralizes lock ordering documentation for Btrfs btree operations.
- The explicit nesting classes are important because tree balancing and COW frequently lock peer or replacement nodes while a related node is already locked.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/locking.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/lru_cache.c -->
# File Research: sources/os/linux/linux/fs/btrfs/lru_cache.c

This file implements a small generic Btrfs LRU cache built on a maple tree plus per-key linked lists.

Core responsibilities:
- Initialize cache state with optional maximum size.
- Look up entries by 64-bit key plus optional generation.
- Store new entries and evict the least-recently-used entry when a bounded cache is full.
- Remove and free entries.
- Clear all entries.

Key mechanisms:
- The maple tree maps the key value to a `list_head` containing one or more entries.
- `match_entry()` scans the per-key list for exact `key` and `gen` matches.
- `btrfs_lru_cache_lookup()` moves a found entry to the tail of the global LRU list.
- `btrfs_lru_cache_store()` allocates a per-key list head for new keys, handles `-EEXIST` by appending to the existing list, rejects duplicate key/generation pairs, and evicts from the global LRU head if `max_size` is reached.
- `btrfs_lru_cache_remove()` removes both list links, erases and frees an empty per-key head, frees the embedded entry object, and decrements size.
- `btrfs_lru_cache_clear()` walks the LRU list and removes everything.

Important invariants:
- Entries are heap-allocated objects whose first member is `struct btrfs_lru_cache_entry`; removal frees the containing object with `kfree()`.
- Cache users must provide external synchronization if needed; this module does not lock internally.
- The per-key list handles 64-bit keys on 32-bit systems where maple tree keys are only unsigned long width.

Cross-file relationships:
- Public types and iteration helpers are in `lru_cache.h`.
- Uses Btrfs `ASSERT()` from `messages.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/lru_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/lru_cache.h -->
# File Research: sources/os/linux/linux/fs/btrfs/lru_cache.h

This header defines the generic Btrfs LRU cache entry and cache container.

Key structures:
- `struct btrfs_lru_cache_entry` is intended to be embedded at offset zero in a caller-owned object. It stores global LRU linkage, 64-bit key, optional generation, and per-key list linkage.
- `struct btrfs_lru_cache` stores the global LRU list, maple tree of key-to-list mappings, current size, and maximum size.

Exported API:
- `btrfs_lru_cache_init()`
- `btrfs_lru_cache_lookup()`
- `btrfs_lru_cache_store()`
- `btrfs_lru_cache_remove()`
- `btrfs_lru_cache_clear()`

Helpers:
- `btrfs_lru_cache_for_each_entry_safe()` iterates entries from most-recent side safely.
- `btrfs_lru_cache_lru_entry()` returns the least recently used entry or NULL.

Design notes:
- The optional generation allows multiple entries for the same key when callers need versioned cache records.
- The key is stored inside the entry to preserve full 64-bit identity even on 32-bit maple-tree key platforms.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/lru_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/lzo.c -->
# File Research: sources/os/linux/linux/fs/btrfs/lzo.c

This file implements Btrfs LZO compression and decompression for compressed extents and inline compressed extents.

On-disk format:
- A 4-byte little-endian extent header records total compressed size including the header.
- Each segment has a 4-byte little-endian segment length followed by compressed payload.
- Each segment represents at most one filesystem sector of uncompressed data.
- Segment headers must not cross sector boundaries; up to three zero padding bytes may be inserted at the end of a sector.
- Inline LZO extents support only one segment.

Workspace management:
- `struct workspace` owns LZO working memory, a decompression buffer, a compression buffer, and a list node.
- `lzo_alloc_workspace()` allocates LZO memory and buffers sized by `lzo1x_worst_compress(sectorsize)`.
- `lzo_free_workspace()` frees workspace allocations.

Compression path:
- `lzo_compress_bio()` compresses file data one sector at a time from the inode mapping.
- It allocates compressed folios, reserves space for the total-size header, writes segment headers and payloads, pads sector tails when needed, and queues folios into the compressed bio.
- `copy_compressed_data_to_bio()` enforces segment-header alignment, copies compressed payload in sector-bounded chunks, checks output growth against the original length, and manages folio rollover.
- Compression aborts with `-E2BIG` when data grows too much, including an early check after more than two sectors.
- On success, the first header is patched with the final compressed byte count.

Decompression path:
- `lzo_decompress_bio()` reads the total-size header, validates it against the compressed bio size and maximum compressed extent size, then iterates all segments.
- Segment payloads are copied into the workspace buffer even when they span folios.
- `lzo1x_decompress_safe()` expands each segment into the workspace buffer, then `btrfs_decompress_buf2page()` copies data into destination pages.
- Corrupt headers return `-EUCLEAN`; oversized segments and LZO failures return I/O-style errors with Btrfs error messages.
- `lzo_decompress()` handles inline extents, validating the outer and segment length headers before decompressing into a destination folio.

Important invariants:
- Segment headers never cross sector boundaries.
- A regular compressed extent may contain multiple sector-sized segments; an inline extent is validated as a single segment.
- Output folios already queued into a bio are released by bio completion; only unqueued folios are freed locally on error.
- The exported compression level descriptor advertises only level 1/default 1 for LZO.

Cross-file relationships:
- Integrates with `compression.h` workspace dispatch and compressed bio helpers.
- Uses Btrfs folio allocation/free helpers, inode/root identifiers for error reporting, and generic LZO library calls.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/lzo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/messages.c -->
# File Research: sources/os/linux/linux/fs/btrfs/messages.c

This file implements Btrfs logging, error decoding, filesystem error handling, fatal panic handling, and 32-bit address-limit warnings.

Core responsibilities:
- Convert selected errno values to stable human-readable Btrfs error strings.
- Format filesystem state bits into compact log suffixes.
- Print Btrfs messages with device id, log level, state suffix, and rate limiting.
- Handle filesystem errors by recording the error, stopping discard, forcing the filesystem readonly, and logging the transition.
- Panic or BUG on fatal errors depending on mount options.
- Warn once when 32-bit kernels approach or reach logical-address limits.

Key mechanisms:
- `btrfs_state_to_string()` converts notable `fs_state` bits into a short state string; plain readonly is intentionally not treated as an error state.
- `btrfs_decode_error()` maps common Btrfs errors including `-EUCLEAN`, `-EDQUOT`, and `-EROFS`.
- `__btrfs_handle_fs_error()` logs critical error context, stores `fs_error`, skips full handling during mount, and forces a born writable superblock readonly.
- `_btrfs_printk()` uses one ratelimit state per printk level so less important floods do not suppress critical logs.
- `__btrfs_panic()` either calls `panic()` when `PANIC_ON_FATAL_ERROR` is set or logs a critical message before the caller BUGs.
- 32-bit limit helpers set warning/error flags so messages are emitted once.

Important behavior:
- `-EROFS` while the superblock is already readonly is treated as safe and does not force additional error handling.
- Device replace is not canceled during forced readonly to avoid deadlock risk.
- Under `CONFIG_BTRFS_DEBUG`, normal Btrfs printk output is not rate-limited.

Cross-file relationships:
- Public macros and prototypes are in `messages.h`.
- Uses filesystem state and mount option definitions from `fs.h`/`super.h`, and stops discard through `discard.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/messages.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/messages.h -->
# File Research: sources/os/linux/linux/fs/btrfs/messages.h

This header defines Btrfs logging macros, assertion behavior, filesystem error handling entry points, panic helpers, and 32-bit limit warning declarations.

Logging API:
- `btrfs_crit()`, `btrfs_err()`, `btrfs_warn()`, and `btrfs_info()` log with filesystem/device context under RCU.
- `btrfs_*_rl()` variants add per-call-site rate limiting.
- `btrfs_debug()` and `btrfs_debug_rl()` integrate with dynamic debug or compile out in non-debug builds.
- When printk is unavailable, logging expands to no-op stubs.

Assertions and debug:
- `ASSERT()` is active under `CONFIG_BTRFS_ASSERT`; it supports optional format strings and BUGs on failure.
- When assertions are disabled, the condition is still compile-checked without generated runtime code.
- `DEBUG_WARN()` emits only for `CONFIG_BTRFS_DEBUG`.

Error and panic API:
- `btrfs_handle_fs_error()` wraps `__btrfs_handle_fs_error()` with function and line metadata.
- `btrfs_decode_error()` exposes errno-to-string mapping.
- `btrfs_panic()` wraps `__btrfs_panic()` and then BUGs unless the panic path terminates first.

32-bit support:
- Defines `BTRFS_32BIT_MAX_FILE_SIZE` and early warning threshold for logical address limits.
- Declares warning/error helpers on 32-bit builds.

Design notes:
- The macros centralize Btrfs log formatting so callers do not manually assemble device and filesystem state context.
- The assertion macro includes format-string compile checking to avoid malformed debug messages.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/messages.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/misc.h -->
# File Research: sources/os/linux/linux/fs/btrfs/misc.h

This header contains small generic Btrfs utility macros and inline helpers.

Utilities:
- `AUTO_KFREE()` and `AUTO_KVFREE()` define cleanup-attribute pointers initialized to NULL.
- `ENUM_BIT()` defines enum values that represent bit masks.
- `bio_iter_phys()` returns the physical address for a bio iterator’s current bvec.
- `btrfs_bio_for_each_block()` and `btrfs_bio_for_each_block_all()` iterate bios in filesystem block-sized chunks.
- `bio_get_size()` sums all bvec lengths in a non-cloned bio.
- `init_bvec_iter_for_bio()` creates a full-size iterator for a bio.

Wait and math helpers:
- `cond_wake_up()` wakes a waitqueue only if sleepers exist and relies on the full barrier implied by `wq_has_sleeper()`.
- `cond_wake_up_nomb()` is a no-extra-barrier variant for paths where previous code already supplies ordering.
- `mult_perc()` computes a percentage of a 64-bit value.
- `is_power_of_two_u64()` and `has_single_bit_set()` provide 64-bit-safe single-bit checks.

Simple rbtree helpers:
- `struct rb_simple_node` is a bytenr-keyed node prefix.
- `rb_simple_search()` finds an exact bytenr.
- `rb_simple_search_first()` finds the first node at or after a bytenr.
- `rb_simple_insert()` inserts by bytenr with `rb_find_add()`.

Bitmap helpers:
- `bitmap_test_range_all_set()` and `bitmap_test_range_all_zero()` test whether a bitmap range is entirely set or clear.

Design notes:
- This header collects low-level helpers used across unrelated Btrfs subsystems.
- Several helpers assume caller-level constraints, such as non-cloned bios or structures beginning with the expected rbtree prefix.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ordered-data.c -->
# File Research: sources/os/linux/linux/fs/btrfs/ordered-data.c

This file implements Btrfs ordered extents: in-memory records for writes whose data I/O has been submitted or is pending and whose file extent/checksum metadata still needs finalization.

Core data model:
- Each inode owns an rbtree of `btrfs_ordered_extent` records keyed by file offset.
- Each root also has an ordered extent list, and filesystem-wide `ordered_roots` tracks roots with pending ordered extents.
- Ordered extents track file range, disk range, ram bytes, compression type, qgroup reservation, checksums, bytes left to write, flags, refs, waitqueue, work items, and root/log list links.
- A slab cache stores ordered extent objects.

Creation and insertion:
- `alloc_ordered_extent()` validates type flags, handles qgroup data reservation transfer/freeing, initializes the object, grabs the inode, and increments outstanding extent accounting.
- `btrfs_alloc_ordered_extent()` adapts `struct btrfs_file_extent` details for regular, NOCOW, PREALLOC, compressed, encoded, and direct I/O cases.
- `insert_ordered_extent()` inserts into the inode rbtree, panics on overlap, increments `ordered_bytes`, and links the entry to the root and filesystem root lists.

I/O completion:
- `can_finish_ordered_extent()` subtracts completed bytes from `bytes_left`, marks I/O errors, sets `BTRFS_ORDERED_IO_DONE` when all data I/O is finished, wakes waiters, and takes a ref for finish work.
- `btrfs_finish_ordered_extent()` handles one completion range and queues metadata finalization work when complete.
- `btrfs_mark_ordered_io_finished()` walks all ordered extents intersecting a range and marks the corresponding portions done.
- `btrfs_dec_test_ordered_pending()` is an older/cached single-extent decrement helper used by completion paths that must atomically test final completion.
- Failed COW writes set `BTRFS_INODE_COW_WRITE_ERROR` so fast fsync waits for ordered completion before logging stale extent maps.

Removal and lifetime:
- `btrfs_remove_ordered_extent()` removes an extent from the inode rbtree and root lists, releases delayed allocation metadata, decrements ordered byte accounting and outstanding extents, handles transaction `pending_ordered` wakeups, sets `BTRFS_ORDERED_COMPLETE`, and wakes extent waiters.
- `btrfs_put_ordered_extent()` drops refs, schedules delayed inode iput, frees checksum records, and returns the object to the slab cache.
- `btrfs_add_ordered_sum()` appends checksum records to an ordered extent.
- `btrfs_mark_ordered_extent_error()` marks the extent and sets mapping error.

Waiting and flushing:
- `btrfs_wait_ordered_extents()` starts and waits for up to `nr` ordered extents in a root, optionally filtered by block group disk range.
- `btrfs_wait_ordered_roots()` iterates filesystem roots with pending ordered extents.
- `btrfs_start_ordered_extent_nowriteback()` starts writeback for dirty pages except an optional excluded range, then waits for `BTRFS_ORDERED_COMPLETE`.
- `btrfs_wait_ordered_range()` starts writeback and waits all ordered extents overlapping a file range, preserving writeback errors after waiting.
- `btrfs_lock_and_flush_ordered_range()` locks an extent range and repeatedly flushes overlapping ordered extents until none remain.
- `btrfs_try_lock_ordered_range()` implements the nonblocking variant.

Lookup and logging:
- `btrfs_lookup_ordered_extent()`, `btrfs_lookup_ordered_range()`, `btrfs_lookup_first_ordered_extent()`, and `btrfs_lookup_first_ordered_range()` provide refcounted ordered extent lookup variants.
- `btrfs_get_ordered_extents_for_logging()` collects not-yet-logged ordered extents for fsync logging while the inode is locked.

Splitting:
- `btrfs_split_ordered_extent()` splits the first `len` bytes of a non-compressed ordered extent into a new ordered extent.
- It rejects zero-length/oversized splits, errored extents, partially completed inconsistent extents, and compressed extents.
- The split moves checksum records for the first range, adjusts disk/file fields, preserves truncated state, and updates root/inode structures under both root ordered lock and inode ordered tree lock.

Important invariants:
- Ordered extents for an inode must never overlap.
- Exactly one exclusive type flag must be set among regular, NOCOW, PREALLOC, and compressed.
- Direct I/O cannot be combined with compressed or encoded flags.
- Encoded ordered extents must also be compressed.
- Metadata completion is distinct from data I/O completion: `IO_DONE` means data I/O finished, `COMPLETE` means the ordered extent was removed after metadata work.
- Transaction commit waiters rely on `BTRFS_ORDERED_PENDING` and `pending_ordered` accounting.
- Free-space inode ordered extents avoid some lockdep annotations because their wait context differs.

Cross-file relationships:
- Public structures and prototypes are in `ordered-data.h`.
- Final metadata insertion is performed by `btrfs_finish_ordered_io()` / `btrfs_finish_one_ordered()` declared here and implemented elsewhere.
- Integrates with delalloc-space metadata release, qgroup accounting, compressed I/O, direct I/O, fsync logging, writeback, transaction commit, and block-group relocation/waiting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ordered-data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ordered-data.h -->
# File Research: sources/os/linux/linux/fs/btrfs/ordered-data.h

This header defines Btrfs ordered extent data structures, flags, and public APIs.

Key structures:
- `struct btrfs_ordered_sum` stores a logical checksum range and flexible checksum array.
- `struct btrfs_file_extent` captures target file extent item details for write setup.
- `struct btrfs_ordered_extent` records a pending write range, corresponding disk extent fields, bytes left, truncation state, flags, compression type, qgroup reservation, refs, inode pointer, checksum/log/root lists, waitqueue, rbtree node, work items, completion, and bio-context list.

Flags:
- Status bits include `BTRFS_ORDERED_IO_DONE`, `BTRFS_ORDERED_COMPLETE`, `BTRFS_ORDERED_IOERR`, `BTRFS_ORDERED_TRUNCATED`, `BTRFS_ORDERED_LOGGED`, `BTRFS_ORDERED_LOGGED_CSUM`, and `BTRFS_ORDERED_PENDING`.
- Exclusive type bits are `BTRFS_ORDERED_REGULAR`, `BTRFS_ORDERED_NOCOW`, `BTRFS_ORDERED_PREALLOC`, and `BTRFS_ORDERED_COMPRESSED`.
- Extra modifiers are `BTRFS_ORDERED_ENCODED` and `BTRFS_ORDERED_DIRECT`.
- `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS` define valid creation masks.

Exported API groups:
- Completion/removal: `btrfs_finish_one_ordered()`, `btrfs_finish_ordered_io()`, `btrfs_finish_ordered_extent()`, `btrfs_mark_ordered_io_finished()`, `btrfs_dec_test_ordered_pending()`, `btrfs_remove_ordered_extent()`, and `btrfs_put_ordered_extent()`.
- Allocation/checksums: `btrfs_alloc_ordered_extent()` and `btrfs_add_ordered_sum()`.
- Lookup/logging: ordered extent lookup by offset/range/first range and `btrfs_get_ordered_extents_for_logging()`.
- Waiting/flushing: `btrfs_start_ordered_extent_nowriteback()`, inline `btrfs_start_ordered_extent()`, `btrfs_wait_ordered_range()`, `btrfs_wait_ordered_extents()`, and `btrfs_wait_ordered_roots()`.
- Range locking: `btrfs_lock_and_flush_ordered_range()` and `btrfs_try_lock_ordered_range()`.
- Split/error/lifecycle: `btrfs_split_ordered_extent()`, `btrfs_mark_ordered_extent_error()`, `ordered_data_init()`, and `ordered_data_exit()`.

Design notes:
- The header documents the semantic difference between data I/O done and ordered extent complete.
- Ordered extents act as the bridge between writeback/direct I/O completion and eventual file extent/checksum metadata insertion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ordered-data.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/orphan.c -->
# File Research: sources/os/linux/linux/fs/btrfs/orphan.c

This file implements simple Btrfs orphan item insertion and deletion helpers.

Core responsibilities:
- Insert a zero-sized orphan item at key `(BTRFS_ORPHAN_OBJECTID, BTRFS_ORPHAN_ITEM_KEY, offset)`.
- Delete the matching orphan item from a root.
- Return `-ENOENT` when deletion is requested for a missing orphan item.

Key mechanisms:
- Both helpers allocate a Btrfs path with `BTRFS_PATH_AUTO_FREE`.
- `btrfs_insert_orphan_item()` calls `btrfs_insert_empty_item()`.
- `btrfs_del_orphan_item()` searches with modification intent and deletes the found item with `btrfs_del_item()`.

Cross-file relationships:
- Public prototypes are in `orphan.h`.
- Used by inode/subvolume orphan cleanup paths to persist objects that need cleanup across crashes or transaction boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/orphan.h -->
# File Research: sources/os/linux/linux/fs/btrfs/orphan.h

This header declares the Btrfs orphan item API.

Exports:
- `btrfs_insert_orphan_item()` inserts an orphan item for a root and object offset in a transaction.
- `btrfs_del_orphan_item()` deletes the corresponding orphan item.

Design notes:
- The header forward declares transaction and root structures, keeping the orphan API small and independent from broader Btrfs internals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/orphan.h -->