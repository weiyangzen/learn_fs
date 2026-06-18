<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_vsc.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_vsc.c

## Purpose

This is the libata PCI driver for Vitesse VSC7174 and compatible Intel 31244 DPA SATA controllers. It maps one MMIO BAR, exposes four SATA ports, customizes taskfile and interrupt handling, optionally enables MSI, and works around cache-line and LED-control hardware behavior.

## Important APIs, types, and functions

`vsc_sata_ops` inherits BMDMA operations but overrides lost-interrupt handling, taskfile load/read, freeze/thaw, and SCR access. Important functions are `vsc_sata_tf_load()`, `vsc_sata_tf_read()`, `vsc_intr_mask_update()`, `vsc_error_intr()`, `vsc_port_intr()`, `vsc_sata_interrupt()`, `vsc_sata_setup_port()`, and `vsc_sata_init_one()`.

## Control flow

Probe allocates four ports, enables PCI, maps BAR0, assigns per-port taskfile/BMDMA/SCR addresses using a 0x200 stride starting at port offset 1, sets a 32-bit DMA mask, fixes a zero PCI cache-line size, enables MSI when possible, clears a shared-activity LED bit, and activates with `vsc_sata_interrupt()`. Taskfile writes use 16-bit paired address registers for LBA48. Interrupt flow reads global status, extracts one byte per port, freezes on PHY-change or major error bits, aborts on other errors, or dispatches normal BMDMA completion.

## State and persistence behavior

State is MMIO interrupt masks, PCI cache-line/LED config, MSI/INTx state, and libata runtime state. There is no persistent storage and no custom suspend/resume path.

## Dependencies and integration points

The driver depends on PCI, DMA mapping, MSI, libata BMDMA/SFF helpers, and SCSI host exposure. Device IDs match both Vitesse and Intel-compatible class/subclass encodings.

## Risks

Interrupt masking is split per port and tied to ATA_NIEN handling rather than standard SFF control writes. Lost-interrupt handling is disabled because the hardware is not standard SFF. Error-bit classification determines freeze versus abort; incorrect classification can either over-reset or miss link recovery. The 32-bit DMA mask reflects poor 64-bit support.

## Test signals

Test VSC7174/Intel 31244 enumeration, MSI fallback, per-port interrupt masking, DMA I/O, induced PHY changes, CRC/error interrupts, LBA48 taskfile correctness, and cache-line-size initialization. Dmesg should not show repeated spurious IRQ or PCI-fault status except on removal/fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_vsc.c -->
