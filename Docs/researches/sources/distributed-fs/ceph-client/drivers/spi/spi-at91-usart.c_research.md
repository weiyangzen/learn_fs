# sources/distributed-fs/ceph-client/drivers/spi/spi-at91-usart.c

## Purpose
Microchip AT91 USART-as-SPI controller driver. It reuses a USART parent device register block as an 8-bit SPI host with mandatory TX and RX, GPIO chip selects, optional DMA, interrupt-driven PIO fallback, and system/runtime PM.

## Important APIs, Types, and Functions
`struct at91_usart_spi` stores parent platform device, current transfer, registers, clock, completion, spinlock, physical base, IRQ, remaining byte counters, cached status, and DMA flag. DMA functions configure, release, stop, and execute slave DMA. PIO helpers read status, write THR, read RHR, and handle overrun. SPI callbacks are `at91_usart_spi_setup()`, `at91_usart_spi_prepare_message()`, `at91_usart_spi_transfer_one()`, `at91_usart_spi_unprepare_message()`, and cleanup.

## Control Flow
Probe obtains the parent USART memory and IRQ, gets the USART clock, allocates a SPI controller, sets GPIO CS support, maps registers, requests IRQ, enables the clock, initializes USART SPI mode, tries to configure DMA, initializes lock/completion, and registers the controller. Setup stores a per-device mode register in `spi->controller_state`. Prepare enables RX/TX, enables overrun/RX-ready interrupts, and writes the saved mode. Transfer programs baud rate, initializes byte counters, and loops while TX or RX remains. For sufficiently large transfers and available DMA, it submits RX and TX SG descriptors and waits for RX DMA completion. Otherwise it polls TX-ready and writes one byte, while RX data is drained by IRQ. Unprepare resets/disables RX/TX and interrupts.

## State and Persistence
Per-device mode state is dynamically allocated and freed in cleanup. Transfer state lives in remaining-byte counters and `current_transfer`. DMA channel pointers are stored in the SPI controller. Runtime PM gates the USART clock and pinctrl state.

## Dependencies and Integration Points
It depends on a parent USART platform device, clk, GPIO descriptors, pinctrl, DMAengine, IRQ, PM runtime, and SPI core flags `SPI_CONTROLLER_MUST_RX` and `SPI_CONTROLLER_MUST_TX`.

## Risks
DMA setup failure currently exits the probe path after clock enable instead of treating DMA as optional, despite transfer code having PIO fallback. PIO has no explicit per-transfer timeout in the main loop, relying on hardware progress and overrun detection. Cleanup declares a different pointer type name than setup allocated, but only frees it. DMA callback re-enables RX-ready IRQ after DMA and sets RX remaining to zero.

## Test Signals
Validate probe with and without DMA channels, 8-bit loopback, short PIO transfers, large DMA transfers, TX-only/RX-only core-provided dummy buffers, overrun injection, suspend/resume reinitialization, GPIO CS polarity, and baud-rate limits.
