# File Research: sources/block-storage/lvm2/lib/locking/lvmlockd.c

## Purpose
Implements the LVM command-side client for `lvmlockd`, covering shared VG lockspaces, global/VG/LV locks, sanlock internal LV management, DLM/IDM integration, persistent reservation support hooks, lock argument parsing, LV lifecycle lock allocation/freeing, rename/remove flows, and clustered LV refresh.

## Main Responsibilities
- Tracks lvmlockd socket configuration, enabled state, connection state, and initialization failures.
- Recognizes lockd lock types: `dlm`, `sanlock`, and `idm`.
- Parses user `--lockopt` and `--setlockargs` strings into internal bit flags and validates conflicting options.
- Builds daemon requests, optionally attaching PV path lists for IDM, and normalizes daemon replies into result codes, result flags, owner details, and generation values.
- Initializes and frees lockd VGs for DLM, IDM, and sanlock.
- Creates, activates, deactivates, extends, refreshes, and removes the hidden sanlock `lvmlock` LV.
- Starts, stops, waits for, and queries VG lockspaces.
- Acquires/releases global locks, VG metadata locks, and LV locks, with mode-specific error handling and retry behavior.
- Initializes and frees LV lock metadata during `lvcreate` and `lvremove`.
- Redirects locks for LV families whose synchronization is represented by another LV, such as thin volumes, VDO volumes, COW snapshots, and cache components.
- Handles shared-lock resize exceptions and remote LV refresh after `lvresize`.
- Coordinates VG rename and VG removal with lockspace state and sanlock lease state.

## Important Control Flow
The daemon protocol is centered on `_lockd_request`. It returns `0` only when no usable result could be obtained from lvmlockd; otherwise it returns `1` even if the daemon operation result is negative. Higher-level functions then decide whether a negative result is fatal, ignorable, or a warning based on the requested mode and command context.

Sanlock VG initialization creates a hidden `lvmlock` LV sized from PV sector size, configured sanlock alignment, local host id bounds, and existing LV lock count. The LV is activated before the `init_vg` request so sanlock can initialize leases. On failure it delays briefly, deactivates/removes the internal LV, and commits metadata cleanup.

`lockd_start_vg` joins a lockspace. For sanlock it activates the internal `lvmlock` LV and passes the local host id. For IDM it builds a PV path list. It handles already-started and starting states as success-like outcomes, reports lock-manager and lease repair errors, and updates persistent reservation generation keys when required.

`lockd_global_create` handles the first sanlock VG bootstrap case where no sanlock global lock can exist until the new VG exists. It allows creation without a global lock only when lvmlockd reports no global lockspace/no lockspaces and no existing sanlock VG is visible in `lvmcache`.

`lockd_global` enforces exclusive global lock failures as hard failures, while several shared global lock failures are downgraded to read-without-global-lock warnings. It also supports adopt and repair lock options and tracks `cmd->lockd_global_ex`.

`lockd_vg` records lock results into `struct lockd_state` because the caller may not yet know whether the VG is local or shared. Shared lock failures often allow a read path to continue with warning state, while exclusive failures generally stop the command.

`lockd_lv_name` performs the actual LV lock request. It handles disabled LV locking, readonly rejection, persistent locks, adoption/repair options, IDM PV list attachment, shared-lock incompatibility, already-held locks, inactive locks on unlock, sanlock lease space refresh, and detailed negative daemon results.

`lockd_lv` decides whether the LV itself owns a lock. Thin volumes and thin pool components use the thin pool lock; VDO volumes use the VDO pool lock; COW snapshots use the origin lock; cache pool/vol internals generally do not own independent locks.

LV creation/removal code allocates or frees locks only for LV types that need them. Thin and VDO creation lock the relevant pool; COW snapshot creation locks the origin; cache pools and thin volumes may not get their own lock args. LV removal queues lock frees until the command has decided to remove all requested LVs.

## Dependencies
Depends on command context lock options, metadata and LV type helpers, activation/deactivation/refresh routines, `lvmcache`, daemon client APIs, lvmlockd client protocol constants, persistent reservation helpers, device path/PV helpers, config values such as local host id and sanlock sizing, and mount table inspection for GFS2/OCFS2 resize exceptions.

## Risk Notes
- Many functions intentionally distinguish "lvmlockd unavailable" from "daemon returned a negative operation result"; collapsing those cases would break local VG fallback and shared VG safety.
- Sanlock uses real on-disk leases in the hidden `lvmlock` LV, so activation, sizing, zeroing, extension, and cleanup order are safety-critical.
- Some shared-lock failures permit read-only progress, but exclusive lock failures must remain strict to protect metadata and orphan PV state.
- `cmd->lockopt` flags such as `skipgl`, `skipvg`, `skiplv`, adopt, repair, `shupdate`, and `norefresh` deliberately weaken or alter default locking behavior and must be audited carefully in new call paths.
- Thin, VDO, cache, COW, mirror, and RAID LVs often use indirect or no LV locks; assuming every LV has independent `lock_args` is incorrect.
- VG removal and rename require other hosts to have stopped the lockspace; sanlock global lock removal can leave the command unable to safely remove later VGs.
