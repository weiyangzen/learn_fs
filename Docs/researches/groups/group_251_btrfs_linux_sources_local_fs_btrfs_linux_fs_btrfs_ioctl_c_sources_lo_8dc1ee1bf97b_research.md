# Group Research: group_251_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_ioctl_c_sources_lo_8dc1ee1bf97b

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/btrfs-linux`. All requested files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.c

## Purpose

Implements the main Btrfs ioctl control plane plus file attribute integration and io_uring encoded I/O commands. This is the primary user-kernel interface for subvolume/snapshot operations, device management, balance/scrub/quota controls, tree and inode lookup queries, feature flags, labels, send/receive metadata, encoded reads/writes, sync controls, and forced shutdown.

## Main Responsibilities

- Maps VFS and Btrfs inode flags for `FS_IOC_GETFLAGS`/fileattr operations.
- Validates and applies mutable inode flags, including compression, no-COW, append, immutable, sync, noatime, and dirsynchronous flags.
- Handles subvolume and snapshot create/delete, readonly flag updates, default subvolume selection, root references, and subvolume sync wait operations.
- Provides tree search, inode-to-path, logical-to-inode, unprivileged inode lookup with permission checks, and subvolume metadata/rootref queries.
- Manages filesystem/device operations: resize, add/remove device, device replace, fs/device info, dev stats.
- Coordinates long-running exclusive operations: resize, device remove, balance, and device add interactions with paused balance.
- Runs defrag, trim, scrub, balance, quota/qgroup, quota rescan, and transaction sync ioctls.
- Supports send ioctl and receive metadata update through `SET_RECEIVED_SUBVOL`, including 32-bit compat layouts.
- Implements encoded read/write ioctl and io_uring command paths for encoded data streams.
- Dispatches all Btrfs-specific ioctl commands through `btrfs_ioctl()` and compat conversion through `btrfs_compat_ioctl()`.

## Key Behaviors and Invariants

- UAPI structs are copied with `memdup_user()`/`copy_from_user()` and string paths are NUL-checked before use.
- Most mutating operations require `CAP_SYS_ADMIN`, `mnt_want_write_file()`, and explicit readonly/root-state validation.
- Subvolume and snapshot creation reserve metadata and qgroup space before starting transactions; anon device ownership is carefully transferred to new roots.
- Snapshot creation forces future writes to COW and waits ordered extents before creating the snapshot.
- Subvolume deletion supports name-based and id-based v2 deletion; idmapped mount deletion by subvolid is deliberately restricted.
- Tree search copies results incrementally, pre-faults user buffers to avoid livelock, and preserves v1 overflow behavior.
- Balance, resize, remove, device replace, and device add rely on Btrfs exclusive-operation state to prevent conflicting long operations.
- Scrub copies progress back to userspace even on selected errors so userspace can resume.
- Received-subvolume UUID changes check UUID-tree overflow before transaction start to avoid user-triggered transaction aborts.
- Encoded I/O requires `CAP_SYS_ADMIN`; writes require `FMODE_WRITE` and reject invalid reserved fields, unsupported compression/encryption ids, and invalid unencoded ranges.
- io_uring encoded read may return to userspace with an inode lock held; lockdep handoff annotations are paired with task-work completion cleanup.

## Dependencies

Heavy dependencies include transaction handling, roots, qgroups, device management, block groups, scrub, send, compression, encoded I/O helpers, fsverity, locking helpers, and VFS permission/write-mount APIs.

## Research Notes

This file is a high-risk integration hub: correctness depends less on local algorithms and more on preserving ordering between permission checks, mount write acquisition, exclusive-operation state, transaction lifetime, root references, qgroup reservation, and userspace copy-back semantics.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.h

## Purpose

Declares the ioctl/fileattr interfaces exported from `ioctl.c` to the rest of Btrfs.

## Contents

- Main ioctl entry points: `btrfs_ioctl()` and `btrfs_compat_ioctl()`.
- File attribute handlers: `btrfs_fileattr_get()` and `btrfs_fileattr_set()`.
- Supported feature ioctl helper.
- Inode flag synchronization helper.
- Balance status argument updater.
- io_uring encoded command entry and encoded read endio callback.

## Dependencies

Uses forward declarations for VFS objects, Btrfs inode/fs structures, balance args, and `io_uring_cmd`, keeping this header lightweight.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/locking.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/locking.c

## Purpose

Implements Btrfs extent-buffer tree locking and the DREW lock used for A-B exclusion without excluding same-side readers/writers.

## Main Responsibilities

- Defines debug lockdep keysets per tree root objectid and B-tree level.
- Assigns extent-buffer lock classes to avoid false lockdep reports across roots and B-tree levels.
- Wraps extent-buffer read/write locking with tracing and optional debug owner tracking.
- Provides root-node lock acquisition loops that retry if the root node changes while acquiring the lock.
- Provides safe path unlock helpers.
- Implements `btrfs_drew_lock`, used where two operation classes must exclude each other but same-class operations may coexist.

## Key Behaviors and Invariants

- Lockdep classes assume `BTRFS_MAX_LEVEL == 8`; the file has a compile-time guard.
- Root-node lock helpers take a reference, lock, verify it is still the current root node, otherwise unlock/free/retry.
- DREW lock gives priority to readers: pending readers prevent new writers from settling.
- Atomic barriers around DREW counters ensure waiters observe state transitions before sleeping/waking.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/locking.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/locking.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/locking.h

## Purpose

Declares Btrfs tree-locking APIs, lockdep annotation helpers, lock nesting classes, and the DREW lock structure.

## Main Contents

- `BTRFS_WRITE_LOCK` and `BTRFS_READ_LOCK` path lock constants.
- `enum btrfs_lock_nesting` with subclasses for normal, COW, left/right siblings, split, and new-root locking.
- Lockdep wait-event annotation macros for transaction state, ordered extents, pending ordered extents, and io_uring inode-lock handoff.
- Tree lock/read lock prototypes and inline normal-nesting wrappers.
- Debug assertions for read/write-held extent buffer locks.
- DREW lock structure and operations.

## Key Invariants

- `BTRFS_NESTING_MAX <= MAX_LOCKDEP_SUBCLASSES` is statically asserted.
- io_uring encoded I/O explicitly models returning to userspace while inode locks are later released in task work.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/locking.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.c

## Purpose

Implements a small generic Btrfs LRU cache built on a maple tree from key to collision/generation lists plus a global LRU list.

## Main Responsibilities

- Initializes cache state and maximum size.
- Looks up entries by `u64 key` and generation, moving hits to the LRU tail.
- Stores entries, handling maple-tree insertion, same-key generation lists, duplicate detection, and max-size eviction.
- Removes entries, including cleanup of now-empty per-key list heads.
- Clears all entries.

## Key Behaviors and Invariants

- Entries are freed by the cache on removal, so callers must allocate them compatibly with `kfree()`.
- `max_size == 0` means unlimited; caller is then responsible for trimming.
- Same key with different generation is represented by a linked list, mainly for 32-bit maple-tree key truncation and low-collision use cases.
- Eviction removes the least-recently-used entry before adding the new one when the cache is full.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.h

## Purpose

Defines the generic LRU cache structures and API.

## Main Contents

- `struct btrfs_lru_cache_entry`, intended to be embedded as the first member of caller-owned structures.
- `struct btrfs_lru_cache`, containing the LRU list, maple tree, current size, and max size.
- Safe reverse iteration macro and helper for current LRU entry.
- Init, lookup, store, remove, and clear prototypes.

## Key Contract

The entry must be first in its containing allocation and allocated with `kmalloc()` semantics because cache removal calls `kfree()` on the entry pointer.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/lzo.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/lzo.c

## Purpose

Implements Btrfs LZO compression and decompression for regular compressed bios and inline extents.

## Format

Btrfs LZO data starts with a 4-byte little-endian total compressed length. It then contains one or more segments. Each segment has a 4-byte little-endian segment payload length followed by compressed payload. Segment headers never cross sector boundaries, so padding zeros may appear near sector ends. Inline extents allow only one segment.

## Main Responsibilities

- Allocates/frees LZO workspaces: compression memory, decompression buffer, and compressed temporary buffer.
- Compresses filemap data sector-by-sector into compressed folios and queues them into a bio.
- Writes the top-level LZO length after compression completes.
- Rejects compression when output grows too large.
- Decompresses compressed bios by validating top-level length, reading segment headers/payloads across folios, and copying decompressed data to target pages.
- Decompresses inline LZO data into a destination folio.
- Exports Btrfs LZO compression level metadata.

## Key Behaviors and Invariants

- One segment represents at most one sector of uncompressed data.
- Segment headers must fit within a sector; compression pads when fewer than 4 bytes remain.
- Folio ownership transfers to the bio once queued; error cleanup only frees unqueued folios.
- Decompression validates total length against compressed bio size and max compressed extent size, returning corruption or I/O errors for invalid headers/segments.
- Inline decompression expects exact nested length headers and zero-fills short output before returning error.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/lzo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/messages.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/messages.c

## Purpose

Implements Btrfs logging, error decoding, filesystem error handling, 32-bit address-limit warnings, and fatal panic behavior.

## Main Responsibilities

- Converts fs state bits into compact printable state suffixes.
- Decodes common negative errno values into human-readable strings.
- Handles filesystem errors by recording `fs_error`, stopping discard, marking the superblock readonly, and logging critical context.
- Provides ratelimited per-level `_btrfs_printk()` with device id and state annotations.
- Emits one-time warnings/errors for 32-bit logical address limits.
- Implements `__btrfs_panic()`, honoring the panic-on-fatal-error mount option or falling through for caller `BUG()`.

## Key Behaviors

- `-EROFS` on an already readonly superblock is treated as safe and not escalated.
- Full forced-readonly handling is skipped before `SB_BORN`, avoiding mount-time overreaction.
- Ratelimiting is per log level to prevent low-priority floods from suppressing critical messages.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/messages.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/messages.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/messages.h

## Purpose

Defines Btrfs logging macros, assertion behavior, error-handling wrappers, panic wrappers, and 32-bit limit declarations.

## Main Contents

- Severity macros: `btrfs_crit`, `btrfs_err`, `btrfs_warn`, `btrfs_info`, plus ratelimited variants.
- Dynamic-debug aware `btrfs_debug` macros.
- RCU-wrapped printk helpers.
- `ASSERT()` implementation under `CONFIG_BTRFS_ASSERT`, including optional format strings.
- `DEBUG_WARN()` under `CONFIG_BTRFS_DEBUG`.
- `btrfs_handle_fs_error()` and `btrfs_panic()` wrappers that capture function and line.
- 32-bit page-cache logical address limit constants and declarations.

## Key Contract

`btrfs_panic()` calls `__btrfs_panic()` and then `BUG()` unless the helper panics first due to mount options.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/messages.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/misc.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/misc.h

## Purpose

Collects small generic helpers used across Btrfs.

## Main Contents

- Cleanup-attribute pointer macros: `AUTO_KFREE` and `AUTO_KVFREE`.
- `ENUM_BIT()` helper for enum-backed bit definitions.
- Bio physical address and block-iteration helpers that support large folios/highmem.
- Bio total-size and full-bio iterator initialization helpers.
- Conditional waitqueue wakeups with and without implied memory barriers.
- Numeric helpers: percentage multiplication and 64-bit power-of-two test.
- Simple bytenr-indexed rb-tree node/search/insert helpers.
- Bitmap range-all-set and range-all-zero tests.

## Key Behaviors

- `cond_wake_up()` relies on `wq_has_sleeper()` barrier semantics.
- `cond_wake_up_nomb()` is only for callers whose preceding operations already imply the necessary barrier.
- `rb_simple_node` must be the prefix of any structure using the simple rb-tree helpers.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.c

## Purpose

Implements ordered extent tracking: the bridge between submitted file data I/O and later metadata insertion/accounting completion. Ordered extents record pending writes by inode range, disk extent, qgroup reservation, checksum list, completion state, and root-level pending ordered lists.

## Main Responsibilities

- Allocates ordered extent objects from a slab cache.
- Inserts non-overlapping ordered extents into per-inode rb-trees and per-root ordered lists.
- Tracks ordered bytes globally and outstanding extents per inode.
- Stores checksum lists for later metadata insertion.
- Marks ordered I/O progress, handles errors, and queues finish work when all bytes complete.
- Removes completed ordered extents from inode/root tracking and wakes transaction/order waiters.
- Starts and waits ordered extents by root, filesystem, block group, or inode range.
- Looks up ordered extents by exact offset, first-before/near offset, or overlapping range.
- Provides ordered extent lists for logging/fsync.
- Locks and flushes ranges until no ordered extents overlap.
- Splits non-compressed ordered extents, moving checksum records and adjusting disk/file ranges.
- Initializes/destroys the ordered extent slab cache.

## Key Behaviors and Invariants

- Ordered extents in an inode rb-tree must not overlap; insertion panics on overlap.
- Exactly one exclusive type flag must be set: regular, nocow, prealloc, or compressed.
- Encoded extents must also be compressed; direct I/O cannot be compressed or encoded.
- NOCOW/PREALLOC qgroup reservations are freed immediately; COW reservations transfer to the ordered extent until completion.
- `bytes_left` is the gate for setting `BTRFS_ORDERED_IO_DONE`; completion work is queued once.
- Write errors set `BTRFS_ORDERED_IOERR` and propagate mapping error; COW write errors also mark the inode to force future fast fsync to wait for ordered completion.
- Removal clears rb-tree state, root list membership, ordered counters, metadata reservations, pending transaction ordered counts, and wakes waiters.
- Waiting roots splices lists under locks, queues flush work, and restores skipped/spliced list entries.
- `btrfs_lock_and_flush_ordered_range()` repeatedly locks the extent range, checks for overlap, unlocks and waits if needed, and returns with the range locked and no overlapping ordered extent.
- Splitting refuses compressed, errored, zero-length, partially inconsistent, or disk/file length-mismatched ordered extents.

## Dependencies

Uses transaction lockdep annotations, inode/root ordered locks, qgroup accounting, delalloc metadata reservation, extent locking, workqueues, page writeback, block-group range filtering, tracing, and delayed iput.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.h

## Purpose

Defines ordered extent data structures, flags, and APIs.

## Main Contents

- `struct btrfs_ordered_sum` for queued checksum ranges.
- Ordered extent status flags: I/O done, complete, error, truncated, logged, logged csum, pending.
- Ordered extent type flags: regular, nocow, prealloc, compressed, encoded, direct.
- `BTRFS_ORDERED_EXCLUSIVE_FLAGS` and `BTRFS_ORDERED_TYPE_FLAGS` masks.
- `struct btrfs_ordered_extent`, containing file extent fields, state flags, qgroup reservation, refs, inode pointer, checksum/log/root/work lists, rb node, waits, and completion.
- `struct btrfs_file_extent`, mirroring file extent item details needed to allocate ordered extents.
- APIs for allocation, reference release, removal, finish/mark completion, lookup, wait, range lock/flush, splitting, error marking, and slab init/exit.

## Key Contract

The flags encode both lifecycle state and extent type. Callers creating ordered extents must pass exactly one exclusive type and respect direct/encoded/compressed compatibility rules enforced in `ordered-data.c`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ordered-data.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/orphan.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/orphan.c

## Purpose

Provides minimal helpers for inserting and deleting orphan items in a Btrfs root.

## Main Responsibilities

- `btrfs_insert_orphan_item()` inserts an empty item with key `(BTRFS_ORPHAN_OBJECTID, BTRFS_ORPHAN_ITEM_KEY, offset)`.
- `btrfs_del_orphan_item()` searches for the same key and deletes it.

## Key Behaviors

- Both functions allocate a Btrfs path with automatic cleanup.
- Delete returns `-ENOENT` if the orphan item is not found.
- Insert delegates duplicate/error behavior to `btrfs_insert_empty_item()`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/orphan.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/orphan.h

## Purpose

Declares orphan item insertion and deletion helpers.

## Contents

- Forward declarations for transaction handles and roots.
- Prototypes for `btrfs_insert_orphan_item()` and `btrfs_del_orphan_item()`.

## Role

This is the small public interface for root orphan-item maintenance used by transaction-aware callers.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/orphan.h -->