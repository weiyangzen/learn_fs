# sources/distributed-fs/ceph-client/drivers/spi/spi-altera-core.c

## Purpose

`spi-altera-core.c` is the shared transfer engine for Altera SPI controllers. It owns register-level chip-select handling, PIO transmit/receive, optional IRQ-driven completion, and host initialization. Bus-specific wrappers supply the regmap, register offset, IRQ, and controller registration.

## Important APIs, types, and functions

- Register definitions cover RX/TX data, status, control, and target-select registers.
- `altr_spi_writel()` and `altr_spi_readl()` wrap regmap accesses and add device error logging.
- `altera_spi_set_cs()` selects or deselects a chip by writing target-select and the SSO control bit.
- `altera_spi_tx_word()` and `altera_spi_rx_word()` marshal 1-, 2-, or 4-byte words between transfer buffers and hardware data registers.
- `altera_spi_txrx()` implements `host->transfer_one`, using either interrupt-driven or polling mode.
- `altera_spi_irq()` handles receive-ready interrupts and finalizes the transfer.
- `altera_spi_init_host()` assigns callbacks, disables interrupts, clears status, and flushes stale RX data.

## Control flow

For polling transfers, `altera_spi_txrx()` writes one word, spins until receive-ready, reads the word, and repeats until all words are complete, then calls `spi_finalize_current_transfer()`.

For IRQ transfers, it enables receive-ready interrupts, sends the first word, and returns `1` to indicate asynchronous completion. The IRQ handler reads the received word, writes the next word if any remain, or disables receive interrupts and finalizes the transfer.

Chip select is asserted before transfers by selecting `BIT(chipselect)` and setting SSO; it is deasserted by clearing SSO and target-select.

## State and persistence behavior

Per-transfer mutable state lives in `struct altera_spi` fields owned by the wrapper-provided controller data: `tx`, `rx`, `count`, `len`, `bytes_per_word`, `imr`, `regmap`, `regoff`, and `irq`. Hardware control state persists in the control and target-select registers until changed.

## Dependencies and integration points

The core depends on `linux/spi/altera.h` for `struct altera_spi`, the SPI framework, regmap, and exported symbols consumed by `spi-altera-platform.c` and `spi-altera-dfl.c`.

## Risks and edge cases

- Polling mode spins with `cpu_relax()` and no timeout; broken hardware can hang the transfer path.
- Only byte widths of 1, 2, and 4 are explicitly handled. Wrapper `bits_per_word_mask` must prevent unsupported widths.
- Error returns from regmap reads/writes are logged but transfer code generally continues with default values.
- Transfer length is divided by `bytes_per_word`; non-multiple lengths would truncate words and should be rejected by the SPI core or wrapper configuration.

## Test signals

Build both platform and DFL wrappers. Runtime tests should cover polling and IRQ modes, chipselect changes, 8/16/32-bit transfers, RX-only and TX-only buffers, and regmap error injection if available.
