# Group Research: group_878_linux_sources_os_linux_linux_fs_xfs_xfs_trace_h_sources_os_linux_lin_d03b2b958634

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trace.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_trace.h

## Purpose

`xfs_trace.h` defines the Linux ftrace/tracepoint instrumentation surface for XFS. It is not a stable ABI; it is a developer and diagnostic interface for observing allocation, logging, transaction, inode, directory, attribute, reflink, realtime, health, media verification, and shutdown behavior inside the kernel XFS implementation.

The file is intentionally broad: it centralizes `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_DEFINE_ENUM` declarations so XFS subsystems can emit consistent structured events without each C file defining its own trace metadata.

## Main Contents

- Tracepoint include guard and `TRACE_SYSTEM xfs` setup, followed by forward declarations for XFS structs used by trace prototypes.
- Unit and naming conventions for trace fields, such as `agno`, `agino`, `agbno`, `rgbno`, `startblock`, `fileoff`, `daddr`, `bbcount`, `rtx`, `rtxcount`, `owner`, `pos`, and `bytecount`.
- Event classes and generated events for:
  - Attribute list iteration, attribute operations, delayed attribute state machines, and parent-pointer listing.
  - Allocation group and generic group reference tracking, including active/passive refs.
  - Realtime groups, zoned realtime allocation, open-zone accounting, and zone garbage collection when `CONFIG_XFS_RT` is enabled.
  - Inode garbage collection, block garbage collection, shrinker scans, inode cache walks, and speculative preallocation cleanup.
  - Buffer cache lifecycle, buffer IO errors, buffer log items, and transaction buffer joins/logging.
  - Inode locks, inode references, inode lifecycle, file operations, iomap mappings, writeback invalidation, and direct/buffered/DAX IO.
  - Directory, namespace, rename, dir2, xattr, and da-btree operations.
  - Quota objects, quota transaction deltas, and dquot reservation accounting.
  - Log grants, log tickets, CIL/AIL log item movement, iclog state transitions, log recovery records/items, log forcing, and shutdown.
  - Free-space allocation, AGF state, busy extents, discard, btree cursor operations, and fake-root btree rebuild state.
  - Deferred operation framework events and deferred extent-free, bmap, rmap, refcount, and exchange-mapping intents.
  - Reverse mapping, refcount btree, reflink, copy-on-write, unshare, and swapext/remap paths.
  - `fsmap`/`getfsmap` key and mapping iteration.
  - Transaction reservation calculation and transaction lifecycle events.
  - Unlinked inode bucket updates and unlinked-list reloads.
  - Health state transitions, health monitor ring-buffer operations, health event formatting, media/file IO error reporting, and media verification.
  - Optional in-memory buffer and in-memory btree events under `CONFIG_XFS_MEMORY_BUFS` and `CONFIG_XFS_BTREE_IN_MEM`.

## Important Design Points

- Most event families are implemented as event classes plus small `DEFINE_*_EVENT` macros. This keeps repeated tracepoint payloads consistent across many XFS operations.
- The tracepoints record stable diagnostic identifiers instead of raw internal pointers where possible: filesystem device, group type/index, inode number, fork, owner, file offset, physical block, extent length, reservation state, flags, and LSN fields.
- Many enums are wrapped in `TRACE_DEFINE_ENUM` so ftrace can decode symbolic names from ring-buffer values.
- Several trace classes are group-type aware. Newer XFS code can report both allocation groups and realtime groups through `enum xfs_group_type` and `XG_TYPE_STRINGS`.
- Log and transaction tracepoints align with `xfs_trans.c`, `xfs_log.c`, CIL, and AIL behavior: transaction allocation/commit/roll/free, reservation calculations, log grant waits, ticket regrant/ungrant, iclog state changes, and recovery replay.
- Health monitor tracepoints expose both internal queue behavior and formatted events for mount, filesystem, group, inode, media, file-range, shutdown, and lost-event domains.
- The file ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` inclusion, making this the header that instantiates tracepoint definitions when included from the corresponding trace compilation unit.

## Cross-File Relationships

- Transaction tracepoints are emitted from `xfs_trans.c` for allocation, duplicate, roll, commit, cancel, free, item add/free, and transaction reservation calculation.
- Buffer-related tracepoints are emitted by XFS buffer cache and buffer-log-item code.
- Log grant, iclog, AIL, and log recovery tracepoints are used by log manager, CIL, AIL, and recovery code.
- Rmap, refcount, bmap, extent-free, and exchange-map deferred-intent tracepoints mirror deferred operation item types implemented across XFS intent item files.
- Reflink and COW tracepoints are used by XFS reflink, iomap, and writeback paths.
- Health monitor and media verification tracepoints connect to XFS health reporting, forced shutdown, media-scrub, and file IO error reporting code.

## Risks / Review Notes

- This file is a diagnostic contract, not a user ABI, but tracepoint field names and formatting are still heavily relied on by debugging tools and developer workflows.
- Because many event classes dereference internal objects in `TP_fast_assign`, call sites must only trace while the referenced mount, inode, group, buffer, dquot, or cursor remains valid.
- Changes to enum values or flag sets should update both `TRACE_DEFINE_ENUM` declarations and `__print_symbolic` / `__print_flags` string tables, or trace output becomes harder to decode.
- Adding support for new XFS group/device domains must preserve formatting consistency for `agno`/`rgno`, `agbno`/`rgbno`, and generic `gbno` fields.
- The file is compiled through the kernel tracepoint machinery; syntax errors in one trace event can break XFS builds even if the tracepoint is rarely enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trans.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_trans.c

## Purpose

`xfs_trans.c` implements the core XFS transaction handle lifecycle: initialization of transaction reservations, allocation, reservation of log/space resources, superblock delta tracking, log item management, precommit processing, commit/cancel, transaction rolling, and helper allocators that combine transactions with inode locking and quota reservation.

It is the bridge between higher-level metadata mutations and the XFS log/CIL, quota, superblock counter, block reservation, and deferred-operation systems.

## Main Functions

- `xfs_trans_init()`: computes mount-specific transaction reservation values and emits reservation tracepoints when tracepoints are enabled.
- `xfs_trans_free()`: clears busy extents, emits free tracepoint, restores NOFS/writecount state, frees dquot accounting, and releases the transaction object.
- `xfs_trans_dup()`: creates the next transaction in a permanent-reservation chain, transferring remaining block/realtime reservations, sharing the log ticket, preserving selected flags, and moving deferred ops.
- `xfs_trans_reserve()`: reserves filesystem data blocks, log space, and realtime extents; unwinds earlier reservations on failure.
- `xfs_trans_alloc()` and `xfs_trans_alloc_empty()`: allocate transaction handles, apply freeze/writecount and NOFS context handling, reserve resources, and retry once after blockgc flush on ENOSPC.
- `xfs_trans_mod_sb()`: records superblock field deltas in the transaction and marks the transaction dirty and/or superblock-dirty as needed.
- `xfs_trans_apply_sb_deltas()`: joins the superblock buffer, applies logged on-disk deltas, and logs either contiguous counter fields or the whole superblock for noncontiguous changes.
- `xfs_trans_unreserve_and_mod_sb()`: releases unused reservations and applies transaction deltas to in-core counters and the in-core superblock.
- `xfs_trans_add_item()`, `xfs_trans_del_item()`, and `xfs_trans_free_items()`: manage transaction log item membership and release/abort cleanup.
- `xfs_trans_run_precommits()`: sorts log items to avoid lock-order inversions and runs dirty item precommit hooks.
- `__xfs_trans_commit()` and `xfs_trans_commit()`: apply superblock/quota deltas, finish deferred work for permanent transactions, run precommits, commit dirty transactions to the CIL, handle synchronous log forcing, or unreserve/free empty or failed transactions.
- `xfs_trans_cancel()`: aborts a transaction, cancels deferred ops, forces shutdown if dirty state cannot be safely rolled back, unreleases reservations, ungrants log tickets, aborts items, and frees the handle.
- `xfs_trans_roll()`: duplicates a permanent transaction, commits the current chunk with ticket regrant, restores NOFS context, and regrants log space for the next chunk.
- `xfs_trans_alloc_inode()`, `xfs_trans_reserve_more_inode()`, `xfs_trans_alloc_icreate()`, `xfs_trans_alloc_ichange()`, and `xfs_trans_alloc_dir()`: higher-level helpers that combine transaction allocation with inode locking, dquot attachment, quota reservation, retry after blockgc/quota cleanup, and directory update fallback behavior.

## Key Data Flow

1. A caller selects a precomputed `struct xfs_trans_res` and calls `xfs_trans_alloc()` or a helper such as `xfs_trans_alloc_inode()`.
2. `__xfs_trans_alloc()` allocates the transaction, takes write/freeze protection unless suppressed, saves the NOFS allocation context, initializes item/deferred/busy lists, and records the mount.
3. `xfs_trans_reserve()` deducts requested data blocks and realtime extents from global counters and obtains a log ticket through `xfs_log_reserve()`.
4. Metadata operations attach buffers, inodes, dquots, and deferred intents to the transaction. Superblock changes accumulate as deltas in `struct xfs_trans`.
5. Commit applies superblock and quota deltas, runs per-log-item precommit hooks, and either queues dirty items to the CIL via `xlog_cil_commit()` or unreserves resources for empty transactions.
6. Cancel releases reservations and log tickets; if dirty metadata cannot be backed out, it forces filesystem shutdown so dirty in-memory objects cannot later reach disk as valid metadata.
7. Permanent transactions can roll: remaining reservations and deferred operations move to a duplicate transaction while the old transaction commits and the shared ticket is regranted.

## Important Design Points

- Dirty transaction cancellation is treated as corruption risk. The code forces shutdown rather than attempting partial rollback of already-modified metadata.
- Lazy superblock counters affect whether changes are logged to the on-disk superblock. In-core counters still need updates even when on-disk counter logging is skipped.
- Realtime free-extent accounting has special handling: older non-rtgroup filesystems require `sb_frextents` to stay consistent on disk with the realtime bitmap, whereas rtgroups can treat it as a lazy counter.
- `XFS_TRANS_RES_FDBLKS` lets freed blocks replenish the transaction reservation before excess blocks return to the global pool, supporting chains of rolls that repeatedly free and allocate blocks.
- Precommit log items are sorted by `iop_sort` to reduce ABBA deadlocks when different transactions lock shared items such as inode cluster buffers.
- The transaction lifecycle is tightly coupled to `memalloc_nofs_save()` / `memalloc_nofs_restore()` so metadata operations do not recurse into filesystem reclaim unsafely.
- High-level inode/directory helpers retry quota or ENOSPC failures after blockgc cleanup, but only in bounded ways to avoid unbounded retry loops while locks may be involved.

## Cross-File Relationships

- Uses transaction types and exported prototypes from `xfs_trans.h`.
- Calls log manager APIs such as `xfs_log_reserve()`, `xfs_log_regrant()`, `xfs_log_ticket_regrant()`, `xfs_log_ticket_ungrant()`, `xfs_log_force_seq()`, and `xlog_cil_commit()`.
- Uses deferred operation APIs from `xfs_defer.h` to move, finish, and cancel deferred items.
- Uses quota APIs to attach dquots, reserve quota for block/inode/directory changes, apply deltas, and unreserve dquots.
- Uses superblock/mount helpers for lazy counters, realtime group behavior, realtime extent conversions, and in-core counter updates.
- Emits many tracepoints declared in `xfs_trace.h`, especially transaction, reservation, quota, and log item events.

## Risks / Review Notes

- Reservation unwind paths must keep global block, realtime extent, log ticket, and transaction counters synchronized; mistakes here cause leaks or false ENOSPC.
- Dirty-item precommit failures intentionally force shutdown. New `iop_precommit` implementations need strong guarantees because failure occurs after metadata has been modified.
- `xfs_trans_dup()` transfers remaining reservation capacity and marks the old transaction `XFS_TRANS_NO_WRITECOUNT`; changes to roll semantics must preserve writecount ownership.
- `xfs_trans_alloc_dir()` can downgrade to a reservationless directory update after ENOSPC/quota failure. Callers must honor the returned `dblocks` and `nospace_error`.
- Helpers that unlock or keep inode locks have precise contracts; changing cancel paths can easily introduce double unlocks or leaked locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trans.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_trans.h

## Purpose

`xfs_trans.h` is the public internal header for the XFS transaction subsystem. It defines log item state, log item operation callbacks, transaction state, transaction flags helpers, buffer/inode transaction APIs, commit/cancel/roll entry points, and convenience helpers for transaction NOFS context handling.

## Main Contents

- Forward declarations for log, buffer, mount, inode, dquot, btree, and intent item structures used by transaction APIs.
- `struct xfs_log_item`: the common embedded object for everything that participates in the log, AIL, CIL, and transaction item lists.
- Log item flag bit numbers and `XFS_LI_FLAGS` string table:
  - `XFS_LI_IN_AIL`
  - `XFS_LI_ABORTED`
  - `XFS_LI_FAILED`
  - `XFS_LI_DIRTY`
  - `XFS_LI_WHITEOUT`
  - `XFS_LI_FLUSHING`
- `struct xfs_item_ops`: polymorphic callbacks for sizing, formatting, pin/unpin, sort, precommit, committing/committed, push, release, match, and intent lookup behavior.
- Log item operation flags:
  - `XFS_ITEM_RELEASE_WHEN_COMMITTED`
  - `XFS_ITEM_INTENT`
  - `XFS_ITEM_INTENT_DONE`
- Inline helpers `xlog_item_is_intent()` and `xlog_item_is_intent_done()`.
- Return codes for `iop_push()` implementations: success, pinned, locked, and flushing.
- `struct xfs_trans`: active transaction state, including log reservation, block and realtime reservations, flags, highest AG locked, log ticket, mount pointer, dquot accounting, superblock deltas, item list, busy extent list, deferred operation list, and saved process allocation flags.
- Exported transaction functions for allocation, extra reservation, empty allocation, superblock modification, buffer get/read/join/log/release operations, inode logging/joining, commit, roll, cancel, AIL init/destroy, buffer type tagging, and specialized inode/quota/directory allocation helpers.
- `xfs_trans_set_context()` and `xfs_trans_clear_context()` wrappers around `memalloc_nofs_save()` / `memalloc_nofs_restore()`.

## Important Design Points

- `struct xfs_log_item` is the common abstraction used by buffers, inodes, dquots, and intent/done items to participate in the same transaction and log commit machinery.
- Log item flags use atomic bit operations because AIL/CIL/writeback paths can update item state without serializing all changes under the AIL lock.
- `struct xfs_item_ops` forms the transaction subsystem's object model. Each log item type supplies the callbacks needed to format itself into the log, participate in pinning, precommit ordering, AIL pushing, and release.
- `struct xfs_trans` stores both resource reservations and logical deltas. This lets transaction code reserve conservatively up front, then release unused space and apply exact counter changes at commit/cancel time.
- The header intentionally exposes many buffer transaction operations because most XFS metadata code manipulates buffers through transaction ownership rather than direct buffer lifecycle management.
- `xfs_trans_set_sync()` is a macro that marks a transaction for synchronous log forcing after commit.

## Cross-File Relationships

- Implemented primarily by `xfs_trans.c`, plus buffer transaction code, inode item code, dquot item code, AIL code, and intent item implementations.
- Trace formatting in `xfs_trace.h` uses `XFS_LI_FLAGS` and transaction fields such as `t_ticket`, `t_flags`, and log item fields.
- Log item callbacks are consumed by CIL, AIL, log recovery, item push, and transaction precommit code.
- Buffer APIs declared here are used broadly by allocation, btree, directory, attribute, quota, log recovery, and repair code.

## Risks / Review Notes

- Any field layout or semantic change to `struct xfs_trans` has wide impact across transaction allocation, commit, quota accounting, deferred ops, and tracepoints.
- New log item types must implement `xfs_item_ops` carefully; missing sort/precommit/release behavior can lead to deadlocks, leaked locks, or incorrect log replay.
- The transaction context helpers are part of filesystem reclaim safety. Callers that allocate or duplicate transactions must preserve NOFS save/restore pairing.
- The inline single-buffer map wrappers hide `xfs_buf_map` construction; callers still need to pass correct targets, disk addresses, lengths, flags, and verifier ops.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_trans.h -->