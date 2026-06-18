# sources/distributed-fs/ceph-client/drivers/spi/spi-rb4xx.c

## Purpose
`spi-rb4xx.c` is a minimal SPI controller driver for MikroTik RB4xx boards using AR71xx-style GPIO-mode SPI registers. It bit-bangs bytes through a memory-mapped IOC register, supports a board-specific dual-bit transmit mode for the CPLD, and exposes three chip selects.

## Important APIs, Types, And Functions
- `struct rb4xx_spi` stores the MMIO base and AHB clock.
- `rb4xx_read()` and `rb4xx_write()` access raw registers.
- `do_spi_clk()` clocks one output bit through DO and CLK fields.
- `do_spi_byte()` sends one byte MSB-first in single-bit mode.
- `do_spi_clk_two()` and `do_spi_byte_two()` send two bits per clock using CS2 as the second data line.
- `rb4xx_transfer_one()` selects board-specific CS mask, bit-bangs each byte, optionally reads `RDS`, and finalizes the transfer.
- `rb4xx_spi_probe()` maps resources, enables AHB clock, configures SPI controller capabilities, registers it, and switches hardware to GPIO/SPI function mode.

## Control Flow
Probe maps the MMIO resource, allocates a SPI host, enables the AHB clock, sets `num_chipselect = 3`, advertises `SPI_TX_DUAL`, requires TX buffers, registers `transfer_one` and `set_cs`, then writes the function-select register to enable GPIO SPI mode. Transfers compute the IOC chip-select baseline: CS2 devices use CS0 for MMC, while boot flash/CPLD use CS1 due to board wiring. Each TX byte is clocked as single-bit or dual-bit based on `t->tx_nbits`; RX reads capture the read-data-shift register after each byte.

## State And Persistence Behavior
The driver has no persistent storage and minimal runtime state. It does not maintain per-device state. Chip select is encoded directly in each IOC write during bit-banging. Probe-managed resources handle lifetime cleanup.

## Dependencies And Integration Points
It depends on platform/OF matching (`mikrotik,rb4xx-spi`), the common clock framework, SPI core, and board-specific AR71xx register semantics. It marks `SPI_CONTROLLER_MUST_TX`, so the SPI core should provide dummy TX when clients request reads.

## Risks
- Board-specific CS sharing between boot flash and CPLD is encoded in the transfer path and relies on non-clashing command sets.
- Dual-bit mode abuses CS2 as a second data output, so generic dual-SPI assumptions do not apply.
- There is no speed control, delay tuning, error reporting, or runtime PM.
- Raw MMIO access and bit-banging depend on CPU timing and AHB clock behavior.

## Test Signals
- Boot flash, CPLD, and MMC chip-select behavior on RB4xx hardware.
- Single-bit and `SPI_NBITS_DUAL` TX transfers.
- RX sampling from `RDS` with controller-provided dummy TX.
- Probe with AHB clock and function-select register write.
