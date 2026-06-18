# sources/distributed-fs/ceph-client/drivers/ufs/core/ufshcd.c lines 1-9437

## Scope

This chunk covers the main body of the Linux UFS host-controller core driver from the file header through `ufshcd_probe_hba()`. It includes controller register helpers, UIC/DME command plumbing, SCSI command submission and completion, device-management query/NOP/raw-UPIU paths, link startup and power-mode changes, clock gating/scaling, exception handling, error recovery, task-management functions, descriptor probing, WriteBooster and BKOPS policy, MCQ setup, and the first-stage HBA/device probe sequence. The chunk ends immediately after `ufshcd_probe_hba()` and before the `ufshcd_async_scan()` implementation continues in the next range.

## Purpose

`ufshcd.c` is the transport/core layer that turns a platform-specific UFS host into a SCSI host. In this range it:

- Initializes UFSHCI controller state and DMA descriptor memory.
- Issues UniPro/UIC commands for link startup, DME attribute access, Hibern8, and power-mode changes.
- Presents UFS logical units and well-known LUNs through the SCSI midlayer.
- Converts SCSI requests, query requests, NOPs, raw UPIUs, RPMB operations, and task-management functions into UFS transfer or task request descriptors.
- Handles interrupts, completions, polling, OCS/UPIU response decoding, and SCSI error-handler callbacks.
- Maintains runtime state for clocks, power modes, WriteBooster, BKOPS, device descriptors, exception events, MCQ, and recovery.

The file is intentionally generic. Silicon-specific behavior is pushed through `ufshcd_vops_*()` hooks and helper modules such as MCQ, crypto, BSG, RPMB, sysfs, debugfs, fault injection, and hwmon.

## Important APIs, Types, and Data

The central object is `struct ufs_hba`, which stores MMIO register access state, `Scsi_Host`, UTP descriptor bases, command/tag bitmaps, clocks/regulators, power state, cached device descriptors, MCQ queues, error state, workqueues, and vendor parameters. This chunk heavily mutates fields such as `ufshcd_state`, `curr_dev_pwr_mode`, `uic_link_state`, `pwr_info`, `max_pwr_info`, `capabilities`, `nutrs`, `nutmrs`, `outstanding_reqs`, `outstanding_tasks`, `active_uic_cmd`, `dev_cmd`, `clk_gating`, `clk_scaling`, `ufs_stats`, `dev_info`, `dev_quirks`, `ee_ctrl_mask`, `ee_drv_mask`, and `force_reset`.

Important request-side types include `struct scsi_cmnd`, `struct ufshcd_lrb`, `struct utp_transfer_req_desc`, `struct utp_transfer_cmd_desc`, `struct utp_upiu_req`, `struct utp_upiu_rsp`, `struct utp_task_req_desc`, `struct uic_command`, `struct ufs_pa_layer_attr`, `struct ufs_dev_info`, and MCQ `struct ufs_hw_queue` / `struct cq_entry`.

Exported or externally relevant APIs in this range include:

- Register, IRQ, and controller helpers: `ufshcd_dump_regs()`, `ufshcd_enable_irq()`, `ufshcd_disable_irq()`, `ufshcd_enable_intr()`, `ufshcd_is_hba_active()`, `ufshcd_make_hba_operational()`, `ufshcd_hba_stop()`, `ufshcd_hba_enable()`.
- PM and clock helpers: `ufshcd_pm_qos_init()`, `ufshcd_pm_qos_exit()`, `ufshcd_pm_qos_update()`, `ufshcd_scale_clks()`, `ufshcd_opp_config_clks()`, `ufshcd_hold()`, `ufshcd_release()`, `ufshcd_clkgate_delay_set()`.
- UIC/DME and link helpers: `ufshcd_send_uic_cmd()`, `ufshcd_dme_reset()`, `ufshcd_dme_configure_adapt()`, `ufshcd_dme_enable()`, `ufshcd_dme_set_attr()`, `ufshcd_dme_get_attr()`, `ufshcd_dme_rmw()`, `ufshcd_uic_tx_eqtr()`, `ufshcd_send_bsg_uic_cmd()`, `ufshcd_uic_change_pwr_mode()`, `ufshcd_link_recovery()`, `ufshcd_uic_hibern8_enter()`, `ufshcd_uic_hibern8_exit()`, `ufshcd_auto_hibern8_update()`, `ufshcd_change_power_mode()`, `ufshcd_config_pwr_mode()`, `ufshcd_parse_dev_ref_clk_freq()`.
- Device-management/query APIs: `ufshcd_copy_query_response()`, `ufshcd_query_flag()`, `ufshcd_query_attr()`, `ufshcd_query_attr_retry()`, `ufshcd_query_descriptor_retry()`, `ufshcd_read_desc_param()`, `ufshcd_read_string_desc()`, `ufshcd_exec_raw_upiu_cmd()`, `ufshcd_advanced_rpmb_req_handler()`, `ufshcd_read_device_lvl_exception_id()`.
- Error and recovery APIs: `ufshcd_update_evt_hist()`, `ufshcd_schedule_eh_work()`, `ufshcd_force_error_recovery()`, `ufshcd_try_to_abort_task()`, `ufshcd_cmd_inflight()`, `ufshcd_release_scsi_cmd()`, `ufshcd_compl_one_cqe()`.
- WriteBooster and exception controls: `ufshcd_write_ee_control()`, `ufshcd_update_ee_control()`, `ufshcd_wb_toggle()`, `ufshcd_wb_toggle_buf_flush()`, `ufshcd_wb_set_resize_en()`.

Module parameters in this chunk are `use_mcq_mode`, `uic_cmd_timeout`, and `dev_cmd_timeout`. Their setters constrain UIC and query timeout ranges, and `use_mcq_mode` gates use of UFSHCI 4.0 multi-circular-queue mode.

The `ufs_pm_lvl_states[]` table maps UFS PM levels to device power mode plus UIC link state. The `ufs_fixups[]` table applies known device quirks by manufacturer/model, later augmented through vendor ops.

## Control Flow

### Initialization and Probe

`ufshcd_hba_capabilities()` reads host capabilities, derives `nutrs`, `nutmrs`, RTT capacity, MCQ/LSDB support, and crypto capabilities. `ufshcd_memory_alloc()` allocates coherent DMA memory for command descriptors, transfer request descriptors, and task-management descriptors with UFSHCI-required alignment. `ufshcd_host_memory_configure()` programs UTRD command descriptor base addresses and response/PRDT offsets.

Controller enable starts in `ufshcd_hba_enable()`. Most controllers use `ufshcd_hba_execute_hce()`, which stops any active controller, marks the link off, calls vendor pre/post notifications, sets HCE, waits for readiness, and enables UIC interrupts. Broken-HCE controllers use DME reset/enable directly. `ufshcd_make_hba_operational()` enables interrupts, configures interrupt aggregation, writes UTRL/UTMRL base registers, checks list readiness, and sets run-stop bits.

Device bring-up runs through `ufshcd_device_init()`: link startup, optional MCQ reconfiguration after reset, NOP-OUT verification, `fDeviceInit` set/poll, descriptor/device-parameter initialization on first probe, and `ufshcd_post_device_init()`. Post init applies UniPro/device quirks, marks the device active, resets BKOPS state, sets timestamps where supported, updates reference-clock attributes in LS mode, and switches to the negotiated maximum power mode. `ufshcd_probe_hba()` then optionally performs a quirk-driven reinit after max gear switch, sets active ICC level, enables WriteBooster, writes exception-event control, and configures auto-Hibern8.

### SCSI and Device Commands

`ufshcd_queuecommand()` is the main SCSI midlayer entry. It rejects, queues, or fails commands based on `ufshcd_state`, holds clocks, initializes the LRB, composes a SCSI command UPIU, maps SG entries into PRDT entries, applies crypto PRDT metadata, chooses an MCQ hardware queue if enabled, and rings either an MCQ submission queue or the legacy UTRL doorbell.

Reserved device-management commands use `ufshcd_get_dev_mgmt_cmd()` and `hba->dev_cmd.lock`, with clock-scaling read locking through `ufshcd_dev_man_lock()`. Query, NOP, raw UPIU, and advanced RPMB paths compose UTRD-backed management requests, execute them through `blk_execute_rq()`, and decode NOP IN, Query RSP, RPMB response, or reject UPIU. Query helpers build flag, attribute, and descriptor requests with retry wrappers and descriptor length/type validation.

Task-management commands use a separate blk-mq queue only to allocate TMF tags. `__ufshcd_issue_tm_cmd()` fills `UTMRDL`, marks `outstanding_tasks`, rings `REG_UTP_TASK_REQ_DOOR_BELL`, waits up to `TM_CMD_TIMEOUT`, clears timed-out TMFs, and copies back the descriptor on success. `ufshcd_issue_tm_cmd()` wraps this for logical reset, query task, and abort task service responses.

### Completion and Interrupts

Legacy single-doorbell completions are detected by comparing `REG_UTP_TRANSFER_REQ_DOOR_BELL` with `hba->outstanding_reqs`; MCQ completions are consumed from completion queues. `ufshcd_compl_one_cqe()` timestamps, updates monitor accounting, traces, decodes response status through `ufshcd_transfer_rsp_status()`, unmaps DMA/crypto state, updates clock-scaling busy state, and calls `scsi_done()`.

`ufshcd_transfer_rsp_status()` maps OCS and SCSI status into Linux SCSI result bytes, copies sense data, sets residuals, schedules exception-event work on device alerts, and dumps request/host state for non-requeue errors. Device-management completions use `ufshcd_dev_cmd_completion()` and copy query payloads separately.

Interrupt handling is split between `ufshcd_intr()` and `ufshcd_threaded_intr()`. The hard handler either wakes the threaded handler or handles status immediately when MCQ ESI can do the heavy work. The threaded handler loops over status until no enabled interrupt remains or retry budget is exhausted. `ufshcd_sl_intr()` dispatches UIC completion, error checking, task management completion, transfer completion, MCQ CQ events, and MCQ interrupt-aggregation events.

UIC power-control commands are special. `ufshcd_uic_pwr_ctrl()` disables normal UIC completion interrupts, uses `hba->uic_async_done`, waits for power-status interrupts such as power-mode change or Hibern8 enter/exit, checks UPMCRS, and schedules recovery if the link becomes broken.

### Error Handling and Recovery

Hardware and UIC errors are gathered by `ufshcd_check_errors()` and `ufshcd_update_uic_error()`. Fatal interrupt errors, UIC PA/DL/NL/TL/DME errors, auto-Hibern8 errors, and QoS notifications update sticky fields, event history, debug dumps, and then schedule `eh_work`.

`ufshcd_err_handler()` quiesces the tagset, resumes enough power/clocks to recover, cancels exception work, marks error handling in progress, completes requests already cleared by hardware, and either aborts outstanding transfers or performs full reset/restore. Nonfatal PA generic LINERESET can trigger power-mode restore; fatal link errors, forced resets, DL NAC/replay cases, and broken links go through `ufshcd_reset_and_restore()`. Reset recovery stops the controller, completes/forces pending requests, scales clocks up, enables the HBA, reinitializes the device without rereading all parameters, probes the HBA, and reports a SCSI bus reset.

SCSI EH callbacks include `ufshcd_abort()`, `ufshcd_eh_device_reset_handler()`, and `ufshcd_eh_host_reset_handler()`. Abort first prints diagnostics, handles the illegal device-WLUN abort case by scheduling full recovery, branches to MCQ abort when needed, or queries/aborts/clears the specific task in legacy mode. LU reset issues `UFS_LOGICAL_RESET` and clears pending requests for the target LUN. Host reset forces `eh_work`, except PM-in-progress cases use direct link recovery to avoid deadlock.

## State and Persistence Behavior

Most persistent state is in `struct ufs_hba` and the attached UFS device, not in static globals. Software state includes:

- Controller state machine: reset, operational, error, fatal EH scheduled, nonfatal EH scheduled.
- Link/device PM state: cached device power mode, UIC link state, PA layer attributes, max supported power mode, auto-Hibern8 timer, RTC baseline/update period, active ICC level.
- Command state: per-command LRBs, SG/PRDT contents, request tags, `outstanding_reqs`, `outstanding_tasks`, reserved management command state, and MCQ SQ/CQ state.
- Error state: `errors`, `uic_error`, sticky `saved_err`, `saved_uic_err`, event-history rings, abort counters, force-reset flag, link-broken state, DME QoS notification.
- Feature state: WriteBooster enable/flush flags and lifetime checks, BKOPS enablement and urgent level, exception masks, temperature/health/device-level exception counters, RTT override, reference-clock setting, device quirk bits, model/device ID strings.
- Clock/PM state: clock-gating active request count and work state, clock-scaling active request count and busy windows, devfreq target frequency, PM QoS request, runtime-PM references, and regulator/clock modes.

Device-visible persistent attributes are changed through Query and DME commands: `fDeviceInit`, `bActiveICCLevel`, `bRefClkFreq`, reference-clock gating wait, `bMaxNumOfRTT`, exception event control, BKOPS flag, WriteBooster flags and resize mode, timestamp, seconds-passed RTC, and PA/DME link attributes. Several are volatile across reset, so the probe and recovery paths deliberately rewrite them.

DMA descriptor memory is coherent and owned by the device while commands are outstanding. The code relies on strict tag ownership: a tag maps to one UTRD/UCD/PRDT/LRB, and request completion must release DMA mappings, crypto PRDT metadata, clock holds, and busy accounting exactly once.

## Dependencies and Integration Points

This chunk integrates with:

- Linux SCSI midlayer and blk-mq: `Scsi_Host`, `scsi_cmnd`, internal/reserved commands, `blk_execute_rq()`, queue maps, polling, EH callbacks, device links, runtime PM, and queue-depth configuration.
- UFSHCI MMIO definitions and UFS protocol structures from UFS headers, including UTRL/UTMRL registers, UIC registers, Query OSF fields, UPIU transaction codes, descriptors, flags, attributes, and UniPro MIBs.
- Vendor operations in `ufshcd_vops_*()` for HCE notifications, link startup, power negotiation, clock scaling, hibern8, event notification, quirks, task-management setup, MCQ ESI, gear mapping, and controller-specific configuration.
- MCQ helpers for UFSHCI 4.0 queue allocation, queue operation, CQ polling, SQ cleanup, MAC programming, and ESI configuration.
- Crypto helpers for host crypto capabilities, request descriptor crypto fields, PRDT fill/clear, and block-queue crypto registration.
- PM infrastructure: runtime PM, devfreq, OPP, PM QoS, clocks, regulators, hibern8, autosuspend, and device links between the UFS device WLUN and user LUNs.
- Feature modules: `ufs_bsg` for user raw UPIU/UIC access, `ufs_rpmb`, debugfs, sysfs, hwmon temperature notifications, fault injection, and ftrace tracepoints from `ufs_trace.h`.

## Risks

- Lock ordering is delicate. Paths combine `host_sem`, `host_lock`, `outstanding_lock`, `uic_cmd_mutex`, `dev_cmd.lock`, `clk_scaling_lock`, `wb_mutex`, runtime-PM references, and blk-mq quiescing. Reordering can deadlock PM, SCSI EH, or device-management paths.
- Tag lifetime bugs can double-complete or leak commands. The code has separate legacy, MCQ, reserved, and TMF tag paths, each with different completion and cleanup rules.
- Error recovery runs while the device may be runtime suspended, system suspended, or mid-PM operation. Missing a clock/regulator/IRQ restore step can make recovery hang; over-resuming can deadlock.
- UIC power-control sequencing is timing-sensitive. Normal UIC completion, async power-status completion, timeout recovery, and link-broken marking must stay synchronized with `active_uic_cmd` and `uic_async_done`.
- Device descriptor data is untrusted hardware input. Length, offset, endianness, and UTF-16 string conversion checks protect against malformed descriptors; changes should preserve those checks.
- Query/DME attributes often have volatile or reset-default behavior. Removing reprogramming from probe/recovery can silently break WriteBooster, BKOPS, active ICC, RTT, reference-clock, exception, timestamp, or power-mode behavior after reset.
- MCQ and legacy single-doorbell modes share many call sites but diverge in queue mapping, completions, aborts, resource allocation, and interrupt handling. Feature additions must test both.
- Quirk handling is broad and vendor-specific. A fix for one device can affect link startup, DME timing, Hibern8, PA attributes, LCC, OCS handling, WriteBooster, or reinit behavior on another device.
- Diagnostic printing can occur in PM-sensitive paths. The code deliberately uses `dev_dbg()` in some places to avoid storage writes causing runtime-resume loops.

## Test and Validation Signals

Useful validation for this chunk includes:

- Build coverage for `drivers/ufs/core/ufshcd.c` with combinations of MCQ, crypto, BSG, RPMB, hwmon, PM, devfreq/OPP, debugfs, and fault-injection options.
- Boot/probe tests on UFS 2.x, 3.x, and 4.x devices, including both legacy single-doorbell and MCQ-capable hosts, verifying link startup, NOP OUT, `fDeviceInit`, descriptor reads, WLUN creation, LUN scan, queue depths, and active ICC programming.
- Runtime PM and system suspend/resume tests with clock gating, Hibern8, auto-Hibern8, devfreq clock scaling, PM QoS updates, and delayed RTC update work enabled.
- I/O stress with reads, writes, UNMAP, polled I/O, high queue depth, MCQ read/default/poll queues, interrupt aggregation, and fault-injection completion errors.
- SCSI EH tests for abort, logical unit reset, host reset, timeout, MCQ abort, device-WLUN abort escalation, and forced error recovery.
- Link/error tests that inject or observe UIC PA/DL/NL/TL/DME errors, DL NAC/replay quirks, auto-Hibern8 failures, fatal controller errors, and reset/restore loops.
- Query/descriptor tests for flag, attr, descriptor, string descriptor, raw UPIU via BSG, advanced RPMB request/response EHS, and invalid buffer/length cases.
- Feature-specific tests for WriteBooster enable/flush/lifetime/resize behavior, BKOPS urgent exception handling, temperature and health exception events, UFS 4.0 timestamp/RTT/device-level exceptions, and reference-clock programming.
