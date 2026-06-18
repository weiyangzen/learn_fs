# sources/distributed-fs/ceph-client/include/linux/serial_core.h

## Purpose

`serial_core.h` is the central UART/TTY driver contract for serial drivers in this kernel tree. It defines the `struct uart_ops` hardware callback ABI, the persistent state objects used by the serial core, UART port metadata, locking wrappers, transmit FIFO helpers, console and early-console declarations, registration APIs, power management APIs, and helper paths for modem status, SysRQ, break handling, and RS485 mode discovery.

## Important APIs, Types, And Functions

Key types are `struct uart_ops`, `struct uart_port`, `struct uart_state`, `struct uart_driver`, `struct earlycon_device`, and `struct earlycon_id`. `struct uart_ops` is the lower-level driver vtable, covering transmitter empty checks, modem control, TX/RX start and stop, throttle/unthrottle, high-priority XON/XOFF characters, startup/shutdown, termios changes, power management, resource request/release, port verification, ioctls, and optional console polling. `struct uart_port` combines hardware accessors, IRQ/clock/FIFO properties, flow-control state, port flags, console/sysrq data, RS485/ISO7816 config, and platform-private data.

Important helpers include `uart_port_set_cons()`, the `uart_port_lock*()` and `uart_port_unlock*()` wrappers, `serial_port_in()`, `serial_port_out()`, `uart_xmit_advance()`, `uart_fifo_out()`, `uart_fifo_get()`, `uart_port_tx*()` macros, `uart_update_timeout()`, `uart_get_baud_rate()`, `uart_get_divisor()`, `uart_fifo_timeout()`, `uart_poll_timeout()`, `OF_EARLYCON_DECLARE()`, `EARLYCON_DECLARE()`, `setup_earlycon()`, `uart_parse_options()`, `uart_set_options()`, `uart_console_write()`, `uart_register_driver()`, `uart_add_one_port()`, `uart_suspend_port()`, `uart_resume_port()`, `uart_handle_dcd_change()`, `uart_handle_cts_change()`, `uart_insert_char()`, `uart_xchar_out()`, and `uart_get_rs485_mode()`.

## Control Flow

The header describes the serial core lifecycle: a low-level driver registers a `uart_driver`, adds one or more `uart_port` instances, implements `uart_ops`, and then the TTY layer opens, configures, transmits, receives, suspends, resumes, and removes ports through those callbacks. Startup is expected to acquire hardware resources and enable reception without asserting RTS/DTR; shutdown disables hardware and releases resources after users disappear. `set_termios()` is the primary reconfiguration path for word length, parity, stop bits, input error masks, and flow-control behavior.

Transmit helpers implement a reusable loop: send `x_char` first, stop if `uart_tx_stopped()` reports software or hardware flow stop, pull bytes from `tty_port.xmit_fifo`, run the driver-supplied write expression, update TX accounting, wake writers below `WAKEUP_CHARS`, and optionally call `ops->stop_tx()` when empty. Break handling first calls a driver hook, then toggles the serial SysRQ window for console ports when enabled, and finally performs SAK if `UPF_SAK` is set.

## State And Persistence

`struct uart_state` is explicitly persistent across opens and contains the TTY port, PM state, refcount, remove waitqueue, and current `uart_port`. `struct uart_port` keeps long-lived hardware configuration, counters in `uart_icount`, modem-control state, flags, status bits, sysrq state, console pointer, RS485/ISO7816 settings, and a private pointer. The header documents locking requirements: many `uart_ops` callbacks run under `port->lock` with local interrupts disabled, while configuration calls usually run under `tty_port->mutex` or the port semaphore.

The port lock wrappers also coordinate with nbcon consoles. When a port is the registered non-blocking console with atomic write support, the wrapper acquires or releases the console device context around the spinlock. The `uart_port_set_cons()` helper updates `port->cons` under the port lock to avoid stale console pointers while another context holds the wrapped lock.

## Dependencies And Integration Points

Dependencies include TTY core, console/nbcon, sysrq, kfifo via `tty_port`, termios, UAPI serial flags, device model, interrupt and spinlock primitives, RS485/ISO7816 UAPI structs, early console table sections, and optional `CONFIG_CONSOLE_POLL`, `CONFIG_SERIAL_CORE_CONSOLE`, `CONFIG_SERIAL_EARLYCON`, and `CONFIG_MAGIC_SYSRQ_SERIAL`. Integration points are serial hardware drivers, platform/OF/ACPI early console discovery, KGDB polling, PM suspend/resume, and TTY line discipline behavior.

## Risks And Test Signals

Major risks are incorrect callback locking, sleeping in no-sleep contexts, using raw `port->lock` instead of the UART lock wrappers when nbcon is involved, stale `port->state` use after shutdown, wrong UAPI flag mappings, incorrect FIFO accounting, and mishandled SysRQ/break paths. Test signals include serial console boot, earlycon boot logs, open/close loops, CTS/DCD transitions, XON/XOFF and RTS/CTS flow control, break and SysRQ behavior, suspend/resume, RS485 configuration ioctls, KGDB polling if enabled, and stress tests that force TX FIFO empty and wakeup thresholds.
