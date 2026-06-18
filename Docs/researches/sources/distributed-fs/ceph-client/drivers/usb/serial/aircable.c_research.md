<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/aircable.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/aircable.c

Purpose: AIRcable USB Bluetooth dongle serial driver; ignores the firmware/control interface and binds the serial interface. The complete 160-line source was read.

Important APIs/types/functions: USB ID `16ca:1502`; `aircable_calc_num_ports()`, `aircable_prepare_write_buffer()`, `aircable_process_read_urb()`, `aircable_process_packet()`, and `struct usb_serial_driver aircable_device`.

Control flow and state: probe rejects interfaces with no bulk-out endpoint. Writes prepend a four-byte `0x20 0x29` little-endian length header to FIFO data. Reads process 64-byte frames, stripping four-byte headers when the URB starts with receive header `0x00`, otherwise passing no-header overflow data directly. It owns no private state beyond usbserial FIFOs and tty buffers.

Dependencies and integration points: USB serial core, tty flip buffers, unaligned little-endian helpers, generic throttle/unthrottle.

Risks and test signals: risks include malformed short packets, mixed header/no-header frames, and not validating header length against payload. Test interface filtering, framed writes, framed and unframed reads, short packets, and throttle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/aircable.c -->
