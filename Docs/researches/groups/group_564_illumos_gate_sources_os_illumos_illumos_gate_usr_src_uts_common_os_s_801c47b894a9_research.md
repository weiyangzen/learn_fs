# Group Research: group_564_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_s_801c47b894a9

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunpm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunpm.c

## Overview

`sunpm.c` is the illumos kernel-resident power management framework implementation. It implements device power-management policy for `dev_info_t` nodes, including automatic idle scanning, direct `/dev/pm`-controlled power management, platform power manager integration, dependency handling, console framebuffer protection, CPR suspend/resume interactions, and no-involuntary-power-cycle accounting.

The file was read completely: 9,350 lines.

This source sits in the OS/kernel lane of subset A. Its filesystem/storage relevance is indirect but important: it participates in attach/detach/probe/configure flows for all device nodes, keeps parents powered while children are active, prevents unsafe power removal from protected devices, and includes disk power-cycle policy logic via `pm_trans_check()`.

## Major Responsibilities

- Initializes PM global locks, callback hooks, and the dependency worker thread.
- Parses device PM properties such as `pm-components`, `pm-hardware-state`, `pm-class`, `pm-want-child-notification?`, and `no-involuntary-power-cycles`.
- Creates, destroys, and manages per-device PM component state.
- Maintains current and normal power levels, per-component thresholds, busy/idle timestamps, and scan scheduling.
- Implements driver-facing APIs including `pm_raise_power()`, `pm_lower_power()`, `pm_power_has_changed()`, `pm_busy_component()`, `pm_idle_component()`, `pm_create_components()`, and `pm_destroy_components()`.
- Routes power transitions through platform power managers (`PPM`) using `DDI_CTLOPS_POWER`, with a default handler when no PPM claims a node.
- Enforces implicit parent-child power dependencies and explicit “keeps up / kept up” dependencies from power policy.
- Coordinates direct PM with user processes through watcher queues, poll wakeups, and rendezvous blocking.
- Tracks `no-involuntary-power-cycles` devices across detach/reattach and driver removal.
- Protects console framebuffer availability before PROM/debug output.
- Integrates with CPR, panic, halt, modunload, devfs attach/probe/detach, MDI, and AutoS3.

## Core State And Locking

The file opens with an extensive lock-ordering comment that is essential to understanding the implementation. Important locks include:

- `pm_scan_lock`: protects scan scheduling enablement, `autopm_enabled`, and `cpupm`.
- `pm_clone_lock`: protects `/dev/pm` clone poll/event state.
- `pm_rsvp_lock`: protects direct-PM rendezvous state and blocked requests.
- `ppm_lock`: protects registered platform power manager callbacks.
- `pm_compcnt_lock`: protects `pm_comps_notlowest`, the global count of components above lowest power.
- `pm_dep_thread_lock`: protects the dependency worker queue.
- `pm_noinvol_rwlock` and `pm_remdrv_lock`: protect detached no-involuntary-power-cycle records.
- `pm_cfb_lock`: high-level spin lock for console framebuffer state.
- Per-dip `devi_pm_lock`, power lock via `ndi_devi_enter()`, and `devi_pm_busy_lock`.

The code is highly lock-sensitive. Many functions assert that PM dip locks or power locks are or are not held, and several paths deliberately drop locks before blocking or calling into drivers.

## Initialization And CPR

`pm_init_locks()` initializes global PM locks and condition variables before devices attach. `pm_init()` initializes thresholds and counters, registers CPR/panic/halt callbacks, creates `pm_dep_thread`, and attaches platform PM driver modules from `platform_module_list`.

`pm_cpr_callb()` disables scans during checkpoint, stops scan activity across devices, saves `autopm_enabled` and `cpupm`, and restores them on resume. Resume also calls `pm_reset_timestamps()` so devices are not immediately powered down because of elapsed suspended time.

`pm_save_direct_levels()` and `pm_restore_direct_levels()` preserve directly managed device power levels while user processes are stopped for CPR. Direct-PM waiters are released so drivers do not hang while their controlling processes are unavailable.

## Component Model

The framework supports both old “backwards compatible” devices and modern `pm-components` devices.

Modern devices describe components using a `pm-components` property. `pm_autoconfig()` parses strings of the form `NAME=...` followed by numeric power levels and labels. It validates that each component has at least two monotonically increasing levels and unique component names. It creates component storage with `e_pm_create_components()` and records normal/max power levels.

Backwards-compatible devices can still call `pm_create_components()` during attach. They receive synthetic two-level components using `bc_comp` with `"off"` and `"on"` level names. `pm_set_normal_power()` and `pm_destroy_components()` are retained for old drivers, with debug warnings when modern drivers call obsolete interfaces.

Important helpers:

- `cur_power()` converts stored current power index to the real level value, preserving `PM_LEVEL_UNKNOWN`.
- `e_pm_valid_info()`, `e_pm_valid_comp()`, and `e_pm_valid_power()` validate managed device state, component index, and level.
- `pm_level_to_index()` maps level values to internal indices.
- `e_pm_set_cur_pwr()` updates current level and global not-lowest accounting.
- `pm_get_normal_power()` / `pm_get_current_power()` expose normal/current levels.
- `pm_update_maxpower()` changes normal power and lowers current power if necessary.

## Automatic Scanning

Automatic PM is driven by scan state attached to each managed non-BC device.

`pm_scan_init()` creates or restarts per-device `pm_scan_t`. `pm_scan_fini()` frees it after scans are stopped. `pm_rescan()` either dispatches `pm_scan()` on `system_taskq`, schedules a timeout, or marks `PM_SCAN_AGAIN` if a scan is already running. `pm_scan_stop()` cancels timeout scans and waits for dispatched/running scans to finish.

`pm_scan_dev()` is the policy core for idle power-down. It skips devices that are attaching, not scanable, stopped, held up by children, directly managed, or protected by no-involuntary-power-cycle rules. It snapshots component timestamps, checks busy counts and thresholds, computes the next lower power level, calls `pm_set_power(... PM_LEVEL_DOWNONLY ...)`, and returns the next useful scan interval.

Threshold policy is handled by:

- `pm_set_device_threshold()`: distributes a device threshold across component transitions, with special handling for nexus defaults.
- `cur_threshold()`: gets the effective threshold for a component.
- `pm_next_lower_power()`: picks the next lower level.
- `pm_apply_recorded_thresh()`, `pm_record_thresh()`, `pm_valid_thresh()`, `pm_unrecord_threshold()`, and `pm_discard_thresholds()`: manage thresholds recorded by user policy before devices attach.

CPU PM is represented by `cpupm`, `cpupm_default_mode`, `pm_cpu_idle_threshold`, and CPU-specific scan timing. AutoS3 is triggered from `pm_ppm_notify_all_lowest()` when all managed components reach their lowest levels and `autoS3_enabled` is set.

## Power Transition Flow

The main transition entry point is `pm_set_power()`. It builds a `BUS_POWER_CHILD_PWRCHG` request and routes it either directly to `pm_busop_set_power()` if the caller already holds the needed locks, or from the root through `pm_busop_bus_power()` to walk down the device tree and power ancestors as needed.

`pm_busop_bus_power()` handles:

- `BUS_POWER_CHILD_PWRCHG`: walks from an ancestor to the target, powering intermediate non-notifying parents to normal power and holding them during the child transition.
- `BUS_POWER_NEXUS_PWRUP`: powers nexus components to normal via child-power-change semantics.
- `BUS_POWER_NOINVOL`: walks no-involuntary accounting updates down the tree.

`pm_busop_set_power()` performs the actual checked transition. It handles direct PM blocking, BC component-0 semantics, parent pre/post notifications, parent power holds, scan-time busy/threshold rechecks, console framebuffer powerdown constraints, platform/device power calls, dependency worker dispatch, watcher notifications, and parent hold release.

`power_dev()` invokes the PPM path (`PMR_PPM_SET_POWER`) and handles BC suspend/resume around component 0 transitions. It also clears voluntary no-involuntary accounting when a protected subtree is power-cycled.

`pm_power()` is the default no-PPM implementation. It calls the driver `devo_power()` entry point and updates framework current power on success.

`pm_power_has_changed()` is the reverse path: a driver reports that hardware power changed externally. It validates the level, tries to acquire parent/child power locks, detects a specific deadlock against `pm_set_power()`, updates state through `pm_phc_impl()`, notifies watchers/parents, adjusts parent holds, and schedules rescans. The deadlock path uses `PM_PHC_WHILE_SET_POWER` plus `pmc_phc_pwr` to keep the oldest old level and newest reported level until the set-power path can reconcile state.

## Platform Power Manager Integration

Platform power managers register with `pm_register_ppm()`. The framework stores up to `MAX_PPM_HANDLERS` callbacks and asks them to claim nodes with `pm_ppm_claim()`. Claimed nodes store their PPM dip in `devi_pm_ppm`.

`pm_ctlops()` dispatches `DDI_CTLOPS_POWER` either to a claimed PPM bus control entry point or to `pm_default_ctlops()` when no PPM exists.

The default handler supports:

- `PMR_PPM_SET_POWER`
- attach/detach/probe/resume notifications
- `PMR_PPM_POWER_CHANGE_NOTIFY`
- `PMR_PPM_UNMANAGE`
- power lock, unlock, try-lock, and lock-owner queries

PPMs can also return a device list of related transitions; `pm_enqueue_notify_others()` emits state-change notifications for those auxiliary devices.

## Dependency Handling

The framework models explicit dependencies as keeper/kept relationships. If any component of a keeper is on, the kept device should be brought to normal power and held up. Dependency work is asynchronous through `pm_dep_thread`.

Key structures and functions:

- `pm_dep_head`: list of dependency records.
- `pm_record_keeper()` / `newpdr()`: record device or property dependencies.
- `pm_kept()` and `pm_keeper()`: resolve dependencies when devices attach.
- `pm_apply_recorded_dep()` and `pm_set_keeping()`: apply a resolved dependency.
- `bring_wekeeps_up()` / `bring_pmdep_up()`: power kept devices and hold them.
- `pm_rele_dep()`: releases kept-device holds when a keeper powers off.
- `pm_free_keeps()`, `pm_free_keeper()`, `pm_free_kept()`: detach cleanup.
- `pm_discard_dependencies()`: reset dependency policy.

`pm_dispatch_to_dep_thread()` queues dependency commands. `pm_process_dep_request()` handles power-on, power-off, detach, remove-dependency, direct-PM release bring-up, add-dependent, add-dependent-property, attach, kept/keeper checks, and CPR suspend/resume dependency rebuilds.

## Direct PM And User Notifications

Direct PM allows a user process controlling `/dev/pm` to take ownership of device power. While directly managed, scan and dependencies do not control the device, and driver requests can block until the controlling process acts.

Important pieces:

- `pm_register_watcher()` and `pm_deregister_watcher()` maintain per-clone watcher/control structures.
- `psc_entry()` writes ring-buffer event entries, including overflow/lost-event handling.
- `pm_enqueue_notify()` queues `PSC_PENDING_CHANGE` and `PSC_HAS_CHANGED` events to direct controllers and interest watchers.
- `pm_block()` places a driver request on `pm_blocked_list`, queues a pending-change event, and waits for the controlling process.
- `pm_proceed()` wakes blocked requests on release or matching `PM_SET_CURRENT_POWER`.
- `pm_busop_match_request()` decides whether direct-PM requests succeed immediately, fail, block, or retry after release.
- `pm_psc_clone_to_direct()` and `pm_psc_clone_to_interest()` find pending event buffers for `/dev/pm` readers.

The code carefully avoids blocking when `pm_processes_stopped` is set for CPR.

## No-Involuntary-Power-Cycles

The `no-involuntary-power-cycles` property prevents the framework from powering off devices without active driver participation. The same machinery is used to protect the console framebuffer.

Runtime attached-node checks use `pm_noinvol()`. Detached-node state is stored in `pm_noinvol_head`, with entries holding path, major, flags, no-involuntary descendant count, voluntary-powered-down count, and driver-removed state.

Major flows:

- `e_pm_props()` marks `PMC_NO_INVOL`.
- `pm_record_invol()` records detached protected nodes and updates ancestors.
- `pm_noinvol_specd()` restores no-invol state when a device reattaches.
- `pm_noinvol_update()` walks the tree with `BUS_POWER_NOINVOL`.
- `pm_noinvol_update_node()` adjusts per-node counters for attach, detach, rem_drv, console framebuffer, and power-cycle events.
- `pm_reattach_noinvol()` forces protected detached devices to reattach before CPR so drivers can participate.
- `pm_driver_removed()` / `i_pm_driver_removed()` remove stale no-invol state on `rem_drv`.
- `adjust_ancestors()` and `pm_noinvol_process_ancestors()` repair ancestor counters when detached nodes or drivers disappear.
- `pm_noinvol_detached()` answers whether a detached path still inhibits involuntary power removal.

## Console Framebuffer Handling

The console framebuffer is treated specially because PROM/debug output may require it to be powered before printing.

`pm_cfb_setup()` records whether stdout is a framebuffer, suppresses console PM when kernel debugging is present unless overridden, marks the framebuffer as `PMC_CONSOLE_FB | PMC_NO_INVOL`, or records path-based no-invol entries before the driver attaches.

`pm_cfb_setup_intr()` installs a high-level soft interrupt and registers PROM output callbacks. `pm_cfb_check_and_hold()` increments `cfb_inuse` and tells callers whether power-up is needed. `pm_cfb_powerup()` raises all framebuffer components to normal power. `pm_cfb_check_and_powerup()` combines both. `pm_cfb_trigger()` schedules a soft interrupt to enter the debugger and power up the framebuffer from a safe level; repeated pending triggers panic.

`pm_busop_set_power()` blocks console framebuffer powerdown when PM is disabled for it and waits for `cfb_inuse` to drop before exact downward transitions. `calc_cfb_comps_incr()` and `update_comps_off()` maintain `pm_cfb_comps_off`.

## Attach, Detach, Probe, And Config Hooks

This file is deeply integrated with devfs lifecycle:

- `pm_init_child()` / `pm_uninit_child()` notify PPMs about child node setup/teardown.
- `pm_pre_probe()` / `pm_post_probe()` wrap probe activity.
- `pm_pre_attach()` / `pm_post_attach()` handle attach and resume. Successful attach starts PM via `pm_start()`; failed attach calls `pm_stop()`.
- `pm_pre_detach()` / `pm_post_detach()` stop scanning, power up BC/console devices if needed, notify PPMs, record no-involuntary state, and permanently stop PM on success or resume it on failure.
- `pm_pre_config()` / `pm_post_config()` and `pm_pre_unconfig()` / `pm_post_unconfig()` hold parent power during configuration, with MDI-specific routing for VHCI nodes.
- `pm_detaching()` and `pm_detach_failed()` manage scan suspension/restart across detach attempts.
- `pm_stop()` stops scan state, unmanages PPM state, destroys components, and releases parent holds left from failed PM setup.

`pm_start()` is the attach/start helper: it parses properties, restores no-invol state, manages components, starts scanning if applicable, and if PM setup fails leaves the parent held up through `PMC_NOPMKID`.

## Busy/Idle And Parent Hold Semantics

Drivers use `pm_busy_component()` and `pm_idle_component()` to manage per-component busy counts and timestamps. Busy sets timestamp to zero; idle sets timestamp to current time when the count reaches zero. Idle can trigger rescans during idle-down or for nexus threshold-zero cases.

Parent holds use `pm_hold_power()` and `pm_rele_power()`, wrappers around `e_pm_hold_rele_power()`, which updates `devi_pm_kidsupcnt`. A nonzero kids-up count prevents scanning from powering down a node. Parent holds are used for child power changes, dependency holds, configuration/probe safety, and implicit parent-child power invariants.

## Disk Power-Cycle Policy

`pm_trans_check()` advises whether a power-off transition should occur based on device-reported cycle budget data.

For SCSI cycle data, it distributes lifetime cycles over five years using a 30/25/20/15/10 percent schedule, computes expected cycles by service date and current time, and returns either advised, delayed with an interval, or error. For SMART data, it compares consumed and allowed cycles. This is the most directly storage-specific logic in the file.

## Debug And Diagnostics

Under `DEBUG`, the file includes:

- `pm_debug` flags and diverted debug output to avoid waking/powering the console framebuffer.
- `pm_log()` circular-buffer logging, optional x86 serial output, and PROM output control.
- `prdeps()` and `pr_noinvol()` structure dumps.
- `pm_desc_pwrchk_walk()` validation that descendants are not powered while an ancestor is powering off.
- x86 low-level serial helpers `pm_getchar()`, `pm_putchar()`, and `pm_printf()`.

## Key External Interfaces

Driver/framework APIs implemented here include:

- `pm_raise_power()`
- `pm_lower_power()`
- `pm_power_has_changed()`
- `pm_busy_component()`
- `pm_idle_component()`
- `pm_get_current_power()`
- `pm_get_normal_power()`
- `pm_update_maxpower()`
- `pm_create_components()`
- `pm_destroy_components()`
- `pm_set_normal_power()`
- `pm_powerup()`
- `ddi_dev_is_needed()`
- `ddi_power()`
- `ddi_removing_power()`
- `e_ddi_suspend()`
- `e_ddi_resume()`
- `e_pm_manage()`
- `e_pm_props()`
- `e_new_pm_props()`

Framework/lifecycle APIs include the `pm_pre_*` and `pm_post_*` attach/probe/detach/config functions, PPM registration/claiming/control functions, watcher registration functions, dependency and threshold record functions, CPR direct-level save/restore functions, and console framebuffer helpers.

## Risks And Maintenance Notes

- The file depends on strict lock ordering and contains multiple paths that call drivers or PPMs while coordinating per-dip and parent locks. Any modification needs lock-order review.
- `pm_power_has_changed()` has explicit deadlock detection against `pm_set_power()`; changes around `PM_PHC_WHILE_SET_POWER`, `pmc_phc_pwr`, or power-lock owner queries are high risk.
- Direct PM paths bridge kernel requests to user-space controllers. Event queue overflow, clone cleanup, and CPR process-stopped behavior are important edge cases.
- Dependency and no-involuntary state use path strings and linear lists. Correct attach/detach/rem_drv accounting depends on exact path matching and ancestor counter updates.
- Console framebuffer paths run at unusual interrupt/debug boundaries. `pm_cfb_lock` is a high-level spin lock, and power-up is deferred to soft interrupt when necessary.
- Threshold and dependency records may be created before target devices attach, so attach-time replay must remain consistent.
- Backwards-compatible PM support still exists and has special component-0 suspend/resume behavior, even though modern `pm-components` devices dominate.

## Mental Model

At a high level, `sunpm.c` keeps a device tree power invariant: children and explicit kept devices should not require power from ancestors or dependencies that the framework has allowed to power off. Automatic scans opportunistically lower idle components. Driver calls and user direct-PM calls can raise or lower power explicitly. Every transition is routed through the bus-power walk so ancestors, PPMs, direct controllers, dependencies, no-involuntary rules, and watchers all get a chance to participate.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunpm.c -->