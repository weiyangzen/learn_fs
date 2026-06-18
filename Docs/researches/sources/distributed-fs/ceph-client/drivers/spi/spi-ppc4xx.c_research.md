# sources/distributed-fs/ceph-client/drivers/spi/spi-ppc4xx.c

## Purpose
`spi-ppc4xx.c` is a simple Open Firmware platform driver for IBM PPC4xx SPI controllers. The hardware has no FIFO, so the driver sends one byte at a time and waits for an interrupt for each received byte. It uses the legacy `spi_bitbang` helper to provide SPI controller services while still driving native controller registers.

## Important APIs, Types, And Functions
- `struct spi_ppc4xx_regs` describes the byte-wide mode, RX, TX, control, status, and clock divisor registers.
- `struct ppc4xx_spi` stores the bitbang controller, completion, register mapping, IRQ, OPB clock frequency, active transfer length/counter, current TX/RX buffers, and SPI controller pointer.
- `struct spi_ppc4xx_cs` stores the precomputed mode register value for each SPI device.
- `spi_ppc4xx_setup()` validates `max_speed_hz` and builds mode bits from SPI mode and `SPI_LSB_FIRST`.
- `spi_ppc4xx_setupxfer()` programs mode and clock divisor for a transfer.
- `spi_ppc4xx_txrx()` starts byte zero and sleeps on a completion until the IRQ handler finishes the buffer.
- `spi_ppc4xx_int()` handles byte completion, reads RX, writes the next TX byte, and completes the transfer when all bytes are done.
- `spi_ppc4xx_of_probe()` performs OF resource lookup, OPB clock discovery, mapping, IRQ request, controller setup, and `spi_bitbang_start()`.

## Control Flow
Probe allocates a SPI controller with `struct ppc4xx_spi`, configures `spi_bitbang` callbacks, reads the OPB `clock-frequency`, maps the SPI register block, requests the IRQ, enables the shared SPI/I2C pinmux via DCR, and starts the bitbang controller. Per-device setup caches the static mode register value. Per-transfer setup programs the cached mode and computes the CDM prescaler from the requested speed.

During a transfer, `spi_ppc4xx_txrx()` stores buffer pointers and length, writes the first byte to `txd`, sets `SPI_PPC4XX_CR_STR`, and waits. Each IRQ reads status, busy-waits briefly if `BSY` is still set, reads `rxd`, stores it if RX is present, writes the next byte if any, or completes the transfer.

## State And Persistence Behavior
There is no persistent on-disk state. Per-device `controller_state` holds only the cached mode byte. Active transfer state in `struct ppc4xx_spi` is overwritten for each transfer and synchronized by completion. The register mapping and IRQ live from probe to remove. Remove stops bitbang, releases memory/IRQ resources, unmaps registers, and releases the SPI controller.

## Dependencies And Integration Points
The file depends on OF platform probing, PowerPC DCR access for pinmux enablement, `spi_bitbang`, and standard SPI core setup/cleanup callbacks. Chip selects are expected to be represented by GPIO descriptors; `num_chipselect` is set to zero so SPI core derives the count from GPIO descriptors.

## Risks
- One interrupt per byte can produce high CPU load; the header comment explicitly points to `max_speed_hz` throttling via DT as mitigation.
- The IRQ handler has a fixed short busy-wait loop for undocumented BSY/RBR timing; if the hardware remains busy it completes with a partial count rather than a rich error path.
- Clock divisor calculation clamps to 8 bits and can only approximate requested speeds.
- No DMA or FIFO path exists, so large transfers are inherently expensive.

## Test Signals
- OF probe with `ibm,ppc4xx-spi`, valid OPB node, clock property, memory resource, and IRQ.
- SPI mode 0-3 and `SPI_LSB_FIRST` setup.
- Transfers with TX-only, RX-only, and full-duplex buffers.
- Slow device operation where status remains busy at IRQ entry.
- Removal after active controller registration.
