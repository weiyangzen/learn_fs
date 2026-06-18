# Group Research: group_1008_linux_stable_sources_os_linux_linux_stable_fs_jbd2_journal_c_source_44c1ab2ba141

Scope: `Docs/research_subset_a.md`, covering Linux stable JBD2 journal/transaction/recovery/revoke internals and JFFS2 configuration, ACL, background GC, and mount-time filesystem build files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/journal.c -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/journal.c

## Scope
Implements core JBD2 journal object lifecycle, kjournald2 thread management, commit scheduling/waiting, log block allocation, journal superblock validation/update, feature negotiation, flush/wipe/abort handling, journal-head allocation, JBD inode lifecycle, proc stats, shrinker integration, and module cache initialization/destruction.

## Primary APIs
Exports journal control and lifecycle APIs including `jbd2_journal_init_dev()`, `jbd2_journal_init_inode()`, `jbd2_journal_load()`, `jbd2_journal_destroy()`, `jbd2_journal_flush()`, `jbd2_journal_wipe()`, `jbd2_journal_abort()`, `jbd2_journal_errno()`, `jbd2_journal_clear_err()`, `jbd2_journal_ack_err()`, `jbd2_log_wait_commit()`, `jbd2_journal_start_commit()`, `jbd2_journal_force_commit()`, `jbd2_complete_transaction()`, fast-commit buffer helpers, and journal-head helpers.

## Behavior
`kjournald2()` runs the journal thread, waking for explicit commit requests, commit timer expiry, freezer events, and unmount. It calls `jbd2_journal_commit_transaction()` outside `j_state_lock` and coordinates completion with `j_wait_done_commit`.

Commit control is transaction-id based. `__jbd2_log_start_commit()` requests commit of the running transaction, `jbd2_log_wait_commit()` sleeps until `j_commit_sequence` reaches a requested TID, and force/complete helpers start commits when needed before waiting.

Log allocation advances the circular log head with `jbd2_journal_next_log_block()`. Descriptor buffers are allocated and initialized with JBD2 magic, block type, and transaction sequence. Metadata write buffers handle magic-number escaping and shadow/frozen-data attachment.

Journal initialization loads and validates the on-disk superblock, checks block size, max length, feature flags, checksum versions, checksum type, and fast-commit area sizing. `journal_reset()` positions head/tail and starts kjournald2 after recovery.

Superblock writes use high-priority journal request flags, optional barriers/FUA, checksum refresh, synchronous buffer submission, and abort-on-write-error behavior. Flush checkpoints all committed transactions, cleans the tail, marks the journal empty, and can discard or zero journal blocks.

## State And Data
Key state includes `j_running_transaction`, `j_committing_transaction`, checkpoint lists, `j_head`, `j_tail`, `j_free`, transaction sequences, `j_flags`, superblock buffer, fast-commit bounds/buffers, revoke tables, waitqueues, shrinker counters, proc stats, and slab caches.

## Dependencies
Depends on block-device buffer I/O, transaction commit/checkpoint code, revoke setup, recovery replay, kernel shrinkers, procfs/seq_file, timers, kthreads, freezer support, slab/vmalloc allocation, and tracepoints.

## Risks And Invariants
Journal tail updates must reach stable storage before log space is reused. Feature bits and checksum fields must remain consistent for readonly and recovery paths. Journal abort is permanent for the mount and must record errno carefully, with `-ESHUTDOWN` precedence. Journal-head refcounting protects buffer attachment from VM release and RCU slab reuse hazards.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/recovery.c -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/recovery.c

## Scope
Implements journal mount-time recovery and skip-recovery logic. It scans, validates, revokes, and replays committed log transactions, including descriptor, commit, revoke, checksum, and fast-commit replay handling.

## Primary APIs
Main entry points are `jbd2_journal_recover()` and `jbd2_journal_skip_recovery()`. Internal helpers include `do_one_pass()`, `jread()`, `do_readahead()`, `count_tags()`, checksum verifiers, `jbd2_do_replay()`, `scan_revoke_records()`, and `fc_do_one_pass()`.

## Behavior
Recovery is three-pass:
- `PASS_SCAN` finds the valid transaction range, validates commit records, counts revoke records, tracks head block, and detects stale or corrupt journal tails.
- `PASS_REVOKE` builds the revoke table from revoke blocks.
- `PASS_REPLAY` replays descriptor-tagged data blocks that are not revoked.

`jread()` maps logical journal offsets through `jbd2_journal_bmap()`, reads the physical block, and triggers sequential readahead. Log traversal wraps between `j_first` and `j_last`.

Descriptor replay reads each tagged journal data block, checks block-tag checksums, skips revoked blocks, restores escaped magic numbers, copies data into the filesystem block device buffer, and marks it dirty/uptodate.

Checksum handling supports old transaction checksums plus v2/v3 descriptor, commit, and block-tag checksums. Scan logic distinguishes interrupted commits from stale lazy-init journal contents using commit-time monotonicity and async-commit rules.

Fast commit replay is delegated to `j_fc_replay_callback()` across the fast-commit block range on scan/replay passes, excluding revoke pass.

## State And Data
`struct recovery_info` carries start/end transactions, replay head block, replay count, revoke count, and revoke-hit count. Recovery updates `j_transaction_sequence`, `j_head`, `j_failed_commit`, and temporary replay revoke-table selection.

## Dependencies
Uses revoke APIs from `revoke.c`, log mapping and tag sizing from `journal.c`, block-device sync/flush, checksum helpers, buffer-head I/O, and optional filesystem fast-commit replay callbacks.

## Risks And Invariants
Only complete committed transactions should replay. Revokes for a block at transaction N suppress replay for N and earlier, but not later updates. IO errors attempt partial replay but report failure. Fast-commit replay errors must fall back or fail consistently through the filesystem callback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/revoke.c -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/revoke.c

## Scope
Implements JBD2 revoke records, which prevent stale logged metadata blocks from being replayed after deletion/reallocation. Covers revoke hash table allocation, runtime revoke/cancel operations, commit-time revoke descriptor writing, and recovery-time revoke tests.

## Primary APIs
Exports or provides `jbd2_journal_init_revoke_record_cache()`, `jbd2_journal_init_revoke_table_cache()`, `jbd2_journal_init_revoke_table()`, `jbd2_journal_init_revoke()`, `jbd2_journal_destroy_revoke()`, `jbd2_journal_revoke()`, `jbd2_journal_cancel_revoke()`, `jbd2_clear_buffer_revoked_flags()`, `jbd2_journal_switch_revoke_table()`, `jbd2_journal_write_revoke_records()`, `jbd2_journal_set_revoke()`, `jbd2_journal_test_revoke()`, and `jbd2_journal_clear_revoke()`.

## Behavior
Runtime revoke inserts a block record into the running transaction’s revoke hash and marks matching buffer heads with `BH_Revoked`/`BH_RevokeValid`. If a buffer is passed, it also calls `jbd2_journal_forget()` to remove it from current journaling state.

Cancel revoke is called when a block is journaled again in the same transaction. It uses cached buffer revoke bits when valid, otherwise searches the hash table and removes the record. It also clears revoked state on a hashed alias if the current buffer is not the blockdev mapping buffer.

Commit-time code switches revoke tables so the committing transaction owns one table and the new running transaction owns the other. It writes revoke records into `JBD2_REVOKE_BLOCK` descriptors, using 32-bit or 64-bit block numbers, with optional descriptor checksums.

Recovery-time revoke insertion records the latest sequence for each block. Replay tests skip a logged block when its transaction sequence is not newer than the revoke sequence.

## State And Data
`jbd2_revoke_record_s` stores hash link, transaction sequence, and block number. `jbd2_revoke_table_s` stores power-of-two hash size, shift, and list heads. `journal->j_revoke` points to the active runtime or replay table.

## Dependencies
Depends on transaction handles, buffer-head revoke state bits, journal descriptor allocation, feature setting (`JBD2_FEATURE_INCOMPAT_REVOKE`), commit code log buffer lists, and recovery replay.

## Risks And Invariants
A revoke after a journaled write must take precedence during recovery. A journaled write after a revoke must cancel the revoke. Revoke credits are enforced per handle. The committing revoke table is single-threaded under kjournald2; the running table uses `j_revoke_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/revoke.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/transaction.c -->
# File Research: sources/os/linux/linux-stable/fs/jbd2/transaction.c

## Scope
Implements JBD2 transaction and handle management: transaction creation, handle start/stop/restart, credit accounting, reserved handles, update barriers, write/create/undo access, metadata dirtying, forget/invalidate/free-buffer paths, transaction buffer-list management, and ordered-data inode tracking.

## Primary APIs
Key APIs include `jbd2__journal_start()`, `jbd2_journal_start()`, `jbd2_journal_start_reserved()`, `jbd2_journal_free_reserved()`, `jbd2_journal_extend()`, `jbd2__journal_restart()`, `jbd2_journal_restart()`, `jbd2_journal_stop()`, `jbd2_journal_lock_updates()`, `jbd2_journal_unlock_updates()`, write/create/undo access functions, `jbd2_journal_dirty_metadata()`, `jbd2_journal_forget()`, `jbd2_journal_try_to_free_buffers()`, `jbd2_journal_invalidate_folio()`, buffer filing/refiling helpers, and ordered inode range helpers.

## Behavior
Starting a handle attaches it to the running transaction or creates a new one. Credit accounting enforces per-transaction limits, reserved-credit limits, revoke descriptor space, and log-space availability before metadata is dirtied. Handles enter `memalloc_nofs` context to avoid filesystem recursion.

Reserved handles can join locked transactions without waiting for commits, supporting writeback paths that must not deadlock. Update barriers block new normal handles, wait for reserved credits and active updates to drain, then serialize special operations with `j_barrier`.

Write access attaches buffers to `BJ_Reserved`, handles copy-out when an older committing transaction owns the buffer, waits on shadow buffers, preserves frozen/committed copies for undo access, and cancels revokes. Dirty metadata moves buffers to `BJ_Metadata` and consumes credits once per modified buffer.

Forget/invalidate paths handle buffers in current, committing, checkpointed, or no transaction state. They preserve checkpoint dependencies with `BJ_Forget`, mark committing buffers freed, and avoid unsafe truncation of partial-page buffers belonging to the committing transaction.

Stopping a handle returns unused credits, accounts revoke descriptor credits actually needed, optionally batches synchronous commits, requests commits for sync or expired transactions, and waits for sync commit completion.

## State And Data
Transactions track state, TID, start/expiry times, update count, outstanding credits/revokes, buffer lists (`BJ_Metadata`, `BJ_Reserved`, `BJ_Shadow`, `BJ_Forget`), inode list, and commit statistics. Journal heads track current/next/checkpoint transactions, list type, frozen data, committed data, triggers, modified state, and buffer linkage.

## Dependencies
Integrates with `journal.c` commit scheduling, `commit.c` transaction commit, `checkpoint.c`, revoke cancellation, buffer-head/page-cache APIs, folio invalidation, VFS writeback, tracepoints, and filesystem ordered-data users such as ext4.

## Risks And Invariants
Credit accounting is central: dirtying without credits corrupts transaction bounds. Copy-out must protect committing transaction contents while allowing new writes. `b_transaction`/`b_next_transaction` transitions require correct lock ordering. Truncate invalidation depends on filesystem orphan/i_size ordering to avoid replaying stale data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jbd2/transaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/Kconfig

## Scope
Defines build-time configuration options for JFFS2 in Linux stable.

## Options
`JFFS2_FS` enables the filesystem and depends on MTD. It selects CRC32 and describes JFFS2 as a flash-oriented journalling filesystem for embedded MTD devices, not normal block devices.

`JFFS2_FS_DEBUG` controls debug verbosity. `JFFS2_FS_WRITEBUFFER` enables write-buffering needed for NAND, NOR with transparent ECC, and DataFlash. `JFFS2_FS_WBUF_VERIFY` verifies write-buffer reads.

`JFFS2_SUMMARY` enables summary nodes for faster mount, typically generated by `sumtool`. `JFFS2_FS_XATTR` enables extended attributes. `JFFS2_FS_POSIX_ACL` depends on xattrs and selects `FS_POSIX_ACL`. `JFFS2_FS_SECURITY` enables security-label xattr support.

Compression options include advanced selection plus zlib, LZO, RTIME, and RUBIN compressors. Default compression mode is chosen among none, priority, size, and favour-LZO.

## Dependencies
Links JFFS2 to MTD, CRC32, xattr, ACL, security-label, zlib, and LZO kernel facilities.

## Risks And Invariants
ACL and security labels require xattr support. Some compressors affect filesystem image compatibility with older kernels or bootloaders. Write-buffering is required for several flash classes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/Makefile

## Scope
Defines the JFFS2 kernel object composition.

## Build Behavior
`obj-$(CONFIG_JFFS2_FS) += jffs2.o` builds the aggregate module/built-in object. Core files include compression dispatch, directory/file/ioctl, node management, allocation, read/write, scanning, garbage collection, symlink, build, erase, background GC, filesystem/superblock, debug, and writev support.

Conditional objects add write-buffering, xattr handlers, trusted/user/security xattrs, POSIX ACLs, individual compressors, and summary support according to Kconfig symbols.

## Dependencies
Directly mirrors feature gates from `Kconfig`.

## Risks And Invariants
Feature-specific source files are only linked when their config dependencies are enabled; callers must use config stubs or guards for optional ACL/xattr/compressor behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/acl.c

## Scope
Implements JFFS2 POSIX ACL serialization/deserialization and VFS ACL get/set/init hooks backed by JFFS2 xattrs.

## Primary APIs
Provides `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`. Internal helpers are `jffs2_acl_size()`, `jffs2_acl_count()`, `jffs2_acl_from_medium()`, `jffs2_acl_to_medium()`, and `__jffs2_set_acl()`.

## Behavior
On-medium ACL format stores a versioned header and entries. The first four ACL entries use a short format without IDs when possible; named user/group entries use the full format with UID/GID.

`jffs2_get_acl()` maps access/default ACL type to a JFFS2 xattr prefix, reads xattr length, allocates a buffer, fetches xattr data, converts it to `struct posix_acl`, and returns `NULL` for missing or unsupported xattr storage.

`jffs2_set_acl()` validates type, updates inode mode for access ACLs via `posix_acl_update_mode()`, writes mode changes through `jffs2_do_setattr()`, rejects default ACLs on non-directories, serializes ACLs into xattrs, and updates the inode ACL cache.

`jffs2_init_acl_pre()` computes inherited ACLs before inode creation, caches them on the inode, and updates the mode. `jffs2_init_acl_post()` writes cached default/access ACL xattrs after inode creation.

## State And Data
Uses `struct jffs2_acl_header`, `jffs2_acl_entry_short`, and `jffs2_acl_entry`, with JFFS2 endian conversion helpers and init-user-namespace UID/GID conversion.

## Dependencies
Depends on POSIX ACL core, JFFS2 xattr get/set routines, JFFS2 setattr, inode ACL cache helpers, and mount idmap interfaces.

## Risks And Invariants
Deserializer must reject malformed sizes, unknown version, invalid tags, and trailing bytes. Access ACL mode updates must happen before xattr persistence. The code uses `nop_mnt_idmap` for mode update rather than the passed idmap.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/acl.h

## Scope
Declares JFFS2 on-medium ACL structures and POSIX ACL function prototypes/stubs.

## Contents
Defines `jffs2_acl_entry`, `jffs2_acl_entry_short`, and `jffs2_acl_header`. The header uses JFFS2 integer types and a flexible `a_entries[]` payload.

When `CONFIG_JFFS2_FS_POSIX_ACL` is enabled, declares `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`. Otherwise, maps ACL hooks to `NULL` or no-op success stubs.

## Dependencies
Relies on POSIX ACL types, inode/dentry declarations from including context, and JFFS2 endian integer typedefs.

## Risks And Invariants
The disabled-config stubs allow callers to avoid preprocessor branching. Structure layout must match `acl.c` serialization and existing on-flash ACL data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/background.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/background.c

## Scope
Implements the JFFS2 background garbage-collection kernel thread lifecycle and wake/stop signaling.

## Primary APIs
Provides `jffs2_garbage_collect_trigger()`, `jffs2_start_garbage_collect_thread()`, and `jffs2_stop_garbage_collect_thread()`. The thread body is `jffs2_garbage_collect_thread()`.

## Behavior
Start initializes completion objects, creates `jffs2_gcd_mtd%d`, waits until the thread publishes `c->gc_task`, and returns the thread pid or error.

Trigger requires `erase_completion_lock` held and sends `SIGHUP` when the GC task exists and `jffs2_thread_should_wake()` says work is needed.

Stop sends `SIGKILL` under `erase_completion_lock` if a GC task is active and waits for thread exit completion.

The GC thread allows `SIGKILL`, `SIGSTOP`, and `SIGHUP`, sets low priority, becomes freezable, sleeps until GC is needed, adds a 50 ms throttle delay to reduce boot-time starvation, handles freezer and signals, blocks SIGHUP while running a pass, and calls `jffs2_garbage_collect_pass()`. `-ENOSPC` terminates the thread.

## State And Data
Uses `c->gc_task`, `gc_thread_start`, `gc_thread_exit`, `erase_completion_lock`, and MTD index for thread naming.

## Dependencies
Depends on JFFS2 GC policy/pass functions, kernel kthreads, signals, freezer, completions, scheduler, and MTD metadata.

## Risks And Invariants
`gc_task` is protected by `erase_completion_lock`. SIGHUP is a wake signal, SIGKILL is teardown, and freezer handling must return to the sleep check after thaw.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/background.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/build.c -->
# File Research: sources/os/linux/linux-stable/fs/jffs2/build.c

## Scope
Implements JFFS2 mount-time filesystem build from scanned flash nodes, including inode-cache link counting, dead inode removal, temporary dirent cleanup, xattr subsystem build, trigger-level calculation, and eraseblock list initialization.

## Primary APIs
The exported entry point is `jffs2_do_mount_fs()`. Internal helpers include inode-cache iteration helpers, `jffs2_build_inode_pass1()`, `jffs2_build_filesystem()`, `jffs2_build_remove_unlinked_inode()`, and `jffs2_calc_trigger_levels()`.

## Behavior
`jffs2_do_mount_fs()` initializes eraseblock accounting from flash/sector size, allocates the eraseblock array with `vzalloc()` or `kzalloc()`, initializes all block lists, starts summary support, builds the filesystem, and computes space reservation thresholds.

`jffs2_build_filesystem()` sets scanning/building flags, calls `jffs2_scan_medium()`, then pass 1 walks directory scan dirents and increments child inode link counts. Missing child inode caches cause the dirent raw node to be marked obsolete.

Pass 2 removes inode caches with zero link count by marking all raw nodes obsolete. If such an inode is a directory, child link counts are decremented and newly unlinked children are queued for iterative removal via `dead_fds`.

After dead cleanup, directory hardlink detection is revisited. Temporary `scan_dents` are freed, and directory child inode caches store parent inode numbers in `pino_nlink`. Then the xattr subsystem is built, lists are rotated for wear leveling, and build flags are cleared.

`jffs2_calc_trigger_levels()` computes reserved eraseblock thresholds for deletion, writes, GC wakeup, GC merge, bad-block GC, very-dirty GC triggering, and minimum dirty space needed for useful GC.

## State And Data
Touches `free_size`, `nr_blocks`, `blocks[]`, eraseblock lists, `highest_ino`, summary state, `JFFS2_SB_FLAG_SCANNING`, `JFFS2_SB_FLAG_BUILDING`, inode-cache `pino_nlink`, `scan_dents`, flags, and reservation thresholds.

## Dependencies
Depends on medium scanning, raw node obsoletion, inode cache lookup/free, full-dirent allocation/free, xattr subsystem build/clear, summary init/exit, eraseblock management, wear-level list rotation, and MTD sizing.

## Risks And Invariants
Mount reconstruction relies on physical scan results plus dirent link counts. Dead directory cleanup is iterative to avoid recursion. Directory hardlinks are treated as anomalous and warned after dead entries are removed. Failure paths must free temporary dirents, xattrs, summary state, raw refs, inode caches, and block arrays.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jffs2/build.c -->