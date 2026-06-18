<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sx4.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sx4.c

## Purpose

This is the Promise PDC20621/FastTrak S150 SX4 libata driver. The controller uses local DIMM memory and a single host-DMA copy engine; the driver stages disk data through DIMM, submits controller packet programs, initializes SDRAM over I2C/SPD, and multiplexes the HDMA engine across four SATA ports.

## Important APIs, types, and functions

Key state is `struct pdc_port_priv` with DIMM packet buffers and coherent packet DMA, and `struct pdc_host_priv` with the HDMA active flag and ring queue. `pdc_20621_ops` supplies custom queue prep/issue, reset/EH, freeze/thaw, port start, taskfile command wrappers, and IRQ clear. Core helpers include `pdc20621_dma_prep()`, `pdc20621_nodata_prep()`, `pdc20621_packet_start()`, `pdc20621_push_hdma()`, `pdc20621_pop_hdma()`, `pdc20621_host_intr()`, `pdc20621_interrupt()`, DIMM window helpers, I2C SPD reads, DIMM programming, ECC clearing, `pdc_20621_init()`, and `pdc_sata_init_one()`.

## Control flow

Probe maps MMIO BAR3 and DIMM BAR4, assigns four port taskfile windows, sets a 32-bit ATA DMA mask, initializes DIMM timing/ECC using SPD, resets HDMA, then activates with a custom IRQ handler. DMA prep builds host and ATA packets plus PRD tables in a per-port DIMM window. Writes run host-to-DIMM HDMA first, then ATA write from DIMM; reads run ATA read into DIMM first, then DIMM-to-host HDMA. The interrupt handler reads sequence-mask bits, maps sequence IDs back to ports and HDMA/ATA phases, completes or schedules the next phase, and advances the single HDMA queue.

## State and persistence behavior

Runtime state includes local DIMM contents, HDMA queue producer/consumer counters, in-flight queued commands, MMIO sequence masks, and optional module parameter `dimm_test`. No filesystem persistence occurs, but the driver programs volatile SDRAM/PLL/controller registers at probe.

## Dependencies and integration points

The driver depends on PCI, libata SFF command helpers, Promise packet helper definitions in `sata_promise.h`, DMA mapping, I2C-over-controller SPD access, kernel delay/sleep APIs, and SCSI opcode checks for ATAPI DMA policy.

## Risks

This driver has high state complexity: a single HDMA engine is shared by all ports, and read/write completion alternates between ATA and HDMA phases. Queue corruption or missed sequence bits can deadlock I/O. DIMM SPD parsing and ECC initialization are hardware-sensitive. Several comments still mark HDMA reset/freeze gaps as FIXME. Because ATAPI is mostly disabled and PIO polling is used, changing feature flags can expose untested paths.

## Test signals

Probe with real SX4 hardware and DIMMs of different sizes/speeds, enable `dimm_test`, run parallel four-port DMA read/write stress with data verification, inject errors during each HDMA/ATA phase, run reset/EH while HDMA is queued, and watch sequence-mask, HDMA dump, and DIMM initialization dmesg output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sx4.c -->
