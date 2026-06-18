# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.c

## Purpose
This file is the Linux-facing glue for the `sym53c8xx_2` PCI SCSI host driver. It translates Linux SCSI midlayer, SPI transport, PCI probe/remove, module parameters, DMA mapping, IRQ/timer handling, proc controls, and PCI error recovery into calls into the OS-independent HIPD core in `sym_hipd.c`.

## Important APIs, Types, and Functions
Global setup is held in `sym_driver_setup` and exposed through module parameters such as `cmd_per_lun`, `burst`, `led`, `diff`, `irqm`, `buschk`, `hostid`, `verb`, `debug`, `settle`, `nvram`, `excl`, and `safe`. `sym2_setup_params()` parses `excl` and applies the legacy safe-mode profile.

The SCSI host template `sym2_template` wires Linux callbacks to this driver: `sym53c8xx_queue_command`, `sym53c8xx_sdev_init`, `sym53c8xx_sdev_configure`, `sym53c8xx_sdev_destroy`, error handlers for abort/target reset/bus reset/host reset, and optional proc read/write handlers. `struct sym_ucmd` stores the per-command error-handler completion pointer in `scsi_cmd_priv()`. `sym_xpt_done()`, `sym_xpt_async_bus_reset()`, `sym_set_cam_result_error()`, `sym_setup_data_and_start()`, `sym_scatter()`, and `sym_log_bus_error()` are the main glue functions called from the core.

PCI lifecycle is implemented by `sym2_probe()`, `sym_attach()`, `sym2_remove()`, `sym_detach()`, `sym_iomap_device()`, `sym_check_supported()`, `sym_check_raid()`, `sym_set_workarounds()`, and `sym_config_pqs()`. PCI error recovery is implemented by `sym2_io_error_detected()`, `sym2_io_slot_dump()`, `sym2_io_slot_reset()`, and `sym2_io_resume()`. SPI transport integration is via `sym2_transport_functions`, including setters for offset, period, width, and DT mode.

## Control Flow
Module init attaches the SPI transport and registers the PCI driver. Probe enables the PCI device, requests BAR regions, identifies the chip, maps register/SRAM resources, skips RAID-owned chips, applies hardware workarounds, reads NVRAM when enabled, and calls `sym_attach()`. Attach allocates `Scsi_Host`, allocates the HCB, selects DMA mask, calls `sym_hcb_attach()` to initialize the core and SCRIPTS state, requests IRQ, resets the SCSI bus, starts SCRIPTS, starts the timer, and fills host limits before `scsi_add_host()` and `scsi_scan_host()`.

Command submission enters `sym53c8xx_queue_command_lck()` with the host lock held. It respects bus-settle suspension after resets, allocates a CCB through `sym_queue_command()`, maps DMA/scatterlist entries in `sym_scatter()`, builds the CDB and data pointers in `sym_setup_data_and_start()`, and starts the core via `sym_put_start_queue()`. IRQ handling calls `sym_interrupt()` under the host lock. The timer keeps the settle interval and can reap missed completions on affected bridges.

Error handlers synchronize with the core using completions and SEM/SIGP-driven SCRIPTS stops. Abort marks a CCB and may wait up to five seconds for completion. Target reset asks the core to send a target reset and waits for affected CCBs. Bus reset calls `sym_reset_scsi_bus()`. Host reset also cooperates with PCI error recovery via `sym_data->io_reset`.

## State and Persistence Behavior
Runtime state is split between Linux objects and the core HCB. `struct sym_data` binds a `Scsi_Host` to `struct sym_hcb`, `struct pci_dev`, and the optional PCI reset completion. `struct sym_shcb` in the HCB tracks MMIO/SRAM mappings, timer, instance names, settle timing, and the `Scsi_Host`. Per-LUN Linux state in `struct sym_slcb` records requested tags and configured queue depth. Module parameters persist only as module/global runtime configuration; device transfer settings are negotiated dynamically and may be seeded from NVRAM.

## Dependencies and Integration Points
This file depends on the Linux SCSI midlayer, SPI transport class, PCI core, DMA mapping API, interrupt and timer APIs, proc info support when configured, and `sym_nvram.c`. It is the only layer that calls `scsi_done()`, `scsi_dma_map()`, `scsi_dma_unmap()`, `scsi_add_host()`, `scsi_scan_host()`, `spi_attach_transport()`, and PCI error-recovery callbacks. It integrates with `sym_hipd.c` through exported core functions such as `sym_hcb_attach()`, `sym_interrupt()`, `sym_queue_scsiio()`, `sym_abort_scsiio()`, `sym_reset_scsi_target()`, and `sym_hcb_free()`.

## Risks
Resource unwind is complex because BAR mappings are owned by `sym_iomap_device()` until `sym_attach()` succeeds, then by the HCB teardown path. Error handlers mix host-lock sections with waits and must clear `eh_done` on timeout without racing a late completion. `sym53c8xx_eh_target_reset_handler()` currently returns `SCSI_SUCCESS` even after some timeout/failure paths set `sts`, which is a behavior worth reviewing. DMA scatter setup adjusts odd-byte wide transfers by increasing mapped lengths, so residual and unmap behavior depend on the core's accounting. PCI recovery disables IRQ and device access, so all paths must respect `pci_channel_offline()`.

## Test Signals
Primary validation is build coverage across MMIO/proc/NVRAM options, module parameter parsing, probe and remove on supported PCI IDs, failure injection at each probe step, SCSI scan with NVRAM scan restrictions, queue-depth configuration and tagged-command enablement, DMA mapping with max-SG and odd-wide transfers, IRQ-driven completions, timer fallback where configured, all SCSI EH callbacks, PCI AER or slot-reset recovery, SPI transport sysfs setters, proc read/write controls when enabled, and clean module unload after active I/O.
