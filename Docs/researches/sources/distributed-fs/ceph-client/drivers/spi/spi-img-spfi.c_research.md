# sources/distributed-fs/ceph-client/drivers/spi/spi-img-spfi.c

## Purpose

`spi-img-spfi.c` is the Imagination Technologies SPFI controller driver. It supports PIO and DMA transfers, CPOL/CPHA, dual and optional quad modes, runtime PM, system sleep, configurable maximum frequency, and per-chipselect clock/mode programming.

## Important APIs, Types, and Functions

`struct img_spfi` stores the SPI controller, lock, MMIO base/physical address, IRQ, clocks, DMA channels, and DMA busy flags. PIO helpers are `spfi_pio_write32()`, `spfi_pio_write8()`, `spfi_pio_read32()`, `spfi_pio_read8()`, and `img_spfi_start_pio()`. DMA helpers are `img_spfi_start_dma()`, `img_spfi_dma_rx_cb()`, and `img_spfi_dma_tx_cb()`. Controller callbacks are `img_spfi_prepare()`, `img_spfi_unprepare()`, `img_spfi_config()`, `img_spfi_transfer_one()`, `img_spfi_can_dma()`, and `img_spfi_handle_err()`.

## Control Flow

Probe allocates a controller, maps MMIO, requests an IRQ for illegal-access reporting, enables `sys` and `spfi` clocks, resets the controller, enables only the IACCESS interrupt, configures SPI mode and speed limits, optionally requests TX/RX DMA channels, enables runtime PM, and registers the controller. Message prepare programs chip select, CPOL, and CPHA in `SPFI_PORT_STATE`; unprepare resets the controller after a message.

For each transfer, `img_spfi_config()` calculates the bit clock divider, programs transaction size, selects DMA directions, selects single/dual/quad transfer mode, and enables the serial engine bit. Small transfers use PIO polling: start SPFI, write/read FIFO windows until buffers drain, then wait for ALLDONE. Larger transfers use DMA if both channels exist: configure bus widths based on transfer length alignment, submit RX before starting the controller, start SPFI, submit TX, and finalize when both DMA callbacks have run.

## State and Persistence Behavior

Persistent driver state is limited to clock handles, DMA channel handles, and busy flags. Hardware registers are reset after each message and after PIO timeout. Runtime suspend disables both clocks; runtime resume re-enables them. DMA callbacks update volatile busy flags under a spinlock. No persistent storage is maintained.

## Dependencies and Integration Points

The driver depends on platform resources, OF compatible `img,spfi`, optional DT property `img,supports-quad-mode`, optional `spfi-max-frequency`, Linux clock APIs, DMAengine, IRQ handling, runtime PM, and the SPI core. It uses GPIO descriptors for chip selects.

## Risks and Edge Cases

PIO pointer arithmetic is performed on `void *` buffers, relying on GNU C behavior. DMA completion callbacks call `spfi_wait_all_done()`, so both RX and TX callbacks may poll ALLDONE; races are moderated by busy flags but timing should be tested. DMA is selected solely by length greater than 64 bytes and requires both channels; partial DMA availability falls back to PIO. `img_spfi_handle_err()` terminates DMA but does not reset the controller itself. Transfer length is limited to 16 bits.

## Test Signals

Test PIO lengths below/equal/above FIFO size, DMA with aligned and unaligned lengths, RX-only/TX-only/full-duplex, illegal access IRQ, timeout reset, dual and quad transfers, `spfi-max-frequency` clamping, missing DMA channel fallback, runtime suspend/resume, system suspend/resume reset, and transfer length rejection above `0xffff`.
