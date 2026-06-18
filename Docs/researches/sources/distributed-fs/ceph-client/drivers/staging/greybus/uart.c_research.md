# sources/distributed-fs/ceph-client/drivers/staging/greybus/uart.c

## Purpose
Implements a Greybus UART protocol driver that exposes remote Greybus UART modules as Linux TTY devices named `ttyGB*`. It bridges unsolicited RX/control/credit messages and synchronous TX/configuration operations into the TTY core.

## Important APIs, Types, and Functions
`struct gb_tty` holds gbphy and Greybus connection state, `tty_port`, minor number, line coding, input/output modem controls, write FIFO, TX work, credit accounting, completion, and locks. The unsolicited operation dispatcher `gb_uart_request_handler()` handles `GB_UART_TYPE_RECEIVE_DATA`, `GB_UART_TYPE_SERIAL_STATE`, and `GB_UART_TYPE_RECEIVE_CREDITS`. TTY operations include install/open/close/cleanup/hangup, write, write_room, chars_in_buffer, break, termios, modem get/set, throttle/unthrottle, serial info, ioctl, and icount. Probe/remove are `gb_uart_probe()` and `gb_uart_remove()`, with module init registering the TTY driver before the gbphy driver.

## Control Flow and State
Probe allocates a Greybus connection, validates max payload, allocates `gb_tty`, initializes a `tty_port`, TX work, FIFO, credits, minor IDR entry, locks, connection data, default control lines, default 9600n81 line coding, and registers the TTY device. Writes enter a FIFO under `write_lock`; `gb_uart_tx_write_work()` drains up to available firmware credits and Greybus payload capacity, sends `GB_UART_TYPE_SEND_DATA`, and returns credits on error. Incoming credit operations add credits, schedule TX, wake the TTY, and complete close waits when all credits are restored. Shutdown cancels TX, resets FIFO, flushes the remote transmitter, waits for credits, then autosuspends.

## Dependencies and Integration Points
Integrates with Greybus gbphy runtime PM, Linux TTY core, IDR minor allocation, KFIFO, workqueues, completions, GPIO-less modem control abstractions, and line coding Greybus requests. Runtime PM is acquired on port activation and dropped on shutdown.

## Risks and Test Signals
Risks include credit accounting races, blocking close if credits never return, missing `iocount` updates despite wait/ioctl support, global minor exhaustion, and handling disconnect while TTY references remain. Test signals include opening/closing multiple minors, RX flag propagation for break/parity/framing/overrun, TX backpressure via write_room/chars_in_buffer, termios-driven baud/parity/flow-control writes, throttle/unthrottle control lines, disconnect hangup, and runtime PM balance.
