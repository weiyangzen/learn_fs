# File Research: sources/block-storage/lvm2/tools/polldaemon.c

## Purpose

`polldaemon.c` implements LVM2's generic polling engine for long-running LV copy operations, especially `pvmove` and mirror/lvconvert-style synchronization. It supports both the older in-process/background polling model and the `lvmpolld` daemon-backed model.

## Main Responsibilities

- Poll mirror copy progress through `poll_mirror_progress()`.
- Re-read VG metadata safely while a long-running copy is in progress.
- Finish or advance copy segments through operation-specific `poll_functions`.
- Support abort handling through `finish_copy`.
- Support polling a single operation by `poll_operation_id` or scanning all VGs for matching in-progress operations.
- Fork a background poller for classic polling when requested.
- Delegate polling to `lvmpolld` when compiled and enabled.

## Key Entry Points

- `poll_daemon()`: public entry point. Initializes `daemon_parms`, chooses `lvmpolld` vs classic polling, and narrows classic mode to `PVMOVE`.
- `wait_for_single_lv()`: repeatedly reads and locks the target VG/LV, checks progress, handles inactive/missing LV cases, and invokes finish/update callbacks.
- `poll_mirror_progress()`: mirror progress callback using `lv_mirror_percent()` for segment status and `copy_percent()` for overall progress.

## Classic Polling Flow

- `_poll_daemon()` optionally daemonizes with `become_daemon()`.
- It clears stale cache/label-scan state inherited from the parent.
- For a specific operation, it calls `wait_for_single_lv()`.
- For all operations, it uses `process_each_vg()` and `_poll_vg()`.
- `_poll_vg()` first collects stable copied `poll_operation_id` records, then checks each matching LV. This avoids mutating the VG list while iterating it.
- `_poll_for_all_vgs()` repeats VG scans until no outstanding pollable operations remain.

## `lvmpolld` Flow

When `LVMPOLLD_SUPPORT` is enabled and `lvmpolld_use()` is true:

- `_lvmpoll_daemon()` dispatches to daemon-backed polling.
- `_lvmpoll_daemon_id()` initializes one daemon poll request and optionally waits in foreground.
- `_lvmpolld_poll_for_all_vgs()` initializes daemon polling for all matching LVs and tracks foreground completion with `lvmpolld_request_info()`.
- `_report_progress()` reads VG metadata and calls the operation progress callback without taking a VG lock, relying on same-host operation locality.

## Locking and Metadata Safety

- `wait_for_single_lv()` uses `lockd_vg(..., "ex")` for lockd VGs because completion can write metadata.
- VG reads that may finish a copy use `READ_FOR_UPDATE`.
- The first successful LV lookup captures the LVID if no UUID was supplied, preventing stale pollers from acting on a newly-created LV with the same name.
- Missing VG/LV is generally treated as completed or no longer active rather than fatal, depending on the case.
- Inactive LVs stop polling because kernel status cannot be queried.

## Timing and Interrupt Handling

- `_nanosleep()` allows SIGINT during sleep and returns false if interrupted.
- Zero interval sleeps still wait at least `WAIT_AT_LEAST_NANOSECS` unless explicitly allowed.
- `_sleep_and_rescan_devices()` drops stale cache and label-scan state before sleeping and rescans after wakeup.

## Extension Points

The behavior is parameterized by `struct poll_functions`:

- `get_copy_name_from_lv`
- `poll_progress`
- `update_metadata`
- `finish_copy`

This lets `pvmove` plug in its own metadata progression and finish behavior while reusing the polling engine.

## Notable Edge Cases

- `CONVERTING` is excluded from some LV type filters because it can be derived at import rather than persisted on disk.
- Background classic poller children call `_exit(lvm_return_code(ret))` and must not return to the caller path.
- `parms->devicesfile` is copied for `lvmpolld`; overly long names are rejected.
- Abort mode sets polling interval to zero for daemon-backed polling.
