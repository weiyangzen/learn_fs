<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.c

## Purpose
`qca_7k.c` implements low-level QCA7000/QCA7K SPI register access helpers and SPI error handling shared by the SPI netdev driver.

## Important APIs, Types, and Functions
- `qcaspi_spi_error()` marks the device out of sync and increments `spi_err` when an SPI transaction fails while ready.
- `qcaspi_read_register()` builds a two-transfer internal-register read command and returns a host-endian 16-bit value.
- `__qcaspi_write_register()` performs the raw internal-register write.
- `qcaspi_write_register()` optionally verifies writes by reading back and retrying up to the caller-supplied count.

## Control Flow
Read/write helpers assemble big-endian SPI command words using `QCA7K_SPI_READ/WRITE | QCA7K_SPI_INTERNAL | reg`, handle legacy mode by splitting command and data into separate `spi_sync()` calls, then return SPI/message status. Verified writes loop until readback matches or retries are exhausted.

## State and Persistence
The functions mutate `qca->sync` and statistics on errors. Successful calls persist values in QCA7K internal registers.

## Dependencies and Integration Points
Depends on Linux SPI and netdev APIs plus `qca_7k.h`/`qca_spi.h`. Higher-level SPI driver code uses these helpers for signature checks, interrupt masking/ack, buffer sizing, reset control, and watermarks.

## Risks and Edge Cases
- `qcaspi_spi_error()` ignores errors before ready, so early sync failures rely on caller logic.
- Verified writes return a boolean mismatch value after retry exhaustion rather than a conventional negative errno.
- Legacy mode doubles transaction boundaries and is timing-sensitive.
- Callers must serialize access through the SPI thread/driver path where appropriate.

## Test Signals
Good signature reads, successful interrupt enable/cause writes, write-verify stats staying at zero, and recovery from induced SPI failures validate the helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.c -->
