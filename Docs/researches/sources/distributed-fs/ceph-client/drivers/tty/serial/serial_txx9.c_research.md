# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_txx9.c

## Purpose

`serial_txx9.c` is the UART core driver for Toshiba TX39/TX49 internal SIO controllers and the TC86C001 PCI SIO. It registers a `uart_driver` named `serial_txx9`, exposes either `ttyTX` or standard `ttyS` minors depending on configuration, and supports platform-data ports, early setup, optional console/polling, suspend/resume, and optional PCI discovery. The source was read as a complete 1268-line file.

## Important APIs, Types, and Functions

The hardware contract is encoded by `TXX9_*` register offsets and status/control bit definitions for line control, interrupt control/status, FIFO control, flow control, baud generator, and TX/RX FIFOs. Low-level accessors are `sio_in()`, `sio_out()`, `sio_mask()`, `sio_set()`, and `sio_quot_set()`, with memory-mapped and `UPIO_PORT` paths.

Core UART operations are implemented by `serial_txx9_pops`: `serial_txx9_start_tx()`, `serial_txx9_stop_tx()`, `serial_txx9_stop_rx()`, `serial_txx9_tx_empty()`, `serial_txx9_get_mctrl()`, `serial_txx9_set_mctrl()`, `serial_txx9_break_ctl()`, `serial_txx9_startup()`, `serial_txx9_shutdown()`, `serial_txx9_set_termios()`, `serial_txx9_pm()`, resource methods, and optional poll methods. Runtime registration flows through `early_serial_txx9_setup()`, `serial_txx9_register_port()`, `serial_txx9_unregister_port()`, `serial_txx9_probe()`, `serial_txx9_remove()`, PCI `pciserial_txx9_init_one()`, and module `serial_txx9_init()`/`serial_txx9_exit()`.

## Control Flow

Module init registers the UART driver, creates a synthetic platform device, registers any statically initialized ports, binds the platform driver, and optionally registers the PCI driver. Platform probe consumes an array of `struct uart_port` platform data until `uartclk == 0`, copies each template into an unused or matching slot in `serial_txx9_ports[]`, and calls `uart_add_one_port()`. PCI probe enables the device, creates a port with `UPIO_PORT`, a fixed 66.67 MHz clock, and CTS capability, then registers it through the same helper.

`serial_txx9_startup()` resets FIFOs, clears interrupt status, requests a shared IRQ, restores modem control, enables RX/TX, and enables receive interrupts. The interrupt handler loops under `PASS_LIMIT`, locks the port, reads `SIDISR`, suppresses TX status if TX interrupts are disabled, services RX with `receive_chars()`, services TX with `transmit_chars()`, clears interrupt bits, and stops when no relevant status remains. RX drains the FIFO until `UVALID` indicates no valid data or the software count expires, updates `icount`, handles break/sysrq/parity/frame/overrun, inserts tty chars, and pushes the flip buffer. TX uses `uart_port_tx_limited()` to move up to the TX FIFO depth.

`serial_txx9_set_termios()` coerces unsupported formats to 8-bit data, disables unsupported modem semantics, computes the baud divisor, builds `read_status_mask` and `ignore_status_mask`, toggles hardware RTS/CTS support only when `CRTSCTS` and `UPF_TXX9_HAVE_CTS_LINE` are present, writes line control, baud generator, FIFO control, and modem state under the port lock. Console and polling paths temporarily disable interrupts, wait for transmitter status, write directly to `SITFIFO`, and restore saved interrupt/flow-control state.

## State and Persistence Behavior

Persistent driver state is in the static `serial_txx9_ports[UART_NR]`, `serial_txx9_reg`, the synthetic `serial_txx9_plat_devs`, and, when PCI is enabled, per-device PCI driver data pointing at a registered `uart_port`. Port hardware state lives in MMIO or I/O registers. There is no file-backed persistence. Runtime state includes UART core FIFOs and termios-derived masks, `up->mctrl`, `up->flags` feature bits, IRQ ownership, resource mappings, and console index state. Suspend/resume delegates to `uart_suspend_port()`/`uart_resume_port()`, while `serial_txx9_pm()` reinitializes hardware only when transitioning back on from a real low-power state, not during initial `uart_configure_port()`.

## Dependencies and Integration Points

The driver integrates with Linux serial core, tty flip buffers, console and console-poll subsystems, platform devices, optional PCI, resource reservation, raw I/O accessors, and `asm/txx9/generic.h`. It depends on platform data providing valid `uart_port` templates and on optional PCI IDs for TC86C001. It uses `uart_handle_break()`, `uart_handle_sysrq_char()`, `uart_get_baud_rate()`, `uart_get_divisor()`, `uart_update_timeout()`, and `uart_console_write()` to stay aligned with UART core behavior.

## Risks and Edge Cases

The RX overrun path temporarily adds `RFDN_MASK` to `ignore_status_mask` to discard the next buffered character, so changes to error handling can easily alter raw-mode behavior. `serial_txx9_config_port()` returns without releasing resources for the active console path after `request_resource()`, matching console expectations but making resource lifetime subtle. Console and poll paths disable interrupts and can busy-wait up to 1 second for flow control. The initialization path contains a TX4925 bus-error workaround after soft reset. PCI and platform registrations share static slots, so matching/unregistering must preserve line ownership and avoid stale `dev` pointers. `serial_txx9_stop_rx()` only updates the read mask rather than disabling hardware receive interrupts.

## Test Signals

Useful validation signals are boot/probe with platform-data ports and TC86C001 PCI, console boot with `CONFIG_SERIAL_TXX9_CONSOLE`, `CONFIG_CONSOLE_POLL` kgdb-style polling, RX error injection for break/parity/frame/overrun, `CRTSCTS` with and without `UPF_TXX9_HAVE_CTS_LINE`, suspend/resume on console and non-console ports, module unload after PCI and platform registration, failed IRQ/resource allocation, and high-throughput TX/RX confirming no `PASS_LIMIT` livelock.
