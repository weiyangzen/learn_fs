# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan_pda.c

## Purpose
This driver supports the USB Keyspan PDA serial converter and compatible Xircom/Entrega devices. It handles both fake pre-firmware devices and the real one-port serial adapter after firmware renumeration. The real device uses one bulk-out endpoint for TX and one interrupt-in endpoint for both RX data and status notifications.

## Important APIs, Types, and Functions
`struct keyspan_pda_private` stores estimated device TX room, unthrottle work, and the associated serial/port pointers. The main callbacks are `keyspan_pda_open`, `keyspan_pda_close`, `keyspan_pda_write`, `keyspan_pda_write_start`, `keyspan_pda_write_bulk_callback`, `keyspan_pda_rx_interrupt`, throttle/unthrottle handlers, `keyspan_pda_set_termios`, break control, modem-control helpers, and `keyspan_pda_fake_startup`.

Vendor requests include request 0 for baud selection, 3 for modem pins, 4 for break, 6 for querying write room, and 7 for requesting a TX unthrottle interrupt. Firmware names are `keyspan_pda/keyspan_pda.fw` and `keyspan_pda/xircom_pgs.fw`.

## Control Flow
The combined device table binds fake IDs and the post-firmware Keyspan PDA ID. Fake devices enter `keyspan_pda_fake_startup`, assert FX1 reset, select firmware by vendor, download it, and return nonzero so the device renumerates. Real devices use `keyspan_pda_port_probe` to allocate private state and initialize unthrottle work.

Open queries device write room with vendor request 6, stores it under `port->lock`, and submits the interrupt-in URB. RX interrupts are message-framed: type 0 carries data after the first byte; type 1 carries status. A status subcode of 2 signals TX unthrottle, restores estimated room to at least `KEYSPAN_TX_THRESHOLD`, starts more queued writes, and wakes the serial core.

Write data is first copied into the port FIFO. `keyspan_pda_write_start` checks whether the single write URB is free, the FIFO is nonempty, and estimated device room is nonzero. It drains up to the smaller of device room and bulk endpoint size into the URB, decrements `tx_room`, submits the URB, and schedules `unthrottle_work` when it exactly fills the remaining room. The work item asks the device to notify when room exceeds the threshold and then re-queries room to avoid missing an already-empty buffer.

## State and Persistence
State is per-port and volatile: `tx_room`, FIFO contents, the write URB free bit, and pending unthrottle work. Termios persistence is minimal because the hardware path only applies baud; unsupported framing/parity settings are copied back from the old termios state. Close kills the interrupt and write URBs, cancels unthrottle work synchronously, and resets the FIFO.

## Dependencies and Integration Points
The file depends on USB serial FIFO/write-URB helpers, TTY flip buffers, workqueues, spinlocks, and EZ-USB firmware loading. It integrates with TTY modem control through `TIOCM_*` bit mapping to a one-byte device pin field, with baud control through discrete index values, and with software flow control by killing/resubmitting the interrupt receive URB.

## Risks
TX room is an estimate maintained by the host and corrected by vendor queries/interrupts; a missed unthrottle signal or failed room query can stall writes. `keyspan_pda_write` returns the negative result of `keyspan_pda_write_start` after bytes may already have entered the FIFO, so callers must tolerate normal serial-core buffering semantics. The device largely ignores non-baud termios changes. RX throttle kills the only interrupt URB, so status notifications are also suppressed while throttled.

## Test Signals
Exercise firmware renumeration for Keyspan, Xircom, and Entrega fake IDs; open/close with interrupt URB submission; RX data and status type parsing; TX FIFO draining and unthrottle threshold behavior; failed room-query handling; baud fallback to 9600; break request behavior; DTR/RTS and modem input bit translation; and disconnect/close while work and write URB are pending.
