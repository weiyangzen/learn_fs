# Group Research: group_759_linux_sources_os_linux_linux_fs_gfs2_lock_dlm_c_sources_os_linux_lin_34f0d490d64e

Scope: `Docs/research_subset_a.md`. All 13 listed GFS2 source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/lock_dlm.c -->
# File Research: sources/os/linux/linux/fs/gfs2/lock_dlm.c

Implements the `lock_dlm` clustered lock-manager backend for GFS2. It translates GFS2 glock states and flags into DLM lock modes/flags, handles DLM AST/BAST callbacks, records lock timing statistics, and coordinates cluster journal recovery through DLM lockspace callbacks.

Key entry points are exposed through `gfs2_dlm_ops`: `gdlm_mount`, `gdlm_first_done`, `gdlm_recovery_result`, `gdlm_unmount`, `gdlm_put_lock`, `gdlm_lock`, and `gdlm_cancel`.

Important behavior:
- `gdlm_lock()` builds DLM resource names from glock type/number, computes conversion flags, tracks blocking requests, retries `-EBUSY`, and submits `dlm_lock()`.
- `gdlm_ast()` maps DLM completion statuses to GFS2 lock outcomes, clears initial lock state on first success, handles unlock completion by freeing dead glocks, and clears invalid LVBs.
- `gdlm_bast()` maps DLM blocking callback modes back to GFS2 callback states for demotion pressure.
- `gdlm_put_lock()` either skips unlock on lockspace teardown when safe or sends `dlm_unlock()` while preserving LVB updates for exclusive locks.
- Recovery uses `control_lock` and `mounted_lock` plus a control-lock LVB containing a generation number and jid bitmap.
- `gfs2_control_func()` propagates DLM failed-slot notifications into LVB bits, starts `gfs2_recover_set()` for pending journals, clears recovered bits, and thaws glocks when all recovery for the generation is complete.
- `control_mount()` distinguishes first mounter, normal mounter, and spectator cases; first mounters recover all journals before allowing others to proceed.
- DLM callbacks `gdlm_recover_prep`, `gdlm_recover_slot`, and `gdlm_recover_done` maintain generation and failed-journal arrays under `ls_recover_spin`.

Dependencies include Linux DLM APIs, GFS2 glock core, recovery workqueues, lock value blocks, and filesystem mount arguments. The main correctness risks are generation ordering, LVB bitmap consistency, lockspace teardown races, and preserving first-mounter recovery semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/lock_dlm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/log.c -->
# File Research: sources/os/linux/linux/fs/gfs2/log.c

Implements GFS2 journal space accounting, log reservation, AIL management, ordered write handling, revoke handling, log flush orchestration, and the `gfs2_logd` kernel thread.

Key exported functions include `gfs2_struct2blk`, `gfs2_log_is_empty`, `gfs2_log_release_revokes`, `gfs2_log_release`, `gfs2_log_try_reserve`, `gfs2_log_reserve`, `gfs2_write_log_header`, `gfs2_remove_from_journal`, `gfs2_log_flush`, `gfs2_log_commit`, `gfs2_ail1_flush`, `log_flush_wait`, `gfs2_add_revoke`, `gfs2_glock_remove_revoke`, `gfs2_flush_revokes`, `gfs2_ail_drain`, and `gfs2_logd`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/log.h -->
# File Research: sources/os/linux/linux/fs/gfs2/log.h

Declares the public log-management interface used by GFS2 transaction, inode, glock, quota, mount, and recovery code. It defines `GFS2_LOG_FLUSH_MIN_BLOCKS`, provides `gfs2_ordered_add_inode()`, and declares reservation, release, flush, commit, AIL, revoke, ordered-inode, and logd APIs implemented in `log.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/lops.c -->
# File Research: sources/os/linux/linux/fs/gfs2/lops.c

Implements low-level journal operations for metadata buffers, journaled data buffers, and revoke records. It provides journal I/O helpers, journal-head search, pin/unpin transitions, and replay handlers. Key exports include `gfs2_pin`, `gfs2_log_incr_head`, `gfs2_log_bmap`, `gfs2_log_submit_write`, `gfs2_log_write`, `gfs2_find_jhead`, and `gfs2_drain_revokes`.

Risk areas include descriptor length/count accounting, buffer pin lifetime, escaped-buffer copy correctness, bio completion, and replay ordering across revoke and payload passes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/lops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/lops.h -->
# File Research: sources/os/linux/linux/fs/gfs2/lops.h

Defines the log-operation dispatch interface and declares core low-level journal helpers from `lops.c`: log-head movement, journal block mapping, log write/submit, buffer pinning, journal-head search, and revoke drain helpers. It exposes `gfs2_log_ops[]` and inline dispatchers for commit and replay phases.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/lops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/main.c -->
# File Research: sources/os/linux/linux/fs/gfs2/main.c

Implements GFS2 module initialization and teardown. It creates global caches, workqueues, shrinkers, mempools, debugfs/sysfs support, and registers the `gfs2` and `gfs2meta` filesystem types. The file owns process-wide resource lifetime; key risks are init failure unwinding and draining RCU-deferred quota data before cache destruction.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/meta_io.c -->
# File Research: sources/os/linux/linux/fs/gfs2/meta_io.c

Implements metadata address-space writeback, metadata buffer lookup/read helpers, metadata readahead, and journal wipe support for freed or deleted blocks. Key exports include `gfs2_meta_new`, `gfs2_meta_read`, `gfs2_meta_wait`, `gfs2_getbuf`, `gfs2_journal_wipe`, `gfs2_meta_buffer`, and `gfs2_meta_ra`.

This version uses current buffer I/O APIs such as `set_buffer_async_write()`, `bh_submit()`, `bh_end_async_write`, and `end_buffer_read_sync()` in metadata write/read completion paths. Risk areas include buffer lifetime/refcounts, dirty/pinned journal interactions during block deletion, and avoiding stale metadata after withdraw.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/meta_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/meta_io.h -->
# File Research: sources/os/linux/linux/fs/gfs2/meta_io.h

Declares metadata I/O helpers and buffer utilities. It exposes `gfs2_meta_aops`, `gfs2_rgrp_aops`, `gfs2_mapping2sbd()`, metadata buffer creation/read/wait/get APIs, journal wipe, typed metadata lookup, readahead, `REMOVE_JDATA`/`REMOVE_META`, and `buffer_busy()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/meta_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/ops_fstype.c -->
# File Research: sources/os/linux/linux/fs/gfs2/ops_fstype.c

Implements GFS2 filesystem type behavior: mount context parsing, superblock setup, lock protocol mounting, journal/statfs/quota/per-node initialization, remount/reconfigure, gfs2meta mounting, and superblock teardown. It coordinates `init_sbd()`, superblock validation, locking, journal selection/recovery, quota/statfs setup, thread startup, `gfs2_fill_super()`, `gfs2_reconfigure()`, and `gfs2_kill_sb()`.

Risk areas include unwind ordering, first-mount recovery boundaries, spectator read-only semantics, immutable remount validation, and teardown ordering while background work may still exist.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/ops_fstype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/quota.c -->
# File Research: sources/os/linux/linux/fs/gfs2/quota.c

Implements GFS2 clustered quota accounting. It maintains per-ID quota data objects, local per-node quota-change slots, quota LVB caching, periodic syncing into the global quota file, allocation checks, and VFS quotactl operations.

Important behavior includes local quota-change files, hash/RCU/refcounted quota data, slot and buffer attachment, quota hold/lock/check/change paths, batched sync into the shared quota file, mount-time reconstruction from local quota changes, cleanup, `gfs2_quotad()`, and `gfs2_quotactl_ops`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/quota.h -->
# File Research: sources/os/linux/linux/fs/gfs2/quota.h

Declares the GFS2 quota subsystem API and quota helper constants, including quota hold/unhold, lock/unlock, check/change, sync/refresh/init/cleanup, quotad, statfs wakeup, `gfs2_quota_lock_check()`, `gfs2_quotactl_ops`, quota shrinker hooks, LRU, and hash initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/recovery.c -->
# File Research: sources/os/linux/linux/fs/gfs2/recovery.c

Implements journal replay and recovery work for dirty GFS2 journals. It reads journal blocks, manages replay revokes, validates log headers, scans descriptors through log operations, updates statfs state, writes clean journal headers, and reports recovery results to the lock manager.

Key behavior includes circular revoke checks, two-pass descriptor replay, local statfs recovery, clean journal header writing, remote journal locking, read-only/freeze checks, log pointer initialization, recovery workqueue use, and DLM result reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/gfs2/recovery.h -->
# File Research: sources/os/linux/linux/fs/gfs2/recovery.h

Declares the journal recovery interface and exposes `gfs2_recovery_wq`. It defines `gfs2_replay_incr_blk()` for wrapping journal block pointers and declares replay block read, revoke add/check/clean, journal recovery queueing, recovery work, log-header validation, and log-pointer initialization APIs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/gfs2/recovery.h -->