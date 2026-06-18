# sources/distributed-fs/ceph-client/drivers/usb/serial/generic.c

## Purpose

This file provides generic USB serial helper operations used by many specific USB serial drivers and, when `CONFIG_USB_SERIAL_GENERIC` is enabled, a testing-only generic driver selected by vendor/product module parameters. Its core value is reusable tty/URB plumbing: open, close, bulk read submission, bulk write buffering, write callbacks, throttling, modem-status waits, sysrq handling, DCD handling, and resume.

## Important APIs, Types, And Functions

The optional generic driver defines `usb_serial_generic_device`, `generic_device_ids`, `usb_serial_generic_probe`, and `usb_serial_generic_calc_num_ports`. Exported helper functions include `usb_serial_generic_register`, `usb_serial_generic_deregister`, `usb_serial_generic_open`, `usb_serial_generic_close`, `usb_serial_generic_write`, `usb_serial_generic_write_start`, `usb_serial_generic_prepare_write_buffer`, `usb_serial_generic_write_room`, `usb_serial_generic_chars_in_buffer`, `usb_serial_generic_wait_until_sent`, `usb_serial_generic_submit_read_urbs`, `usb_serial_generic_process_read_urb`, `usb_serial_generic_read_bulk_callback`, `usb_serial_generic_write_bulk_callback`, `usb_serial_generic_throttle`, `usb_serial_generic_unthrottle`, `usb_serial_generic_tiocmiwait`, `usb_serial_generic_get_icount`, `usb_serial_handle_dcd_change`, and `usb_serial_generic_resume`.

The helpers rely on fields in `struct usb_serial_port`: read/write URB arrays, `write_fifo`, `write_urbs_free`, `read_urbs_free`, `tx_bytes`, `flags`, `lock`, `icount`, and the tty port object.

## Control Flow

Open clears throttling and submits all read URBs if the port has a bulk IN endpoint. Writes push data into the port kfifo under lock, then call `usb_serial_generic_write_start`. The write-start routine serializes itself with `USB_SERIAL_WRITE_BUSY`, finds free write URBs, asks the driver-specific `prepare_write_buffer` hook to fill each transfer buffer, updates `tx_bytes`, submits URBs, and loops until no data or no URBs remain. The write callback frees the URB slot, subtracts transmitted bytes, handles stopped or errored status, then restarts writes and wakes the tty layer.

Read callbacks process successful URBs through the driver-specific `process_read_urb` hook, mark the read URB free with memory barriers, and resubmit unless the URB was stopped or the port is throttled. The default read processor either handles console sysrq characters one byte at a time or inserts the whole buffer into the tty flip buffer. Throttle sets `USB_SERIAL_THROTTLED`; unthrottle clears it, uses a barrier matching the callback path, and submits free read URBs.

Modem-control waits snapshot `port->icount`, wait on `delta_msr_wait`, and wake when requested counters change or the tty port is no longer initialized. Resume walks initialized ports and restarts read URBs and pending writes with `GFP_NOIO`.

## State And Persistence

The file maintains optional module parameters `vendor` and `product` for the generic test driver. Per-port runtime state lives in USB serial core structures: fifos, URB-free bitmaps, flags, counters, and tty state. No persistent device configuration is written. The sysrq timer value in `port->sysrq` is transient and only active for console ports when configured.

## Dependencies And Integration Points

The code depends on Linux USB core, USB serial core, tty and tty flip buffers, kfifo, wait queues, spinlocks, jiffies, signals, serial counters, and optional console sysrq support. It is integrated both as a standalone testing driver and as a library of exported GPL symbols used by device-specific drivers such as Edgeport for `tiocmiwait` and `get_icount`.

## Risks

The highest-risk areas are concurrent URB completion, unthrottle, close, and resume. The read callback uses explicit memory barriers around `read_urbs_free`; changing that ordering could lose read resubmissions or race with unthrottle. Write accounting must keep `tx_bytes`, URB-free bits, and fifo contents consistent on submit failure and completion. The generic driver is intentionally broad and testing-only; enabling it for a real device can bind hardware without device-specific control setup. `wait_until_sent` polls `tx_empty`, so drivers must provide reliable `tx_empty` semantics for close/drain behavior.

## Test Signals

Signals include bulk-IN-only, bulk-OUT-only, and bidirectional devices; write fifo fill/drain under multiple URBs; submit failure rollback; close killing read/write URBs; throttle/unthrottle races under high RX rate; resume after suspend with pending I/O; modem counter waits and hangup behavior; DCD changes with and without `CLOCAL`; sysrq handling for console ports; and generic test-driver probe rejecting devices with no bulk endpoints.
