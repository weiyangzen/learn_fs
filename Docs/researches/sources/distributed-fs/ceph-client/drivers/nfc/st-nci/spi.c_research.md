# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/spi.c

## Purpose
`spi.c` is the SPI physical layer for ST_NCI chips. It mirrors the I2C transport's reset/IRQ behavior while using SPI transfers and feeding full-duplex received bytes back into NDLC.

## Important APIs, types, and functions
- `struct st_nci_spi_phy` stores SPI device, NDLC pointer, IRQ active flag, reset GPIO, and secure-element status.
- `st_nci_spi_enable()`/`st_nci_spi_disable()` reset the chip and manage IRQ active state.
- `st_nci_spi_write()` sends the skb over SPI and allocates an skb from the simultaneous RX buffer to pass to `ndlc_recv()`.
- `st_nci_spi_read()` reads the 4-byte prefix and declared payload via SPI receive-only transfers.
- Probe gets reset GPIO, reads SE properties, calls `ndlc_probe()`, and registers a threaded IRQ.

## Control flow
Runtime open enables reset/IRQ through NDLC. Writes are synchronous SPI transfers; because SPI is full duplex, any MISO data received during TX is wrapped and submitted to NDLC. IRQ-triggered reads perform a two-step size/payload receive and forward complete frames to NDLC. Remove calls `ndlc_remove()`.

## State and persistence
State is reset GPIO, IRQ active flag, NDLC powered/hard-fault state, and SE presence booleans. No persistent data is written.

## Dependencies and integration points
Dependencies include SPI core, GPIO/ACPI/OF, threaded IRQs, NCI packet sizes, and NDLC. Compatible string is `st,st21nfcb-spi`; ACPI ID includes `SMO2101`.

## Risks
`st_nci_spi_write()` feeds RX bytes from every TX transaction into NDLC without validating whether they are meaningful, relying on NDLC to discard/handle them. Invalid length in `st_nci_spi_read()` sets `hard_fault = 1`, unlike I2C, producing a permanent failure latch. The stack buffer is sized for max SPI frame plus headers; future max-size changes must keep it aligned.

## Test signals
Test write full-duplex receive handling, invalid length hard fault, IRQ read while unpowered, reset timing, SE property propagation, SPI/ACPI/OF matching, and cleanup through NDLC remove.
