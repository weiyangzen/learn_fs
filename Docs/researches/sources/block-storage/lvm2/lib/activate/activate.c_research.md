# File Research: sources/block-storage/lvm2/lib/activate/activate.c

## Role

`activate.c` is the high-level activation facade for LVM logical volumes. It exposes the API declared in `activate.h`, gates behavior on activation settings and configuration filters, delegates real device-mapper work to `dev_manager.c`, coordinates critical sections and udev cookie synchronization, and manages dmeventd monitoring.

## Major Responsibilities

- Module discovery: recursively collects device-mapper target module names needed by LV segments, origins, snapshots, and LV areas through `list_segment_modules()` and `list_lv_modules()`.
- Activation filters: evaluates `activation/volume_list`, `activation/auto_activation_volume_list`, and `activation/read_only_volume_list`, supporting `vg`, `vg/lv`, exact tags, and host-tag wildcard matching.
- Devmapper availability: when `DEVMAPPER_SUPPORT` is absent, provides stub functions that either no-op successfully for workflow functions or return inactive/unsupported status for query functions.
- Driver and target probing: wraps libdevmapper library/driver version calls, target version queries, sysfs module detection, `modules.builtin` scanning, and optional `modprobe`.
- LV info and status: resolves active DM devices, including layered forms such as `-real`, `-tpool`, `-vpool`, cache pool users, snapshot merge state, VDO pool status, and combined `lv_info_with_seg_status()` status extraction.
- Activation lifecycle: implements suspend, resume, activate, deactivate, preload, temporary activation, and convenience wrappers over committed metadata.
- Use checks: verifies open counts, sysfs holders, mounted filesystems, active components, active holders, and active sub-LVs before destructive operations.
- Event monitoring: recursively registers/unregisters dmeventd monitoring for snapshots, mirrors, pools, external origins, metadata LVs, AREA_LV dependencies, and segment types that implement monitor hooks.

## Key Public Entry Points

- `set_activation()` / `activation()` control whether device-mapper interactions are attempted.
- `library_version()`, `driver_version()`, `target_version()`, `target_present_version()`, `target_present()`, and `module_present()` expose kernel/libdm capability checks.
- `lv_info()`, `lv_info_with_name_check()`, and `lv_info_with_seg_status()` are status-query APIs used by commands and reports.
- `lv_snapshot_status()`, `lv_raid_status()`, `lv_cache_status()`, `lv_thin_status()`, `lv_thin_pool_status()`, `lv_vdo_pool_status()`, and related percent/message helpers return target-specific runtime state.
- `lv_suspend_if_active()`, `lv_resume()`, `lv_resume_if_active()`, `lv_activate()`, `lv_activate_with_filter()`, `lv_deactivate()`, `lv_mknodes()`, and wrapper forms such as `activate_lv()` and `deactivate_lv()` drive LV lifecycle changes.
- `lv_component_is_active()`, `lv_holder_is_active()`, and `deactivate_lv_with_sub_lv()` protect stacked component relationships.

## Core Flow

Activation first applies filters and partial/degraded activation rules, rejects unknown or invalid RAID-visible sub-LV states, calculates read-ahead, creates a udev cookie, enters a critical section, and calls `dev_manager_activate()`. On success it registers event monitoring. Deactivation performs in-use checks for visible/virtual/merging LVs, unmonitors, enters a critical section, calls `dev_manager_deactivate()`, removes temporary missing RAID subdevices, and verifies that the public device disappeared.

Suspend is more complex because it may preload tables from precommitted metadata before suspending. It handles pvmove removal, detached hidden-to-visible LVs, removed snapshots, flush requirements, dmeventd unmonitoring, filesystem locking for snapshot and thin conversion cases, and critical-section management. Resume reactivates loaded tables, decrements the critical section, and restores monitoring.

## Special-Case Handling

- New thin pools may require querying the `-tpool` layer while reporting the public pool as inactive if only the layer exists.
- VDO volumes query the public VDO LV for info but the VDO pool layer for pool status.
- Snapshot origins and COW volumes redirect status queries depending on merge state.
- Visible LVs that still have private `-real` UUID devices can be detected through `_lv_info_real()` to handle historical RAID/mirror transitions.
- RAID messages are deliberately restricted at the high-level API to user-facing `check` and `repair` transitions from `idle`, even though the lower layer supports more dm-raid messages.

## Dependencies

This file depends on metadata helpers for LV classification and traversal, config-tree readers, locking/critical-section helpers, dmeventd APIs under `DMEVENTD`, libdevmapper task APIs, `dev_manager.h` for all device-tree work, and `fs.h` for udev cookie and node synchronization.

## Risks and Invariants

- Activation functions assume VG locks and committed/precommitted metadata are coherent; many internal failures are logged as `INTERNAL_ERROR`.
- Open-count checks must synchronize pending non-delete fs operations before trusting counts.
- Critical sections must be balanced around suspend/resume and activate/deactivate; `activation_release()` warns if activation is released while still in a critical section.
- Event monitoring recursion must avoid inappropriate unmonitoring of shared thin pools and must preserve snapshot-origin semantics.
- Without devmapper support, success-returning lifecycle stubs can let higher-level command logic proceed while no real kernel device work happens; callers rely on `activation()` and query results to distinguish that mode.
