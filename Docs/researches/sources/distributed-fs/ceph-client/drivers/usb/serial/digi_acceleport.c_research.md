# sources/distributed-fs/ceph-client/drivers/usb/serial/digi_acceleport.c

## Purpose

This file implements the Linux USB serial driver for Digi AccelePort USB-2 and USB-4 adapters. It registers separate `usb_serial_driver` instances for the two-port and four-port products, maps Digi's command protocol onto tty operations, and uses an extra USB serial port as an out-of-band command channel.

## Important APIs, Types, And Functions

The main private types are `struct digi_serial` and `struct digi_port`. `digi_serial` records the out-of-band port, its index, and a one-shot startup flag. `digi_port` stores per-port locks, the small write coalescing buffer, modem-signal cache, transmit-idle state, throttle state, wait queues, and the owning `usb_serial_port`.

Important callbacks are wired through `digi_acceleport_2_device` and `digi_acceleport_4_device`: `digi_open`, `digi_close`, `digi_write`, `digi_write_bulk_callback`, `digi_read_bulk_callback`, `digi_set_termios`, `digi_break_ctl`, `digi_tiocmget`, `digi_tiocmset`, `digi_rx_throttle`, and `digi_rx_unthrottle`. Command helpers include `digi_write_oob_command`, `digi_write_inb_command`, `digi_set_modem_signals`, and `digi_transmit_idle`.

## Control Flow

Module registration uses `module_usb_serial_driver()` with the combined VID/PID table. Attach allocates `struct digi_serial`, identifies the hidden OOB port as `num_ports`, initializes that port, and stores serial-private data. Normal data ports are initialized through `digi_port_probe`.

Opening a port calls `digi_startup_device()` to submit read URBs for all data ports plus the OOB endpoint exactly once. It then enables automatic modem-signal reporting, flushes TX/RX FIFOs through OOB commands, and pushes current termios settings. Writes frame tty bytes as `DIGI_CMD_SEND_DATA` with a length byte; single-byte writes can be buffered while a URB is outstanding. In-band commands share the same write URB and are ordered after any buffered data.

Read URBs dispatch by port number. Data ports expect `[opcode][len][status][payload...]`, translate Digi error bits into tty flags, and respect throttle by deferring URB resubmission. The OOB callback consumes four-byte command responses, updates modem signal state, wakes close/flush/transmit-idle waiters, and notifies tty wakeups on CTS changes.

## State And Persistence

The driver has no persistent storage. Runtime state lives in USB serial private structures, URBs, wait queues, tty flip buffers, cached modem flags, and device-side UART state. `ds_device_started` prevents duplicate read-URB submission. Close waits for transmit idle, sends OOB shutdown commands, kills outstanding writes, and clears `dp_write_urb_in_use`.

## Dependencies And Integration Points

The file depends on the USB serial core, tty core, URB APIs, wait queues, spinlocks, and Digi's adapter protocol constants. Integration points include tty modem-control ioctls, termios baud/parity/flow-control settings, generic USB disconnect handling, and kernel error counters via tty flags.

## Risks

The OOB port indexing is protocol-specific; off-by-one mistakes can treat a data port as the command endpoint. Several paths sleep or wait while coordinating with spinlocks through `cond_wait_interruptible_timeout_irqrestore`, so missed wakeups or early returns can leave locks or in-use flags inconsistent. Packet validation is strict for length but unknown opcodes are mostly logged, so protocol drift may silently drop events. Close has fixed sleeps and a FIXME noting transmit-idle belongs in wait-until-sent logic. The write buffer is intentionally tiny, so throughput behavior depends on timely write callbacks.

## Test Signals

Useful validation includes build coverage for both USB IDs, probing USB-2 and USB-4 devices, tty open/close under disconnect, baud and parity changes, CRTSCTS and XON/XOFF behavior, `TIOCMGET`/`TIOCMSET`, break signaling, throttle/unthrottle with continued RX, close-time drain, and malformed/short USB packet logging without crashes.
