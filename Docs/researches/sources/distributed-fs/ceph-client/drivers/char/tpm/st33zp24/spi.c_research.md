<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/spi.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/spi.c

## Purpose
Implements the SPI physical transport for ST33ZP24 TPM 1.2 devices, including ST-specific status-byte handling and latency detection.

## Important APIs, Types, And Functions
Defines `struct st33zp24_spi_phy`, `st33zp24_status_to_errno()`, `st33zp24_spi_send()`, `st33zp24_spi_read8_reg()`, `st33zp24_spi_recv()`, `st33zp24_spi_evaluate_latency()`, `st33zp24_spi_probe()`, and `st33zp24_spi_remove()`. Registers SPI IDs, OF compatible `st,st33zp24-spi`, ACPI ID `SMO3324`, and PM ops from the common core.

## Control Flow
Probe allocates the SPI physical context, measures required latency by reading `TPM_INTF_CAPABILITY` with increasing dummy-byte counts, then calls `st33zp24_probe()`. Send constructs a pre-header with write direction and locality, optionally inserts FIFO length, appends payload, clocks latency bytes, and decodes the final status byte. Receive constructs a read pre-header, clocks latency plus payload bytes, checks the pre-payload status, and returns the requested byte count on success.

## State And Persistence
The SPI context persists in devm memory and holds large transmit/receive scratch buffers plus the detected latency. The latency value affects every later transaction.

## Dependencies And Integration Points
Integrates with the Linux SPI core, ACPI/OF matching, and shared ST33ZP24 TPM core through `struct st33zp24_phy_ops`.

## Risks And Edge Cases
Latency detection failure prevents probe. ST status codes map to protocol, size, unsupported, or raw errors; an unmapped status is returned directly. FIFO length insertion happens only for `TPM_DATA_FIFO`, so register framing must match hardware expectations.

## Test Signals
SPI transfer tests with varying latency, status-code fault injection, FIFO command/response paths, ACPI/OF matching, suspend/resume, and boundary tests around `ST33ZP24_SPI_BUFFER_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/st33zp24/spi.c -->
