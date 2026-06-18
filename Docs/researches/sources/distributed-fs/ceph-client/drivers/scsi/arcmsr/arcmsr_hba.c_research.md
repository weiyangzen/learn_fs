# sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_hba.c

## Purpose
`arcmsr_hba.c` is the main Areca ARC11xx/12xx/16xx/188x SCSI RAID host driver. It registers a PCI-backed SCSI host, maps adapter registers, negotiates firmware limits, allocates DMA CCB/completion resources, queues SCSI commands to firmware, handles interrupts and management messages, tracks device-map changes, and implements suspend/resume, shutdown, abort, and bus-reset recovery.

## Important APIs and functions
- Module parameters: `msix_enable`, `msi_enable`, `host_can_queue`, `cmd_per_lun`, `dma_mask_64`, `set_date_time`, and `cmd_timeout`.
- SCSI integration uses `arcmsr_scsi_host_template`, with `queuecommand`, `eh_abort_handler`, `eh_bus_reset_handler`, `bios_param`, `sdev_configure`, `change_queue_depth`, `shost_groups`, and queue limits.
- PCI integration uses `arcmsr_device_id_table`, `arcmsr_pci_driver`, `arcmsr_probe()`, `arcmsr_remove()`, `arcmsr_shutdown()`, `arcmsr_suspend()`, and `arcmsr_resume()`.
- Resource setup includes `arcmsr_set_dma_mask()`, `arcmsr_remap_pciregion()`, `arcmsr_alloc_io_queue()`, `arcmsr_alloc_ccb_pool()`, optional `arcmsr_alloc_xor_buffer()`, `arcmsr_request_irq()`, `arcmsr_iop_init()`, `arcmsr_alloc_sysfs_attr()`, and `scsi_scan_host()`.
- Command path is `arcmsr_queue_command_lck()` -> `arcmsr_get_freeccb()` -> `arcmsr_build_ccb()` -> `arcmsr_post_ccb()`; completion is via adapter-specific postqueue ISR -> `arcmsr_drain_donequeue()` -> `arcmsr_report_ccb_state()` -> `arcmsr_ccb_complete()`.
- Management path is exposed both as SCSI virtual target 16 (`arcmsr_handle_virtual_command()`, `arcmsr_iop_message_xfer()`) and sysfs (`arcmsr_Read_iop_rqbuffer_data()`, `arcmsr_write_ioctldata2iop()`, `arcmsr_clear_iop2drv_rqueue_buffer()`).
- Firmware/config paths include `arcmsr_wait_firmware_ready()`, adapter-specific `*_get_config()`, `arcmsr_get_adapter_config()`, `arcmsr_iop_confirm()`, `arcmsr_request_device_map()`, and `arcmsr_message_isr_bh_fn()`.
- Error handling and recovery include `arcmsr_abort()`, adapter-specific polling completion helpers, `arcmsr_bus_reset()`, `arcmsr_iop_reset()`, `arcmsr_hardware_reset()`, `arcmsr_reset_in_progress()`, `arcmsr_abort_allcmd()`, and `arcmsr_done4abort_postqueue()`.

## Control flow
Probe enables the PCI device, allocates a `Scsi_Host`, initializes `AdapterControlBlock` locks and flags, requests BARs, maps the generation-specific register region, allocates queue resources, asks firmware for config, sizes the CCB pool and SCSI host limits, registers the host, requests IRQ vectors, initializes the IOP, starts the periodic device-map timer, optionally starts the time-sync timer, creates sysfs management files, and scans the host.

Normal command flow begins in `arcmsr_queue_command_lck()`. Commands to target 16 are treated as virtual management commands; all other commands acquire a free CCB, build an Areca firmware CDB with SG entries from `scsi_dma_map()`, increment the outstanding count, mark the CCB started, and post it using the adapter-specific queue protocol. Interrupt handlers dispatch by adapter type and drain doorbell events, postqueue completions, and message completions. Completion maps firmware device status to SCSI results, copies sense data when needed, unmaps DMA, returns the CCB to the free list, decrements the outstanding counter, and calls `scsi_done()`.

Device-map refresh is timer-driven. Every six seconds, unless a get-config, bus reset, or abort is active, the driver posts a get-config message. The message ISR schedules bottom-half work, which compares the firmware device map against `acb->device_map` and calls `scsi_add_device()` or `scsi_remove_device()` for changed target/lun slots.

Suspend and shutdown disable interrupts, stop timers/work, stop background rebuild, and flush adapter cache. Resume restores DMA mask/IRQs, resets generation-specific queue pointers/doorbells, reinitializes the IOP, and restarts timers. Remove has a hot-unplug path when PCI device ID reads `0xffff`, and otherwise drains outstanding commands before freeing IRQs, DMA, mappings, regions, and host state.

## State and persistence behavior
Persistent disk state is not owned by this file; it controls live controller state and firmware-visible DMA state. The important volatile state is `AdapterControlBlock`: firmware config, device map, free CCB list, outstanding counter, queue indices, ring buffers, interrupt masks, doorbell toggle shadows, timers, work item, and reset/abort flags. Firmware may persist controller cache and RAID state; the driver explicitly flushes cache and starts/stops background rebuild around lifecycle and management operations. Optional date/time sync writes current system time to firmware periodically when enabled.

## Dependencies and integration points
This file depends heavily on Linux PCI, DMA mapping/coherent allocation, interrupt vector allocation, SCSI midlayer APIs, block queue timeout configuration, timers, workqueues, spinlocks, circular buffers, and I/O memory accessors. It integrates with `arcmsr.h` for all hardware ABI details and with `arcmsr_attr.c` for sysfs management endpoints. It also references SCSI CAM geometry (`scsi_partsize`) and exposes `MODULE_DEVICE_TABLE` for hotplug/autoload.

## Risks and edge cases
- The driver has many adapter-specific branches. Type E and Type F share several helpers by layout compatibility, but Type F uses host memory for message buffers and completion sentinels; misrouting can corrupt DMA state.
- CCB address conversion relies on `vir2phy_offset`, CDB physical address high parts, and firmware-specific encoded completion flags. Address-high/page-boundary mistakes can complete the wrong CCB.
- `arcmsr_build_ccb()` returns `FAILED` after `scsi_dma_map()` errors, but the queue path does not return the acquired CCB to the free list in that failure branch; this is a leak risk in error paths.
- `arcmsr_hbaE_polling_ccbdone()` advances `doneq_index` before reading `cmdFlag`, then checks `acb->pCompletionQ[doneq_index].cmdFlag`, which may refer to the next entry. That is a subtle abort-polling correctness risk.
- Bus reset has long sleeps and retry loops and sets `FW_DEADLOCK` on timeout; user management commands reflect this state with `ARCMSR_MESSAGE_RETURNCODE_BUS_HANG_ON`.
- Hotplug scans are derived from firmware device-map bytes and limited target/lun loops. Bad firmware data or stale flags could add/remove the wrong SCSI devices.
- Management buffers are shared between sysfs, SCSI virtual commands, and interrupt handlers. Locking and overflow flags are critical to avoid lost or duplicated management payloads.
- Remove path includes a comment noting `arcmsr_interrupt(acb)` polling needs a spinlock, indicating a known concurrency risk during teardown with outstanding commands.

## Test signals
- Compile with all relevant configs and exercise probe for each adapter type where hardware or emulation exists.
- Verify MSI-X/MSI/INTx fallback and interrupt-driven completions under parallel I/O.
- Run SCSI read/write, queue-depth changes, SG-heavy commands, check-condition sense propagation, and target 16 management commands.
- Exercise sysfs `mu_read`, `mu_write`, `mu_clear`, and host attributes together with firmware utility tools.
- Test periodic hotplug: firmware device-map additions/removals should trigger `scsi_add_device()` and `scsi_remove_device()`.
- Exercise suspend/resume, shutdown, module remove, surprise removal, abort, and bus reset while I/O is outstanding.
- Watch `host_driver_posted_cmd`, `num_resets`, `num_aborts`, kernel logs, and SCSI error-handler return values for regressions.
