# Research: subset-b-005302

This grouped report covers the MegaRAID SAS base driver and its debugfs companion in `sources/distributed-fs/ceph-client/drivers/scsi/megaraid/`. Each section is source-path aligned for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_base.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_debugfs.c

## Purpose

`megaraid_sas_debugfs.c` provides the optional debugfs interface for MegaRAID SAS Fusion adapters. When `CONFIG_DEBUG_FS` is enabled, it creates a global `megaraid_sas` debugfs directory and per-adapter `scsi_hostN` directories. Each Fusion adapter gets a read-only `raidmap_dump` file that exposes the currently active driver RAID map buffer for inspection.

When debugfs is disabled, the same public functions compile to empty stubs so the base driver can call `megasas_init_debugfs()`, `megasas_exit_debugfs()`, `megasas_setup_debugfs()`, and `megasas_destroy_debugfs()` unconditionally.

## Important APIs, Types, and Functions

The file exports or defines four integration functions:

- `megasas_init_debugfs()`: creates the global `debugfs` root directory `megaraid_sas`.
- `megasas_exit_debugfs()`: recursively removes the global root.
- `megasas_setup_debugfs(struct megasas_instance *instance)`: creates a per-adapter directory and a read-only `raidmap_dump` file for Fusion adapters.
- `megasas_destroy_debugfs(struct megasas_instance *instance)`: removes a per-adapter debugfs subtree.

The debugfs file operations are `megasas_debugfs_raidmap_open()`, `megasas_debugfs_read()`, and `megasas_debugfs_release()`, registered in `megasas_debugfs_raidmap_fops`.

The relevant data type is `struct megasas_debugfs_buffer` from `megaraid_sas_fusion.h`. It stores a raw pointer and length for the data exposed through a debugfs file. The source also touches `struct megasas_instance`, `struct fusion_context`, and debugfs `struct dentry` handles stored on the instance.

## Control Flow

At module load, `megasas_init()` in the base file calls `megasas_init_debugfs()`. With debugfs enabled, the function creates `/sys/kernel/debug/megaraid_sas`. Failure is logged but not fatal.

During adapter probe, `megasas_probe_one()` calls `megasas_setup_debugfs(instance)` after SCSI attach and AEN startup. The function only creates files when `instance->ctrl_context` is non-NULL, so legacy MFI adapters do not get `raidmap_dump`. For Fusion adapters, it creates a directory named `scsi_host%d` under the global root and creates a read-only `raidmap_dump` file with `instance` as `inode->i_private`.

When user space opens `raidmap_dump`, `megasas_debugfs_raidmap_open()` retrieves the instance from `inode->i_private`, gets `fusion = instance->ctrl_context`, allocates a small `megasas_debugfs_buffer`, stores a pointer to `fusion->ld_drv_map[(instance->map_id & 1)]`, stores `fusion->drv_map_sz`, and places that wrapper in `file->private_data`.

Reads call `megasas_debugfs_read()`. It returns zero for missing state and otherwise delegates to `simple_read_from_buffer()` to copy from the RAID map into the user buffer using the supplied file offset. Release frees only the wrapper object, not the RAID map itself.

On adapter removal, `megasas_detach_one()` calls `megasas_destroy_debugfs(instance)` to remove the per-instance subtree. On module unload, `megasas_exit()` calls `megasas_exit_debugfs()` to remove the global root recursively.

## State and Persistence Behavior

The file does not persist data. It exposes live in-memory Fusion RAID map state through debugfs. The only allocated state is the per-open `megasas_debugfs_buffer` wrapper. That wrapper borrows the RAID map pointer owned by the Fusion context and must not free or modify it.

The global `megasas_debugfs_root` dentry persists for the lifetime of the module when debugfs initialization succeeds. Each instance may hold `instance->debugfs_root` and `instance->raidmap_dump` dentries until adapter teardown.

The RAID map snapshot is not copied at open time. It points directly at `fusion->ld_drv_map[instance->map_id & 1]`, so reads observe whichever map buffer was selected at open. If the map is updated or freed concurrently with a debugfs reader, correctness depends on broader driver lifetime and map synchronization.

## Dependencies and Integration Points

The file depends on `CONFIG_DEBUG_FS`, `<linux/debugfs.h>`, SCSI headers, `megaraid_sas_fusion.h`, and `megaraid_sas.h`. It is called by the base driver lifecycle functions and reads Fusion RAID map data maintained by the Fusion code and updated from firmware map-sync DCMDs.

User-space integration is a debug-only inspection path under debugfs, not a stable ioctl or sysfs ABI. The exposed file is read-only and intended for diagnostics of the driver RAID map.

## Risks and Edge Cases

`megasas_debugfs_release()` declares `struct megasas_debug_buffer *debug = file->private_data`, while open allocates `struct megasas_debugfs_buffer`. The searched source tree defines `struct megasas_debugfs_buffer` but not `struct megasas_debug_buffer`; with `CONFIG_DEBUG_FS=y`, this appears to be a build-breaking type-name mismatch unless another hidden typedef exists outside the searched files.

The debugfs read path exposes a borrowed RAID map pointer without taking a map lock or reference. Adapter removal uses `debugfs_remove_recursive()`, which prevents new opens, but concurrent readers still rely on debugfs teardown and broader driver lifetime rules to avoid use-after-free as Fusion maps are freed during detach.

`megasas_setup_debugfs()` removes `instance->debugfs_root` when `raidmap_dump` creation fails but does not clear `instance->debugfs_root`. A later destroy path calling `debugfs_remove_recursive(instance->debugfs_root)` should usually tolerate stale dentries through debugfs semantics, but clearing the pointer would reduce ambiguity.

The code treats a NULL return from `debugfs_create_dir()` or `debugfs_create_file()` as failure. Modern debugfs helpers can also encode errors depending on kernel version, so callers should be checked against the target tree's debugfs API conventions.

There is no explicit validation that `fusion->ld_drv_map[(instance->map_id & 1)]` is non-NULL before exposing it. If debugfs setup runs before map allocation or after map teardown due to a lifecycle regression, reads can return zero only if `debug->buf` is NULL; open itself still succeeds.

## Test Signals

Useful validation signals include a build with `CONFIG_DEBUG_FS=y` to catch the release-path type mismatch, a build with `CONFIG_DEBUG_FS=n` to verify stubs satisfy the base driver references, module load creating `/sys/kernel/debug/megaraid_sas`, Fusion adapter probe creating `scsi_hostN/raidmap_dump`, MFI adapter probe not creating per-adapter map files, reading `raidmap_dump` returning exactly `fusion->drv_map_sz` bytes with normal offset/short-read behavior, repeated open/read/close cycles without leaks, adapter removal while a reader is active, module unload cleaning the global root, and fault injection around debugfs creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_debugfs.c -->
