# sources/distributed-fs/ceph-client/drivers/tty/amiserial.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/amiserial.c` is the serial TTY and optional console driver for the Amiga built-in serial port. It adapts legacy 16550-style serial driver concepts to Amiga custom chip registers and CIA modem-control bits, registers one `ttyS` minor at 64, handles RX/TX/status interrupts, and provides termios, modem-control, ioctl, proc, and console operations. The source was read as a complete 1665-line file for this report.

## Important APIs, Types, and Functions

The central type is `struct serial_state`, containing `struct tty_port`, transmit `circ_buf`, `async_icount`, baud/divisor state, status masks, timeout, interrupt-enable emulation, modem-control bits, and high-priority XON/XOFF character state. Driver globals include `serial_driver`, `serial_state`, and `current_ctl_bits`.

Important interrupt and data-path functions are `receive_chars`, `transmit_chars`, `check_modem_status`, `ser_vbl_int`, `ser_rx_int`, and `ser_tx_int`. TTY operations include `rs_open`, `rs_close`, `rs_write`, `rs_put_char`, `rs_flush_chars`, `rs_write_room`, `rs_chars_in_buffer`, `rs_flush_buffer`, `rs_ioctl`, `rs_set_termios`, `rs_stop`, `rs_start`, `rs_hangup`, `rs_break`, `rs_send_xchar`, `rs_wait_until_sent`, `rs_tiocmget`, `rs_tiocmset`, `rs_get_icount`, `set_serial_info`, and `get_serial_info`. Probe/remove and console functions are `amiga_serial_probe`, `amiga_serial_remove`, `serial_console_write`, and `amiserial_console_init`.

## Control Flow

Probe allocates a one-line TTY driver, initializes `serial_state`, links the `tty_port`, registers the driver, requests Amiga TX and RX IRQs, disables and clears pending hardware interrupts, configures CIA modem-control directions, and stores driver data. Open links the tty to the single port, calls `rs_startup`, allocates the TX page buffer, clears RX state, requests the vertical blank IRQ for modem-status polling, enables RX/TX interrupt sources, asserts DTR/RTS according to baud, programs speed, and blocks until carrier if required.

RX IRQs call `receive_chars`, which reads `amiga_custom.serdatr`, decodes break and overrun status, updates counters, applies termios ignore/read masks, inserts flip-buffer characters, and pushes to the TTY layer. TX IRQs call `transmit_chars`, prioritizing `x_char`, then circular-buffer bytes, disabling transmit interrupts when empty or stopped and waking writers below `WAKEUP_CHARS`. The vertical blank IRQ periodically polls DCD/CTS/DSR, updates counters, wakes modem waiters, handles carrier hangup/open wakeups, and enforces CTS hardware flow control.

Termios changes recompute data framing, baud divisor, timeout, status masks, carrier checking, CTS flow, and hardware SERPER register values. Close disables RX, waits for transmitter drain, shuts down interrupts and buffers, optionally drops DTR/RTS, flushes line discipline state, and completes TTY close. Console writes disable TX interrupt temporarily, emit CR before LF, poll for transmit-ready, and restore interrupt enable state.

## State and Persistence Behavior

Runtime state is kept in the single static `serial_state`, including transmit buffer pointers, counters, modem-control bits, baud divisor, masks, and TTY port lifetime. Hardware-visible state is stored in Amiga custom registers (`serdat`, `serdatr`, `serper`, `intena`, `intreq`, `adkcon`) and CIA port A direction/data bits. No data persists across driver unload or reboot.

## Dependencies and Integration Points

The driver depends on the TTY core, `tty_port`, flip buffers, serial ioctl structures, circ-buffer helpers, Amiga architecture headers (`amigahw.h`, `amigaints.h`, IRQ/setup headers), platform driver probing, optional `CONFIG_SERIAL_CONSOLE`, and proc support via `tty_operations.proc_show`. It is built through `CONFIG_AMIGA_BUILTIN_SERIAL` from the TTY Makefile and aliases `platform:amiga-serial`.

## Risks and Edge Cases

The implementation uses local interrupt disabling around shared state instead of fine-grained locks, reflecting its single-port hardware model. The vertical blank IRQ is used for modem-status polling, so status latency depends on that interrupt. Carrier and CTS bits are active-low in CIA registers, which makes control logic easy to invert accidentally. `TIOCMIWAIT` must handle signals and modem counter races. Baud divisor fallback behavior preserves old termios or falls back to 9600 when invalid. Console output directly touches hardware and temporarily masks TX interrupts.

## Test Signals

Useful signals include Amiga or emulator boot showing `ttyS0 is the amiga builtin serial port`; open/close with carrier-required and `CLOCAL` modes; RX break/overrun counter behavior; TX buffering and `tty_wakeup`; CTS/RTS flow control; `TIOCMGET`, `TIOCMSET`, `TIOCGICOUNT`, `TIOCMIWAIT`, and `TIOCSERGETLSR`; baud and parity termios changes; `/proc/tty/driver` serial info; suspend-free module probe/remove paths; and serial console output with newline CRLF conversion.
