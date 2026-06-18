# sources/distributed-fs/ceph-client/drivers/spi/spi-pxa2xx.c

## Purpose
`spi-pxa2xx.c` is the shared PXA2xx SSP SPI controller core. It supports PXA/CE4100/Quark/Merrifield/Intel LPSS/MMP2 SSP variants, SPI host and target modes, interrupt-driven PIO transfers, DMA transfers through `spi-pxa2xx-dma.c`, LPSS private chip-select handling, runtime/system PM, and exported probe/remove/PM APIs for PCI and platform glue.

## Important APIs, Types, And Functions
- `struct chip_data` stores per-SPI-device CR1 mode bits, Quark DDS rate, FIFO thresholds, and LPSS/MRFLD thresholds.
- `struct lpss_config` describes LPSS private register offsets, thresholds, chip-select select fields, and clock-gating quirks.
- `pxa2xx_spi_probe()` and `pxa2xx_spi_remove()` are exported in namespace `"SPI_PXA2xx"` for glue drivers.
- `pxa2xx_spi_transfer_one()` is the central transfer path, selecting PIO/DMA, programming clocks and frame size, configuring FIFO thresholds, enabling SSP, and returning asynchronous completion.
- `ssp_int()` is the shared IRQ top-level handler; it filters shared/powered-off IRQs and dispatches to `interrupt_transfer()` or `pxa2xx_spi_dma_transfer()`.
- `interrupt_transfer()` drains RX, fills TX, handles overrun/underrun/timeout, and finalizes PIO transfers.
- `setup()` and `cleanup()` allocate/free per-device `chip_data`.
- LPSS helpers `lpss_ssp_setup()`, `lpss_ssp_select_cs()`, and `lpss_ssp_cs_control()` configure private registers and software CS.
- PM operations are exported through `pxa2xx_spi_pm_ops`.

## Control Flow
Glue code constructs `struct pxa2xx_spi_controller` and `struct ssp_device`, then calls `pxa2xx_spi_probe()`. The core allocates host or target controller, initializes mode/bpw masks and callbacks, requests a shared IRQ, attempts DMA setup if requested, enables the SSP clock, programs default SSCR registers per SSP type, initializes LPSS private registers and CS count where applicable, optionally gets target ready GPIO, and registers the SPI controller.

Per-device `setup()` computes thresholds and CR1 mode bits from SSP type, SPI mode, and target/host role. On each transfer, `pxa2xx_spi_transfer_one()` flushes the FIFO, sets TX/RX cursors, computes clock divider including Quark DDS handling, selects reader/writer functions based on bits-per-word, prepares DMA if the SPI core DMA-mapped the transfer, programs SSCR0/SSCR1 and variant threshold registers, enables SSP, primes target-mode TX data and ready GPIO, then enables service/interrupt bits. Completion happens in the IRQ handler for PIO or DMA callback/overrun handling for DMA.

## State And Persistence Behavior
The driver maintains controller lifetime state in `struct driver_data`: SSP pointer/type, controller pointer, masks, DMA running flag, active transfer cursors, active reader/writer callbacks, transfer handler, LPSS base, and optional ready GPIO. Per-device state persists in `chip_data`. Hardware registers are reprogrammed per transfer when relevant. Runtime PM only gates the SSP clock; system suspend stops the SPI queue, disables SSP, and conditionally disables the clock depending on runtime state.

## Dependencies And Integration Points
The core depends on PXA SSP register definitions/helpers, SPI core asynchronous transfer API, DMA support from `spi-pxa2xx-dma.c`, platform data/glue in `spi-pxa2xx-platform.c` and `spi-pxa2xx-pci.c`, clocks, GPIO descriptors, runtime PM, firmware CS translation, and target-mode SPI support. It exports its APIs under `"SPI_PXA2xx"`.

## Risks
- Variant-specific masks and thresholds are complex; regressions can affect only one SSP generation.
- Transfer length is assumed to align with bits-per-word because `n_words = len / w_size`; odd lengths with wide words need SPI core validation coverage.
- MMP2 has special behavior where disabling SSE corrupts RX FIFO, and code works around possible garbage in TX FIFO.
- DMA is limited to `MAX_DMA_LEN` and transfers larger than that are forced to PIO with a ratelimited warning.
- LPSS CS switching uses a delay derived from `max_speed_hz` and toggles private clock-gating registers for some variants.
- Shared IRQ filtering must correctly handle runtime-suspended or powered-off devices.

## Test Signals
- PIO transfers for 4-32 bpw, TX-only, RX-only, and full-duplex paths.
- DMA transfer setup, completion, overrun race, and fallback when channels are absent.
- Quark DDS clock divisor accuracy and CE4100/PXA25x clock paths.
- LPSS chip-select selection, CS-high behavior, and clock-gating workaround.
- Target mode with `ready` GPIO.
- Runtime PM, system suspend/resume, and shared IRQ noise.
