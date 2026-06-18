# sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.c

## Purpose

`rsci.c` adds Renesas RSCI UART support to the shared SH-SCI serial framework. It provides RSCI-specific register definitions, serial-core operations, SH-SCI port operations, SoC match data for RZ/G3E, RZ/G3L, and RZ/T2H-style ports, and optional early console setup. The implementation focuses on FIFO asynchronous UART mode and delegates common probe, clock, IRQ, console, and PM scaffolding to `sh-sci-common`.

## Important APIs, Types, and Functions

The file exports three `struct sci_of_data` instances: `of_rsci_rzg3e_data`, `of_rsci_rzg3l_data`, and `of_rsci_rzt2h_data`. These bind the RSCI port type, `rsci_port_ops`, `rsci_uart_ops`, and FIFO/error parameters. `rsci_serial_in()` and `rsci_serial_out()` are the MMIO accessors used by both local code and SH-SCI common code. `rsci_set_termios()` programs RSCI CCR registers, baud divisors, FIFO mode, reset bits, RX trigger level, error masks, hardware flow-control/autorts state, and RX enable. `rsci_transmit_chars()` and `rsci_receive_chars()` are the SH-SCI data movers. `rsci_poll_put_char()`, `rsci_prepare_console_write()`, and `rsci_finish_console_write()` support console paths.

## Control Flow

Common SH-SCI probe code selects one of the exported OF data blocks and uses the supplied ops. Termios setup calculates the maximum usable baud from available SCI clocks and sampling-rate constraints, uses `sci_scbrr_calc()` to choose FCK divisor values, enables the port, locks the UART, disables CCR0, programs FIFO mode and CCR2 baud fields, resets FIFOs, applies RX trigger level, updates autorts/CTS state, clears common and FIFO flags, enables receive, and finally enables RX interrupts only when `CREAD` is set. TX starts by enabling TIE and TE together as required by hardware. The transmit worker waits for TDRE, fills TDR while TX room is available, wakes writers, and switches from TIE to TEIE when the xmit FIFO empties. RX checks CSR/FRSR, reserves tty buffer room, reads RDR entries, maps FIFO framing/parity bits into tty flags, handles sysrq, clears RDRF/DR flags, and pushes tty data.

## State and Persistence Behavior

No filesystem persistence exists. Runtime state lives mostly in the common `sci_port` and `uart_port`: selected clocks, GPIO modem controls, autorts flag, FIFO trigger, error masks, and tty buffers. RSCI hardware state is fully register-based: CCR0-CCR4 mode/control, FIFO control, status clear registers, baud divisors, and modem/CTS configuration. `rsci_suspend_regs_size()` returns zero, so this RSCI layer does not add a private suspend-register image; common SCI PM must reestablish relevant state.

## Dependencies and Integration Points

The driver depends on `sh-sci-common.h`, `serial_sci.h`, SH-SCI exported namespace symbols, `serial_mctrl_gpio`, bitfield helpers, MMIO polling, serial core, and tty flip buffers. It integrates with common SCI startup/shutdown/PM/request/release/config/verify functions, OF early console through `scix_early_console_setup()`, and modem GPIO helpers for CTS/DSR/DCD when not handled by hardware.

## Risks and Edge Cases

Only CS7 and CS8 are supported; other sizes are coerced to CS8. The receive path notes that 9-bit data is not supported but masks a 9-bit field, so true multiprocessor/9-bit modes are not implemented. If tty buffers are full, it reads one RDR entry and clears flags to prevent lockup, which drops data. `rsci_set_mctrl()` only sets loopback and does not clear it when `TIOCM_LOOP` is absent. Baud setup currently only considers the standard FCK divisor calculation visible in this file. Error clearing is explicit and must match hardware write-one-to-clear semantics.

## Test Signals

Test all three OF data variants and FIFO sizes, early console setup for each compatible, CS7/CS8 and unsupported size coercion, parity and stop bits, baud divisor accuracy, RX trigger clamping, CRTSCTS/autorts with and without GPIO CTS, modem GPIO reads, loopback set/clear behavior, TX empty/TEIE transition, RX parity/frame/overrun/buffer-full paths, break control, console polling timeout, and suspend/resume through the shared SCI layer.
