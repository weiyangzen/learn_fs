# sources/distributed-fs/ceph-client/drivers/ata/pata_sil680.c

## Purpose
`pata_sil680.c` is a Silicon Image/CMD SiI 680 PATA controller driver. It programs device timing registers, supports 100/133 MHz clock variants, optionally uses MMIO on selected PowerPC Cell systems, and falls back to PCI I/O-port BMDMA initialization otherwise.

## Important APIs, Types, and Functions
Register selectors `sil680_selreg()` and `sil680_seldev()` map logical offsets into PCI config space. Core callbacks are `sil680_cable_detect()`, `sil680_set_piomode()`, `sil680_set_dmamode()`, `sil680_sff_exec_command()`, `sil680_sff_irq_check()`, `sil680_init_chip()`, `sil680_init_one()`, and resume-only `sil680_reinit_one()`. `sil680_port_ops` inherits `ata_bmdma32_port_ops`.

## Control Flow, State, and Persistence
Probe enables PCI, initializes the chip, selects UDMA6 or slower UDMA5 caps based on clocking, and either configures MMIO BAR 5 manually or calls `ata_pci_bmdma_init_one()`. `sil680_init_chip()` adjusts cache-line and clock config, writes default timing registers for both channels, and rejects disabled clocking. PIO setup writes per-device data timings, shared taskfile timing using the slowest peer PIO mode, and IORDY/mode bits in config register `0x80 + 4 * port`. DMA setup programs MWDMA or UDMA timing words and mode bits, selecting a UDMA timing table based on 100/133 MHz clock state.

## Dependencies and Integration Points
This driver integrates with libata SFF/BMDMA helpers, PCI managed MMIO mapping, DMA mask setup, PPC `machine_is(cell)` conditional MMIO behavior, and ATA IRQ checking through a controller-specific config-space status bit. Its `sff_exec_command` flushes PCI posting by reading BMDMA command space.

## Risks and Test Signals
Risks include clock misconfiguration, wrong UDMA table selection, shared taskfile timing too fast for the peer device, config-space versus MMIO path differences, and disabled-clock probe rejection. Tests should exercise PIO peer speed mixing, MWDMA and UDMA0-6 programming, cable-detect behavior, both MMIO and I/O-port paths where hardware allows, interrupt status handling, resume reinitialization, and long DMA transfers on 100 MHz and 133 MHz clock configurations.
