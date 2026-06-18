# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_base.c

## Purpose

`megaraid_sas_base.c` is the central Linux SCSI/PCI driver implementation for Broadcom/LSI MegaRAID SAS controllers. It owns module parameters, PCI device matching, adapter probe/remove/shutdown, firmware initialization, interrupt setup, SCSI host registration, command construction, completion, reset/error recovery, asynchronous event notification, sysfs attributes, and the privileged management character-device ioctl interface.

The file supports both legacy MFI adapters and newer Fusion-family adapters. It uses a `struct megasas_instance_template` dispatch table so adapter families can provide different MMIO register operations, interrupt clearing, reset operations, and command issue paths while sharing the SCSI and management-layer logic. Fusion-specific request building and reset helpers live in other files, but this file selects them, initializes shared state, and integrates them with the SCSI mid-layer.

## Important APIs, Types, and Functions

Important externally visible functions include `megasas_readl()`, `megasas_set_dma_settings()`, `megasas_get_cmd()`, `megasas_return_cmd()`, `megasas_issue_polled()`, `megasas_issue_blocked_cmd()`, `megasas_complete_cmd()`, `megasas_transition_to_ready()`, `megasas_alloc_cmds()`, `megasas_free_cmds()`, `dcmd_timeout_ocr_possible()`, `megasas_get_ctrl_info()`, `megasas_set_crash_dump_params()`, `megasas_setup_irq_poll()`, `megasas_setup_jbod_map()`, `megasas_get_device_list()`, `megasas_alloc_ctrl_dma_buffers()`, `megasas_free_ctrl_dma_buffers()`, and `megasas_get_target_prop()`. These functions are used by the local SCSI/PCI paths and by other MegaRAID source files such as the Fusion implementation.

Core local entry points are the SCSI host callbacks in `megasas_template`: `megasas_queue_command()`, `megasas_sdev_init()`, `megasas_sdev_configure()`, `megasas_sdev_destroy()`, `megasas_task_abort()`, `megasas_reset_target()`, `megasas_reset_bus_host()`, `megasas_reset_timer()`, `megasas_map_queues()`, and `megasas_bios_param()`.

Major initialization and lifecycle functions are `megasas_probe_one()`, `megasas_init_fw()`, `megasas_init_adapter_mfi()`, `megasas_io_attach()`, `megasas_suspend()`, `megasas_resume()`, `megasas_detach_one()`, `megasas_shutdown()`, module `megasas_init()`, and module `megasas_exit()`.

Important firmware and management helpers include `megasas_get_pd_list()`, `megasas_get_ld_list()`, `megasas_ld_list_query()`, `megasas_host_device_list_query()`, `megasas_update_device_list()`, `megasas_add_remove_devices()`, `megasas_start_aen()`, `megasas_register_aen()`, `megasas_service_aen()`, `megasas_aen_polling()`, `megasas_get_seq_num()`, `megasas_flush_cache()`, and `megasas_shutdown_controller()`.

The file defines adapter-family templates for xscale, ppc, skinny, and gen2 MFI controllers. A Fusion template is declared externally. Each template supplies `fire_cmd`, `enable_intr`, `disable_intr`, `clear_intr`, `read_fw_status_reg`, `adp_reset`, `check_reset`, `service_isr`, `tasklet`, `init_adapter`, `build_and_issue_cmd`, and `issue_dcmd`.

Module parameters form part of the public behavior: `max_sectors`, `msix_disable`, `msix_vectors`, `allow_vf_ioctls`, `throttlequeuedepth`, `resetwaittime`, `smp_affinity_enable`, `rdpq_enable`, `dual_qdepth_disable`, `scmd_timeout`, `perf_mode`, `event_log_level`, `enable_sdev_max_qd`, `poll_queues`, and `host_tagset_enable`.

## Control Flow

Module load registers the management character device, initializes debugfs, registers the PCI driver, and creates driver sysfs attributes for version, release date, polling support, device-change support, debug level, NVMe encapsulation, and PCI lane margining. In kdump mode (`reset_devices`) it deliberately reduces features such as MSI-X vector count, RDPQ, dual queue depth, and poll queues to lower memory footprint and avoid inherited controller state.

Probe starts in `megasas_probe_one()`. It rejects selected non-secure Aero device IDs, enables PCI memory resources, allocates a `Scsi_Host` with embedded `struct megasas_instance`, sets adapter type from the PCI ID, and calls `megasas_init_fw()`. After firmware initialization it optionally allocates SR-IOV VF affiliation buffers, stores the instance in PCI drvdata, publishes it in the global `megasas_mgmt_info` array for management ioctls, attaches to the SCSI mid-layer through `megasas_io_attach()`, scans devices, starts AEN registration, sets up debugfs, and reads initial SR-IOV affiliation.

`megasas_init_fw()` is the main hardware bring-up path. It maps the first PCI memory BAR, selects the adapter template, transitions firmware to ready, initializes per-instance locks and state, sets DMA masks, allocates controller memory and DMA buffers, reads scratch-pad registers for firmware capabilities, sizes MSI-X and poll queues, configures reply maps, initializes tasklets, calls the adapter-specific `init_adapter`, requests interrupts, enables interrupts, initializes JBOD maps, fetches the physical/logical device list, allocates stream-detection state on Ventura+ adapters, computes I/O limits, starts SR-IOV heartbeat when running as a VF, and starts the Fusion watchdog.

The SCSI I/O path begins at `megasas_queue_command()`. It rejects commands during unload, reset, critical hardware error, missing per-device private data, deleted logical drives, unsupported logical target/LUN combinations, or unsupported synchronize-cache cases. For MFI paths, `megasas_build_and_issue_cmd()` takes a command from the MFI pool, chooses logical read/write (`megasas_build_ldio()`) or passthrough/DCDB (`megasas_build_dcdb()`), builds 32-bit, 64-bit, or IEEE scatter-gather lists, records the command in `megasas_priv(scmd)->cmd_priv`, increments `fw_outstanding`, and posts the frame through the selected adapter template. Fusion adapters use the external Fusion `build_and_issue_cmd` implementation through the same template indirection.

Interrupt handling enters `megasas_isr()`, which checks the no-PCI-access reset flag, holds `hba_lock`, and calls `megasas_deplete_reply_queue()`. That function clears adapter-family interrupt status, detects firmware state changes, schedules online controller reset work if firmware enters fault state and OCR is enabled, or schedules the completion tasklet. MFI completion uses `megasas_complete_cmd_dpc()` to drain the producer/consumer reply queue and call `megasas_complete_cmd()` for each context.

`megasas_complete_cmd()` is the main completion demultiplexer. It maps firmware command/status combinations into SCSI results, copies sense data, unmaps DMA, calls `scsi_done()`, returns commands to the free pool, wakes synchronous DCMD waiters, services AEN completions, handles LD map and JBOD sequence-map update DCMDs, and completes abort commands. It also updates Fusion fast-path state when map validation succeeds and marks logical targets deleted when firmware removes them from the RAID map.

Reset and error recovery are layered. `megasas_reset_timer()` throttles queue depth before handing timeout recovery to SCSI EH. `megasas_reset_bus_host()` routes MFI controllers to `megasas_generic_reset()` and Fusion controllers to `megasas_reset_fusion()`. MFI recovery waits for outstanding commands, may call `megasas_do_ocr()`, defers outstanding commands through `megasas_internal_reset_defer_cmds()`, runs `process_fw_state_change_wq()`, reinitializes firmware, reissues deferred commands, and re-registers AEN. Failure paths mark the HBA critical and call `megaraid_sas_kill_hba()`.

AEN flow starts with `megasas_start_aen()`, which fetches event sequence numbers and issues `MR_DCMD_CTRL_EVENT_WAIT`. On completion, `megasas_service_aen()` wakes poll/fasync listeners and schedules `megasas_aen_polling()`. The delayed work decodes the firmware event, refreshes controller info or PD/LD lists as needed, adds/removes SCSI devices, and registers the next AEN sequence. Device list refresh can use the newer firmware combined host-device list or the older PD list plus LD list query.

The management character device only opens for `CAP_SYS_ADMIN`. `MEGASAS_IOC_FIRMWARE` copies a user ioctl packet, validates command type and feature support, mirrors user SGL buffers into coherent DMA memory, optionally sets a sense buffer pointer, issues a synchronous firmware command under `ioctl_sem`, copies data/status/sense back to user space, and frees DMA buffers. `MEGASAS_IOC_GET_AEN` requires prior fasync setup and registers the requested AEN class/locale. Compat ioctls translate 32-bit user pointers into the native packet format.

Suspend, resume, detach, and shutdown all stop user-visible activity before controller shutdown. They mark unload, stop SR-IOV heartbeat and Fusion watchdog where applicable, flush caches, issue shutdown/hibernate DCMDs, cancel pending AEN work, kill tasklets, disable interrupts, destroy IRQs, free MSI-X vectors, and release DMA/MMIO resources. Resume re-runs ready transition, DMA mask setup, interrupt allocation, firmware init, map sync, controller info fetch, AEN registration, heartbeat, and watchdog startup.

## State and Persistence Behavior

The file does not persist data to disk, but it maintains extensive in-kernel state and firmware-visible DMA state for each controller. `struct megasas_instance` owns PCI and SCSI host pointers, adapter type, register mapping, interrupt and reply-queue configuration, command pools, DMA buffers, logical/physical device maps, firmware capability flags, reset state, outstanding command counters, crash-dump state, SR-IOV state, AEN command state, and debugfs/sysfs-visible values.

Command state is split between `instance->cmd_pool`, `instance->cmd_list`, per-command MFI frames, per-command sense buffers, `fw_outstanding`, and `megasas_priv(scmd)->cmd_priv`. The command index is stored in firmware frames as a 32-bit context so completions can recover the driver command from `cmd_list`.

Firmware-derived topology persists in `pd_list`, `local_pd_list`, `ld_ids`, `ld_ids_prev`, `ld_ids_from_raidmap`, `ld_tgtid_status`, host-device list buffers, Fusion RAID maps, and JBOD sequence maps. AEN and OCR paths refresh these structures and then add or remove SCSI devices.

Recovery state is stored in atomics and flags such as `adprecovery`, `fw_reset_no_pci_access`, `issuepend_done`, `unload`, `disableOnlineCtrlReset`, `MEGASAS_FW_BUSY`, and Fusion reset flags. Deferred commands live on `internal_reset_pending_q` during OCR.

Crash-dump state is exposed through sysfs. The driver allocates a firmware crash buffer if supported, lets user space read it in page-sized chunks via `fw_crash_buffer`, and frees it when `fw_crash_state` is set to copied or error.

Global state includes module parameters, management major number, `megasas_mgmt_info`, async AEN queue state, global poll wait state, support booleans exported through sysfs, and the global debug level. These values affect all controller instances.

## Dependencies and Integration Points

The file integrates with Linux PCI, DMA, IRQ/MSI-X, SCSI, block-mq, sysfs, debugfs, char-device, poll/fasync, timer, workqueue, tasklet, and compatibility ioctl APIs. It includes `megaraid_sas.h` and `megaraid_sas_fusion.h`, which define firmware ABIs, adapter state structures, DCMD opcodes, Fusion helpers, and external routines.

Important external MegaRAID dependencies include Fusion request/reset/map helpers such as `megasas_reset_fusion()`, `megasas_task_abort_fusion()`, `megasas_reset_target_fusion()`, `megasas_alloc_fusion_context()`, `megasas_ioc_init_fusion()`, `megasas_get_map_info()`, `megasas_sync_map_info()`, `megasas_sync_pd_seq_num()`, `megasas_release_fusion()`, `megasas_fusion_start_watchdog()`, `megasas_fusion_stop_watchdog()`, `megasas_blk_mq_poll()`, and `megasas_irqpoll()`.

User-space integration is through `/dev` character-device registration named `megaraid_sas_ioctl`, driver sysfs attributes, host sysfs attributes, debugfs raid-map dumping, and fasync/poll event notification. Hardware integration is through MMIO registers, coherent DMA buffers, firmware DCMDs, MFI frames, Fusion descriptors, MSI-X vectors, and PCI shutdown/reset behavior.

## Risks and Edge Cases

The highest-risk areas are reset and timeout paths. The driver mixes SCSI EH, firmware OCR, watchdog-triggered recovery, interrupt handlers, synchronous management commands, and AEN work. Incorrect locking around `reset_mutex`, `hba_lock`, `mfi_pool_lock`, or `completion_lock` can cause double completion, leaked commands, stale SCSI devices, or PCI access while reset code forbids it.

Command lifetime is delicate. `megasas_issue_blocked_abort_cmd()` returns `DCMD_INIT` on hardware critical error without returning the allocated command, and timeout paths deliberately avoid returning commands when they expect OCR handling to consume them. These paths depend on later reset cleanup and are easy to break.

Several DCMD timeout handlers unlock and relock `reset_mutex` around Fusion OCR. Callers must hold the mutex exactly as expected; otherwise these helpers can unbalance locking or trigger reset while another firmware command path is active.

The ioctl path is privileged but still handles user-controlled frame contents, SGL offsets, lengths, and sense offsets. It validates maximum SGE count and sense offset, but any changes here must preserve bounds checks, coherent DMA cleanup, compat pointer translation, and feature gates for NVMe passthrough and toolbox/lane-margining commands.

Device discovery is feature-dependent. Firmware may expose the combined host-device list or require separate PD and LD list queries. SR-IOV VFs use affiliation maps, and hidden logical drives can change whether a scan occurs. AEN-driven add/remove must handle devices disappearing while SCSI references exist.

I/O limits and queue topology depend on module parameters, firmware scratch-pad registers, PCI link speed, adapter family, managed interrupt affinity, poll queues, and kdump mode. Regressions can overstate `host->can_queue`, use bad queue maps, or allocate an IRQ/vector combination the firmware does not support.

The file contains a likely type-name defect in the companion debugfs release path, visible when comparing `struct megasas_debugfs_buffer` allocation with `struct megasas_debug_buffer *` in `megaraid_sas_debugfs.c`. If no typedef exists elsewhere, a debugfs-enabled build would catch this.

Crash-dump sysfs reads depend on `fw_crash_buffer_offset` and firmware-provided buffer size. Bounds and state checks must remain strict to avoid exposing invalid DMA memory after user space marks dumps copied or errored.

## Test Signals

Useful test signals include successful kernel build with `CONFIG_SCSI_MEGARAID_SAS`, `CONFIG_COMPAT`, and `CONFIG_DEBUG_FS`; probe logs for supported MFI, Thunderbolt, Invader, Ventura, and Aero adapters; correct DMA mask selection; MSI-X allocation and fallback to INTx; SCSI host queue map shape with and without poll queues; successful logical and physical device scans; read/write I/O on LD and system-PD devices; SCSI inquiry, queue-depth, timeout, and NVMe property behavior; sysfs crash-dump and queue-depth attributes; management ioctl passthrough with 32-bit and 64-bit user-space packets; AEN poll/fasync delivery; hot add/remove events for PD and LD devices; SR-IOV heartbeat and VF affiliation changes; suspend/resume; shutdown and detach; kdump boot with `reset_devices`; firmware DCMD timeout injection; OCR recovery under active I/O; and critical-error adapter kill behavior.
