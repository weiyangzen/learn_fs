# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.c

## Purpose

`aic79xx_osm.c` is the Linux operating-system module for the Adaptec AIC790x Ultra320 SCSI driver. It adapts the portable AHD core to the Linux SCSI mid-layer, SPI transport class, PCI config wrappers, DMA allocation model, IRQ handling, module parameters, queue-depth policy, error recovery, and command completion semantics.

## Important APIs, Types, and Functions

- Module configuration globals include `aic79xx_no_reset`, `aic79xx_extended`, `aic79xx_pci_parity`, `aic79xx_allow_memio`, `aic79xx_seltime`, `aic79xx_periodic_otag`, `aic79xx_slowcrc`, `aic79xx_verbose`, `aic79xx_tag_info[]`, and per-adapter I/O cell options.
- `aic79xx_setup()` parses boot/module strings, including brace-form `tag_info`, `slewrate`, `precomp`, and `amplitude` lists through `ahd_parse_brace_option()`.
- `aic79xx_driver_template` exports Linux SCSI callbacks: queue command, abort, device reset, bus reset, host info, proc info/write hooks, target and device allocation/configuration, and i386 BIOS geometry.
- Low-level accessors `ahd_inb()`, `ahd_outb()`, `ahd_outw_atomic()`, `ahd_insb()`, `ahd_outsb()`, `ahd_pci_read_config()`, and `ahd_pci_write_config()` abstract memory-mapped versus PIO register access and Linux PCI config APIs.
- DMA shims `ahd_dma_tag_create()`, `ahd_dmamem_alloc()`, `ahd_dmamem_free()`, and `ahd_dmamap_load()` map the BSD-style core DMA contract onto Linux coherent DMA allocation.
- Host/device lifecycle functions include `ahd_linux_register_host()`, `ahd_linux_initialize_scsi_bus()`, `ahd_platform_alloc()`, `ahd_platform_free()`, `ahd_platform_init()`, `ahd_linux_target_alloc()`, `ahd_linux_target_destroy()`, `ahd_linux_sdev_init()`, and `ahd_linux_sdev_configure()`.
- Command path functions include `ahd_linux_queue_lck()`, `ahd_linux_run_command()`, `ahd_done()`, `ahd_linux_handle_scsi_status()`, and `ahd_linux_queue_cmd_complete()`.
- Error recovery functions include `ahd_linux_abort()`, `ahd_linux_queue_abort_cmd()`, `ahd_linux_dev_reset()`, and `ahd_linux_bus_reset()`.
- SPI transport setters `ahd_linux_set_width()`, `ahd_linux_set_period()`, `ahd_linux_set_offset()`, `ahd_linux_set_dt()`, `ahd_linux_set_qas()`, `ahd_linux_set_iu()`, `ahd_linux_set_rd_strm()`, `ahd_linux_set_wr_flow()`, `ahd_linux_set_rti()`, `ahd_linux_set_pcomp_en()`, `ahd_linux_set_hold_mcs()`, and `ahd_linux_get_signalling()` connect sysfs/SPI transport requests to AHD negotiation state.

## Control Flow and State

Module initialization optionally parses `aic79xx`, attaches an SPI transport template, reserves per-device transport storage for `struct ahd_linux_device`, then delegates PCI registration to `ahd_linux_pci_init()`. Probe and core configuration happen in the PCI files, then `ahd_linux_register_host()` allocates a `Scsi_Host`, stores the `ahd_softc` pointer in `hostdata`, sets queue and topology limits, initializes/reset-negotiates the bus, enables interrupts, calls `scsi_add_host()`, and starts scanning.

The normal I/O path starts at `ahd_linux_queue_lck()`, sets the CAM status field in `cmd->result`, and calls `ahd_linux_run_command()`. That routine maps Linux scatterlist DMA, allocates an SCB, fills hardware SCB fields such as `scsiid`, `lun`, CDB, control bits, tag attribute, negotiation flags, and S/G list, updates per-device counters (`openings`, `active`, `commands_issued`, ordered-tag interval), links the SCB into `pending_scbs`, and queues it to the sequencer. Completion enters through `ahd_linux_isr()` -> `ahd_intr()` -> core completion -> `ahd_done()`, which removes the SCB, unmaps DMA, converts transmission or SCSI status into CAM state, adjusts adaptive tag counters, frees the SCB, maps CAM status to Linux `DID_*`, and calls `scsi_done()`.

Error recovery pauses the controller and reasons about whether the timed-out command is queued, active on the bus, or disconnected. Aborts can remove commands from QINFIFO, assert ATN for active commands, or requeue a disconnected SCB with task-management state. Device reset builds a recovery SCB carrying `SIU_TASKMGMT_LUN_RESET` and waits on a completion. Bus reset calls the core channel reset and reports success to the mid-layer.

Queue-depth state is persistent per Linux SCSI device in `struct ahd_linux_device`: active/opening counts, queue-freeze count, max tags, queue-full history, tag success count, and periodic ordered-tag accounting. The driver throttles on `TASK_SET_FULL`, slowly grows openings after successful completions, and can lock a fixed tag depth after repeated queue-full responses at the same depth.

## State and Persistence Behavior

Persistent module/global state comes from kernel config and module parameters. Per-adapter state lives in `struct ahd_platform_data` and `struct ahd_softc`; per-target SPI state is stored in Linux `scsi_target` transport fields and AHD transinfo tables; per-LUN queue state is in transport-reserved `struct ahd_linux_device`. There is no filesystem persistence here, but SEEPROM-backed policy read by PCI code influences target allocation defaults, and procfs write support in `aic79xx_proc.c` can update adapter NVRAM.

## Dependencies and Integration Points

The file integrates Linux SCSI mid-layer headers, SPI transport helpers, PCI config APIs, DMA mapping APIs, IRQ APIs, and core AHD files. It expects PCI attachment from `aic79xx_osm_pci.c`, chip setup from `aic79xx_pci.c`, core SCB/sequencer functions from `aic79xx.c` and generated register definitions, and procfs display/write functions from `aic79xx_proc.c`.

## Risks

- The command path is sensitive to lock ordering and pause/unpause correctness; missed locking can corrupt `pending_scbs`, device openings, or sequencer mode state.
- `ahd_delay()` uses `usec % 1024`, so exact delays above 1024 microseconds are chunked in a non-obvious way and should be reviewed if timing-sensitive code changes.
- Error recovery has multiple paths that wait up to five seconds; stale `eh_done` or missed completion can make recovery fail and escalate resets.
- Queue-depth adaptation assumes queue-full semantics reflect target resource pressure; unusual targets can oscillate or underutilize tags.
- Low-level memory-mapped I/O relies on barriers after byte accesses; architecture-specific ordering changes need careful validation.

## Test Signals

- Build with `CONFIG_SCSI_SPI_ATTRS`, PCI, and AIC79xx options enabled.
- Probe an AIC7901/AIC7902 controller and confirm `scsi_add_host()`, `scsi_scan_host()`, IRQ registration, and SPI transport attributes are present.
- Exercise normal reads/writes with S/G DMA and autosense paths, including check-condition sense copying.
- Force `QUEUE FULL`, abort, target reset, and bus reset paths and confirm command completion status maps to Linux `DID_*` values without leaks in `active/openings`.
- Validate module parameter parsing for global tag depth and per-adapter/per-target brace lists.
