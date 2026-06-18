# sources/distributed-fs/ceph-client/drivers/spi/spi-ar934x.c

## Purpose
SPI controller driver for Qualcomm Atheros AR934x and QCA95xx SoCs. It exposes a simple register-shift engine with three chip selects, fixed supported word sizes, and no DMA or interrupt handling.

## Important APIs, Types, and Functions
`struct ar934x_spi` stores controller, MMIO base, clock, and cached input clock rate. `ar934x_spi_clk_div()` computes the 6-bit divider for the hardware control register. `ar934x_spi_setup()` clamps max speed to the hardware range. `ar934x_spi_transfer_one_message()` implements all transfer handling and finalizes messages. Probe maps registers, enables the clock, initializes function-select and IOC defaults, fills `spi_controller` callbacks, and calls `spi_register_controller()`.

## Control Flow
At probe, flash mapping is disabled by writing `AR934X_SPI_ENABLE` to the function-select register, and IOC is restored to inactive CS and low DO/CLK. Transfer processing iterates each `spi_transfer`, selects bytes per word from bits-per-word, computes and writes the clock divider, then chunks the buffer into one hardware word at a time. For TX, bytes are packed MSB-first into `DATAOUT`. The driver writes `SHIFT_CTRL` with enable, CS, termination flag for the final word of the final transfer, and bit count. It polls for `SHIFT_EN` to clear with a 5 usec timeout, then unpacks `DATAIN` into RX buffers.

## State and Persistence
There is little software state beyond the cached clock rate. The hardware register state persists until remove or next transfer. Message accounting is maintained by `m->actual_length` and `m->status`.

## Dependencies and Integration Points
It depends on platform resources, clk, MMIO, OF match `qca,ar934x-spi`, and the SPI core `transfer_one_message` path. It supports `SPI_LSB_FIRST` as a mode bit but the transfer packing is otherwise explicit.

## Risks
The hardware poll timeout is very short, so slow or wedged hardware immediately fails the message. Only 8, 16, 24, and 32 bpw are advertised; other values fall into 32-bit packing if somehow passed. The `term` flag is not reset inside the outer loop once set, so correctness depends on it being set only at the last chunk. Divider failures are converted to `-EIO`, losing the more precise cause.

## Test Signals
Exercise all advertised word sizes, per-transfer speed changes, multi-transfer messages, RX-only and TX-only buffers, final chip-select termination behavior, and divider lower/upper limits. A logic analyzer should confirm CS and bit counts.
