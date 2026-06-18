# sources/distributed-fs/ceph-client/drivers/scsi/arm/eesox.c

## Purpose

`eesox.c` implements the EESOX Fast SCSI expansion-card driver. It is a FAS216 wrapper with card-specific control latch management, optional real DMA, pseudo-DMA FIFO helpers, sysfs/proc termination control, IRQ wiring, and expansion-card lifecycle.

## Important APIs, Types, and Functions

`struct eesoxscsi_info` embeds `FAS216_Info`, card/base/control pointers, a control latch, and a fixed SG array. Key functions are `eesoxscsi_irqenable()`, `eesoxscsi_irqdisable()`, `eesoxscsi_terminator_ctl()`, `eesoxscsi_intr()`, `eesoxscsi_dma_setup()`, `eesoxscsi_buffer_in()`, `eesoxscsi_buffer_out()`, `eesoxscsi_dma_pseudo()`, `eesoxscsi_dma_stop()`, `eesoxscsi_set_proc_info()`, sysfs `bus_term` show/store handlers, `eesoxscsi_probe()`, and `eesoxscsi_remove()`.

## Control Flow

Probe maps IOCFAST space, allocates a host, initializes the control latch from the `term[]` module parameter, sets FAS216 base/shift/timing/DMA callbacks, configures expansion-card IRQ status, creates a `bus_term` sysfs file, initializes FAS216, requests IRQ and optional DMA, then calls `fas216_add()`. Runtime commands and error handling are provided by FAS216.

Real DMA maps the current command SG list and programs the platform DMA channel when the transfer is required or at least 512 bytes. Otherwise the FAS216 core uses pseudo-DMA callbacks. Pseudo-DMA polls FAS216 status and board DMA status, uses FIFO count to decide transfer sizes, and performs aligned 16/32-bit FIFO accesses for input and output.

## State and Persistence Behavior

Runtime state consists of the control latch, termination bit, fixed SG array, optional DMA ownership, and embedded FAS216 command/device state. `term[]` only controls initial state. Sysfs/proc writes update the live control latch but do not persist across reload.

## Dependencies and Integration Points

The driver depends on ecard APIs, FAS216 APIs, `arm_scsi.h`, ARM DMA APIs, Linux device attributes, and Linux SCSI host callbacks. It exposes termination through both proc host write and `bus_term` sysfs attribute.

## Risks and Edge Cases

Control-latch updates are protected by `host_lock` for termination paths, but IRQ enable/disable also mutate the latch through ecard callbacks; concurrency should be checked. As in similar wrappers, `dma_map_sg()` return value and unmap behavior are risk points. Pseudo-DMA uses `(u32)buf` alignment tests, which are architecture-sensitive. `device_create_file()` return is ignored during probe.

## Test Signals

Check probe with and without DMA channel, sysfs and proc termination changes, IRQ enable/disable preserving termination bits, pseudo-DMA input/output for unaligned buffers and odd lengths, FAS216 scan/sync/disconnect behavior, and cleanup of sysfs, IRQ, DMA, and host resources on failure and remove.
