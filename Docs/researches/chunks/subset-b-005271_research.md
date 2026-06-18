# sources/distributed-fs/ceph-client/drivers/scsi/ipr.c lines 1-9236

Chunk id: `subset-b-005271`

This chunk covers the main body of the IBM Power RAID SCSI adapter driver up through `ipr_wait_for_pci_err_recovery()`. The remaining tail of the file, starting after line 9236, contains the rest of probe/PCI driver registration and module exit paths and should be reconciled by later chunk merge work.

## Purpose

`ipr.c` implements a Linux SCSI host adapter driver for IBM Power RAID adapters. In this chunk it defines the adapter chip tables, module parameters, command submission path, interrupt completion path, error logging and adapter dump handling, SCSI mid-layer hooks, device discovery, firmware download, adapter reset/reload state machine, PCI error recovery callbacks, and memory/resource allocation helpers.

The driver supports older SIS32 adapters and newer SIS64 adapters. Most logic branches on `ioa_cfg->sis64` to choose 32-bit versus 64-bit IOARCB/IOADL layouts, register access width, config-table layout, resource addressing, dump format, and MSI-X/multiple HRRQ behavior.

## Important APIs, Types, and Tables

Key global state:

- `ipr_ioa_head`: global list of active IOA configs used by later shutdown/reboot paths.
- `ipr_driver_lock`: protects `ipr_ioa_head`.
- Module parameters: `max_speed`, `log_level`, `fastfail`, `transop_timeout`, `debug`, `dual_ioa_raid`, `max_devs`, `number_of_msix`, and `fast_reboot`. These tune bus speed, logging, reset timeout policy, supported devices, MSI-X count, and reboot behavior.
- `ipr_chip_cfg[]` and `ipr_chip[]`: map PCI device ids to chip capabilities, SIS32/SIS64 mode, BIST method, register offsets, command limits, and default irq_poll weight.
- `ipr_error_table[]`: IOASC-to-message dispatch table, including whether an HCAM or IOASA should be logged and at which log level.
- `ipr_ses_table[]`: known enclosure/product entries used to cap SCSI bus speed.

Important local data structures come from `ipr.h` and are heavily used in this chunk:

- `struct ipr_ioa_cfg`: per-adapter control block. Holds PCI/SCSI pointers, mapped registers, HRRQ queues, command blocks, config table, VPD buffers, hostrcb buffers, resource tables, reset/dump state, workqueues, waitqueues, feature flags, and runtime counters.
- `struct ipr_cmnd`: DMA-backed command block containing IOARCB, IOASA, IOADLs, sense buffer, timer, completion, work item, queue links, reset job callbacks, and associated SCSI command or async buffer.
- `struct ipr_hrr_queue`: Host Request Response Queue state, including free/pending command lists, response ring, toggle bit, command id range, locking, interrupt state, and optional `irq_poll`.
- `struct ipr_resource_entry`: driver-side resource/device representation. It tracks resource handle, address/path, type, inquiry data, queueing model, SCSI device pointer, virtual bus/target/lun assignment, raw mode, ERP state, and mid-layer add/remove flags.
- `struct ipr_hostrcb`: DMA-backed async notification buffer for HCAM config-change and error-log events.

The main kernel integration APIs in this chunk are:

- SCSI host template callbacks: `queuecommand`, error handlers, device init/configure/destroy, target destroy, queue-depth change, BIOS geometry, scan completion.
- PCI APIs: config space save/restore, capability probing, MMIO mapping, DMA mask setup, IRQ vector allocation, EEH/error recovery callbacks, config access locks, and PCIe reset state.
- DMA APIs: coherent allocations for control blocks/rings/tables, DMA pools for command blocks, `scsi_dma_map()` and `dma_map_sg()` for SCSI and firmware transfer payloads.
- Workqueues and timers: deferred device add/remove, dump collection, SCSI unblocking, reset slot work, command/reset timeouts.
- sysfs attributes and binary files: adapter attributes, device attributes, trace, async error log, dump, firmware update, diagnostics, reset, and iopoll weight.

## Command Lifecycle and Control Flow

Command blocks are allocated from per-HRRQ free lists. `__ipr_get_free_ipr_cmnd()` removes an available command from a queue; `ipr_get_free_ipr_cmnd()` initializes one from the internal HRRQ. `ipr_reinit_ipr_cmnd()` clears the command packet and IOASA state while preserving DMA address and HRRQ id. `ipr_init_ipr_cmnd()` also sets completion callbacks and resets per-use fields.

Driver-generated commands flow through `ipr_do_req()`. It links the command on the HRRQ pending queue, installs the done and timeout callbacks, starts the timer, traces the command, and writes the command DMA address to the adapter inbound register through `ipr_send_command()`. SIS64 command submission annotates the DMA address with IOARCB size flags.

Blocking internal commands use `ipr_send_blocking_cmd()`: the command is submitted with `ipr_internal_cmd_done()`, the host lock is dropped while sleeping on a completion, and the host lock is reacquired before returning. This pattern is used by reset/error paths that need synchronous adapter responses.

SCSI mid-layer commands enter at `ipr_queuecommand()`. The driver selects a HRRQ, rejects work when resets or removal block commands, obtains a free command, copies the CDB, chooses request type (`SCSICDB`, IOA command, or raw pipe), sets task/link/underlength flags, builds SIS32 or SIS64 IOADLs from the SCSI scatterlist, marks `SYNC_COMPLETE` when needed, queues the command, and rings the adapter. Dead/offline paths synthesize `DID_NO_CONNECT` and call `scsi_done()`.

Completions are consumed from HRRQs by `ipr_process_hrrq()`. It validates command indexes from adapter response handles, moves completed commands to a local done queue, advances the ring pointer/toggle bit, and honors polling budgets. `ipr_isr()` handles the primary interrupt path including HRRQ clearing and "other" interrupts. `ipr_isr_mhrrq()` handles additional HRRQ/MSI-X vectors and may schedule `irq_poll` via `ipr_iopoll()`. Completion callbacks run after dropping the HRRQ lock enough to avoid long work in the ring walk.

Normal SCSI success completion is `ipr_scsi_done()`: residual is set from IOASA, DMA is unmapped, `scsi_done()` is called, any error-handler completion is signaled, and the command returns to the free list. Error completion enters `ipr_erp_start()` under locks.

## Error Handling, ERP, and Sense Behavior

Error handling is centered on IOASC values from IOASA or HCAM buffers.

For SCSI command errors, `ipr_erp_start()` maps known IOASC cases into SCSI result codes, generated sense data, retries, aborts, bus-reset reporting, or device queue synchronization. It logs IOASA data through `ipr_dump_ioasa()` according to log level and the error table. For hardware device bus status with check condition, `ipr_get_autosense()` copies adapter autosense when available; otherwise non-NACA devices can issue `ipr_erp_cancel_all()` before `REQUEST_SENSE`. `ipr_gen_sense()` synthesizes fixed or descriptor-style sense for non-generic-SCSI and virtual-set devices, including failing LBA for medium errors.

SCSI EH support includes:

- `ipr_eh_abort()` and `ipr_cancel_op()`: detect the outstanding command, issue `IPR_CANCEL_ALL_REQUESTS`, and wait for affected commands to finish. Abort timeout escalates to a bus/device reset through `ipr_abort_timeout()`.
- `ipr_eh_dev_reset()` and `ipr_device_reset()`: issue `IPR_RESET_DEVICE`, mark reset state on the resource, and wait for outstanding device commands.
- `ipr_eh_host_reset()`: initiates adapter reset/reload and waits for reset completion.
- `ipr_wait_for_ops()`: scans command pools across all HRRQs and uses per-command `eh_comp` completions to wait for matching SCSI commands to finish.

Adapter async errors are received through HCAM log-data buffers. `ipr_process_error()` logs successful HCAMs with `ipr_handle_log_data()`, initiates abbreviated reset on `IPR_IOASC_NR_IOA_RESET_REQUIRED`, moves the buffer to the report queue for sysfs readers, gets/reclaims another HCAM, and resubmits log-data HCAMs. Config-change HCAMs flow through `ipr_process_ccn()` and `ipr_handle_config_change()`.

`ipr_handle_log_data()` dispatches by HCAM overlay id to specialized log decoders for cache, config, array, dual-IOA, fabric, SIS64 device, SIS64 config, SIS64 array, SIS64 service-required, or generic hex logs. It also reports bus resets to the SCSI mid-layer on non-SIS64 bus-reset IOASCs.

## Resource Discovery and SCSI Device Integration

Resources are initialized from adapter config-table entries. SIS64 resources are assigned virtual bus/target/lun positions based on resource type: generic SCSI, IOAFP, array, volume set, or fallback target id. SIS32 resources use direct bus/target/lun addresses from the config table. `ipr_is_same_device()` compares stable identifiers between current resources and newly read config entries.

Config changes and full reset discovery update the `used_res_q` and `free_res_q` lists:

- `ipr_handle_config_change()` handles incremental HCAM notifications, creates new entries when possible, updates existing entries, marks mid-layer add/remove work, and resubmits the config HCAM.
- `ipr_init_res_table()` rebuilds resource state after reset by moving current entries to an old list, matching config-table entries, allocating new entries, marking removed entries, and preserving active SCSI devices long enough for deferred removal.
- `ipr_clear_res_target()` releases SIS64 target/array/vset id bits when resources are freed.

Deferred add/remove is handled by workqueues. `ipr_worker_thread()` unblocks SCSI requests after reset, schedules `ipr_add_remove_thread()` when scanning is enabled, and runs dump collection when requested. `ipr_add_remove_thread()` removes devices marked `del_from_ml`, adds resources marked `add_to_ml`, and emits a host kobject change event when scanning completes.

SCSI device callbacks bind SCSI devices to resource entries. `ipr_sdev_init()` finds a matching resource, installs it in `sdev->hostdata`, rejects no-longer-supported SATA/GATA devices, and requests sync-complete for non-NACA devices. `ipr_sdev_configure()` adjusts type, SCSI level, `no_uld_attach`, report-opcodes behavior, queue timeout, and sector limits for arrays, IOAFP, and volume sets. Device and target destroy callbacks release pointers and SIS64 target id bits when appropriate.

## Reset, Bring-up, and Dump State Machine

The reset path is a callback-driven state machine routed by `ipr_reset_ioa_job()`. Each step sets `ipr_cmd->job_step`, possibly submits a command or timer, and returns either continue or return. If a step sees a failing IOASC, `job_step_failed` handles it, defaulting to `ipr_reset_cmd_failed()`, which logs and restarts reset.

Reset initiation uses `ipr_initiate_ioa_reset()` and `_ipr_initiate_ioa_reset()`. It blocks new SCSI commands across HRRQs, marks the host as SCSI-blocked, allocates an internal command, stores it as `ioa_cfg->reset_cmd`, and enters the reset job. Retry exhaustion takes the IOA offline, fails outstanding commands, and wakes reset waiters; bringdown state uses the same machinery.

Main reset stages in this chunk:

- `ipr_reset_shutdown_ioa()`: optional IOA shutdown or quiesce handling, with longer timeouts for normal shutdown, firmware download, and dual IOA abbreviated shutdown.
- `ipr_reset_ucode_download()`: optional `WRITE_BUFFER` microcode download using pre-mapped firmware scatterlist.
- `ipr_reset_alert()`: tells the adapter a reset is pending, masks/clears interrupts, and waits for safe reset timing.
- `ipr_reset_wait_to_start_bist()`, `ipr_reset_block_config_access()`, and `ipr_reset_block_config_access_wait()`: wait for critical operations/config access before reset.
- `ipr_reset_start_bist()`, `ipr_reset_slot_reset()`, `ipr_reset_reset_work()`, and `ipr_reset_bist_done()`: run adapter BIST or pulse PCIe warm reset depending on hardware setup.
- `ipr_reset_restore_cfg_space()`: restore PCI config state, restore PCI-X command settings, reenable irq balancing, fail outstanding ops, collect unit-check/dump data if needed, and choose bringdown or bring-up next step.
- `ipr_reset_enable_ioa()`: reset HRRQ memory, allow interrupts, set SIS64 endian mode, enable adapter diagnostics, unmask operational interrupts, and wait for transition-to-operational or stage-change.
- `ipr_reset_next_stage()`: for SIS64, tracks IPL feedback register stage and stage time, waits for operational transition, and advances to HRRQ identification.
- `ipr_ioafp_identify_hrrq()` through inquiry/query/mode-select functions: identify all host response queues, read adapter VPD/capabilities, optionally set cache parameters, query IOA config, initialize resources, configure dual-IOA and bus mode pages, set supported devices, and finish at `ipr_ioa_reset_done()`.

Adapter dump and unit-check behavior is intertwined with reset. `sdt_state` progresses through `INACTIVE`, `WAIT_FOR_DUMP`, `GET_DUMP`, `READ_DUMP`, `DUMP_OBTAINED`, and `ABORT_DUMP`. `ipr_get_ldump_data_section()` reads adapter dump memory through SIS64 dump registers or SIS32 mailbox/IODEBUG handshaking. With `CONFIG_SCSI_IPR_DUMP`, `ipr_get_ioa_dump()` constructs a driver dump plus adapter SDT dump pages. sysfs `dump` write arms or frees dump buffers, and sysfs read streams the driver header, SDT, and page data. Krefs protect dump memory while reads and worker collection overlap.

## Sysfs and User-Visible Operations

Adapter attributes:

- `fw_version`: firmware version from page 3 VPD.
- `log_level`: per-adapter log verbosity, writable.
- `run_diagnostics`: CAP_SYS_ADMIN-only reset/diagnostic cycle, failing if reset or logged errors remain.
- `online_state`: online/offline state, writable to bring a dead IOA online and reset it.
- `reset_host`: CAP_SYS_ADMIN-only host reset trigger.
- `update_fw`: CAP_SYS_ADMIN-only firmware request by filename, copied into DMAable pages and applied through reset/microcode download.
- `fw_type`: reports SIS64 flag.
- `iopoll_weight`: shows/sets irq_poll budget for SIS64 multi-vector adapters.

Binary host attributes include optional `trace`, `async_err_log`, and optional `dump`. The async error log exposes the first reported HCAM buffer and advances/reclaims it on write. Device attributes expose adapter handle, resource path, device id, resource type, and `raw_mode`.

## State and Persistence Behavior

Persistent hardware-facing state includes adapter firmware, non-volatile write cache state, adapter persistent error log, and microcode update state. The driver takes care to avoid resetting during critical adapter operations because doing so can lose persistent error-log data or damage flash error-log segments. The `ipr_reset_wait_to_start_bist()` comment explicitly calls out this risk.

Kernel runtime state is kept in `struct ipr_ioa_cfg`, DMA control buffers, resource queues, HRRQ rings, command pending/free queues, workqueues, waitqueues, and timers. There is no durable driver-owned filesystem state in this chunk. sysfs operations mutate live adapter state and, for `update_fw`, initiate adapter firmware persistence through a reset-time `WRITE_BUFFER DOWNLOAD_AND_SAVE`.

Important state flags and counters include `in_reset_reload`, `in_ioa_bringdown`, `reset_retries`, `reset_cmd`, `scan_enabled`, `scan_done`, `scsi_blocked`, `scsi_unblock`, `ioa_unit_checked`, `errors_logged`, `dump_timeout`, `probe_done`, `needs_hard_reset`, `needs_warm_reset`, `ucode_sglist`, and per-HRRQ `allow_cmds`, `allow_interrupts`, `ioa_is_dead`, and `removing_ioa`.

## Dependencies and Integration Points

This file integrates with:

- Linux SCSI mid-layer through `struct scsi_host_template`, SCSI device lifecycle, request completion, SCSI EH, `scsi_report_bus_reset()`, and scan completion.
- Linux PCI subsystem through probe-time setup, MMIO register access, IRQ/MSI-X allocation, DMA masks, PCI-X capabilities, PCI config save/restore, PCIe warm reset, and error recovery callbacks.
- Linux block layer queue limits and request timeout setup for volume-set devices.
- Firmware loader through `request_firmware()` for microcode updates.
- Kernel sysfs, binary attributes, device attributes, and uevents.
- IRQ and polling infrastructure through MSI/MSI-X/legacy IRQs, `irq_poll`, and IRQ affinity/no-balance flags during reset.
- DMA and memory allocation subsystems through coherent memory, DMA pools, scatterlists, and vmalloc-backed dump page pointer arrays.
- Adapter protocol structures in `ipr.h`, including IOARCB, IOASA, HCAM, config tables, mode pages, VPD pages, and dump SDT formats.

## Risks and Edge Cases

- Reset state is highly asynchronous and lock-sensitive. It mixes timers, interrupts, waitqueues, workqueues, and synchronous sleeps after dropping host locks. Race regressions can deadlock reset waiters, double-free commands, leave SCSI blocked, or lose completion notifications.
- Command ownership depends on free/pending list membership and HRRQ command id ranges. `ipr_cmnd_is_free()` is list-based, so list corruption or missing moves can confuse EH waiting and command reuse.
- SIS32 and SIS64 paths diverge in IOADL layout, config table parsing, resource addressing, dump access, interrupt masks, and HRRQ identification. Changes must be checked on both adapter families.
- sysfs write paths can trigger destructive operations: reset, firmware download, raw mode changes, diagnostics, and dump allocation/free. CAP_SYS_ADMIN checks exist for the most sensitive adapter-wide operations, but `raw_mode` is writable per device without an explicit capability check in this chunk.
- Firmware update maps a scatterlist, starts a reset, and relies on reset-time cleanup to unmap. Any reset abort or early failure path must still clear `ucode_sglist` and unmap correctly.
- Dump handling allocates potentially large memory, uses krefs, and can be aborted by reset timeouts. Offset math in `ipr_read_dump()` spans fixed driver dump, variable SDT area, and per-page IOA data.
- `ipr_get_free_hostrcb()` reclaims from the report queue if free HCAM buffers run out. That can drop unread async error logs under pressure.
- `ipr_check_term_power()` and mode page modification assume mode page 28 exists after `ipr_get_mode_page()`. Failure behavior relies on earlier command failure/adapter support assumptions.
- PCI error recovery can enter reset while probe is incomplete or while an adapter is already in reset. Paths distinguish `probe_done`, wake `eeh_wait_q`, and use a freeze reset step, but ordering remains delicate.

## Test Signals

Useful validation signals for this chunk:

- Build with relevant configs: `CONFIG_SCSI_IPR`, `CONFIG_SCSI_IPR_TRACE`, and `CONFIG_SCSI_IPR_DUMP` combinations to cover conditional sysfs and dump paths.
- Static analysis around locking/list ownership in `ipr_queuecommand()`, `ipr_scsi_done()`, `ipr_erp_start()`, `ipr_fail_all_ops()`, reset job steps, and `ipr_wait_for_ops()`.
- Probe tests on SIS32 and SIS64 hardware or emulation: DMA mask fallback, MSI/MSI-X allocation, IRQ registration, HRRQ identification, VPD inquiry chain, config-table parsing, and SCSI scan completion.
- Fault injection: command timeout, operational timeout, invalid HRRQ response handle, HCAM failure IOASC, `IPR_IOASC_NR_IOA_RESET_REQUIRED`, bus reset IOASCs, `scsi_dma_map()` failure, firmware DMA map failure, and allocation failures in `ipr_alloc_mem()`.
- SCSI EH tests: abort escalation to bus reset, device reset, host reset while reset is already in progress, and waiting for outstanding ops.
- sysfs tests: read/write `log_level`, `online_state`, `reset_host`, `run_diagnostics`, `iopoll_weight`, `async_err_log`, optional `dump`, and `update_fw` with missing and valid firmware names.
- PCI EEH/error recovery tests: frozen channel, MMIO restored, slot reset, permanent failure, and probe-time offline-channel wait.
- Runtime log signals: "Starting IOA initialization sequence", "Adapter firmware version", "IOA initialized", "Adapter being reset", "IOA taken offline", dump initiated/completed/failure, and async error messages from the IOASC table.
