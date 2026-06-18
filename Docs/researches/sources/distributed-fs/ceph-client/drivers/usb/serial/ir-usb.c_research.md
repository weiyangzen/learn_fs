<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ir-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ir-usb.c

## Purpose
Implements a "dumb" USB IrDA serial driver for devices that can be treated as byte-stream serial endpoints without using the full IrDA network stack. It wraps payload bytes with USB IrDA packet headers carrying baud-rate and additional-BOF information.

## Important APIs, Types, And Functions
The `ir_device` usb-serial driver exposes one port with one bulk-in and one bulk-out endpoint, custom attach, write, write-room, write callback, read processing, and termios handling. `irda_usb_find_class_desc()` retrieves the USB IrDA class descriptor with `USB_REQ_CS_IRDA_GET_CLASS_DESC`; `ir_startup()` validates it, logs supported rates, and stores default additional BOF count. `ir_xbof_change()` maps BOF counts to USB IrDA header bits. `ir_write()` reserves the single write URB, prefixes the outbound IrDA header, submits the URB, and tracks `tx_bytes`. `ir_process_read_urb()` consumes the inbound header and pushes payload to tty. `ir_set_termios()` maps requested tty baud to USB IrDA line-speed codes and sends a one-byte bulk message to change speed.

## Control Flow
Registration is manual through `ir_init()` so the `buffer_size` module parameter can modify bulk buffer sizes before driver registration. Attach requires a valid class descriptor and records the device-provided BOF value. Writes are limited to `bulk_out_size - 1` because byte zero is reserved for the IrDA header. Write completion frees the single write URB bit and wakes the tty. Reads ignore empty packets, update the global baud nibble when the inbound header reports a rate change, and pass bytes after the header to the tty layer. Termios changes preserve only speed changes by restoring old hardware flags, encoding the accepted baud, and sending an empty data packet with the desired header.

## State And Persistence
The file uses module-global `ir_baud`, `ir_xbof`, and `ir_add_bof`, so comments explicitly note only one device is effectively supported per system for those settings. Module parameters `buffer_size` and `xbof` alter transfer sizing and forced BOF count. No persistent device storage is changed.

## Dependencies And Integration Points
It depends on USB IrDA class definitions from `linux/usb/irda.h`, usb-serial port locking and write URB bitmaps, tty termios helpers, and standard USB bulk/control APIs. It overlaps in purpose with the full `usb-irda` network driver but intentionally exposes a tty stream.

## Risks And Edge Cases
Global speed/BOF state can cross-contaminate multiple devices. `ir_set_termios()` does not verify requested baud against descriptor-supported rates despite a FIXME. Unsupported speed requests silently fall back to 9600. A device that returns a malformed class descriptor is rejected. Because only one write URB is used, write throughput and backpressure depend on the tty layer honoring `ir_write_room()`.

## Test Signals
Useful tests include descriptor fetch success/failure, supported-rate logging, every baud mapping from 2400 through 4000000, forced `xbof` module parameter behavior, payload header stripping on reads, header prefixing on writes, single-URB backpressure, custom `buffer_size`, and multi-device testing to expose global-state limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ir-usb.c -->
