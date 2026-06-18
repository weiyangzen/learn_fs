# sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_spi.c

## Purpose

`mmc_spi.c` implements an MMC host driver that speaks the SD/MMC SPI transport over a generic Linux SPI controller. It maps MMC requests into SPI command frames, response parsing, block tokens, CRC handling, chip-select management, optional platform power/card-detect glue, and MMC host registration for `"mmc-spi-slot"` devices.

## Important APIs, Types, And Functions

- Protocol constants define SPI data-response codes, data tokens, 512-byte block size, busy/init timeouts, and maximum blocks per request.
- `struct scratch` holds per-command status bytes, a data token, and CRC storage.
- `struct mmc_spi_host` stores the MMC host, SPI device, power state, platform data, reusable SPI transfers/messages for data and status, scratch buffer, and an all-ones transmit buffer.
- `mmc_spi_readbytes()`, `mmc_spi_skip()`, `mmc_spi_wait_unbusy()`, and `mmc_spi_readtoken()` implement low-level polling while keeping chip select active.
- `mmc_spi_response_get()` parses SPI R1/R1B/R2/R3/R4/R5/R7-style responses, including bit-shifted response recovery and busy waiting.
- `mmc_spi_command_send()` formats a 6-byte command plus CRC7, performs a full-duplex SPI transfer, and delegates response parsing.
- `mmc_spi_setup_data_message()` builds reusable SPI messages for read/write block bodies, CRCs, data tokens, and early write status.
- `mmc_spi_writeblock()` sends one data block, validates the data-response token bit pattern, advances TX buffer, and waits until not busy.
- `mmc_spi_readblock()` scans for a data token, handles bit-shifted data streams, optionally validates CRC16, and advances RX buffer.
- `mmc_spi_data_do()` iterates scatterlist entries and 512-byte blocks, maps pages with `kmap()`, transfers each block, updates `bytes_xfered`, flushes read pages, and sends multi-block write stop token.
- `mmc_spi_request()` locks the SPI bus, sends command/data/stop, retries CRC data errors up to five times using a synthetic STOP_TRANSMISSION, releases the bus, and completes the MMC request.
- `mmc_spi_set_ios()` handles platform power switching, initialization clocks with chip-select high, power-off line grounding, and SPI clock updates.
- `mmc_spi_probe()` validates full-duplex SPI, configures mode/bits, allocates buffers/host, reads platform data/OCR/caps, sets MMC limits/caps, initializes card-detect glue/GPIOs, and adds the host.

## Control Flow And State

MMC requests are serialized by `spi_bus_lock()`. The driver sends the command with chip select left active if data follows. Data transfers use SPI block tokens rather than native controller DMA descriptors: for each SG segment, the driver maps the page, points the reusable SPI transfer at the SG data, and loops block by block through `mmc_spi_writeblock()` or `mmc_spi_readblock()`. Multi-block writes end with a `SPI_TOKEN_STOP_TRAN` sequence and busy wait. If data had a CRC error, the request path sends STOP_TRANSMISSION, clears the data error, and retries the full command up to five times.

Response state is stored in `cmd->resp[0]` for SPI R1/R2-style status and `cmd->resp[1]` for four-byte SPI responses. The scratch buffer is reused for command status, data token, CRC, and busy polling. Power state persists in `host->power_mode`, and `mmc_spi_set_ios()` only performs platform power or init sequence when the mode changes.

Probe state includes an allocated all-ones block buffer used as TX filler for reads and busy polling, plus platform data callbacks for init/exit/setpower. Remove disables future detect callbacks, removes the host, frees buffers, restores `spi->max_speed_hz`, and releases platform data.

## Dependencies And Integration Points

The driver depends on Linux SPI core full-duplex transfer support, MMC core SPI response flags, CRC7 and CRC-ITU-T helpers, scatterlists, highmem `kmap/kunmap`, GPIO slot helpers, and optional `linux/spi/mmc_spi.h` platform data. It matches both SPI ID and OF compatible `"mmc-spi-slot"`.

## Risks And Edge Cases

- The driver requires full-duplex SPI controllers and warns when the controller cannot go down to 400 kHz.
- Chip-select behavior is critical. The comments call out dependence on controllers honoring `cs_change` and lack of safe shared-bus semantics.
- Response and data tokens may be bit-shifted by real cards; the driver contains custom recovery paths that are easy to regress.
- Multi-block write stop token handling is not the same as MMC command STOP_TRANSMISSION and must preserve chip select and busy polling.
- Data transfers use `kmap()` and do not allow highmem-style asynchronous DMA ownership; each block is transferred synchronously.
- Power-off mode temporarily rewrites SPI mode and clocks a null byte to ground card inputs; failure paths only log debug messages.
- Card detect GPIOs are requested after `mmc_add_host()`, so deferred GPIO probe removes the host and unwinds buffers.

## Test Signals

Validation should include probe rejection on half-duplex controllers, SPI mode 0 and platform-selected mode 3, command-only requests, all SPI response types, bit-shifted response/data token recovery, single and multi-block reads/writes, CRC enabled/disabled operation, CRC retry loop, multi-block write stop token, card-detect IRQ/GPIO and polling fallback, write-protect GPIO, platform power callbacks and init/exit, speed changes from `set_ios`, and removal cleanup.
