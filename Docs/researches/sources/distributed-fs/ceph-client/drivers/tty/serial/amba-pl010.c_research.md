# sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl010.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl010.c` is the Linux serial-core driver for ARM AMBA PL010 UARTs. It binds AMBA devices with PrimeCell ID `0x00041010`, exposes up to eight `ttyAM` ports, supports optional console output, and handles a simple interrupt-driven RX/TX datapath. The source was read as a complete 804-line file.

## Important APIs, Types, and Functions

The private wrapper is `struct uart_amba_port`, containing the generic `struct uart_port`, the UART clock, AMBA device pointer, optional platform callbacks, and cached modem status. The serial-core operation table is `amba_pl010_pops`, implemented by `pl010_startup()`, `pl010_shutdown()`, `pl010_set_termios()`, `pl010_start_tx()`, `pl010_stop_tx()`, `pl010_stop_rx()`, `pl010_enable_ms()`, `pl010_get_mctrl()`, `pl010_set_mctrl()`, `pl010_break_ctl()`, and port request/config/verify helpers. Runtime data movement is in `pl010_rx_chars()`, `pl010_tx_chars()`, `pl010_modem_status()`, and `pl010_int()`. Device lifetime is rooted in `pl010_probe()`, `pl010_remove()`, `pl010_suspend()`, and `pl010_resume()`.

## Control Flow

Probe finds a free slot in the static `amba_ports[]`, allocates and maps the AMBA resource, obtains the clock, fills the `uart_port`, registers the shared `uart_driver` lazily, and calls `uart_add_one_port()`. Startup prepares/enables the clock, stores the live UART clock rate, requests the IRQ, snapshots modem status, and enables UART, receive, and receive-timeout interrupts. The interrupt handler locks the port, reads `UART010_IIR`, and loops up to `AMBA_ISR_PASS_LIMIT`, dispatching RX, modem-status, and TX work before rereading pending status.

RX drains the data register while `UART01x_FR_RXFE` is clear, updates `icount`, clears receive errors through `UART01x_ECR`, classifies break/parity/frame/overrun conditions using the current read/ignore masks, honors sysrq, inserts chars into the TTY flip buffer, and pushes the buffer after the drain. TX uses `uart_port_tx_limited()` with half the FIFO as the chunk limit. Termios computes the baud divisor with serial-core helpers, programs word length, stop bits, parity, FIFO enable, read/ignore masks, modem status interrupt enable, and writes LCRM/LCRL before LCRH as required by the hardware. Shutdown frees the IRQ, disables the UART and FIFOs/break, then disables the clock.

## State and Persistence Behavior

State is in the static `amba_ports[]`, the serial-core `uart_state`, `old_status`, UART registers, and the clock enable count. There is no file-backed persistence. Console setup may prepare the clock and infer baud/parity/bits from bootloader-programmed registers. Suspend/resume delegates to `uart_suspend_port()` and `uart_resume_port()`, so open-port configuration is restored through serial-core paths rather than custom persistent storage.

## Dependencies and Integration Points

The driver integrates with the AMBA bus, `serial_core`, TTY flip buffers, Linux clock APIs, AMBA platform data (`struct amba_pl010_data`) for external modem control outputs, optional `CONFIG_SERIAL_AMBA_PL010_CONSOLE`, sysrq, and generic PM. Register definitions come from `<linux/amba/serial.h>`.

## Risks and Edge Cases

`pl010_disable_ms()` casts `struct uart_port *` directly to `struct uart_amba_port *`, relying on the wrapper embedding `uart_port` as the first field. The device has no native DTR/RTS outputs, so modem output correctness depends on platform callbacks. Interrupt storms are bounded by `AMBA_ISR_PASS_LIMIT`, but persistent status bits can delay work. CREAD masking uses `UART_DUMMY_RSR_RX`; RX still drains hardware but suppresses delivery. Console writes temporarily alter control register state and rely on clock enable/disable balancing.

## Test Signals

Useful validation includes AMBA probe/remove with multiple PL010 ports, open/close clock and IRQ balancing, RX error injection for break/parity/frame/overrun, TX wakeup behavior, termios changes across baud/parity/data bits, modem-status change handling, N_PPS line discipline enabling hard PPS on DCD, suspend/resume of open and console ports, and console boot output with and without command-line options.
