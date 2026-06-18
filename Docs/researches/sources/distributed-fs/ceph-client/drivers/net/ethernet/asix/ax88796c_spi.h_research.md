# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_spi.h

## Purpose
Defines the AX88796C SPI transport ABI: command opcodes, SPI state structures, status structure, function prototypes, and inline register/status/wakeup wrappers.

## Important APIs, Types, and Functions
`struct axspi_data` stores the `spi_device`, reusable RX `spi_message`, two RX transfers, command buffer, register RX buffer, and compression flag. `struct spi_status` carries a 16-bit ISR and an 8-bit status with `AX_STATUS_READY`. Public helpers are `axspi_read_rxq()`, `axspi_write_txq()`, `axspi_read_reg()`, `axspi_write_reg()`, `axspi_read_status()`, and `axspi_wakeup()`. Inline wrappers expose `AX_READ`, `AX_WRITE`, `AX_READ_STATUS`, and `AX_WAKEUP`.

## Control Flow and State
No executable logic beyond wrapper calls. The header encodes command constants such as `READ_REG`, `WRITE_REG`, `READ_RXQ`, `WRITE_TXQ`, `READ_STATUS`, and `EXIT_PWD`, which are used by the SPI implementation and TX/RX paths.

## Dependencies and Integration Points
Included by `ax88796c_main.h` and `ax88796c_spi.c`. It depends on `linux/spi/spi.h` and kernel integer types. The compression flag is set by the main driver after soft reset based on private flags and hardware `SPICR` programming.

## Risks and Test Signals
Risk is mostly ABI drift between command constants and silicon behavior. Compile tests catch function signature mismatches. Runtime tests should verify that `AX_READ`/`AX_WRITE` remain serialized by callers and that compression does not change command layout incorrectly.
