# sources/distributed-fs/ceph-client/drivers/scsi/arm/oak.c

## Purpose

`oak.c` implements the Oak 16-bit SCSI expansion-card driver using the generic NCR5380 core. It provides board-specific register access, partial pseudo-DMA helpers, host-template glue, probe/remove, and module registration.

## Important APIs, Types, and Functions

The file specializes NCR5380 through macros for register read/write, queue command, info, and pseudo-DMA setup. Card-specific functions are `oakscsi_pread()`, `oakscsi_pwrite()`, `oakscsi_probe()`, `oakscsi_remove()`, `oakscsi_init()`, and `oakscsi_exit()`. The included `../NCR5380.c` supplies most SCSI protocol behavior.

## Control Flow

Probe claims the card, allocates an NCR5380 host, maps MEMC space, configures no IRQ, initializes the NCR5380 core with DMA fixup and late setup flags, maybe resets the bus, adds the host, and scans. Since `host->irq = NO_IRQ`, behavior is polling-oriented through the NCR5380 core.

`oakscsi_pread()` polls a status register for ready/error bits, reads up to 128 words at a time from the data port, handles trailing bytes, and times out on error. `oakscsi_pwrite()` currently logs the request and then loops forever polling status, never transferring or returning.

## State and Persistence Behavior

Runtime state is NCR5380 hostdata with an MMIO base. The file has no durable settings and no additional private state beyond the generic core.

## Dependencies and Integration Points

The driver depends on ARM ecard APIs, MMIO helpers, Linux SCSI host APIs, and the generic NCR5380 implementation included directly. It matches `MANU_OAK/PROD_OAK_SCSI`.

## Risks and Edge Cases

The write pseudo-DMA path is nonfunctional and can hang indefinitely. This is the dominant risk and should make write-capable use unsafe unless the NCR5380 core never selects that path for writes. `oakscsi_pread()` subtracts two bytes in the trailing branch even when only one byte remained, which can underflow `len` in local accounting after the final byte. The driver has no IRQ and limited error recovery visibility.

## Test Signals

Test probe/scan, read-only workloads, timeout behavior in `oakscsi_pread()`, any write command path to confirm it is blocked or hangs, clean removal, and NCR5380 abort/host reset behavior with `NO_IRQ`.
