# Group Research: group_1120_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_trace_h_sourc_27f22555fe67

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trace.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trace.h

## Purpose
Defines the XFS tracepoint catalog for Linux ftrace/perf. This header is instrumentation infrastructure, not ordinary runtime logic: it declares `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_DEFINE_ENUM` entries that become `trace_xfs_*` callsites when expanded through `<trace/define_trace.h>`.

The file explicitly warns that these tracepoints are not stable kernel ABI. It also documents unit naming conventions for AG numbers, inode numbers, fsblocks, realtime groups/extents, device blocks, file offsets, byte counts, directory/xattr blocks, sizes, owners, and extent counts.

## Major Trace Families
- Attribute listing and xattr state-machine traces: list cursors, node descent, shortform/leaf/node operations, remote-value allocation/removal, deferred attr state returns, and attr filter/op flag formatting.
- Filesystem, group, per-AG, realtime, and zoned realtime traces: mount/fs lifecycle events, per-AG/group reference accounting, inodegc/blockgc activity, realtime group/zone state, open-zone accounting, zone allocation, and zone GC target selection.
- Inode and VFS operation traces: iget cache paths, inode lifecycle/reclaim/inactivation, EOF/COW block tags, inode locks and references, namespace operations, rename, ioctl/fsync/readdir/getattr/setattr/readlink, page faults, timestamp range reporting, inode walks, and unlinked-list repair/reload activity.
- Buffer and buffer-log-item traces: buffer allocation/free/hold/release, locking, IO submission/completion, delwri queues, backing allocation choices, IO errors, transaction buffer reads/joins/logging/holds/invalidations, and buffer item formatting/pinning/unpinning/commit/push behavior.
- Transaction and log traces: reservation calculations, transaction allocation/cancel/commit/dup/free/roll/add-item/free-items, log grant queues and ticket regrant/ungrant operations, CIL waits, log force, AIL insert/move/delete/push states, iclog lifecycle, log tail assignment, and recovery record/item/buffer/inode/icreate handling.
- Allocation and free-space traces: AGF reads, AGFL reset, extent busy tracking and trimming, allocation algorithms, exact/near/size/small allocation paths, vextent allocation modes, per-AG reservations, metadata-file reservations, free-counter reservations, discard, realtime discard, and realtime busy allocation.
- Btree traces: cursor state, key updates, overlapped queries, block allocation/free, btree errors, fake-root commits, bulk-load geometry/block emission, and config-gated in-memory btree buffer/free-space events.
- Directory and da-tree traces: dir2 shortform/block/leaf/node operations, da split/join/link/unlink/root/node/grow/shrink/path-shift operations, and dir leaf-space movement.
- Quota traces: dquot lifecycle/cache/reclaim/flush/read, transaction quota deltas, and detailed `xfs_dqtrx` reservation/delta state for regular blocks, realtime blocks, and inodes.
- Deferred operation traces: defer finish/cancel/roll/error paths, pending intent lifecycle, pending item add/cancel/finish, extent-free intents, rmap intents, bmap intents, refcount intents, and exchange-map intents.
- Rmap/refcount/reflink traces: rmap map/unmap/convert/update/insert/delete and neighbor lookups, refcount lookup/insert/delete/update/adjustment/split/merge operations, shared extent searches, reflink remap/unshare/CoW/end-cow/cancel-cow paths, and swapext rmap activity.
- I/O and iomap traces: buffered/direct/DAX reads and writes, atomic-write CoW decisions, iomap allocation/found/invalid events, delalloc ENOSPC, unwritten conversion, file-size updates, zero EOF, direct-write completion, splice read, zoned block mapping, and writeback invalidation sequence checks.
- Fsmap/getfsmap traces: low/high keys, linear/group keys, reverse-map derived mappings, and emitted getfsmap records.
- Exchange-range and exchange-maps traces: preflight/flush/mapping phases, inode before/after states, freshness checks, reservation estimates, overhead estimates, exchanged mapping records, intent recovery, and extent-count delta calculation.
- Parent pointer, metadir, health, shutdown, media, and file-error traces: getparents records/cursors, metadata directory updates, health monitor queue/copy/read/report/format/drop/merge, shutdown flags, device/media verification, and file IO error reports.

## Integration
The header depends on Linux tracepoint infrastructure and XFS internal structures, but it mostly forward-declares types and extracts fields inside `TP_fast_assign`. It expects implementation files to include the relevant XFS definitions before using the generated tracepoints.

The closing include pattern is the standard kernel tracepoint expansion pattern:
- `TRACE_INCLUDE_PATH .`
- `TRACE_INCLUDE_FILE xfs_trace`
- `#include <trace/define_trace.h>`

## Conditional Coverage
Several trace families only exist for matching kernel build options:
- `CONFIG_XFS_RT` gates realtime, realtime discard/busy allocation, growfs realtime geometry, and zoned realtime traces.
- `CONFIG_XFS_POSIX_ACL` gates ACL inode events.
- `CONFIG_COMPAT` gates compat ioctl tracing.
- `CONFIG_XFS_DRAIN_INTENTS` gates group intent drain traces.
- `CONFIG_XFS_MEMORY_BUFS` gates memory-backed buffer target traces.
- `CONFIG_XFS_BTREE_IN_MEM` gates in-memory btree traces.

## Risk Notes
Trace format changes can break external debugging scripts even though the file declares the tracepoints non-ABI. Many tracepoints dereference deep internal structures, so callsites must pass live, initialized objects. Formatting also encodes subtle XFS distinctions such as AG vs realtime group addressing, segmented fsblocks, legacy realtime behavior, lazy superblock counters, CoW/refcount domains, and owner/offset semantics; incorrect use can make diagnostics misleading even if filesystem behavior is unchanged.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans.c

## Purpose
Implements the core XFS transaction lifecycle: reservation setup, transaction allocation/free, reservation accounting, superblock delta accounting, log item attachment, precommit processing, commit/cancel/roll behavior, and higher-level helpers for inode, inode-create, inode-change, and directory-update transactions.

## Main Entry Points
- `xfs_trans_init` computes mount transaction reservations with `xfs_trans_resv_calc` and traces them when tracepoints are enabled.
- `xfs_trans_alloc` allocates a transaction, starts internal write accounting, enters NOFS allocation context, reserves log/data/realtime resources, and retries initial ENOSPC once after speculative blockgc flushing.
- `xfs_trans_alloc_empty` creates a no-reservation transaction for metadata queries that need transaction buffer regrab behavior without dirtying anything.
- `xfs_trans_mod_sb` records transaction-local superblock deltas and marks the transaction dirty or superblock-dirty when needed.
- `xfs_trans_unreserve_and_mod_sb` returns unused block/realtime reservations and applies in-core superblock/per-cpu counter updates.
- `xfs_trans_add_item` and `xfs_trans_del_item` maintain the transaction log item list.
- `xfs_trans_commit` finishes deferred operations for permanent transactions and commits through `__xfs_trans_commit`.
- `xfs_trans_cancel` releases reservations and items, and forces shutdown if a dirty transaction is cancelled outside an existing shutdown.
- `xfs_trans_roll` duplicates a permanent transaction, commits the old one with log ticket regrant, and reestablishes the NOFS context for the new transaction.
- `xfs_trans_reserve_more` and `xfs_trans_reserve_more_inode` add incremental block/realtime/quota reservations to an existing transaction.
- `xfs_trans_alloc_inode`, `xfs_trans_alloc_icreate`, `xfs_trans_alloc_ichange`, and `xfs_trans_alloc_dir` compose allocation, locking, inode joining, quota attach/reserve, retry, and fallback behavior for common metadata operations.

## Transaction Allocation and Reservation
`__xfs_trans_alloc` allocates from `xfs_trans_cache`, starts `sb_start_intwrite` unless `XFS_TRANS_NO_WRITECOUNT` is set, saves a `memalloc_nofs` context, initializes item/busy/defer lists, records flags, and sets `t_highest_agno` to `NULLAGNUMBER`.

`xfs_trans_reserve` first reserves data blocks via `xfs_dec_fdblocks`, then reserves log ticket space through `xfs_log_reserve`, and finally reserves realtime extents via `xfs_dec_frextents`. Failures unwind in reverse order and return ENOSPC-style errors where appropriate. Permanent log reservations set `XFS_TRANS_PERM_LOG_RES`.

## Commit Path
`__xfs_trans_commit` applies superblock deltas and dquot deltas before precommit callbacks. Dirty log items are sorted by optional item-specific sort keys to reduce precommit lock-order deadlocks, then `iop_precommit` callbacks run. Precommit failure forces filesystem shutdown because dirty in-memory transaction state cannot be recovered safely.

Clean transactions are unreserved and freed without CIL submission. Dirty transactions check for log shutdown, submit to the CIL with `xlog_cil_commit`, free the transaction, and optionally force the committed sequence to disk for synchronous transactions.

## Cancel and Roll Path
`xfs_trans_cancel` treats attached deferred ops as dirty transaction state, cancels them, and forces shutdown if the mount is not already shutting down. It unreserves superblock and dquot accounting, ungrants log tickets, releases log items, marks aborted items when needed, clears NOFS context, ends write accounting, frees quota info, and returns the object to the transaction slab.

`xfs_trans_dup` creates the next transaction in a permanent reservation chain. It transfers the writer reference by marking the old transaction `XFS_TRANS_NO_WRITECOUNT`, shares the log ticket, moves remaining unused block/realtime reservations, moves deferred ops, and duplicates quota accounting. `xfs_trans_roll` commits the old transaction with regrant, restores NOFS context for the new one, and regrants the shared log ticket.

## Superblock Accounting
`xfs_trans_mod_sb` tracks deltas for inode counts, free inodes, free data blocks, reserved-on-disk block updates, free realtime extents, reserved realtime extent updates, data/realtime geometry, AG count, imax percentage, realtime extent size/log fields, realtime bitmap blocks, realtime extent count, and realtime group count.

`xfs_trans_apply_sb_deltas` logs the superblock buffer on commit. It handles lazy superblock counters, older non-rtgroup realtime frextent semantics, target device sector count updates, recomputation of realtime group block log after extent-size changes, and whole-superblock logging when modified fields are noncontiguous.

`xfs_trans_unreserve_and_mod_sb` returns unused reservations to free counters and updates in-core counters. It has special handling for lazy sbcount filesystems, rtgroups, reserved-on-disk deltas that were already applied in-core, and batched inode-count percpu updates.

## Higher-Level Helpers
The inode and directory helpers add policy around the core transaction API:
- Inode transactions lock and join the inode, attach dquots, reserve quota, and retry quota ENOSPC/EDQUOT after blockgc.
- Inode-create transactions can flush inodes once on filesystem ENOSPC and retry quota failures after freeing dquot-backed speculative space.
- Inode-change transactions reserve quota for ownership changes, including delayed allocation and realtime block accounting.
- Directory transactions can fall back to reservationless updates after ENOSPC and report the original space error through `nospace_error`.

## Risk Notes
This file is correctness-critical for journaling, metadata consistency, freeze/write accounting, quota reservations, ENOSPC retry behavior, and shutdown safety. Risky areas include transaction roll reservation transfer, dirty cancel handling, precommit callback ordering, lazy superblock counter interactions, realtime counter semantics, and quota retry paths that cancel transactions and drop locks before retrying.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans.h

## Purpose
Declares the kernel-only XFS transaction subsystem contract: shared transaction/log-item structures, log item operation callbacks, transaction flags/helpers, buffer and inode transaction APIs, transaction allocation helpers, AIL lifecycle hooks, and NOFS context helpers.

## Main Types
`struct xfs_log_item` is the common in-core object embedded by loggable metadata items. It tracks AIL linkage, transaction linkage, last on-disk LSN, log and AIL pointers, item type, atomic item flags, attached buffer, buffer-item list, item ops, CIL linkage, active/shadow log vectors, CIL sequence, and commit ordering id.

`struct xfs_item_ops` defines log item behavior: size calculation, formatting, pin/unpin, sort key generation, precommit, committing/committed callbacks, AIL push, release, match, and intent lookup. Its flags identify release-on-commit items, intent items, and intent-done items.

`struct xfs_trans` is the active transaction handle. It tracks log reservation/count/ticket, block and realtime extent reservations and usage, transaction flags, highest locked AGF, mount pointer, dquot accounting, superblock deltas, log item list, busy extent list, deferred operation list, and saved process allocation flags for NOFS restoration.

## Flags and Helpers
Log item flags include `IN_AIL`, `ABORTED`, `FAILED`, `DIRTY`, `WHITEOUT`, and `FLUSHING`. The comments note that bit operations are used because flag updates can race and should not require serializing everything through the AIL lock.

Important helpers include:
- `xlog_item_is_intent`
- `xlog_item_is_intent_done`
- `xfs_trans_set_sync`
- `xfs_trans_set_context`
- `xfs_trans_clear_context`

AIL push return codes distinguish success, pinned, locked, and flushing states.

## Exported Interfaces
The header exposes transaction allocation and reservation APIs:
- `xfs_trans_alloc`
- `xfs_trans_reserve_more`
- `xfs_trans_alloc_empty`
- `xfs_trans_mod_sb`

It exposes buffer transaction APIs:
- map-based and single-buffer get/read helpers
- superblock and realtime-superblock buffer acquisition
- buffer release/join/detach/hold/hold-release/invalidate
- inode/dquot/inode-allocation buffer marking
- ordered/dirty buffer handling
- buffer logging and buffer type set/copy helpers

It exposes inode and lifecycle APIs:
- `xfs_trans_ijoin`
- `xfs_trans_log_inode`
- `xfs_trans_commit`
- `xfs_trans_roll`
- `xfs_trans_roll_inode`
- `xfs_trans_cancel`
- `xfs_trans_ail_init`
- `xfs_trans_ail_destroy`

It also declares higher-level helpers for inode updates, incremental inode reservations, inode creation, inode ownership changes, and directory updates, plus the global `xfs_trans_cache` slab.

## Integration
This header is the shared transaction interface for XFS metadata code. Transaction core, log/CIL/AIL code, buffer items, inode items, quota code, deferred operations, btree users, and higher-level filesystem operations all depend on its structure layouts and callback semantics. The inline buffer helpers normalize single-buffer operations by creating a one-entry `xfs_buf_map` and routing through the map-based APIs.

## Risk Notes
`struct xfs_log_item` and `struct xfs_trans` are central cross-module structures. Field, flag, callback, or accounting changes can affect journaling, delayed logging, AIL tracking, CIL formatting, metadata lock ordering, quota behavior, and shutdown correctness. The NOFS context helpers are also important because transaction code often executes while holding filesystem locks and must avoid reclaim recursion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans.h -->