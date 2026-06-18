# Research: sources/distributed-fs/ceph-client/drivers/scsi/ipr.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005271`: lines 1-9236, `Docs/researches/chunks/subset-b-005271_research.md`
- `subset-b-005272`: lines 9237-10096, `Docs/researches/chunks/subset-b-005272_research.md`

## Chunk Research

### subset-b-005271: lines 1-9236

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

### subset-b-005272: lines 9237-10096

# sources/distributed-fs/ceph-client/drivers/scsi/ipr.c lines 9237-10096

## Scope

This chunk is the tail of the IBM Power RAID SCSI (`ipr`) driver. It starts inside `ipr_wait_for_pci_err_recovery()` and covers interrupt-vector naming and MSI probing, first-stage PCI/SCSI host probe, adapter bringdown and hot-remove, second-stage PCI probe registration with sysfs artifacts and SCSI scanning, shutdown/reboot handling, the supported PCI ID table, PCI error-handler and PCI driver registration, the reboot notifier, and module init/exit.

The chunk depends on earlier definitions in the same file for chip tables, module parameters, interrupt handlers, reset state machines, memory allocation/free helpers, SCSI worker threads, sysfs binary attributes, command allocation, and PCI error recovery callbacks. It also depends on `ipr.h` for the core `struct ipr_ioa_cfg`, `struct ipr_hrr_queue`, `struct ipr_chip_t`, `struct ipr_chip_cfg_t`, and `enum ipr_shutdown_type` shapes. The preceding chunk contains most implementation details for the reset path and memory/resource helpers that this tail orchestrates.

## Purpose

The visible code turns a matched PCI function into a live SCSI host and tears it down again. Its responsibilities are:

- recover from probe-time EEH/PCI-channel-offline states before continuing PCI configuration;
- select MSI/MSI-X/INTx interrupt mode, verify MSI delivery, register one interrupt per hardware response queue when vectors are available, and fall back to legacy shared interrupts when needed;
- allocate and initialize the per-adapter `struct ipr_ioa_cfg` hosted in `Scsi_Host->hostdata`;
- map adapter MMIO BARs, configure DMA masks and cache-line size, save PCI state, detect card reset/error state, allocate DMA resources, and place the adapter on the global driver list;
- expose trace, dump, and async error-log sysfs files only after the SCSI host is added, then enable scanning and initialize optional `irq_poll` for multi-HRRQ SIS64 adapters;
- remove or shut down an adapter by stopping scans, flushing reset/work queues, initiating an IOA shutdown/reset sequence, freeing IRQs/resources, and unregistering from the global adapter list;
- register the PCI driver and reboot notifier at module load and unregister them at module unload.

This chunk is therefore the driver lifecycle boundary between the kernel PCI core, SCSI midlayer, low-level adapter reset logic, and system reboot/shutdown paths.

## Important APIs, Types, and Functions

- `ipr_wait_for_pci_err_recovery(struct ipr_ioa_cfg *ioa_cfg)` waits on `ioa_cfg->eeh_wait_q` while `pci_channel_offline(pdev)` is true, bounded by `IPR_PCI_ERROR_RECOVERY_TIMEOUT`, then restores PCI config state. It is called during probe error/retry points.
- `name_msi_vectors(struct ipr_ioa_cfg *ioa_cfg)` writes per-vector IRQ names into `ioa_cfg->vectors_info[]` as `host<host_no>-<vec_idx>`.
- `ipr_request_other_msi_irqs(struct ipr_ioa_cfg *ioa_cfg, struct pci_dev *pdev)` registers MSI/MSI-X vectors 1 through `nvectors - 1` with `ipr_isr_mhrrq` and each corresponding `struct ipr_hrr_queue`; vector 0 is registered separately with `ipr_isr`.
- `ipr_test_intr(int irq, void *devp)` is the temporary interrupt handler used only by the MSI self-test. Under `host_lock`, it sets `ioa_cfg->msi_received` and wakes `msi_wait_q`.
- `ipr_test_msi(struct ipr_ioa_cfg *ioa_cfg, struct pci_dev *pdev)` clears/masks adapter interrupts, installs `ipr_test_intr` on vector 0, triggers `IPR_PCII_IO_DEBUG_ACKNOWLEDGE`, waits one second for delivery, then frees the temporary IRQ. It returns `-EOPNOTSUPP` when the interrupt is not observed so probe can fall back to INTx.
- `ipr_probe_ioa(struct pci_dev *pdev, const struct pci_device_id *dev_id)` performs first-stage adapter allocation and hardware setup. It allocates a `Scsi_Host`, initializes `struct ipr_ioa_cfg`, requests PCI regions, enables the device, maps BAR 0, initializes register offsets, configures DMA masks, allocates IRQ vectors, saves/sets PCI-X command registers, allocates driver memory, saves PCI config state, checks interrupt/reset indicators, registers permanent IRQ handlers, configures the reset method, and adds the adapter to `ipr_ioa_head`.
- `ipr_initiate_ioa_bringdown(struct ipr_ioa_cfg *ioa_cfg, enum ipr_shutdown_type shutdown_type)` marks dump collection as aborting when needed, resets retry counters, marks `in_ioa_bringdown`, and starts the reset/shutdown state machine.
- `__ipr_remove(struct pci_dev *pdev)` is the internal resource-removal path used by hot-remove and probe-failure unwind after `scsi_add_host()`. It waits for active reset reloads, marks HRRQs as removing, initiates normal shutdown, flushes work, removes the adapter from the global list, restores dump state, and calls `ipr_free_all_resources()`.
- `ipr_remove(struct pci_dev *pdev)` is the PCI remove callback. It removes trace/dump/async-error sysfs files, removes the SCSI host, and then delegates to `__ipr_remove()`.
- `ipr_probe(struct pci_dev *pdev, const struct pci_device_id *dev_id)` is the PCI probe callback. It wraps `ipr_probe_ioa()`, starts adapter enable/reset through `ipr_probe_ioa_part2()`, adds the SCSI host, creates sysfs binary files, enables scan work, initializes secondary-HRRQ `irq_poll` where applicable, and calls `scsi_scan_host()`.
- `ipr_shutdown(struct pci_dev *pdev)` is the PCI shutdown callback. It disables secondary `irq_poll`, waits for reset reloads, selects `IPR_SHUTDOWN_QUIESCE` for SIS64 fast reboot, initiates bringdown, waits for completion, and in fast-reboot mode frees IRQs and disables the PCI device.
- `ipr_pci_table[]` lists supported IBM/Mylex/Adaptec PCI vendor/device/subsystem combinations and flags entries needing long transition-to-operational timeouts or PCI warm reset.
- `ipr_err_handler` wires the PCI EEH/error-recovery callbacks defined earlier: `ipr_pci_error_detected`, `ipr_pci_mmio_enabled`, and `ipr_pci_slot_reset`.
- `ipr_driver` is the Linux `struct pci_driver` binding name, ID table, probe/remove/shutdown callbacks, and PCI error handler.
- `ipr_halt_done(struct ipr_cmnd *ipr_cmd)` returns the shutdown-prepare command to its HRRQ free list.
- `ipr_halt(struct notifier_block *nb, ulong event, void *buf)` is a reboot notifier that sends `IPR_IOA_SHUTDOWN` with `IPR_SHUTDOWN_PREPARE_FOR_NORMAL` to all adapters that are accepting commands, except SIS64 fast-reboot restart cases.
- `ipr_init()` registers the reboot notifier and PCI driver; `ipr_exit()` unregisters both.

Key data carried through these paths includes `struct ipr_ioa_cfg` fields such as `host`, `pdev`, `ipr_chip`, `chip_cfg`, `sis64`, `clear_isr`, `max_cmds`, `transop_timeout`, `nvectors`, `hrrq_num`, `vectors_info`, `regs`, `reset`, `reset_work_q`, `needs_hard_reset`, `needs_warm_reset`, `ioa_unit_checked`, `in_reset_reload`, `in_ioa_bringdown`, `sdt_state`, `iopoll_weight`, and per-HRRQ `removing_ioa`/`allow_cmds` state.

## Control Flow

Probe starts in `ipr_probe()`, which calls `ipr_probe_ioa()` for resource acquisition. `ipr_probe_ioa()` first allocates the SCSI host and zeroes `hostdata`, looks up chip metadata from the PCI ID, derives SIS32/SIS64 mode and transition timeout, and initializes software queues and wait queues via `ipr_init_ioa_cfg()` from the previous chunk. It then requests PCI BAR ownership, enables the function, waits and retries if the channel is offline, maps BAR 0, calculates register addresses, and selects a 64-bit DMA mask for SIS64 adapters with 32-bit fallback.

After basic PCI setup, probe writes the PCI cache-line size and performs an MMIO read to surface EEH state. It clamps the global `ipr_number_of_msix` module parameter to `IPR_MAX_MSIX_VECTORS`, requests IRQ vectors with INTx always allowed and MSI/MSI-X allowed only when the chip advertises `has_msi`, and records `ioa_cfg->nvectors`. Legacy interrupt mode forces `clear_isr = 1`.

If MSI/MSI-X is enabled, `ipr_test_msi()` installs a temporary handler on vector 0, unmasks/debug-acknowledges the adapter interrupt, waits for `msi_received`, then removes the test handler. A successful test keeps the allocated vectors. A missing interrupt returns `-EOPNOTSUPP`, causing probe to wait for PCI recovery, free the vectors, reset `nvectors` to 1, set `clear_isr`, and continue with legacy interrupt setup. Other test errors abort probe through the vector-cleanup path.

`hrrq_num` is the minimum of allocated vectors, online CPUs, and `IPR_MAX_HRRQ_NUM`. The function then saves/sets PCI-X command state, allocates coherent resources and command blocks, saves PCI config state for reset recovery, checks adapter interrupt/microprocessor registers for unknown/error/reset-alert state, masks and clears interrupts under `host_lock`, and registers permanent IRQ handlers. With MSI/MSI-X, vector 0 uses `ipr_isr` and remaining vectors use `ipr_isr_mhrrq`; with INTx, `ipr_isr` is registered shared on `pdev->irq`.

Warm-reset-capable hardware is selected from PCI ID flags or an early Obsidian-E revision. Those adapters set `needs_warm_reset`, use `ipr_reset_slot_reset`, and allocate an ordered reset workqueue named by host number. Other adapters use `ipr_reset_start_bist`. Once the reset method is established, the adapter is added to `ipr_ioa_head` under `ipr_driver_lock` and first-stage probe succeeds. Every failure label unwinds only the resources acquired up to that point: IRQs, driver memory, IRQ vectors, MMIO map, PCI enablement, regions, and SCSI host reference.

Second-stage probe continues in `ipr_probe()`. It starts the adapter enable/reset path with `ipr_probe_ioa_part2()`, then registers the host with the SCSI midlayer. Sysfs trace, async error-log, and dump files are created in sequence; each failure path removes previously created files, removes the SCSI host when needed, and calls `__ipr_remove()`. Once sysfs setup succeeds, `scan_enabled` is set under `host_lock`, `work_q` is scheduled to populate devices, optional secondary-HRRQ `irq_poll` instances are initialized for SIS64 multi-vector adapters, and `scsi_scan_host()` starts discovery.

Removal reverses the lifecycle. `ipr_remove()` first removes sysfs files and detaches the SCSI host so no new midlayer operations enter. `__ipr_remove()` waits out active reset reloads, marks every active HRRQ as `removing_ioa`, issues a normal IOA bringdown, waits for reset completion, flushes normal and reset work, clears `used_res_q`, removes the adapter from `ipr_ioa_head`, repairs `sdt_state` from `ABORT_DUMP` back to `WAIT_FOR_DUMP` when appropriate, and frees all hardware/software resources.

Shutdown is similar but optimized for system poweroff/restart. It disables active secondary `irq_poll`, waits for reset reloads, chooses quiesce shutdown for SIS64 fast reboot on `SYSTEM_RESTART`, initiates bringdown, waits for completion, and for that fast-reboot path frees IRQs and disables PCI without freeing the whole host object because normal module/device teardown is not necessarily running.

The reboot notifier runs earlier in reboot/halt/poweroff notification. Under the global adapter lock it iterates `ipr_ioa_head`, locks each host, skips adapters that cannot accept commands or SIS64 fast-reboot restart cases, obtains a free internal command, fills an IOA shutdown-prepare CDB, submits it with `ipr_do_req()`, and relies on `ipr_halt_done()` to return the command to the free queue on completion.

## State and Persistence

Most state in this chunk is volatile kernel and adapter runtime state:

- `pci_set_drvdata()` from earlier initialization makes `struct ipr_ioa_cfg` the persistent per-device handle for all PCI callbacks.
- PCI regions, PCI enablement, BAR mappings, DMA masks, saved PCI state, IRQ-vector allocations, and registered IRQ handlers are acquired during `ipr_probe_ioa()` and released by failure labels, `__ipr_remove()`, or fast reboot shutdown.
- `ioa_cfg->nvectors`, `hrrq_num`, `vectors_info[]`, and each `hrrq[]` determine interrupt distribution and command-completion queue ownership for the lifetime of the adapter instance.
- `ioa_cfg->needs_hard_reset`, `needs_warm_reset`, `ioa_unit_checked`, `reset`, and `reset_work_q` capture detected adapter condition and select the later reset/reload behavior.
- `ioa_cfg->sdt_state` is temporarily changed from `WAIT_FOR_DUMP` to `ABORT_DUMP` during bringdown to stop dump collection and restored during remove if no longer tearing down.
- `scan_enabled` gates asynchronous resource discovery, while `scsi_add_host()`/`scsi_scan_host()` publish the host to the SCSI midlayer.
- `ipr_ioa_head` is the global list used by reboot notification; membership begins after first-stage probe succeeds and ends during internal removal.
- Module parameters from earlier in the file influence persistent runtime policy: `ipr_transop_timeout`, `ipr_number_of_msix`, `ipr_fast_reboot`, `ipr_debug`, and kernel `reset_devices`.

The code does not itself write adapter NVRAM or disk data. It does save PCI config state for later reset recovery and sends shutdown commands intended to flush adapter write cache during remove/shutdown/reboot.

## Dependencies and Integration Points

Kernel subsystem dependencies are broad:

- PCI core: `pci_request_regions()`, `pci_enable_device()`, `pci_ioremap_bar()`, `pci_set_master()`, `pci_alloc_irq_vectors()`, `pci_irq_vector()`, `pci_free_irq_vectors()`, `pci_save_state()`, `pci_restore_state()`, `pci_channel_offline()`, `pci_register_driver()`, `pci_unregister_driver()`, and PCI EEH/error-handler callbacks.
- IRQ and polling layers: `request_irq()`, `free_irq()`, `IRQF_SHARED`, `irq_poll_init()`, `irq_poll_disable()`, and the earlier `ipr_isr`, `ipr_isr_mhrrq`, and `ipr_iopoll` implementations.
- DMA/MMIO: `dma_set_mask_and_coherent()`, coherent allocations from previous helpers, `readl()`, `writel()`, `iounmap()`, and register offsets in `struct ipr_interrupts`.
- SCSI midlayer: `scsi_host_alloc()`, `scsi_host_put()`, `scsi_add_host()`, `scsi_remove_host()`, `scsi_scan_host()`, and the global `driver_template`.
- Workqueues and wait queues: adapter work uses `work_q`, `scsi_add_work_q`, optional ordered `reset_work_q`, `wait_event()`, and `wait_event_timeout()`.
- Sysfs binary attributes: `ipr_trace_attr`, `ipr_dump_attr`, and `ipr_ioa_async_err_log` are created under `host->shost_dev.kobj`; trace/dump helpers compile to no-ops unless their config options are enabled.
- Reboot notifiers: `register_reboot_notifier()`, `unregister_reboot_notifier()`, `SYS_RESTART`, `SYS_HALT`, `SYS_POWER_OFF`, and global `system_state`.

Internal integration points include previous-chunk helpers `ipr_init_ioa_cfg()`, `ipr_init_regs()`, `ipr_save_pcix_cmd_reg()`, `ipr_set_pcix_cmd_reg()`, `ipr_alloc_mem()`, `ipr_free_mem()`, `ipr_free_irqs()`, `ipr_free_all_resources()`, `ipr_probe_ioa_part2()`, `ipr_initiate_ioa_reset()`, `ipr_get_free_ipr_cmnd()`, `ipr_do_req()`, `ipr_timeout()`, and the earlier reset/PCI-error callback implementations. The ID table uses many `IPR_SUBS_DEV_ID_*` and `PCI_DEVICE_ID_*` constants from headers and supplies driver-data flags consumed during probe.

## Risks and Edge Cases

- `ipr_wait_for_pci_err_recovery()` calls `pci_restore_state()` after a bounded wait even if the channel remains offline. Callers often retry or check again, but the helper itself does not report timeout status.
- The MSI self-test temporarily requests vector 0 before permanent IRQ setup. Any mismatch between adapter debug interrupt generation and platform MSI delivery causes fallback to INTx, reducing queue parallelism.
- In the MSI fallback path, `pci_free_irq_vectors()` is called and `nvectors` is set to 1, but the code does not call `pci_alloc_irq_vectors()` again for INTx before the later legacy `request_irq(pdev->irq, ...)`. This relies on `pdev->irq` being valid for legacy INTx after vector cleanup on the target kernel.
- `ipr_request_other_msi_irqs()` frees only vectors already requested in its own loop on failure; vector 0 is freed later by the `cleanup_nolog` path through `ipr_free_mem()` only after jumping to cleanup. In this chunk, an error after vector 0 registration but before `ipr_request_other_msi_irqs()` success jumps to `cleanup_nolog`, which does not free vector 0 directly; later `out_msi_disable` frees IRQ vectors, but a registered IRQ handler still needs `free_irq()` first. The normal vector-registration failure path deserves careful review against the exact kernel IRQ-vector cleanup semantics.
- `name_msi_vectors()` uses `sizeof(desc) - 1` as the `snprintf()` size and then writes a NUL at `strlen(desc)`. This is redundant and leaves one byte unused, but appears bounded for the fixed descriptor buffer.
- `ipr_probe_ioa()` error labels are dense and order-sensitive. Small changes in resource acquisition order can introduce leaks or double frees if the unwind labels are not updated together.
- `ipr_free_irqs()` assumes `ioa_cfg->nvectors` corresponds to registered permanent IRQs. It is correct after successful permanent registration, but unsafe if reused in partially registered states without matching vector-handler accounting.
- `__ipr_remove()` waits for `in_reset_reload` before and after initiating bringdown. If reset completion never wakes `reset_wait_q`, hot-remove or shutdown can block indefinitely.
- `INIT_LIST_HEAD(&ioa_cfg->used_res_q)` in `__ipr_remove()` discards the active resource list before `ipr_free_all_resources()`. That is intentional after `scsi_remove_host()` and bringdown, but any later code expecting to walk used resources during free would observe an empty list.
- `ipr_shutdown()` frees IRQs and disables the PCI device only for the SIS64 fast-reboot path; other shutdowns depend on the adapter shutdown/reset sequence and platform reboot/poweroff, not full resource free.
- `ipr_halt()` obtains a free command without checking for `NULL`. The code assumes `allow_cmds` implies an internal command is available; if the free list is empty during reboot notification, this could dereference a bad pointer.
- `ipr_halt_done()` returns commands to the free list without taking the HRRQ lock in this local function. The surrounding request/completion path may already run under appropriate locking, but the function is fragile if reused outside that context.
- Reboot notifier ordering with PCI shutdown can matter. `ipr_halt()` may send shutdown-prepare commands while later `ipr_shutdown()` also initiates bringdown; fast reboot skips notifier commands for SIS64 restart cases to avoid conflicting with the quiesce path.
- The PCI ID table is large and manually maintained. Missing or incorrect `driver_data` flags can select wrong transition timeouts or reset methods for a hardware revision.

## Test and Validation Signals

Useful validation for this chunk should focus on lifecycle, hardware modes, and failure unwinding:

- Probe supported SIS32 and SIS64 adapters with INTx-only, MSI, and MSI-X-capable platforms. Confirm `scsi_add_host()`, sysfs trace/dump/async-log creation, `scan_enabled`, `scsi_scan_host()`, and command completion all work.
- Force `ipr_number_of_msix` above `IPR_MAX_MSIX_VECTORS` and verify it is clamped with an error message and no out-of-bounds vector naming or IRQ registration.
- Inject MSI test failure and confirm fallback to legacy interrupts, `clear_isr = 1`, `nvectors = 1`, successful permanent legacy `request_irq()`, and no leaked temporary IRQ/vector state.
- Fault-inject each `ipr_probe_ioa()` acquisition step: host allocation, PCI regions, PCI enable, BAR map, DMA mask, cache-line write, vector allocation, PCI-X setup, driver memory allocation, PCI state save, permanent IRQ request, and reset workqueue allocation. Check all acquired resources are released once.
- Exercise EEH/PCI-channel-offline recovery during probe and verify wait-queue wakeups, state restore, retry behavior, and eventual failure if the channel stays offline.
- Probe devices with interrupt registers indicating unmasked HRRQ updates, reset alerts, PCI error interrupts, unit check, and `reset_devices`; verify `needs_hard_reset` and `ioa_unit_checked` feed `ipr_probe_ioa_part2()` as expected.
- Remove an adapter under load and during reset reload. Confirm `removing_ioa` is set on all active HRRQs, outstanding reset waits complete, work queues flush, sysfs files are gone before resource free, and no SCSI commands enter after `scsi_remove_host()`.
- Test sysfs creation failures independently for trace, async error log, and dump paths; each should remove previous artifacts and invoke internal removal without leaking host or PCI resources.
- Validate `irq_poll` setup and teardown for SIS64 multi-vector adapters with nonzero `iopoll_weight`; secondary HRRQs should be initialized after probe and disabled during shutdown.
- Reboot, halt, poweroff, and fast-reboot restart paths should show shutdown-prepare commands for eligible adapters, normal bringdown on shutdown, quiesce mode for SIS64 fast reboot, and no duplicate command submission in the skipped fast-reboot notifier case.
- Module load/unload should verify notifier registration is undone if `pci_register_driver()` fails, and normal unload unregisters notifier before the PCI driver.
