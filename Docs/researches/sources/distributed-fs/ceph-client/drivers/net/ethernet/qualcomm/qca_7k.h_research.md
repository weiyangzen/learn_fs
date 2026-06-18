<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.h

## Purpose
`qca_7k.h` defines QCA7000/QCA7K SPI command bits, register addresses, interrupt bits, buffer sizes, and low-level helper prototypes.

## Important APIs, Types, and Data
- Command flags distinguish read/write and internal/external address spaces.
- Defines command length, hardware packet-length overhead, and hardware buffer length.
- Register addresses cover buffer size, write-buffer space, read-buffer bytes, SPI config/status, interrupt cause/enable, watermarks, signature, and action control.
- Interrupt bits cover write-buffer watermark, CPU-on, address/write/read buffer errors, and packet availability.
- Declares `qcaspi_spi_error()`, `qcaspi_read_register()`, and `qcaspi_write_register()`.

## Control Flow
No runtime flow exists. The constants are used to build SPI transactions and interpret interrupts.

## State and Persistence
The header describes on-chip register state and interrupt bits. It owns no software state.

## Dependencies and Integration Points
Includes `qca_spi.h`, which creates a circular include relationship resolved by include guards. It is used by SPI register helpers, the SPI netdev driver, and debug/ethtool register dumping.

## Risks and Edge Cases
Register address and bit definitions are protocol contracts; mistakes break synchronization, reset, or data movement. The hardware buffer length constrains TX ring sizing and RX validation.

## Test Signals
Successful signature reads (`0xAA55`), interrupt handling, and TX/RX buffer-space accounting are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k.h -->
