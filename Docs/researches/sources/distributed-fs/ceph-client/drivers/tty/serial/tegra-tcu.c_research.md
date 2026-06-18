# sources/distributed-fs/ceph-client/drivers/tty/serial/tegra-tcu.c

## Purpose
This driver exposes NVIDIA Tegra Combined UART as a UART backed by mailbox channels rather than MMIO UART registers. It supports a single `ttyTCU` port and optional console output.

## Important APIs, Types, And Functions
`struct tegra_tcu` owns a dynamically registered `uart_driver`, optional `console`, one `uart_port`, and TX/RX mailbox clients/channels. `tegra_tcu_uart_ops` is minimal: TX empty always true, modem controls are no-ops, startup/shutdown/termios are no-ops, and `start_tx()` drains the xmit FIFO into mailbox messages.

`tegra_tcu_write()` packs up to three bytes plus a byte count into a 32-bit mailbox payload and expands newline into CRLF. `tegra_tcu_receive()` unpacks received mailbox payloads into tty flip chars. Probe requests TX first, registers the driver and port, then requests RX so immediate callbacks have a valid port.

## Control Flow
`tegra_tcu_probe()` allocates state, initializes mailbox clients, requests TX, initializes optional console metadata, registers a one-port uart driver, initializes `uart_port`, adds the port, requests RX, stores drvdata, and registers console if configured. Remove unregisters console, frees RX, removes the port, unregisters the uart driver, and frees TX.

## State And Persistence
The only persistent runtime state is the devm-allocated `tegra_tcu` object and mailbox channel handles. No hardware register state or filesystem persistence exists. The mailbox firmware/remote endpoint owns actual transport state.

## Dependencies And Integration Points
The driver depends on platform/OF matching for `nvidia,tegra194-tcu`, Linux mailbox framework channels named `tx` and `rx`, serial core, tty flip buffers, and optional console core. `port->private_data` points back to `tegra_tcu`.

## Risks
`tegra_tcu_receive()` assumes `tcu->port.state` is valid after RX channel request; probe ordering mitigates but runtime callbacks before open may still need scrutiny. `start_tx()` flushes each mailbox message synchronously, which can block on slow firmware. Modem, baud, break, and flow-control semantics are intentionally absent. Packing allows only three bytes because byte count occupies high bits.

## Test Signals
Test mailbox probe failure unwind, TX CRLF expansion and three-byte packing, RX unpacking for 1-3 byte payloads, console registration/write, tty write wakeups, remove cleanup, and behavior when RX messages arrive before a user opens the tty.
