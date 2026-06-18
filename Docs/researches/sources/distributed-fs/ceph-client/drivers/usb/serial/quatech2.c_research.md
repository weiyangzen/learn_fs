# sources/distributed-fs/ceph-client/drivers/usb/serial/quatech2.c

## Purpose
`quatech2.c` is the USB serial subdriver for second-generation Quatech USB-to-serial adapters with 1, 2, 4, or 8 logical UART ports. The notable hardware model is that all logical ports share a single bulk-in endpoint and a single bulk-out endpoint, so the driver multiplexes transmit payloads with a Quatech control header and demultiplexes receive payloads by parsing in-band control escape records.

## Important APIs, Types, and Functions
The module registers one `usb_serial_driver` named `quatech-serial` with callbacks for open, close, write, write-room, line control, break, modem status, termios, attach, release, disconnect, and per-port probe/remove. `struct qt2_serial_private` holds shared device state, including the shared read URB, read buffer, and the currently selected receive port. `struct qt2_port_private` stores per-port UART number, write URB/buffer, URB busy flag, and cached line/modem status. Important helpers include `qt2_calc_num_ports()`, `qt2_set_port_config()`, `qt2_control_msg()`, `qt2_getregister()`, `qt2_setregister()`, and `update_mctrl()`.

## Control Flow, State, and Persistence
Probe-time port count is derived from product IDs. `qt2_attach()` powers the unit, allocates shared serial-private data, allocates a 512-byte shared read buffer, fills one shared bulk read URB against port 0 endpoints, and immediately submits it. Each port probe allocates its own write URB and 512-byte write buffer but targets the shared bulk-out endpoint. Open switches the selected logical port to RS232 mode, sends `QT_OPEN_CLOSE_CHANNEL`, snapshots initial LSR/MSR bytes, configures default 9600 8N, and applies caller termios. Write serializes one active write URB per port and prepends `ESC ESC <device_port> <le16 length>` before the payload. Read completion parses `ESC ESC` records for line status, modem status, transmit-hold, port switch, flush, and escaped control bytes, changing `current_port` and pushing tty flip buffers at port boundaries.

State lives only in kernel memory: shared URB/buffer data, per-port shadow LSR/MSR, write busy flags, and current demux port. It is reset on disconnect/module removal and not persisted externally. Line changes update `port->icount` and `delta_msr_wait` for generic TIOCM wait integration.

## Dependencies and Integration Points
The file depends on the USB serial core, TTY flip buffer API, USB control/bulk URB APIs, `serial_reg.h` UART bit definitions, and the generic USB serial helpers for `tiocmiwait` and `get_icount`. Integration is through `module_usb_serial_driver()`, `usb_set_serial_data()`, `usb_set_serial_port_data()`, and core callbacks in `struct usb_serial_driver`.

## Risks and Test Signals
Primary risks are malformed in-band control messages corrupting demultiplexing, shared endpoint concurrency bugs, short control responses during open/status reads, and write starvation because each port owns only one write URB. Suspend/resume is not implemented here, so behavior relies on core disconnect/close handling. Useful tests include binding each supported product ID, verifying calculated port counts, opening multiple ports concurrently, injecting data that includes escaped control bytes, changing termios and modem lines, checking break control, and disconnecting while read/write URBs are active.
