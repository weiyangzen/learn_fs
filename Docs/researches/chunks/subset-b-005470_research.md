# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd.c lines 9438-11498

## Scope

This chunk covers the tail of the generic UFS host controller core. It starts with asynchronous device scanning after initial link bring-up and continues through the SCSI host template, regulator and clock helpers, HBA power-up/power-down, WLUN power-management state transitions, exported system/runtime PM callbacks, shutdown/remove, host allocation and initialization, suspend-prepare helpers, the UFS device WLUN SCSI driver, compile-time UPIU/request-header layout checks, and module init/exit.

The immediately preceding code defines `ufshcd_probe_hba()`, which this chunk calls from `ufshcd_async_scan()`. That prelude matters because async scan repeats/finishes device probing by setting active ICC level, configuring WriteBooster, writing exception-event control, and configuring auto-hibern8 before logical units are added.

## Purpose

The code in this range ties the lower-level UFS transport, UIC, memory, interrupt, and device-management routines into the Linux SCSI, block-mq, regulator, clock, runtime PM, system sleep, sysfs, debugfs, and module-driver frameworks.

The main responsibilities are:

- Publish the `scsi_host_template` used by `scsi_host_alloc()` so normal I/O, reserved commands, polling, queue mapping, SCSI device setup, queue-depth changes, and error handlers enter the UFS core.
- Bring an HBA from platform-provided `struct device`, MMIO base, and IRQ into an operational SCSI host through `ufshcd_alloc_host()` and `ufshcd_init()`.
- Manage UFS device rails (`vcc`, `vccq`, `vccq2`), host-controller rail (`vdd_hba`), clocks, PM QoS, clock gating/scaling, and vendor-specific callbacks across init, suspend, resume, shutdown, and remove.
- Implement WLUN-centric power transitions, because UFS START STOP UNIT power-mode commands must be sent to the UFS device well-known LUN.
- Register a small SCSI driver for the UFS device WLUN so runtime/system PM callbacks and shutdown/poweroff behavior can be attached to the WLUN device rather than to a normal block disk.
- Provide exported hooks that platform drivers call from their probe/remove/PM glue.

## Important APIs, Types, and Functions

Primary exported entry points in this chunk:

- `ufshcd_get_vreg(struct device *dev, struct ufs_vreg *vreg)` obtains a named regulator with `devm_regulator_get()` and is available to host/platform code.
- `ufshcd_alloc_host(struct device *dev, struct ufs_hba **hba_handle)` allocates a SCSI host with UFS-private storage, initializes baseline HBA fields, and registers a devres action that will `scsi_host_put()` the host.
- `ufshcd_init(struct ufs_hba *hba, void __iomem *mmio_base, unsigned int irq)` is the central core initialization path used by host drivers after allocating/mapping controller resources.
- `ufshcd_remove(struct ufs_hba *hba)` tears down side subsystems, SCSI host registration, interrupts, controller state, clocks, regulators, debugfs, and variant state.
- `ufshcd_system_suspend()`, `ufshcd_system_resume()`, `ufshcd_runtime_suspend()`, and `ufshcd_runtime_resume()` are exported controller-level PM callbacks.
- `ufshcd_system_freeze()`, `ufshcd_system_thaw()`, and `ufshcd_system_restore()` adapt system sleep for hibernation and restore. Restore rewrites UTRL/UTMRL DMA base registers before new commands can be queued.
- `__ufshcd_suspend_prepare()` and `ufshcd_suspend_prepare()` bridge SCSI system-suspend assumptions with UFS runtime/system PM differences.
- `ufshcd_resume_complete()` releases the runtime-PM reference taken during suspend preparation.

Important local functions:

- `ufshcd_async_scan()` serializes with `host_sem`, calls `ufshcd_probe_hba(hba, true)`, records probe result timing, adds logical units with `ufshcd_add_lus()`, and drops the runtime-PM hold taken by `ufshcd_init()`.
- `ufshcd_eh_timed_out()` normally lets SCSI EH handle timeouts, but during system suspend it performs link recovery directly for the START STOP UNIT timeout case to avoid a deadlock with `ufshcd_err_handler()`.
- `ufshcd_config_vreg_load()`, `ufshcd_enable_vreg()`, `ufshcd_disable_vreg()`, `ufshcd_setup_vreg()`, and `ufshcd_setup_hba_vreg()` implement regulator load/current programming and enable state tracking.
- `ufshcd_init_clocks()` and `ufshcd_setup_clocks()` acquire, rate-program, enable, disable, trace, and notify variant code about clocks.
- `ufshcd_hba_init()` powers and initializes the host-controller side: host regulator, clocks, device regulators, variant init, debugfs, fault injection, and `hba->is_powered`.
- `ufshcd_hba_exit()` reverses powered initialization and releases debug/sysfs/device-descriptor state.
- `ufshcd_execute_start_stop()` and `ufshcd_set_dev_pwr_mode()` send the SCSI START STOP UNIT command to the UFS device WLUN and update `hba->curr_dev_pwr_mode` on success.
- `ufshcd_link_state_transition()` moves the link to Hibern8 or OFF, with auto-BKOPS awareness for link-off transitions.
- `__ufshcd_wl_suspend()` and `__ufshcd_wl_resume()` are the core WLUN PM state machines for runtime PM, system PM, and shutdown.
- `ufshcd_suspend()` and `ufshcd_resume()` manage the controller-level resources around the WLUN/device/link transitions: IRQs, clocks, regulators, HBA rail, and PM QoS.
- `ufshcd_wl_probe()`, `ufshcd_wl_remove()`, `ufshcd_wl_shutdown()`, and `ufshcd_wl_poweroff()` are the UFS device WLUN SCSI-driver hooks.
- `ufshcd_add_scsi_host()` registers the SCSI host and creates the block-mq tag set/queue used to allocate task-management request tags.
- `ufshcd_check_header_layout()` uses `BUILD_BUG_ON()` assertions to verify bitfield and endian layout of request descriptor and UPIU headers at compile time.

Key types and state containers:

- `struct ufs_hba` is the per-controller state object stored in SCSI host private data. This chunk initializes and mutates fields including `host`, `dev`, `mmio_base`, `irq`, `vps`, `rpm_lvl`, `spm_lvl`, `vcc_off_delay_us`, `is_powered`, `is_irq_enabled`, `scsi_host_added`, `ufshcd_state`, `curr_dev_pwr_mode`, `uic_link_state`, `pm_op_in_progress`, `system_suspending`, `is_sys_suspended`, `complete_put`, `shutting_down`, `dme_qos_sysfs_handle`, `tmf_tag_set`, `tmf_queue`, `tmf_rqs`, and delayed/workqueue objects.
- `struct ufs_vreg` and `struct ufs_vreg_info` describe host/device regulators, current limits, `enabled`, and `always_on` behavior.
- `struct ufs_clk_info` entries in `hba->clk_list_head` hold clock names, handles, rate limits, `enabled`, current frequency, and `keep_link_active` behavior.
- `struct ufs_hba_variant_params ufs_hba_vps` provides default host-enable delay, WriteBooster flush threshold, devfreq polling and callbacks, and simple-ondemand thresholds.
- `struct scsi_host_template ufshcd_driver_template` is the SCSI integration contract for the UFS core.
- `enum ufs_pm_level`, `enum ufs_dev_pwr_mode`, `enum uic_link_state`, and `enum ufs_pm_op` drive PM policy. Defaults set runtime and system PM to device sleep plus link Hibern8.

## Control Flow

Initialization has two stages. Platform glue first calls `ufshcd_alloc_host()`, which creates a SCSI host using `ufshcd_driver_template`, stores `struct ufs_hba` in host private data, initializes the clock list and outstanding lock, sets default reference-clock and NOP timeout values, and returns the HBA pointer. The later `ufshcd_init()` call stores `hba` in `dev_set_drvdata()`, validates MMIO, records MMIO/IRQ/default variant params, initializes PM defaults and locks, and calls `ufshcd_hba_init()` to power resources.

`ufshcd_hba_init()` sequences resources carefully: get/enable HBA regulator, get/rate/set clocks, parse reference-clock frequency, enable clocks, get/enable UFS device regulators, call variant init, initialize debugfs/fault injection, then mark `is_powered`. Failure unwinds in reverse by disabling device rails, clocks, and HBA rail.

After HBA power-up, `ufshcd_init()` reads capabilities/version/interrupt mask, sets the DMA mask, allocates and configures host memory, sets SCSI host limits, creates error/exception work, initializes semaphores/mutexes and clock gating/scaling, clears and disables interrupts, registers the threaded IRQ, resets the attached device, initializes crypto, enables the controller, creates delayed work, configures a default auto-hibern8 idle timer, and calls `ufshcd_add_scsi_host()`. It then holds a runtime-PM reference, assumes the boot firmware left the device active, performs link startup and device initialization work inline, publishes sysfs nodes, grabs the DME QoS sysfs dirent, schedules `ufshcd_async_scan()`, enables async suspend, and initializes PM QoS.

The asynchronous scan finishes the device side under `hba->host_sem`. It calls `ufshcd_probe_hba(hba, true)`, processes the result, adds logical units if probing succeeds, and always releases the runtime-PM hold from init with `pm_runtime_put_sync()`. This split means `ufshcd_init()` can return after the SCSI host and early device state are ready while LUN discovery continues asynchronously.

WLUN suspend starts in `ufshcd_wl_runtime_suspend()` or `ufshcd_wl_suspend()`, both calling `__ufshcd_wl_suspend()` with the relevant PM operation. `__ufshcd_wl_suspend()` derives requested device/link states from `rpm_lvl` or `spm_lvl`, or forces device powerdown plus link off for shutdown. It holds the UFS host, marks clock gating suspended, suspends clock scaling, checks whether the requested state is already current, ensures the current state is active before deeper transitions, handles BKOPS and WriteBooster flush policy, flushes exception work, invokes vendor PRE_CHANGE suspend, sends START STOP UNIT if the device power mode must change, transitions the link to Hibern8 or OFF, invokes vendor POST_CHANGE suspend, and schedules RPM flush recheck work if needed. Error paths try to restore link and device active state, re-enable scaling, update event history, clear the gating suspension, and release the host reference.

WLUN resume in `__ufshcd_wl_resume()` mirrors that flow. It calls vendor resume while clocks are on, exits Hibern8 or performs reset-and-restore if the link was off, sends START STOP UNIT to return to active power mode, updates timestamp/RTC work, restores auto-BKOPS/exception-event state, resumes clock scaling, cancels flush recheck state, configures auto-hibern8, then releases the host and clears PM flags. If resume fails after link work, it attempts to return to the old link state and calls vendor suspend callbacks to keep vendor state consistent.

Controller-level suspend/resume are separate from WLUN device/link PM. `ufshcd_suspend()` disables IRQs, disables clocks, marks clock-gating state off, puts device rails and HBA rail into low-power/off state where allowed, and updates PM QoS. `ufshcd_resume()` restores the HBA rail, device rails, clocks, and IRQs. The exported system and runtime callbacks wrap these helpers and emit tracepoints with elapsed time, current device power mode, and link state.

Shutdown marks `hba->shutting_down`, runtime-resumes the controller, quiesces the WLUN, marks non-WLUN SCSI devices offline, calls shutdown-mode WLUN suspend, and if both device and link are off, suspends the controller resources. Remove performs side-subsystem cleanup, cancels delayed work, destroys TMF block-mq resources, removes the SCSI host, disables interrupts, stops the HBA, and exits powered resources.

Module init checks descriptor/header layouts, initializes UFS debugfs, and registers the UFS device WLUN SCSI driver. Module exit exits debugfs and unregisters that driver.

## State and Persistence Behavior

Most durable driver state in this chunk lives in `struct ufs_hba` and survives across I/O until remove or device-managed resource cleanup. `ufshcd_alloc_host()` stores it as SCSI host private data, while `ufshcd_init()` also stores it in `dev_set_drvdata()` for PM, sysfs, devfreq, hwmon, and other callbacks.

Power state is represented in several layers:

- `hba->is_powered` gates HBA exit/suspend/resume and records whether regulators/clocks/variant state were successfully initialized.
- `hba->curr_dev_pwr_mode` is changed only after START STOP UNIT succeeds.
- `hba->uic_link_state` is changed through helpers such as `ufshcd_set_link_active()`, `ufshcd_set_link_hibern8()`, and `ufshcd_set_link_off()` after UIC/controller operations.
- `hba->rpm_lvl` and `hba->spm_lvl` persist the runtime and system PM policy, defaulting to sleep plus Hibern8 but overridable by variant init or sysfs/host logic elsewhere.
- `hba->dev_info.b_rpm_dev_flush_capable` persists a runtime-suspend condition where device power must remain active for auto-BKOPS or WriteBooster flush during Hibern8, and is later cleared on resume or suspend failure.
- `hba->clk_gating.is_suspended` and `hba->clk_gating.state` coordinate clock gating with WLUN/controller PM.
- `hba->system_suspending`, `hba->is_sys_suspended`, `hba->pm_op_in_progress`, `hba->complete_put`, and `hba->shutting_down` coordinate PM, SCSI EH timeout behavior, suspend-prepare runtime-PM references, and shutdown.

Regulator state is partly cached in `struct ufs_vreg.enabled`; disable skips regulators that are unset, already disabled, or `always_on`. Low-power regulator load programming may persist across suspend until restored by `ufshcd_vreg_set_hpm()`. Clock state is cached in each `struct ufs_clk_info.enabled` and `curr_freq`.

The TMF queue and tag set created by `ufshcd_add_scsi_host()` persist until `ufshcd_remove()`. Sysfs nodes and `dme_qos_sysfs_handle` persist after successful init and are released by `ufshcd_hba_exit()`. The delayed RTC and RPM flush-recheck works persist in the HBA and are scheduled/cancelled by PM flows.

Hardware persistence includes UTRL/UTMRL DMA base registers, interrupt-enable/status registers, controller run/stop/reset state, link state, auto-hibern8 timer, regulator voltages/current loads, clocks/rates, and device power mode. `ufshcd_system_restore()` explicitly rewrites transfer and task request-list DMA base registers after hibernation restore.

## Dependencies and Integration Points

This chunk depends heavily on Linux kernel subsystems:

- SCSI midlayer: `scsi_host_alloc()`, `scsi_add_host()`, `scsi_remove_host()`, `scsi_execute_cmd()`, SCSI device state, EH callbacks, host templates, WLUN drivers, and timeout handling.
- Block-mq: reserved command support and the TMF `blk_mq_tag_set`/queue.
- Runtime PM and system sleep: controller device PM callbacks, WLUN `dev_pm_ops`, autosuspend delay, `pm_runtime_*()` interactions, and suspend-prepare/resume-complete sequencing.
- Regulator framework: `devm_regulator_get()`, `regulator_set_load()`, `regulator_enable()`, `regulator_disable()`, and voltage-count checks.
- Common clock and OPP frameworks: `devm_clk_get()`, `clk_set_rate()`, `clk_prepare_enable()`, `clk_disable_unprepare()`, OPP max-rate setup, and clock scaling/gating.
- IRQ and MMIO: `devm_request_threaded_irq()`, top-half/threaded interrupt handlers, interrupt register clearing, and UFSHCI register writes/reads.
- DMA API: coherent DMA mask selection based on controller capabilities or variant override.
- Sysfs/debugfs/fault injection/hwmon/bsg/rpmb/crypto/devfreq/tracepoints, which are initialized or removed through helper calls from other UFS core files.

Variant integration is through `hba->vops`: init/exit, clock setup pre/post callbacks, PM suspend/resume callbacks, DMA-mask override, and many lower-level hooks invoked by helpers called from this chunk. Host-controller platform drivers are responsible for populating `hba->vops`, clock/regulator lists, quirks/caps, OPP settings, and resource mappings before or during `ufshcd_init()`.

Device integration is through UFS descriptors, WLUN discovery, START STOP UNIT power commands, BKOPS, WriteBooster, exception events, RTC timestamp attributes, auto-hibern8, and UIC link commands implemented elsewhere in `ufshcd.c`.

## Risks

- `ufshcd_init()` has a large, ordered bring-up sequence. Moving callbacks before `dev_set_drvdata()`, enabling IRQs before status is cleared, enabling clocks/regulators in the wrong order, or scheduling async scan before the runtime-PM hold can create hard-to-reproduce probe races.
- `ufshcd_setup_clocks()` sets `clki->enabled = on` even for clocks skipped because `keep_link_active` is true while the link is active. Changes in this area must preserve the intended cache semantics or clock gating may disable a clock still required for link state.
- The clock error path disables every clock with `clki->enabled` but does not reset all cached flags in that loop. Follow-on code relies on higher-level unwinding and should be audited if error handling changes.
- `ufshcd_set_dev_pwr_mode()` temporarily sets `host->eh_noresume` and relies on always reaching the cleanup path after `scsi_device_get()`. Any new exit path must restore `eh_noresume` and put the SCSI device.
- During system suspend, `ufshcd_eh_timed_out()` bypasses normal SCSI EH for the START STOP UNIT timeout case. Incorrect `system_suspending` handling can either deadlock PM/EH or skip needed recovery.
- Runtime suspend must not return a raw device-command error in paths where I/O would hang; several failures intentionally force error recovery and convert to `-EBUSY`. Simplifying those paths can regress recovery.
- Auto-BKOPS and WriteBooster flush policy prevents powering down VCC or turning the link off in some runtime-suspend states. Ignoring `b_rpm_dev_flush_capable`, `auto_bkops_enabled`, or DeepSleep exceptions can lose data-integrity or performance guarantees.
- DeepSleep exit requires device reset and host reset/restore with link off. Treating DeepSleep like ordinary Hibern8 can leave the device unreachable.
- Shutdown marks non-WLUN devices offline and then powers down through WLUN suspend. Partial failures are not strongly reported in `ufshcd_wl_shutdown()`, so ordering changes need careful platform shutdown tests.
- `ufshcd_remove()` destroys `tmf_queue` unconditionally after init-time creation. If future code permits partial initialization past `ufshcd_add_scsi_host()` failure or calls remove on an earlier failure path, null/ERR handling may need hardening.
- `ufshcd_add_scsi_host()` falls back from MCQ to SDB and globally sets `use_mcq_mode = false` on MCQ allocation failure. This module-parameter side effect can affect later controllers.
- Header layout checks are skipped for GCC before version 10. ABI-sensitive bitfield layout still depends on compiler and structure definitions, so layout drift can break hardware commands at compile time or, on skipped compilers, at runtime.
- `ufshcd_system_restore()` must rewrite the request-list base registers after resume. Missing the readback barrier or queue-address update can allow new commands against stale DMA addresses.

## Test and Validation Signals

Useful validation for this chunk includes:

- Build coverage for `drivers/ufs/core/ufshcd.c` with `CONFIG_PM`, `CONFIG_PM_SLEEP`, MCQ, crypto, hwmon, debugfs, fault injection, and multiple compiler versions so PM-gated and layout-check code is covered.
- Probe tests on at least one legacy/SDB controller and one MCQ-capable controller, verifying `ufshcd_alloc_host()`, `ufshcd_init()`, async scan, LUN discovery, sysfs node creation, debugfs initialization, IRQ handling, and PM QoS initialization.
- Fault-injection or mocked-platform tests for each init failure step: HBA regulator get/enable, clock get/rate/enable, device regulator get/enable, variant init, DMA mask, memory allocation, IRQ request, controller enable, SCSI host add, TMF tag-set/queue allocation, link startup, NOP OUT, device init, descriptor/device-parameter init, and post-device init.
- Runtime PM tests that exercise active, Hibern8, link-off, and DeepSleep policies; verify tracepoints show expected device power mode and link state, and confirm clocks/regulators/IRQs are toggled in the right order.
- System suspend/resume and hibernation freeze/thaw/restore tests, including the case where the WLUN is already runtime suspended in the same state as system PM and the case where it must be runtime-resumed first.
- START STOP UNIT failure and timeout tests during system suspend to confirm `ufshcd_eh_timed_out()` avoids deadlock and event histories record suspend/resume errors.
- BKOPS and WriteBooster tests where runtime suspend keeps the device active for flush/background work and schedules/cancels `rpm_dev_flush_recheck_work`.
- Shutdown and poweroff tests that verify SCSI devices are quiesced/offlined, WLUN suspend runs with `UFS_SHUTDOWN_PM`, and controller resources are disabled only after device/link powerdown.
- Remove/unbind tests that confirm hwmon, bsg, rpmb, sysfs, RTC work, TMF queue/tag set, SCSI host, interrupts, clocks, regulators, debugfs, and variant state are all released without leaks or use-after-free.
- DMA-mask tests on controllers with and without `MASK_64_ADDRESSING_SUPPORT`, and variants that override `set_dma_mask()`.
- Compile-time or static assertions for request descriptor and UPIU header layout, plus runtime smoke tests that issue SCSI commands, task-management commands, query requests, and raw UPIU paths after any structure-layout change.
