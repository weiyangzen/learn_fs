# sources/distributed-fs/ceph-client/drivers/usb/serial/opticon.c

## Purpose

`opticon.c` is a Linux usb-serial driver for the Opticon 1D USB barcode-to-serial device (`0x065a:0x0009`). The device receives barcode data over a bulk-in endpoint but sends host-to-device data and modem-control changes over vendor control transfers instead of a bulk-out endpoint.

## Important APIs, Types, And Functions

`struct opticon_private` stores RTS and CTS booleans, write pressure counters (`outstanding_urbs`, `outstanding_bytes`), a spinlock protecting those fields, and an anchor for in-flight control-write URBs. Read-side functions are `opticon_process_read_urb()`, `opticon_process_data_packet()`, and `opticon_process_status_packet()`. Control and write functions include `send_control_msg()`, `opticon_write()`, `opticon_write_control_callback()`, `opticon_write_room()`, and `opticon_chars_in_buffer()`.

Lifecycle and tty modem-control hooks are `opticon_port_probe()`, `opticon_port_remove()`, `opticon_open()`, `opticon_close()`, `opticon_tiocmget()`, and `opticon_tiocmset()`. The registered driver uses one bulk-in endpoint with 256-byte input buffers and generic throttle/unthrottle handlers.

## Control Flow

Port probe allocates private state, initializes the spinlock and USB anchor, and stores the private pointer. Open clears cached RTS, sends a vendor control message to clear RTS on the device, clears the read endpoint halt, opens the generic usb-serial read path, and asks the device to resend CTS state. Close kills all anchored control-write URBs before closing the generic read path.

Read URBs use a two-byte packet header. Header `00 00` means the remaining bytes are data and are pushed to the tty. Header `00 01` means a CTS status packet, and the first payload byte updates cached CTS. Unknown or malformed packets are logged and dropped.

Writes first reserve capacity by incrementing outstanding counters under the spinlock, rejecting new data with zero bytes accepted when more than eight URBs are already outstanding. The payload is copied, a control URB and setup packet are allocated, and request `0x01` is sent over endpoint zero with the data as the control payload. The URB is anchored, submitted, and freed from the caller's reference; callback cleanup frees the copied payload and setup packet, decrements counters, and schedules the usb-serial soft interrupt. `write_room()` returns a generous 2048 until write pressure exceeds two thirds of the URB limit, and `chars_in_buffer()` reports outstanding bytes.

`tiocmget()` reports cached RTS and CTS. `tiocmset()` only supports RTS; when RTS changes it sends `CONTROL_RTS` with the inverse of the previous RTS boolean as written in the source.

## State And Persistence

The private state is memory-only per port. RTS is host-requested state, CTS is device-reported status from read packets or the open-time resend request, and outstanding write counters track anchored control URBs. No firmware or filesystem persistence exists. In-flight write URBs are explicitly anchored so close can cancel them.

## Dependencies And Integration Points

The file depends on usb-serial generic open/close/read support, USB control URBs, USB anchors, tty flip buffers, spinlocks, serial modem-control constants, and the tty write-buffer accounting interface. User-space sees a one-port tty with barcode data input, RTS/CTS modem status, and control-endpoint based writes.

## Risks And Edge Cases

`opticon_process_status_packet()` assumes a status payload byte exists; `opticon_process_read_urb()` only verifies the packet is longer than two bytes, so a `00 01` packet with no payload is not possible after that check, but malformed length handling depends on that invariant. The write limit comparison uses `>` rather than `>=`, allowing one more than `URB_UPPER_LIMIT` outstanding before returning zero. `tiocmset()` sends `!rts`, where `rts` is the old state captured before mutation, so this should be reviewed against the device protocol. Control-message failures during open are ignored before generic open, except generic open itself. Close cancels anchored writes, but read/control state races should be tested under disconnect.

## Test Signals

Test barcode data packets, CTS status packets, malformed and unknown headers, open-time RTS clear and CTS resend, generic read startup, control-write submission and callback cleanup, write pressure limits, `write_room()` thresholds, `chars_in_buffer()` counter accuracy under success and submit failure, close with in-flight anchored URBs, `TIOCM_RTS`/`TIOCM_CTS` reporting, RTS changes through `tiocmset()`, disconnect during control writes, and endpoint halt recovery on open.
