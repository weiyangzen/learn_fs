# sources/distributed-fs/ceph-client/drivers/tty/serial/mvebu-uart.c

## Purpose

`mvebu-uart.c` is the Marvell Armada 3700 UART driver and companion UART clock provider. It registers up to two `ttyMV` serial ports, supports standard and extended Armada 3700 UART register layouts, normal and early console output, suspend/resume state save/restore, and a platform clock provider that selects and gates shared UART parent clocks.

The file has two tightly related halves: the serial driver that moves bytes and configures baud divisors, and the `"marvell,armada-3700-uart-clock"` driver that owns shared clock-control bits in UART register space.

## Important APIs, Types, And Functions

Serial hardware variation is represented by `struct mvebu_uart_driver_data`, which embeds `struct uart_regs_layout` and `struct uart_flags` for standard versus extended offsets and ready/interrupt bits. Per-port state is `struct mvebu_uart`, containing the `uart_port`, clock, one summed IRQ or RX/TX IRQ pair, match data, and PM register snapshots.

The serial operation table `mvebu_uart_ops` provides TX/RX control, break control, startup/shutdown, termios, type/request/release, and optional console-poll hooks. RX/TX movement is handled by `mvebu_uart_rx_chars()` and `mvebu_uart_tx_chars()`. IRQ entry points are `mvebu_uart_isr()` for old single-IRQ bindings and `mvebu_uart_rx_isr()`/`mvebu_uart_tx_isr()` for named split IRQs.

Baud programming is in `mvebu_uart_baud_rate_set()`, protected by the global `mvebu_uart_lock` when touching `UART_BRDV` because the register shares baud divisor and clock-control fields. `mvebu_uart_set_termios()` restricts supported termios changes and computes min/max baud based on divisor limits and stability constraints.

Console support includes earlycon (`EARLYCON_DECLARE()` and `OF_EARLYCON_DECLARE()`), `mvebu_uart_console_write()`, and `mvebu_uart_console_setup()`.

The clock provider uses `struct mvebu_uart_clock` and `struct mvebu_uart_clock_base`, `mvebu_uart_clock_ops`, and `mvebu_uart_clock_probe()`. It registers two clocks, `uart_1` and `uart_2`, from parent candidates `TBG-A-P`, `TBG-B-P`, `TBG-A-S`, `TBG-B-S`, and `xtal`.

## Control Flow

`mvebu_uart_init()` registers the UART driver, then the clock platform driver, then the UART platform driver at `arch_initcall`. UART probe selects a line from the `serial` alias or a counter, fills a static `uart_port`, maps resources, allocates `struct mvebu_uart`, attaches standard/extended match data, gets the port clock, records single or split IRQs, soft-resets the UART, and calls `uart_add_one_port()`.

Startup resets TX/RX FIFOs, clears stale error bits, enables break/error interrupts and RX ready interrupts, then requests either the summed IRQ or the RX/TX pair. Shutdown disables UART interrupts and frees the requested IRQs.

The summed ISR reads status and dispatches RX when RX/error/break bits are set and TX when TX-ready is set. Split ISRs perform the same work by direction. RX loops until no RX-ready or break-detect status remains, handling parity, frame, overrun, break, sysrq, ignore masks, and the extended-UART requirement to explicitly clear error bits. TX uses `uart_port_tx_limited()` while the TX FIFO is not full.

Termios sets status masks, ignores unsupported flag changes by copying old termios bits back, constrains baud to a derived min/max range, calls `mvebu_uart_baud_rate_set()`, encodes actual baud, and updates timeout. Only baud, CREAD, INPCK, IGNPAR, and fixed CS8 behavior are supported.

The clock provider maps UART1 and UART2 BRDV register resources with `devm_ioremap()` to avoid exclusive conflicts with the UART drivers. It chooses a usable parent clock that can produce 9600 baud, keeps the chosen parent enabled, registers two child clocks, and exposes them through an OF onecell provider. On first prepare, it reprograms the shared UART clock control register and adjusts both UART baud divisors so active baud rates do not change.

## State And Persistence Behavior

Serial ports are stored in static `mvebu_uart_ports[2]`. `port->private_data` points to managed `struct mvebu_uart`. PM suspend stores UART data/control/status/baud/oversampling registers and resume writes them back before `uart_resume_port()`.

The global `mvebu_uart_lock` serializes `UART_BRDV` access between the UART baud path, suspend/resume, and clock provider. The clock provider has persistent runtime state for selected parent index, parent rates, divider, and a `configured` boolean that makes parent/divisor reconfiguration a one-time operation.

There is no filesystem persistence. Hardware register state is restored across system PM through in-memory snapshots.

## Dependencies And Integration Points

The driver uses serial core, tty flip buffers, console/earlycon, OF/platform helpers, clocks and clk-provider APIs, MMIO, polling helpers, PM, and device-managed resources. It depends on Armada 3700 device-tree compatibles `"marvell,armada-3700-uart"`, `"marvell,armada-3700-uart-ext"`, and `"marvell,armada-3700-uart-clock"`.

It integrates with the common clock framework as both a clock consumer for UART ports and a clock provider for the two UART clocks. This creates an important ordering dependency: extended UART probe treats missing clock as fatal except for probe deferral.

## Risks And Edge Cases

Shared `UART_BRDV` fields are easy to corrupt if any new path omits `mvebu_uart_lock`. The code comments document swapped UART clock-disable bits compared with Marvell documentation; any register cleanup that follows the manual instead of the driver comments would break clock gating.

The extended UART requires explicit error-bit clearing to avoid interrupt loops. RX status/error handling should be tested separately for standard and extended layouts. The old single-IRQ path is noted as UART0-only; using old bindings for other ports would be suspect.

The clock provider intentionally maps registers already used by UART drivers without exclusive reservation. That is safe only because access is locked and field ownership is understood. `mvebu_uart_clock_set_rate()` is a no-op that returns success, relying on determine-rate constraints and the fixed parent/divider model.

## Test Signals

Validate standard and extended compatibles, old summed IRQ and new named RX/TX IRQ bindings, early console and normal console on `ttyMV`, baud changes across low rates and high-rate stability limits, parity/frame/break/overrun insertion, suspend/resume register restoration, and simultaneous use of both UARTs while the clock provider prepares/gates clocks. Clock tests should confirm parent selection, `uart_1`/`uart_2` rates, lock-protected BRDV updates, and no baud jump when the clock provider first prepares.
