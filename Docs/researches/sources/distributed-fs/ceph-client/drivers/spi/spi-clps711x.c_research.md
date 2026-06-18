# sources/distributed-fs/ceph-client/drivers/spi/spi-clps711x.c

## Purpose

`spi-clps711x.c` is a compact SPI bus driver for CLPS711X/EP7209 synchronous I/O hardware. It uses one MMIO syncio register, a syscon register bit for CPHA mode, a clock, and one IRQ to implement byte/frame transfers.

## Important APIs, Types, and Functions

`struct spi_clps711x_data` stores the syncio MMIO pointer, syscon regmap, SPI clock, current TX/RX buffers, bits-per-word, and remaining length. `spi_clps711x_prepare_message()` programs clock phase through `SYSCON3_ADCCKNSEN`. `spi_clps711x_transfer_one()` sets the clock rate, initializes current transfer state, writes the first frame, and returns asynchronous completion. `spi_clps711x_isr()` reads one received frame, writes the next, or finalizes the transfer. `spi_clps711x_probe()` wires platform resources into a SPI host.

## Control Flow

Probe gets the IRQ, allocates the host, sets controller capabilities, obtains the clock, resolves the `syscon` phandle, maps syncio, disables extended mode due hardware problems, clears a pending interrupt by reading syncio, requests the IRQ, and registers the controller. A transfer begins by setting clock rate, storing buffers and length, and writing the first data byte plus frame length and TX frame enable bits. Each interrupt consumes one byte from syncio and writes the next until length reaches zero.

## State and Persistence Behavior

The per-transfer state is stored in the host-private structure and is valid only while one transfer is active. Persistent controller configuration is minimal: syscon CPHA bit, disabled extended mode, and clock rate. There is no runtime PM or file-backed persistence.

## Dependencies and Integration Points

The driver depends on platform/OF, clocks, syscon/regmap, MMIO, IRQs, GPIO descriptor chip-select support, and the SPI core. It matches `cirrus,ep7209-spi`.

## Risks and Edge Cases

The driver treats `xfer->len` as a byte count even when `bits_per_word` may be 1-8; non-8-bit frame semantics should be verified. There is no timeout if interrupts stop. `clk_set_rate()` return value is ignored. Only CPHA and CS-high are advertised, not CPOL. The syscon update in prepare_message is shared system state and could affect non-SPI syncio users.

## Test Signals

Tests should cover probe failure for missing IRQ/clock/syscon/MMIO, CPHA toggling, clock-rate requests, transfers with and without TX/RX buffers, 1-bit through 8-bit frame sizes, interrupt completion, no-interrupt timeout behavior at the SPI core level, and GPIO CS integration.
