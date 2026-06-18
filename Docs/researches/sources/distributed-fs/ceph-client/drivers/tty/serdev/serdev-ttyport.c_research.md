# sources/distributed-fs/ceph-client/drivers/tty/serdev/serdev-ttyport.c

## Purpose
Bridges an existing `tty_port` and `tty_driver` into a serdev controller, allowing serial-attached device drivers to use common tty/UART drivers as their transport.

## Important APIs, types, and functions
- `struct serport` stores the tty port, opened `tty_struct`, tty driver, tty index, and `SERPORT_ACTIVE` flag.
- TTY-port callbacks: `ttyport_receive_buf()` forwards RX bytes to `serdev_controller_receive_buf()`, and `ttyport_write_wakeup()` forwards write wakeups to serdev.
- Serdev controller operations: `ttyport_write_buf()`, `ttyport_write_flush()`, `ttyport_open()`, `ttyport_close()`, `ttyport_set_baudrate()`, `ttyport_set_flow_control()`, `ttyport_set_parity()`, `ttyport_wait_until_sent()`, `ttyport_get_tiocm()`, `ttyport_set_tiocm()`, and `ttyport_break_ctl()`.
- Public registration: `serdev_tty_port_register()` and `serdev_tty_port_unregister()`.

## Control flow
Registration allocates a serdev controller with embedded `struct serport`, records the tty driver/index, installs `client_ops` and `client_data` on the tty port, and calls `serdev_controller_add()`. If controller add fails, the tty port is restored to default client ops and the controller ref is dropped.

When a serdev client opens, `ttyport_open()` initializes the tty with `tty_init_dev()`, validates driver open/close callbacks, calls tty open, unlocks the tty, normalizes termios to raw 8-bit, hardware-flow-control-enabled, carrier-ignore mode, then sets `SERPORT_ACTIVE`. RX bytes are only forwarded while active. Writes set `TTY_DO_WRITE_WAKEUP` and call the tty driver's `.write`. Close clears active, calls tty close under the tty lock, and releases the tty struct.

## State and persistence behavior
State is per controller: active flag, currently opened tty pointer, and tty port client callbacks. No persistent state. Termios is deliberately reprogrammed on open to a known raw baseline.

## Dependencies and integration points
Depends on tty core internals (`tty_init_dev`, driver ops, termios updates, wait queues, modem-control callbacks), `tty_port_client_operations`, and serdev controller core callbacks. It is the integration point that lets normal serial drivers expose serdev children.

## Risks and edge cases
- The bridge assumes the underlying tty driver supplies compatible open/close/write semantics without a userspace file.
- RX and write wakeup are gated by `SERPORT_ACTIVE`; races around open/close must not deliver stale data to serdev clients.
- `ttyport_set_parity()` verifies the resulting termios because hardware may silently reject mark/space parity.
- Registration mutates `port->client_ops`; unregister must always restore defaults.

## Test signals
Register/unregister a tty port as a serdev controller, open/close from a serdev client, RX forwarding while active and suppression while inactive, write wakeup completion, baud/flow/parity termios changes, modem control and break callback propagation, and failure cleanup when controller add fails.
