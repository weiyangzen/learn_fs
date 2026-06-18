# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-pci.c

## Purpose
Provides PCI glue for the DesignWare SPI core on Intel MID and Elkhart Lake PSE controllers. It maps PCI BAR resources, allocates IRQ vectors, applies device-specific descriptors, enables DMA setup, registers the shared DW SPI controller, and wires PM callbacks.

## Important APIs, Types, And Functions
`struct dw_spi_pci_desc` supplies setup callback, chip-select count, bus number, and maximum frequency. `dw_spi_pci_mid_init()` reads the Intel MID clock-control register and installs Medfield DMA ops. `dw_spi_pci_generic_init()` installs generic DMA ops. Probe/remove are `dw_spi_pci_probe()` and `dw_spi_pci_remove()`, with sleep PM handled by `dw_spi_pci_suspend()` and `dw_spi_pci_resume()`.

## Control Flow
Probe enables the PCI device with managed PCI helpers, allocates `struct dw_spi`, stores BAR physical address, enables bus mastering, allocates one IRQ vector, maps BAR0, sets IRQ, applies descriptor fields, calls the descriptor setup hook, registers the DW controller, records drvdata, and enables runtime autosuspend. Remove forbids runtime PM, resumes the device without changing state, unregisters the DW controller, and frees IRQ vectors. Sleep PM delegates entirely to the shared DW core.

## State And Persistence
Runtime state is held in `struct dw_spi` and PCI core structures. Intel MID clock-derived `max_freq`, descriptor bus number, chip-select count, mapped BAR, and DMA ops are established at probe. No persistent state is written.

## Dependencies And Integration Points
Depends on the PCI subsystem, runtime PM, PCI IRQ vector allocation, and `spi-dw.h` shared core APIs. Device IDs cover Intel MID controller IDs and Elkhart Lake PSE SPI PCI IDs. The module imports namespace `SPI_DW_CORE`.

## Risks
MID clock discovery uses a fixed physical control register mapping; incorrect assumptions here affect clock calculations. Probe error handling frees IRQ vectors but relies on managed mapping/allocation for other resources. Descriptor absence is fatal. Runtime PM autosuspend behavior depends on the shared core being prepared for idle transitions.

## Test Signals
PCI probe/remove for all IDs, IRQ allocation failures, BAR mapping failures, MID clock-divisor validation, DMA channel discovery, runtime autosuspend, and suspend/resume transfer continuity are the main signals.
