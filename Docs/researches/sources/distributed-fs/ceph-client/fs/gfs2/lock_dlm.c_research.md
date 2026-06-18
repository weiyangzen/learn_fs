<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lock_dlm.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/lock_dlm.c

## Purpose
`lock_dlm.c` is GFS2's `lock_dlm` lock manager backend. It translates GFS2 glock state requests into kernel DLM lock modes, updates lock timing statistics, services DLM AST/BAST callbacks, mounts and releases a DLM lockspace, and coordinates cluster journal recovery through DLM recovery callbacks plus two special non-disk locks: the mounted lock and the control lock.

## Important APIs, types, and functions
The exported contract is `const struct lm_lockops gfs2_dlm_ops`, with `lm_mount`, `lm_first_done`, `lm_recovery_result`, `lm_unmount`, `lm_put_lock`, `lm_lock`, `lm_cancel`, and DLM hostdata tokens. Core glock operations are `gdlm_lock`, `gdlm_put_lock`, `gdlm_cancel`, `gdlm_ast`, and `gdlm_bast`. Lock mode conversion is handled by `make_mode`, `middle_conversion`, `down_conversion`, and `make_flags`. Recovery control is organized around `gfs2_control_func`, `control_mount`, `control_first_done`, `gdlm_recover_prep`, `gdlm_recover_slot`, `gdlm_recover_done`, and `gdlm_recovery_result`. The DLM callback table is `gdlm_lockspace_ops`.

## Control Flow
For normal glocks, `gdlm_lock` stores the requested GFS2 state in `gl_req`, converts current/requested states to DLM modes, computes DLM flags, builds a fixed-width resource name for initial locks, and calls `dlm_lock` under `ls_sem`. DLM completion calls `gdlm_ast`, which maps DLM status values to GFS2 outcomes, clears `GLF_BLOCKING`, zeroes invalid LVBs, clears `GLF_INITIAL` after the first successful lock, and completes the glock. Blocking callbacks call `gdlm_bast`, which maps DLM modes back to demotion states for `gfs2_glock_cb`. Dead glocks are released through `gdlm_put_lock`, usually by `dlm_unlock`; during lockspace teardown, `SDF_SKIP_DLM_UNLOCK` allows avoiding per-lock unlocks except where an exclusive LVB must be preserved.

DLM lockspace mount parses the `cluster:fsname` table, initializes recovery arrays, calls `dlm_new_lockspace`, and either uses DLM recovery ops or falls back to older userspace control behavior. With ops enabled, `control_mount` takes the control and mounted locks to detect the first mounter, waits for existing recovery generations and journal bitmap bits to clear, and blocks normal locking through `DFL_BLOCK_LOCKS` until it is safe. The first mounter recovers all journals during mount and calls `control_first_done`, which writes the latest generation into the control LVB, demotes mounted lock to PR, and releases the control lock to NL.

During membership recovery, DLM calls `recover_prep`, `recover_slot`, and `recover_done`. These update `ls_recover_block`, `ls_recover_start`, per-jid `recover_submit` arrays, and queue `sd_control_work`. `gfs2_control_func` serializes on the control lock in EX, merges failed-jid bits and successful recovery results into the control LVB, queues `gfs2_recover_set` for each set bit, and finally thaws glocks when all bits are clear and no newer DLM recovery cycle has reblocked locking.

## State and Persistence
Persistent cluster-visible state is in DLM lock value blocks. Individual glocks may have LVBs attached through `DLM_LKF_VALBLK`. The control LVB stores a little-endian generation in the first four bytes and a failed-jid bitmap starting at offset 8. In-memory state in `struct lm_lockstruct` includes the DLM lockspace pointer, synchronous lock completions, mounted/control `dlm_lksb`s, recovery flags, generation counters, the local jid, and variable-sized `recover_submit`/`recover_result` arrays. Lock statistics are maintained in per-glock and per-CPU `gfs2_lkstats`.

## Dependencies and Integration Points
This file depends on the kernel DLM API (`dlm_lock`, `dlm_unlock`, `dlm_new_lockspace`, `dlm_release_lockspace`), GFS2 glock core APIs, `gfs2_recover_set`, recovery result constants, filesystem logging helpers, tracepoints, and sysfs/uevent-visible state in `gfs2_sbd`. `ops_fstype.c` selects `gfs2_dlm_ops` from the lock protocol name; `recovery.c` reports journal recovery results back through `lm_recovery_result`.

## Risks
The recovery protocol depends on subtle generation comparisons and the control LVB bitmap. A missed update, stale generation, or premature `DFL_BLOCK_LOCKS` clear could allow normal locking before required journal replay. DLM callbacks can arrive during unmount or withdraw, so `ls_sem`, `DFL_UNMOUNT`, and dead lockrefs are important lifetime guards. `sync_lock` uses a single completion object and must be used serially. The fallback path without DLM ops has different journal-id and recovery semantics. The fixed resource-name formatting must remain compatible across nodes.

## Test Signals
Useful signals include multi-node mount and unmount, first-mounter election, spectator mount while recovery is pending, node failure during another recovery, repeated `GAVEUP` recovery results, DLM lock cancel/timeouts, LVB preservation for exclusive glocks, journal-id assignment through `recover_done`, `gfs2_control` logs for generation transitions, glock thaw after all jid bits clear, and lock-stat tracepoints for blocking versus nonblocking requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/lock_dlm.c -->
