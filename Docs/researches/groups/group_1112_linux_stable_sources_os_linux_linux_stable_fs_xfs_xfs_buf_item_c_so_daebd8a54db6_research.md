# Group Research: group_1112_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_buf_item_c_so_daebd8a54db6

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.c

## Purpose
Implements the in-core XFS buffer log item (`xfs_buf_log_item`) lifecycle: allocation, dirty-range bitmap tracking, log vector sizing/formatting, pin/unpin behavior, AIL push, transaction release, and stale/cancel cleanup.

## Main APIs
- `xfs_buf_item_init` attaches a new buffer log item to an `xfs_buf`, allocating one log-format header per buffer map segment.
- `xfs_buf_item_log` marks byte ranges dirty in per-segment bitmaps, using `XFS_BLF_CHUNK` granularity.
- `xfs_buf_item_dirty_format` checks whether any segment bitmap contains logged ranges.
- `xfs_buf_item_put` drops a BLI reference and frees clean non-AIL items.
- `xfs_buf_item_done` removes the buffer log item from the AIL and releases it.
- `xfs_buf_inval_log_space` computes worst-case log format overhead for invalidated/stale buffers.
- `xfs_buf_log_check_iovec` validates recovered buffer log format vector bounds.

## Key Behavior
Buffer log vectors consist of one format record plus one data vector for each contiguous dirty bitmap run. Discontiguous buffers are represented as separate format records, making recovery see them like multiple ordinary buffers. Ordered buffers consume no data vectors; stale buffers log only cancel-format records.

Pinning takes both a BLI ref and a buffer ref so unpin completion cannot race with buffer freeing. Stale completion handles attached inode/dquot completion state, removes AIL state, releases log items, and unlocks/releases the buffer from the final owner path.

## Recovery and Correctness Interactions
The code sets `XFS_BLF_INODE_BUF` at format time for inode buffers, with special handling for newly allocated inode buffers so recovery can distinguish full inode initialization from later unlinked-list-only replay. `xfs_buf_item_committed` preserves the original LSN for newly allocated inode buffers until original inode images are flushed.

## Dependencies
Uses `xfs_bit` bitmap helpers, transaction/log item infrastructure, AIL helpers, buffer cache primitives, quota/dquot and inode buffer completion hooks, tracepoints, and metadata verifiers under `DEBUG_EXPENSIVE`.

## Failure Handling
Oversized dirty bitmap requirements cause `-EFSCORRUPTED` at init. Shutdown/abort paths carefully avoid stale BLI double-free and simulate failed async I/O when an unpin removes an item.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.h

## Purpose
Declares the in-core buffer log item structure, buffer log item flags, and public helpers used by XFS transaction, buffer, quota, inode, and recovery code.

## Main Types and Flags
`struct xfs_buf_log_item` embeds the common `xfs_log_item`, points to the backing `xfs_buf`, tracks BLI flags, recursion/reference counts, and stores one or more `xfs_buf_log_format` records. A single embedded format is used for common one-map buffers; multi-map buffers use a dynamically allocated array.

Flags record hold/dirty/stale/logged state plus inode allocation, stale inode, inode buffer, and ordered-buffer semantics.

## Public API
Declares initialization, completion, reference release, dirty range logging, dirty-format testing, inode/dquot/buffer I/O completion hooks, log iovec validation, and invalidation log-space estimation.

## Dependencies and Configuration
`xfs_buf_dquot_iodone` is compiled as a no-op without `CONFIG_XFS_QUOTA`. The header is kernel-only and depends on log-format and buffer definitions supplied by including translation units.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item_recover.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item_recover.c

## Purpose
Implements recovery for logged buffer items, including cancellation tracking, replay ordering, type validation, LSN-based replay skipping, inode-buffer special replay, dquot-buffer handling, and primary superblock grow recovery.

## Main APIs
- `xlog_buf_item_ops` wires buffer item reorder, readahead, pass1, and pass2 recovery callbacks.
- `xlog_alloc_buf_cancel_table`, `xlog_free_buf_cancel_table`, and debug `xlog_check_buf_cancel_table` manage the cancellation hash table.
- `xlog_is_buffer_cancelled` exposes cancel-table lookup.

## Key Behavior
Recovery pass 1 records `XFS_BLF_CANCEL` buffer items by block/length with a refcount so pass 2 can suppress replay until the final cancel record is consumed. Reordering sends normal buffers first, inode buffers later, and cancel records last.

Pass 2 skips canceled buffers, reads the target block, compares on-disk metadata LSNs for CRC filesystems, and replays only when the log item is newer or the current block cannot be trusted. Skipped buffers still get verifier ops attached and read-verified when possible.

## Specialized Replay
Regular buffer replay copies logged chunk vectors into the destination buffer according to the dirty bitmap. Dquot buffers are suppressed if quotaoff was logged for that quota type. Inode buffers replay only `di_next_unlinked` fields unless they are full newly allocated inode buffers. Primary superblock replay updates in-core superblock, data/realtime buftarg sizes, last AG/rtgroup sizing, perag/rtgroup initialization, and allocator set-aside state.

## Metadata Validation
`xlog_recover_validate_buf_type` maps log buffer type flags and on-disk magic values to the correct buffer verifier ops. `xlog_recover_get_buf_lsn` extracts LSN/UUID pairs from many metadata formats and forces replay for unrecognized, stale, inode, dquot, or non-CRC cases.

## Failure Handling
Malformed vectors, bad dquot records, impossible grow/shrink state, verifier failures, and corrupted inode-buffer unlinked fields return corruption errors. Recovery queues dirty buffers for delayed write with `_XBF_LOGRECOVERY`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_item_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.c

## Purpose
Provides a shmem-backed XFS buffer target for in-memory files, mainly for online fsck staging structures that want to reuse buffer-cache and btree infrastructure without a block device.

## Main APIs
- `xmbuf_alloc` creates an unlinked kernel shmem file, configures an `xfs_buftarg`, and sets memory-buffer sector geometry.
- `xmbuf_free` destroys the buftarg and drops the shmem file.
- `xmbuf_map_backing_mem` maps exactly one page-sized buffer to a shmem folio.
- `xmbuf_verify_daddr` checks that an address is within the shmem maximum file size.
- `xmbuf_finalize` discards stale folios or runs the buffer structural verifier.
- `xmbuf_trans_bdetach` forcibly detaches a memory buffer from a transaction without writeback.

## Key Behavior
The only supported block size is `PAGE_SIZE`; buffers must have one map, page-aligned positions, and no highmem folios. Folios are marked dirty to prevent reclaim after the buffer drops its reference. Stale buffers call `shmem_truncate_range` to discard backing memory.

## Dependencies and Invariants
Uses tmpfs/shmem, page cache folios, XFS buftarg initialization/destruction, buffer log item flags, and verifier error reporting. Caller is responsible for concurrency; VFS freezer/inode locking is intentionally not used.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.h

## Purpose
Declares constants and helpers for XFS memory-backed buffer targets.

## Main Contents
Defines `XMBUF_BLOCKSIZE` and `XMBUF_BLOCKSHIFT` as page-size/page-shift. Under `CONFIG_XFS_MEMORY_BUFS`, `xfs_buftarg_is_mem` identifies memory targets by `bt_bdev == NULL` and declares allocation, free, address verification, transaction detach, and finalize helpers.

## Configuration Behavior
Without `CONFIG_XFS_MEMORY_BUFS`, memory-buffer detection and address verification are compile-time false. `xmbuf_map_backing_mem` remains declared outside the feature guard for buffer-cache integration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_buf_mem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dahash_test.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dahash_test.c

## Purpose
Provides an init-time deterministic regression test for XFS directory/attribute name hash functions.

## Main Data
Contains a 4096-byte aligned random test buffer and 100 test cases. Each test specifies a start offset, length, expected `xfs_da_hashname` result, and expected ASCII case-insensitive hash result.

## Main API
`xfs_dahash_test` iterates all test cases, computes the normal DA hash and `xfs_ascii_ci_hashname`, counts mismatches, prints a kernel error if any mismatch occurs, and returns `-ERANGE` on failure or zero on success.

## Dependencies
Uses directory/attribute hash APIs from XFS dir2/DA code and is marked `__init`/`__initdata`, so the data and function are init-only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dahash_test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dahash_test.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dahash_test.h

## Purpose
Tiny header declaring the init-time directory/attribute hash self-test entry point.

## API
Declares `int xfs_dahash_test(void);`.

## Dependencies
No conditional compilation or extra types are introduced here; including code must provide normal XFS/kernel context.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dahash_test.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dir2_readdir.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dir2_readdir.c

## Purpose
Implements XFS `readdir` support for shortform, block, leaf, and node directory formats, translating XFS directory entries into VFS `dir_context` emissions.

## Main APIs
- `xfs_dir3_get_dtype` maps XFS filetype values to VFS `DT_*`, returning `DT_UNKNOWN` when unsupported or invalid.
- `xfs_readdir` is the public entry point; it validates shutdown/zapped state, builds DA args, chooses the directory format, and dispatches to format-specific walkers.

## Format Walkers
Shortform readdir emits `.` and `..`, then walks local entries in the inode fork. Block readdir reads the single block directory, drops the inode data-map lock while emitting, skips unused regions, checks names, and emits entries. Leaf/node readdir scans mapped data blocks below `XFS_DIR2_LEAF_OFFSET`, uses a sliding readahead window, and handles sparse mappings.

## Cookies and Locking
Directory positions use XFS dataptrs masked to 31 bits for VFS cookies. Leaf/node walking reacquires the data-map lock only to read mappings and releases it before processing buffers. Optional transactions collect buffer releases without dirtying metadata.

## Corruption Handling
All walkers validate names with `xfs_dir2_namecheck`; invalid names mark the directory data fork sick and return `-EFSCORRUPTED`. Shutdown or zapped forks return `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dir2_readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_discard.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_discard.c

## Purpose
Implements online discard and FITRIM support for XFS data and realtime devices, using busy extent records to prevent allocation while discard I/O is in flight.

## Main APIs
- `xfs_discard_extents` issues discard bios for a list of busy extents and clears them asynchronously on completion.
- `xfs_ioc_trim` handles the user-facing FITRIM ioctl range validation and dispatches trimming for data and realtime devices.

## Data Device Trim
The data-device path repeatedly locks AGF state, searches free-space btrees in bounded batches, marks eligible free extents busy-under-discard, drops AGF locks, and issues discard asynchronously. Cursor state supports by-length scans for full AGs and by-block-number scans for partial ranges.

## Realtime Trim
With `CONFIG_XFS_RT`, realtime trimming supports both legacy non-rtgroup and rtgroup modes. Legacy realtime device discard uses synchronous `submit_bio_wait` because it does not use the normal busy extent machinery. Rtgroup mode queues busy extents and reuses `xfs_discard_extents` for async completion.

## FITRIM Semantics
`xfs_ioc_trim` requires `CAP_SYS_ADMIN`, discard-capable data or realtime devices, and no norecovery mount. User byte ranges are converted to daddrs; the realtime device appears after the data device in FITRIM address space. `minlen` is raised to device discard granularity.

## Failure and Stop Conditions
Loops stop for fatal signals or freezing. Corrupt btree records mark the btree sick and return corruption errors. Per-AG/rtgroup errors are remembered and the last error is returned after attempting remaining ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_discard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_discard.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_discard.h

## Purpose
Declares XFS discard/FITRIM entry points.

## API
- `xfs_discard_extents` issues discard I/O for busy extents.
- `xfs_ioc_trim` implements the FITRIM ioctl for an XFS mount and user `fstrim_range`.

## Dependencies
Forward-declares `fstrim_range`, `xfs_mount`, and `xfs_busy_extents`; implementation details live in `xfs_discard.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_discard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.c

## Purpose
Implements core XFS dquot management: in-core allocation/destruction, on-disk allocation/read, cache lookup/insert, quota defaults/timers, dquot flushing, attached buffer handling, locking helpers, and slab cache setup.

## Main APIs
- `xfs_qm_dqget`, `xfs_qm_dqget_inode`, `xfs_qm_dqget_uncached`, and `xfs_qm_dqget_next` load dquots from cache or disk.
- `xfs_qm_dqrele` releases references and adds unused dquots to the quota LRU.
- `xfs_qm_init_dquot_blk` initializes an on-disk block of dquots.
- `xfs_qm_dqflush` writes an in-core dquot to its backing buffer and wires I/O completion to AIL cleanup.
- `xfs_dquot_attach_buf`, `xfs_dquot_use_attached_buf`, and `xfs_dquot_detach_buf` manage reclaim-safe buffer references for dirty dquots.
- `xfs_dqlock2` and `xfs_dqlockn` provide deadlock-safe multi-dquot locking.
- `xfs_qm_init` and `xfs_qm_exit` create/destroy dquot and transaction-accounting slabs.

## On-Disk Handling
Dquot reads map quota inode file offsets to disk, read dquot chunks with verifiers, and copy one `xfs_disk_dquot` into in-core counters. Holes can be allocated with a quota allocation transaction, initialized as a full dquot chunk, held through commit, and returned locked.

## Limits and Timers
Default limits are applied when non-root dquots have zero limits. Timers start when usage exceeds soft or hard limits and reset when usage returns below limits. Grace periods are clamped. Preallocation watermarks are derived from soft/hard block and realtime-block limits.

## Cache and Locking
Cache lookup uses per-quota-type radix trees and `lockref_get_not_dead` to avoid resurrecting freeing dquots. Insert runs under `memalloc_nofs` to avoid reclaim recursion through quota tree locks. Lock ordering is documented: inode lock, quota tree lock, dquot lock, flush lock, LRU lock; multiple dquots lock by type/id order.

## Flush and AIL Coordination
Flush checks in-core consistency, copies fields to the disk dquot, writes CRC/LSN for CRC filesystems, attaches the log item to the buffer I/O list, and forces the log if the buffer is pinned. I/O completion removes unchanged dquots from the AIL and releases attached buffers/flush locks.

## Failure Handling
Quota metadata verifier errors mark the corresponding quota health flag sick. Flush corruption forces shutdown before deleting the AIL item to avoid unrecoverable log-tail advancement.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.h

## Purpose
Defines the in-core dquot data model, quota resource accounting structures, flush synchronization helpers, inline quota-state helpers, and dquot management APIs.

## Main Types
- `struct xfs_dquot_res` tracks reserved count, actual count, hard/soft limits, and timer/grace state for blocks, inodes, or realtime blocks.
- `struct xfs_dquot_pre` stores speculative preallocation watermarks and low-space thresholds.
- `struct xfs_dquot` stores identity, cache reference state, disk buffer location, block/inode/realtime resource counters, embedded dquot log item, preallocation thresholds, dquot lock, flush completion, pin count, and pin waitqueue.

## Inline Helpers
Provides resource limit checks, dquot flush lock/unlock primitives, type masking, per-type quota-on and enforcement checks, inode-to-dquot lookup, low-space detection, and `xfs_qm_dqhold`.

## Public API
Declares dquot read/get/release/flush/destruction, timer/default-limit adjustment, quota ID extraction from inodes, multi-dquot locking, preallocation setup, attached-buffer helpers, and dquot block initialization.

## Invariants
`q_flush` is a completion used as a single-access flush gate. Metadata inodes do not have attached dquots. `xfs_dquot_type` masks record flags such as bigtime from the base user/group/project type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.c

## Purpose
Implements dquot log item operations for transaction logging, pinning, AIL push, release, and precommit buffer attachment.

## Main Behavior
Dquot log items format as two vectors: an `xfs_dq_logformat` plus the serialized `xfs_disk_dquot`. Pin/unpin updates the dquot pin count and wakes waiters when it reaches zero. `xfs_qm_dqunpin_wait` forces the log before waiting for pins to drain.

## AIL Push
`xfs_qm_dquot_logitem_push` skips pinned or locked dquots, grabs the dquot lock and flush gate, obtains the pre-attached dquot buffer, calls `xfs_qm_dqflush`, and queues the buffer for delayed write. It temporarily drops the AIL lock while doing buffer work.

## Transaction Integration
Release unlocks the dquot because dquot locking is hidden inside transaction commit. Precommit optionally verifies the dquot under `DEBUG_EXPENSIVE` and always attaches the backing buffer so later AIL pushes do not need to allocate/read from reclaim context.

## Public API
`xfs_qm_dquot_logitem_init` initializes the embedded log item, spinlock, back pointer, and dirty-since-flush state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.h

## Purpose
Declares the in-core dquot log item structure and initializer.

## Main Type
`struct xfs_dq_logitem` embeds the common `xfs_log_item`, points back to the owning dquot, records the LSN captured at the last flush, and contains a spinlock protecting the attached buffer pointer in `li_buf` and the `qli_dirty` flag.

## API
Declares `xfs_qm_dquot_logitem_init`.

## Invariants
`qli_dirty` records whether the dquot was dirtied since the last flush began; it determines whether flush completion can drop the attached buffer reference.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item_recover.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item_recover.c

## Purpose
Implements log recovery for dquot items and quotaoff items.

## Main APIs
- `xlog_dquot_item_ops` provides pass2 readahead and commit replay for `XFS_LI_DQUOT`.
- `xlog_quotaoff_item_ops` records quotaoff state during pass1 for `XFS_LI_QUOTAOFF`.

## Dquot Recovery
Recovery ignores dquot items if mount quota flags are absent or if a matching quotaoff was logged. It validates the logged disk dquot, reads the destination dquot buffer with verifier ops, skips replay when the on-disk dquot LSN is newer on CRC filesystems, copies the logged dquot into place, recalculates CRC, validates the full dquot block, and queues delayed write with `_XBF_LOGRECOVERY`.

## Readahead
Pass2 readahead reads the target dquot buffer unless quota is off, the log vector is missing/too small, or quotaoff already disables that type.

## Quotaoff Recovery
Pass1 inspects quotaoff flags and records user/project/group quota types in `log->l_quotaoffs_flag`, suppressing subsequent dquot item and dquot-buffer replay for those types.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_dquot_item_recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_drain.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_drain.c

## Purpose
Implements a passive drain counter for deferred metadata intents, used by scrub/repair to wait until active intent chains for an allocation group or realtime group have finished.

## Main APIs
- `xfs_defer_drain_wait_enable` and `xfs_defer_drain_wait_disable` toggle a static branch for waiter wakeup checks.
- `xfs_defer_drain_init` and `xfs_defer_drain_free` initialize and validate a drain.
- `xfs_group_intent_get` takes a group reference and increments its intent drain count.
- `xfs_group_intent_put` decrements the count and releases the group.
- `xfs_group_intent_drain` waits killably for the count to reach zero.
- `xfs_group_intent_busy` checks whether intents are pending.

## Key Behavior
The static key avoids waitqueue overhead when no drain waiters exist. Releasing the final intent wakes waiters only when the static branch is enabled and the waitqueue is active. A memory barrier pairs with waiter state setting before checking the waitqueue.

## Invariants
Callers waiting for a drain must not hold locks that prevent intent completion. Intent users hold a passive group reference for the lifetime of the declared update.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_drain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_drain.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_drain.h

## Purpose
Declares the deferred intent drain mechanism and documents why scrub needs it.

## Main Types and APIs
With `CONFIG_XFS_DRAIN_INTENTS`, `struct xfs_defer_drain` contains an atomic pending count and waitqueue. The header declares drain init/free, waiter static-key enable/disable, group intent get/put, drain wait, and busy check.

## Design Notes
The documentation explains that deferred work can roll transactions and temporarily drop AG header locks while still updating related metadata. Scrub must therefore wait for both AG locks and zero active intents to avoid false corruption findings or unsafe repairs.

## Configuration Behavior
Without `CONFIG_XFS_DRAIN_INTENTS`, the drain type is empty and group intent helpers reduce to ordinary group get/put; drain waiting/busy APIs are not provided in that configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_drain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_error.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_error.c

## Purpose
Implements XFS error reporting, corruption reporting, verifier diagnostics, inode verifier diagnostics, and debug-only error injection tags.

## Debug Error Injection
Under `DEBUG`, errortags are exposed through a per-mount `errortag` sysfs kobject. Users can set random factors by tag name/id, restore defaults, copy active tags between mounts, clear all tags, test random injection, or inject millisecond delays. Removed injection types such as dropped writes are rejected.

## Reporting APIs
- `xfs_error_report` emits internal error alerts and stack traces according to `xfs_error_level`.
- `xfs_corruption_error` optionally hex-dumps corrupted buffers, reports the internal error, and tells the user to run repair.
- `xfs_buf_corruption_error` reports relationship/semantic buffer corruption outside verifier paths.
- `xfs_buf_verifier_error` records buffer I/O error state and reports CRC versus corruption failures, with optional first-128-byte dump and stack trace.
- `xfs_verifier_error` is a convenience wrapper for whole-buffer verifier failures.
- `xfs_inode_verifier_error` reports inode metadata CRC/corruption diagnostics.

## Dependencies
Uses XFS sysfs helpers, alert/warn logging, panic tags, random numbers, delay primitives, stack trace/hex dump helpers, buffer I/O error marking, and inode/buffer metadata context.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_error.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_error.h

## Purpose
Declares XFS error/corruption reporting helpers, debug errortag hooks, error levels, dump sizing, and panic tag constants.

## Main APIs
Provides prototypes for internal error, corruption, buffer corruption, buffer verifier, generic verifier, and inode verifier reporting. Macros `XFS_ERROR_REPORT` and `XFS_CORRUPTION_ERROR` capture file, line, and return address.

## Debug Configuration
Under `DEBUG`, declares errortag init/delete/test/delay/add/add-by-name/copy/clear helpers and macros that inject file/line context. Without `DEBUG`, errortag operations compile to disabled or `-ENOSYS` behavior.

## Panic Tags
Defines panic tag bits used by XFS alert paths and `XFS_PTAG_MASK`, with string mappings for sysctl-facing configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.c

## Purpose
Implements log intent/done items for deferred file mapping exchange operations (`XMI`/`XMD`), including transaction formatting, deferred-op integration, recovery, relogging, and intent cancellation.

## Main Types and Caches
Uses `xfs_xmi_cache` for exchange mapping intent items and `xfs_xmd_cache` for done items. XMI items carry inode numbers/generations, start offsets, block count, sizes, flags, and a unique intent id. XMD items reference an XMI and log completion by id.

## Log Item Lifecycle
XMI allocation sets a two-reference count: one for log/unpin and one for done/cancel processing. Release removes from the AIL when the last reference drops. XMD release drops the associated XMI reference and frees the done item. XMI match compares intent ids for recovery cancellation.

## Deferred Operation Integration
`xfs_exchmaps_defer_type` supports one item per intent. `create_intent` logs the current exchange request, `create_done` logs completion, `finish_item` calls `xfs_exchmaps_finish_one`, and `cancel_item` frees unfinished in-core requests. `-EAGAIN` means work remains and the intent is requeued after other deferred work to avoid pinning too many XMI items.

## Recovery
XMI recovery validates feature support, padding, flags, inode numbers, and file extents; reopens both inodes by handle including generation checks; estimates resources; locks both inodes; ensures reflink/extent-count prerequisites; finishes the recovered intent; and captures/commits deferred work. XMD recovery releases a matching recovered XMI by id.

## Relogging
`xfs_exchmaps_relog_intent` clones the old XMI format into a fresh XMI so long-running recovery can move the log tail forward.

## Failure Handling
Malformed log vector sizes, nonzero padding, invalid flags/inodes/extents, inode handle failures, or corrupted finish operations return corruption errors and release held inodes/transactions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.h

## Purpose
Declares in-core log item structures and public deferred-add helper for file mapping exchange intents.

## Main Types
`struct xfs_xmi_log_item` embeds the common log item, an atomic reference count, and the logged XMI format. `struct xfs_xmd_log_item` embeds a done log item, points to the associated XMI, and stores the XMD format.

## Design Contract
The header documents redo-style logging: the intent item is logged in the first transaction of a rolled sequence, and done items are logged with the bmap updates that complete the exchange. If a crash occurs between intent and final done item, recovery replays the remaining mapping exchanges.

## API
Declares external XMI/XMD slab caches and `xfs_exchmaps_defer_add`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_exchmaps_item.h -->