# sources/distributed-fs/ceph-client/drivers/scsi/arm/powertec.c

## Purpose

`powertec.c` implements the PowerTec SCSI expansion-card driver. It wraps the generic FAS216 core with PowerTec-specific register offsets, IRQ control, terminator control, optional real DMA setup, sysfs/proc reporting, and expansion-card lifecycle.

## Important APIs, Types, and Functions

`struct powertec_info` embeds `FAS216_Info`, card/base pointers, terminator latch state, and a fixed SG array. Key functions are `powertecscsi_irqenable()`, `powertecscsi_irqdisable()`, `powertecscsi_terminator_ctl()`, `powertecscsi_intr()`, `powertecscsi_dma_setup()`, `powertecscsi_dma_stop()`, `powertecscsi_info()`, `powertecscsi_set_proc_info()`, sysfs `bus_term` show/store handlers, `powertecscsi_probe()`, and `powertecscsi_remove()`.

## Control Flow

Probe claims resources, maps IOCFAST space, allocates a host, sets initial termination from `term[]`, fills FAS216 hardware/timing fields and DMA callbacks, installs ecard IRQ ops, creates the `bus_term` device attribute, initializes FAS216, requests IRQ and optional DMA, enables `FASCAP_DMA` when DMA is available, and calls `fas216_add()`. Runtime SCSI flow is handled by `fas216_queue_command()` and `fas216_intr()`.

DMA setup only uses real DMA when the FAS216 capability bit is set and the core requires `fasdma_real_all`; otherwise it returns `fasdma_pio`. Unlike EESOX/Cumana II, `info->info.dma.pseudo` is NULL, so no pseudo-DMA fallback is advertised.

## State and Persistence Behavior

Runtime state includes the terminator latch, fixed SG array, optional DMA channel, and embedded FAS216 queues/device/transfer state. The module parameter `term[]` controls initial termination by slot but changes through sysfs/proc are live only.

## Dependencies and Integration Points

The driver depends on ecard APIs, FAS216 APIs, `arm_scsi.h`, ARM DMA APIs, Linux device attributes, and SCSI host-template callbacks. It matches `MANU_ALSYSTEMS/PROD_ALSYS_SCSIATAPI`.

## Risks and Edge Cases

As with other DMA wrappers, `dma_map_sg()` return value and unmap behavior are risk points. `device_create_file()` return is ignored. Termination control is not protected by `host_lock`, unlike EESOX, so concurrent sysfs/proc and IRQ paths should be reviewed. If real DMA is unavailable, the FAS216 core falls back to byte PIO, which may be slow but avoids a NULL pseudo callback because `fasdma_pio` is returned.

## Test Signals

Validate initial and live termination control, IRQ enable/disable, probe with DMA available and unavailable, real DMA transfers requiring `fasdma_real_all`, PIO fallback, FAS216 sync/disconnect/request-sense behavior, sysfs cleanup, and failure unwinding for IRQ/DMA/host resources.
