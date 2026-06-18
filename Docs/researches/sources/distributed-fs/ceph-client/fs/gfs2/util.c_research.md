# sources/distributed-fs/ceph-client/fs/gfs2/util.c

## Purpose
`util.c` provides GFS2 global caches, assertion/consistency reporting, freeze-glock helpers, journal-clean checking, I/O error handling, and filesystem withdrawal orchestration.

## Important APIs, Types, And Functions
The file defines global slab caches for glocks, inodes, bufdata, rgrps, quota data, and transactions, plus `gfs2_page_pool`. Exported helpers include `gfs2_assert_i`, `check_journal_clean`, `gfs2_freeze_lock_shared`, `gfs2_freeze_unlock`, `gfs2_lm`, `gfs2_withdraw_func`, `gfs2_withdraw`, `gfs2_assert_withdraw_i`, `gfs2_assert_warn_i`, `gfs2_consist_i`, `gfs2_consist_inode_i`, `gfs2_consist_rgrpd_i`, `gfs2_meta_check_ii`, `gfs2_metatype_check_ii`, `gfs2_io_error_i`, and `gfs2_io_error_bh_i`.

## Control Flow
`check_journal_clean` locks a journal inode glock in shared recovery-aware mode, validates the journal descriptor, finds the journal head, and requires an unmount log header for spectator safety. Freeze helpers acquire and release the shared freeze glock.

Withdrawal starts in `gfs2_withdraw`, which honors mount error policy: withdraw/deactivate schedules async work once, panic policy panics. `gfs2_withdraw_func` optionally emits an offline uevent and waits for `gfs2_withdraw_helper` status, then orders lock-manager unmount relative to local cache drain depending on whether the block device was deactivated. `do_withdraw` clears `SDF_JOURNAL_LIVE`, drains AIL transactions, wakes log/quota waiters, waits briefly for the log to empty, marks the VFS superblock read-only, and dequeues glock holders that can no longer complete.

## State And Persistence
The file modifies `sd_flags` (`SDF_WITHDRAWN`, `SDF_JOURNAL_LIVE`), `s_flags` (`SB_RDONLY`), withdraw-helper status/completion, log wait queues, and lock-manager state. It does not directly write normal filesystem metadata, but withdrawal controls whether future writes can happen and whether remote recovery can proceed.

## Dependencies And Integration Points
It integrates with glocks, log/AIL, recovery, rgrp dump, superblock journal checks, sysfs uevents, lock managers, quota waiters, and kernel panic/BUG policy. The consistency helpers are called from most metadata validation paths.

## Risks And Test Signals
Risks include deadlock during withdrawal, helper timeout policy errors, duplicate withdrawal work, missed read-only transition, and over-aggressive BUG/panic behavior under debug or panic-on-error settings. Signals include forced I/O error tests, withdraw sysfs tests, spectator dirty-journal rejection, cluster recovery after offline uevent success/failure, and absence of hung log/quota waiters.
