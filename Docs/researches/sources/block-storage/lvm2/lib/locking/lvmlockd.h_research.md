# File Research: sources/block-storage/lvm2/lib/locking/lvmlockd.h

## Purpose
Declares the public command-side lvmlockd integration API, lock state/result/option flags, lockd LV operation flags, and stub implementations used when LVM is built without lvmlockd support.

## Main Contents
- Defines `struct lockd_state`, carrying lock result flags and generation data from VG locking into later VG read validation.
- Defines the sanlock internal LV name `lvmlock`.
- Defines LV lock flags such as no-shared-mode, persistent lock, shared-exists-ok, and thin/snapshot creation context bits.
- Defines result flags reported by lvmlockd, including missing lockspaces, missing global lockspace, duplicate global lockspaces, missing lock manager, existing shared locks, and unknown host state.
- Defines lock state failure flags used by VG lock callers.
- Defines `--lockopt` flags for force, shupdate, norefresh, skip global/VG/LV, auto/nowait, adopt, nodelay, and repair variants.
- Declares APIs for lvmlockd connection management, VG init/free/start/stop/status, global/VG/LV locks, LV creation/removal lock handling, VG rename, running lock manager discovery, LV refresh, LV lock query, lock option parsing, and sanlock lock-args changes.
- Provides inline no-op or failure stubs when `LVMLOCKD_SUPPORT` is disabled.

## Dependencies
Includes LVM logging, daemon client utilities, and lvmlockd protocol client definitions. It forward-declares `lvresize_params` and `lvcreate_params`.

## Risk Notes
The stub behavior is part of the build-time contract: local VG operations usually become no-ops without lvmlockd, while creating or using shared lock types must fail. Callers should not assume lvmlockd functions always perform locking.
