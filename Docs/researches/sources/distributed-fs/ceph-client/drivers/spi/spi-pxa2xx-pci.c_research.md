# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx-pci.c

## Purpose
`spi-pxa2xx-pci.c` is PCI glue for PXA2xx-compatible Intel SPI/SSP controllers, including Quark X1000, Bay Trail, Merrifield, Braswell, CE4100, and Lynx Point. It maps PCI resources, creates fixed-rate clocks, fills `pxa2xx_spi_controller` and `ssp_device` platform data, wires platform-specific DMA filter parameters, and delegates the actual SPI controller implementation to `pxa2xx_spi_probe()`.

## Important APIs, Types, And Functions
- `struct pxa_spi_info` holds a setup callback selected from the PCI ID table.
- Static `dw_dma_slave` structures encode source/destination request IDs for each LPSS/Merrifield/Braswell/LPT instance.
- `pxa2xx_spi_pci_clk_register()` creates a fixed-rate clock named from the SSP port ID.
- `lpss_dma_filter()` binds DesignWare DMA channels by `dma_dev` and stores the slave config in `chan->private`.
- `lpss_spi_setup()`, `mrfld_spi_setup()`, `ce4100_spi_setup()`, and `qrk_spi_setup()` fill SSP type, port ID, chip select count, clock rate, DMA parameters, and DMA burst size.
- `pxa2xx_spi_pci_probe()` enables the PCI function, maps BAR0, runs the selected setup, allocates IRQ vectors, calls the PXA2xx core probe, and enables runtime PM.
- `pxa2xx_spi_pci_remove()` disables runtime PM and calls `pxa2xx_spi_remove()`.

## Control Flow
The PCI ID table associates each supported device with a setup profile. Probe uses managed PCI enablement and BAR mapping, allocates a controller data object, initializes `ssp_device` physical/MMIO fields, applies the selected profile, marks the device bus-master capable, allocates one IRQ vector, stores `ssp->irq`, and calls the shared PXA2xx core. Runtime PM autosuspend is configured only after the core probe succeeds.

## State And Persistence Behavior
This file creates only runtime kernel state. Fixed-rate clocks are registered with a managed cleanup action. DMA device references from `pci_get_slot()` are released via managed cleanup. `pxa2xx_spi_controller` and embedded `ssp_device` persist for the PCI device lifetime and are consumed by `spi-pxa2xx.c`.

## Dependencies And Integration Points
The file integrates PCI, runtime PM, fixed-rate clock provider, DesignWare DMA platform data, and the exported `"SPI_PXA2xx"` namespace from the core driver. Hardware identity and per-function port numbering are encoded in the PCI ID table and setup switch statements.

## Risks
- Correct DMA operation depends on hard-coded DMA request IDs and DMA-device slot lookup for each Intel platform.
- `pci_get_slot()` returning NULL is not explicitly checked before storing `dma_dev->dev`, so unusual PCI topology could be fragile.
- CE4100 sets `num_chipselect` to `devfn`, which is legacy-specific and should be tested with actual firmware descriptions.
- Runtime PM is enabled after core probe; failures before that rely on managed cleanup plus PCI core cleanup.

## Test Signals
- Probe/remove for every PCI ID table entry.
- DMA channel matching on BYT, BSW, LPT, and MRFLD devices.
- Fixed-rate clock registration names and rates: 50 MHz LPSS/Quark, 25 MHz MRFLD, 3.6864 MHz CE4100.
- IRQ vector allocation and transfer IRQ delivery.
- Runtime autosuspend/resume after transfers.
