# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_main.c

## Purpose
Implements the generic native SPI TPM TIS/PTP PHY and SPI driver dispatch layer.

## Important APIs, Types, And Functions
Exports `tpm_tis_spi_transfer()` and `tpm_tis_spi_init()`. Transfer helpers are `tpm_tis_spi_flow_control()`, `tpm_tis_spi_transfer_half()`, `tpm_tis_spi_transfer_full()`, `tpm_tis_spi_read_bytes()`, and `tpm_tis_spi_write_bytes()`. Probe dispatch uses `tpm_tis_spi_probe()`, `tpm_tis_spi_driver_probe()`, and device-id/of-match function pointers.

## Control Flow
Generic probe allocates the SPI PHY, sets standard flow control, enables `SPI_TPM_HW_FLOW` for half-duplex controllers, chooses device IRQ if present, initializes completion, and calls `tpm_tis_spi_init()`. Full-duplex transfer locks the SPI bus, sends a four-byte TPM SPI header with chip-select held, performs flow control by clocking one-byte reads until ready, transfers up to 64 data bytes, and repeats. Half-duplex transfer builds one SPI message with command, address, and data phases so capable controllers can manage hardware flow control. Driver probe dispatches to Cr50 or generic probe based on OF/SPI id data.

## State And Persistence
Per-device state stores SPI device, flow-control callback, completion, wake-after timestamp, and reusable I/O buffer. No persistent TPM state is stored.

## Dependencies And Integration Points
Integrates with `tpm_tis_core_init()` through PHY ops, SPI controller flags, OF compatibles, ACPI `SMO0768`, and optional Cr50 probe.

## Risks And Edge Cases
Full-duplex flow control requires bus lock and explicit chip-select deactivation on error. Half-duplex controllers depend on controller-level `SPI_TPM_HW_FLOW`. Maximum SPI frame is 64 bytes, so large FIFO transfers are chunked. Probe dispatch must handle missing id match data cleanly.

## Test Signals
Full-duplex and half-duplex controllers, flow-control timeout, chunked reads/writes, error cleanup deasserting chip select, IRQ and no-IRQ modes, generic device IDs, Cr50 dispatch, and PM resume callback wiring.
