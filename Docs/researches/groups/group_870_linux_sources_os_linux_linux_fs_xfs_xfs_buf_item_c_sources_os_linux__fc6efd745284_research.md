# Group Research: group_870_linux_sources_os_linux_linux_fs_xfs_xfs_buf_item_c_sources_os_linux__fc6efd745284

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`. This grouped report covers the listed XFS buffer, quota, discard, directory, drain, error, in-memory buffer, hash-test, and exchange-mapping intent files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_item.c

Implements the in-core buffer log item lifecycle for XFS metadata buffers. It allocates and frees `struct xfs_buf_log_item`, tracks dirty bitmap ranges per buffer segment, formats dirty ranges into log vectors, pins/unpins buffers during log commit, pushes dirty buffers from the AIL, and releases or invalidates stale buffers.

Key behavior:
- `xfs_buf_item_init` attaches a log item to a buffer and creates one log-format bitmap per buffer map segment.
- `xfs_buf_item_log` marks byte ranges dirty in `XFS_BLF_CHUNK` units, handling discontiguous buffers segment by segment.
- `xfs_buf_item_size` and `xfs_buf_item_format` compute and emit log vectors, including stale/cancel and ordered-buffer special cases.
- Pin/unpin logic deliberately holds buffer and BLI references to avoid races with AIL I/O completion and shutdown abort paths.
- Stale buffers use `XFS_BLF_CANCEL`; stale inode buffers also trigger inode-specific I/O completion.
- `xfs_buf_item_done` removes a buffer log item from the AIL and releases it after writeback or recovery write completion.

This file is central to XFS physical metadata logging. Correctness depends on reference counts, buffer locks, AIL membership, and dirty bitmap consistency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_item.h

Declares the in-core XFS buffer log item API and state flags.

Key contents:
- `XFS_BLI_*` flags describe transaction-local and persistent BLI state: held, dirty, stale, logged, inode allocation buffer, stale inode, inode buffer, and ordered.
- `struct xfs_buf_log_item` embeds the common `xfs_log_item`, points at the real `xfs_buf`, stores flags, recursion/refcount state, and one or more `xfs_buf_log_format` records.
- Declares buffer log item lifecycle and logging functions: `xfs_buf_item_init`, `xfs_buf_item_done`, `xfs_buf_item_put`, `xfs_buf_item_log`, and `xfs_buf_item_dirty_format`.
- Declares I/O completion helpers for inode and dquot buffers.
- Exposes `xfs_buf_log_check_iovec` and `xfs_buf_inval_log_space` for recovery/log reservation validation.

This header is the contract between transaction code, buffer code, quota code, inode code, and log recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_item_recover.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_item_recover.c

Implements log recovery for physical buffer log items. It performs two-pass cancel handling, validates recovered buffer types, replays dirty buffer regions, handles special inode/dquot/superblock cases, and manages the recovery cancel table.

Key behavior:
- Maintains a 64-bucket `l_buf_cancel_table` of cancelled buffer ranges so old freed metadata is not replayed into reused blocks.
- Pass 1 validates buffer log format iovecs and records `XFS_BLF_CANCEL` entries.
- Pass 2 skips cancelled buffers, reads target buffers, compares on-disk metadata LSNs against the log transaction LSN, and replays only when needed.
- `xlog_recover_validate_buf_type` maps logged buffer type flags and magic numbers to correct buffer verifier ops for writeback.
- Regular buffer recovery copies logged chunks according to the dirty bitmap.
- Inode buffer recovery only replays `di_next_unlinked` fields, because inode core data is logged separately.
- Dquot buffer recovery skips quota types disabled by recovered QUOTAOFF items.
- Primary superblock recovery updates in-core superblock, device size, per-AG, and realtime group state after growfs replay.

This file is safety-critical for crash recovery because it prevents stale metadata replay and ensures recovered buffers carry correct verifier/LSN state before delayed writeback.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_item_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_mem.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_mem.c

Implements memory-backed XFS buffer targets used by online fsck and ephemeral ordered recordsets. Instead of a block device, the buffer target is backed by an unlinked shmem file.

Key behavior:
- `xmbuf_alloc` creates a private shmem file, configures a buftarg with no block device, sets PAGE_SIZE sector geometry, and initializes buffer target state.
- `xmbuf_free` destroys the buftarg and drops the shmem file reference.
- `xmbuf_map_backing_mem` maps exactly one PAGE_SIZE folio for a buffer, marks it dirty to keep it resident, and exposes the folio address through `bp->b_addr`.
- `xmbuf_verify_daddr` validates addresses against the shmem inode maximum size.
- `xmbuf_finalize` discards stale folios or runs buffer structure verification for non-stale buffers.
- `xmbuf_trans_bdetach` forcibly detaches memory-backed buffers from transactions after clearing dirty/logged/stale state, because direct-mapped memory buffers do not need ordinary writeback.

This file adapts the existing XFS buffer cache to in-memory, verifier-checked metadata structures without exposing the backing storage to userspace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_mem.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_buf_mem.h

Declares the memory-backed buffer target interface.

Key contents:
- Defines `XMBUF_BLOCKSIZE` and `XMBUF_BLOCKSHIFT` as PAGE_SIZE/PAGE_SHIFT.
- Under `CONFIG_XFS_MEMORY_BUFS`, `xfs_buftarg_is_mem` identifies buftargs with no block device.
- Declares allocation/free, address verification, transaction detach, finalize, and backing-memory mapping helpers.
- Without memory buffer support, most helpers collapse to simple false/no-op style macros, while `xmbuf_map_backing_mem` remains declared for shared build integration.

This header isolates conditional memory-buffer support from the rest of XFS buffer-cache code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_buf_mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dahash_test.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dahash_test.c

Provides an init-time regression test for XFS directory/attribute name hashing.

Key contents:
- A 4096-byte aligned pseudo-random test buffer.
- A table of 100 test cases, each with a start offset, length, expected normal directory/attribute hash, and expected ASCII case-insensitive hash.
- `xfs_dahash_test` iterates the test cases, computing `xfs_da_hashname` and `xfs_ascii_ci_hashname`, counting mismatches.
- On any mismatch, it prints a kernel error and returns `-ERANGE`; otherwise it returns success.

This file protects the on-disk hash algorithm from accidental changes, which matters because directory and attribute btree ordering depends on stable hash values.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dahash_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dahash_test.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dahash_test.h

Small header declaring `xfs_dahash_test`.

It exists so XFS initialization code can run the directory/attribute hash regression test without exposing the test data or implementation details.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dahash_test.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dir2_readdir.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dir2_readdir.c

Implements XFS directory iteration for shortform, block, leaf, and node directory formats.

Key behavior:
- `xfs_dir3_get_dtype` maps XFS on-disk file type values to VFS `DT_*`, returning `DT_UNKNOWN` when file type support is unavailable or invalid.
- Shortform readdir emits `.` and `..`, then local entries from the inode data fork, checking names for corruption.
- Block directory readdir reads the single directory data block, unlocks the inode while emitting entries, skips unused records, validates names, and advances `ctx->pos`.
- Leaf/node readdir scans mapped data blocks up to `XFS_DIR2_LEAF_OFFSET`, using extent lookup and a sliding readahead window to reduce I/O stalls.
- `xfs_readdir` dispatches based on directory format after shutdown/zapped-fork checks and records getdents statistics.

The code carefully manages inode data-map locks around buffer reads and user emission, and marks directory/attribute health sick on name-format corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dir2_readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_discard.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_discard.c

Implements XFS FITRIM/discard support for data and realtime devices.

Key behavior:
- Data-device trimming walks AG free-space btrees in bounded batches, marks selected free extents busy-under-discard while holding AGF protection, then issues discards asynchronously.
- `xfs_discard_extents` chains discard bios and clears busy extents from workqueue completion.
- The trim cursor can scan by block number for subrange trims or by extent length for whole-AG trims.
- Busy extents are skipped to avoid discarding blocks that might still be unsafe to reuse.
- Realtime support has two paths: classic realtime device extents use synchronous discard under rtbitmap locking, while rtgroups use the same busy-extent asynchronous machinery as AGs.
- `xfs_ioc_trim` validates privileges, discard capability, no-recovery state, userspace range, granularity, minlen, data/realtime address mapping, and copies the effective range back to userspace.

This file’s design avoids holding AGF locks across slow device discard operations, preventing log and transaction stalls during large fstrim runs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_discard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_discard.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_discard.h

Declares the XFS discard interface:
- `xfs_discard_extents` issues discard I/O for a prepared busy extent list.
- `xfs_ioc_trim` implements the FITRIM ioctl path.

The header forward-declares the userspace trim range, mount, and busy extent structures to keep dependencies light.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_discard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot.c

Implements in-core XFS dquot allocation, cache lookup, on-disk read/allocation, limit/timer adjustment, flush, buffer attachment, reference release, locking, and slab lifecycle.

Key behavior:
- Defines dquot lock ordering: inode lock, quota tree lock, dquot lock, flush completion, LRU lock; multiple dquots are ordered by ID.
- Applies default limits and grace periods, computes speculative preallocation thresholds, and manages soft/hard limit timers.
- `xfs_qm_init_dquot_blk` initializes a quota chunk on disk and logs or orders the buffer depending on quotacheck state.
- `xfs_dquot_disk_read` maps quota inode extents and reads the dquot buffer; `xfs_dquot_disk_alloc` allocates missing quota chunks transactionally.
- `xfs_qm_dqread`, `xfs_qm_dqget`, `xfs_qm_dqget_inode`, and `xfs_qm_dqget_next` implement uncached/cache-backed dquot retrieval.
- Cache insertion uses `memalloc_nofs_save` to avoid reclaim recursion while holding quota tree locks.
- `xfs_qm_dqflush` validates in-core quota state, copies it to disk, updates LSN/CRC, attaches the dquot log item to buffer I/O completion, and forces the log if the buffer is pinned.
- Buffer attachment helpers let transaction precommit retain a dquot buffer so AIL pushing can flush without allocating in reclaim context.

This file is the main quota metadata runtime implementation and coordinates tightly with dquot log items, AIL push, quota inode mapping, buffer verifiers, and filesystem health reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot.h

Defines XFS in-core dquot structures and public quota helper APIs.

Key contents:
- `struct xfs_dquot_res` tracks reserved count, actual count, hard/soft limits, and grace timer for blocks, inodes, and realtime blocks.
- `struct xfs_dquot_pre` stores speculative preallocation watermarks and low-space thresholds.
- `struct xfs_dquot` includes LRU/cache linkage, mount/type/id, location in quota inode and buffer, three resource counters, embedded log item, prealloc thresholds, mutex, flush completion, pin count, and waitqueue.
- Inline helpers manage flush locking, quota type extraction, quota-on/enforcement checks, inode-to-dquot lookup, over-limit checks, low-space checks, and reference holds.
- Declares dquot lookup, flush, destroy, timer/limit adjustment, buffer attachment, locking, and initialization routines.

This header is the primary type contract for quota accounting, transaction logging, reclaim, and ioctl-facing quota code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot_item.c

Implements transaction log item operations for dquots.

Key behavior:
- Formats a dquot log item as two vectors: `xfs_dq_logformat` plus an on-disk `xfs_disk_dquot` copy.
- Pins/unpins dquots with `q_pincount`, waking waiters when the count drops to zero.
- `xfs_qm_dqunpin_wait` forces the log and waits until a locked dquot is unpinned.
- AIL push tries to lock the dquot, acquire the flush completion, use an attached buffer, flush the dquot, and queue the buffer for delayed writeback.
- Precommit optionally verifies the on-disk-form dquot under expensive debug checks, then attaches a dquot buffer to avoid later reclaim-time allocation.
- Release unlocks the dquot because dquot locking is hidden inside transaction commit.

This file bridges in-memory quota modifications to the generic XFS log item and AIL infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot_item.h

Defines the in-core dquot log item.

Key contents:
- `struct xfs_dq_logitem` embeds a common `xfs_log_item`, points back to the owning `xfs_dquot`, records the LSN at the last flush, and uses a spinlock to protect the attached buffer pointer and `qli_dirty`.
- Declares `xfs_qm_dquot_logitem_init`.

The structure supports AIL push and flush completion coordination for quota metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot_item_recover.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_dquot_item_recover.c

Implements log recovery for dquot and quotaoff log items.

Key behavior:
- Dquot readahead skips recovery when quotas are off, the logged dquot payload is missing/too small, or a recovered QUOTAOFF disabled that quota type.
- Dquot pass 2 validates the logged disk dquot, reads the target quota buffer with dquot verifiers, compares on-disk dquot LSN against current recovery LSN for CRC filesystems, and copies/rechecks the recovered dquot.
- Recovered buffers are marked `_XBF_LOGRECOVERY` and queued for delayed writeback.
- QUOTAOFF pass 1 records disabled user/project/group quota types in `log->l_quotaoffs_flag`; dquot item and dquot-buffer recovery consult this state.

This file prevents replay of quota metadata after quotaoff and preserves newer on-disk quota records during recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_dquot_item_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_drain.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_drain.c

Implements the deferred-intent drain mechanism used to let online scrub/repair wait for active deferred metadata updates in an allocation group or realtime group.

Key behavior:
- Uses a static branch `xfs_defer_drain_waiter_gate` so release-side waiter checks are cheap when nobody can wait.
- `xfs_defer_drain_init/free` initialize and assert zero pending count.
- Internal grab/release helpers increment/decrement the atomic count and wake waiters when it reaches zero.
- `xfs_group_intent_get` obtains a group reference and declares an intent against that group.
- `xfs_group_intent_put` releases the intent and the group reference.
- `xfs_group_intent_drain` waits killably until no intents remain.
- `xfs_group_intent_busy` reports whether any intent is active.

The comments explain the core invariant: deferred work must hold intent counts across transaction rolls so scrub does not observe transient cross-structure inconsistency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_drain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_drain.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_drain.h

Declares the deferred intent drain interface and documents why it exists.

Key contents:
- Under `CONFIG_XFS_DRAIN_INTENTS`, `struct xfs_defer_drain` stores an atomic pending count and waitqueue.
- Declares drain initialization, cleanup, waiter gate toggles, group intent get/put, drain, and busy checks.
- The large design comment explains scrub/repair collision risks with deferred metadata intent chains across transaction rolls and why per-group intent counting prevents false corruption findings or unsafe repair.
- Without drain-intent support, the drain struct is empty and group intent operations fall back to ordinary group get/put.

This header is mostly a concurrency contract for deferred work, scrub, and realtime/AG group metadata updates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_drain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_error.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_error.c

Implements XFS error reporting, corruption reporting, verifier diagnostics, and debug-only error injection sysfs controls.

Key behavior:
- Under DEBUG, builds errortag default probability/delay tables and sysfs attributes from `xfs_errortag.h`.
- Supports setting errortags by numeric tag or name, copying tags between mounts, and clearing all tags.
- `xfs_errortag_test` randomly injects tagged errors based on configured frequency; `xfs_errortag_delay` injects millisecond delays.
- `xfs_error_report` logs internal errors and stack traces according to `xfs_error_level`.
- `xfs_corruption_error` can hex-dump corrupt buffers and instructs users to unmount and run repair.
- Buffer, generic verifier, and inode verifier reporting functions distinguish CRC from structural corruption, set buffer I/O error state where appropriate, dump initial corrupt bytes based on error level, and optionally stack trace.

This file centralizes XFS diagnostic policy and debug fault injection hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_error.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_error.h

Declares XFS error/corruption reporting APIs, debug errortag APIs, and panic tag constants.

Key contents:
- Reporting functions for generic internal errors, corruption errors, buffer corruption, buffer verifier errors, generic verifier errors, and inode verifier errors.
- Macros `XFS_ERROR_REPORT` and `XFS_CORRUPTION_ERROR` capture file, line, and return address.
- Defines error levels and corruption dump length.
- Under DEBUG, declares errortag init/test/delay/add/copy/clear helpers; non-debug builds provide inert or `-ENOSYS` stubs.
- Defines panic tag bits and string mappings for sysctl-controlled panic behavior.

This header is included widely by XFS metadata verification and recovery code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.c

Implements log intent/done items and recovery support for exchanging file mappings between two inode forks.

Key behavior:
- Defines XMI intent and XMD done slab caches and log item operations.
- XMI items carry inode numbers, generation numbers, start offsets, blockcount, sizes, and logged exchange flags.
- XMI reference counting handles both log/AIl lifecycle and XMD cancellation.
- XMD done items reference their XMI and are released when committed, dropping the matching intent.
- `xfs_exchmaps_defer_add` submits exchange work to the deferred operation framework.
- Deferred finish calls `xfs_exchmaps_finish_one`; `-EAGAIN` keeps the intent queued for later progress.
- Recovery validates feature support, padding, flags, inode numbers, and file extents; reopens both inodes by handle/generation; estimates resources; recreates incore intent state; and finishes/captures deferred work in recovery transactions.
- Relogging creates a fresh XMI from the old format to move the log tail forward.
- Log recovery pass 2 recreates XMI intent items from log records and releases them when matching XMD records are found.

This file is the transactional crash-recovery layer for multi-step file range exchange operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.h

Declares in-core XFS exchange-mapping intent and done log item structures.

Key contents:
- Documents that XMI records the first transaction of a rolled exchange operation and XMD records completion with the bmbt updates.
- `struct xfs_xmi_log_item` embeds a common log item, refcount, and on-disk XMI log format.
- `struct xfs_xmd_log_item` embeds a common log item, points to the associated XMI, and stores the XMD log format.
- Exposes XMI/XMD slab caches and `xfs_exchmaps_defer_add`.

This header is the public logging/defer interface for exchange-range mapping operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_exchmaps_item.h -->