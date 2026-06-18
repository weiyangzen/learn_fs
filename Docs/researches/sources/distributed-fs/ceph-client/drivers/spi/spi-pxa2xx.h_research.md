# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.h

## Purpose
`spi-pxa2xx.h` is the private shared header for the PXA2xx SPI core, DMA helper, and glue drivers. It defines the controller platform-data contract, the shared runtime `driver_data`, register access helpers, DMA constants, and exported core/DMA/PM entry points.

## Important APIs, Types, And Functions
- `struct pxa2xx_spi_controller` is the glue-to-core configuration: chip-select count, DMA enable/burst size/filter parameters, target/slave mode, and embedded `ssp_device` for non-PXA enumeration.
- `struct driver_data` is the central runtime state used by core and DMA code: SSP, type, SPI controller, masks, `atomic_t dma_running`, transfer cursors, bytes-per-word, reader/writer callbacks, transfer handler, LPSS base, and optional ready GPIO.
- `pxa2xx_spi_read()` and `pxa2xx_spi_write()` wrap PXA SSP register access.
- `pxa25x_ssp_comp()`, `clear_SSCR1_bits()`, `read_SSSR_bits()`, and `write_SSSR_CS()` encode common variant-specific register handling.
- Constants `DMA_ALIGNMENT`, `MAX_DMA_LEN`, and `DEFAULT_DMA_CR1` define DMA constraints and service bits.
- Declarations expose DMA helper functions, `pxa2xx_spi_probe()`, `pxa2xx_spi_remove()`, and `pxa2xx_spi_pm_ops`.

## Control Flow
The header itself has no runtime control flow, but it defines the shared call graph: platform/PCI glue fills `pxa2xx_spi_controller` and calls `pxa2xx_spi_probe()`, the core fills `driver_data`, transfer code optionally calls DMA helpers, and remove/PM callbacks are shared back to glue modules.

## State And Persistence Behavior
All state described here is in-memory kernel runtime state. The embedded `ssp_device` allows glue drivers without legacy PXA SSP registration to still pass MMIO/IRQ/clock/type data to the core. The `atomic_t dma_running` field is a cross-file synchronization point between DMA callbacks and IRQ error handling.

## Dependencies And Integration Points
This header depends on Linux DMA engine, IRQ return types, size constants, `linux/pxa2xx_ssp.h`, SPI forward declarations, and GPIO descriptors. It is the integration boundary between `spi-pxa2xx.c`, `spi-pxa2xx-dma.c`, `spi-pxa2xx-platform.c`, and `spi-pxa2xx-pci.c`.

## Risks
- Any change to `struct driver_data` affects both core and DMA code.
- `write_SSSR_CS()` preserves alternate frame bits only for CE4100 and Quark; adding variants requires revisiting this helper.
- `MAX_DMA_LEN` and `DMA_ALIGNMENT` are exported policy for all glue users.
- The platform-data structure mixes firmware-derived config, DMA filter state, and embedded hardware object, so initialization ownership must remain clear.

## Test Signals
- Compile coverage with and without each PXA2xx glue module.
- DMA and non-DMA builds using all declared helper functions.
- Variant behavior in `pxa25x_ssp_comp()` and `write_SSSR_CS()`.
- Namespace imports from PCI/platform modules.
