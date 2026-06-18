# sources/distributed-fs/ceph-client/drivers/usb/serial/keyspan.c

## Purpose
This is the main Keyspan USB-to-serial converter driver for many post-renumeration Keyspan adapters plus a pre-renumeration firmware loader. It binds one-, two-, and four-port Keyspan products, downloads EZ-USB FX1 firmware for unconfigured devices, maps product IDs to device-specific endpoint layouts and message formats, and exposes serial ports through the Linux `usb_serial_driver` and TTY interfaces.

## Important APIs, Types, and Functions
The central device descriptor is `struct keyspan_device_details`, which records product ID, message format (`msg_usa26`, `msg_usa28`, `msg_usa49`, `msg_usa90`, `msg_usa67`), port count, endpoint maps, baud clock, and baud-rate callback. Per-device state lives in `struct keyspan_serial_private` with global status/control/data URBs and buffers. Per-port state lives in `struct keyspan_port_private` with input/output URB pairs, control URBs, baud and termios cache, modem input/output state, flip indexes, transmit start timestamps, and pending control resend state.

The public USB serial hooks are `keyspan_open`, `keyspan_close`, `keyspan_write`, `keyspan_write_room`, `keyspan_set_termios`, `keyspan_break_ctl`, `keyspan_tiocmget`, `keyspan_tiocmset`, `keyspan_dtr_rts`, `keyspan_startup`, `keyspan_disconnect`, `keyspan_release`, `keyspan_port_probe`, and `keyspan_port_remove`. `keyspan_fake_startup` selects and downloads firmware using `ezusb_fx1_ihex_firmware_download`. `keyspan_setup_urb` and `keyspan_setup_urbs` build URBs from endpoint descriptors and the `keyspan_callbacks` dispatch table.

## Control Flow
Module registration publishes four serial drivers: `keyspan_no_firm`, `keyspan_1`, `keyspan_2`, and `keyspan_4`. Pre-renumeration devices enter `keyspan_fake_startup`, pick a firmware filename from the product ID, download it, and deliberately return a nonzero attach result so the temporary device is not bound while it renumerates. Real devices enter `keyspan_startup`, match a `keyspan_device_details`, allocate global buffers/URBs, submit status URBs, and optionally submit the USA49WG aggregate data URB.

Each port is initialized by `keyspan_port_probe`, which allocates per-port buffers, constructs data/control URBs according to the selected endpoint map, and stores private state. `keyspan_open` resets modem defaults, submits all input URBs, derives the initial baud and flow-control settings from termios, then calls `keyspan_send_setup(..., 1)` to enable RX/TX and reset data toggles. `keyspan_close` drops RTS/DTR, sends a close setup message, delays for legacy transfer behavior, and kills per-port URBs.

Writes are split into protocol-sized packets: USA90 can use 64 bytes with no prefix; the others reserve byte 0 for the request-ack flag and send up to 63 payload bytes. For devices with endpoint flipping, `out_flip` alternates between URBs. If an output URB remains busy for more than ten seconds, it is unlinked before retry.

Inbound control flow is protocol-specific. USA26/49/67 parse a leading status byte and mark parity/framing/overrun errors with TTY flip flags. USA28 can flip between two input URBs and treat input as raw data. USA90 switches between by-hand error/status framing at lower baud rates and DMA/raw framing above 57600. USA49WG receives aggregate messages containing a port number and payload length, demultiplexing the single global IN endpoint to individual TTY ports. Status callbacks update cached CTS/DSR/DCD/RI values and hang up the TTY on DCD drops where implemented.

## State and Persistence
All runtime state is in kernel memory and attached to `usb_serial` or `usb_serial_port`; there is no persistent storage beyond required firmware blobs. State includes cached termios/baud fields, cached modem state, input/output endpoint flip indexes, `resend_cont` control-message retry intent, and the allocated URB/buffer graph. Open/close mutates port enablement, RX/TX flags, DTR/RTS, and break state through device-specific setup messages. Disconnect and release kill/free URBs and buffers.

## Dependencies and Integration Points
The file depends on the Linux USB serial core, TTY flip-buffer APIs, URB submission/killing, `usb_control`/bulk/interrupt pipe helpers, `linux/usb/ezusb.h`, and the five local Keyspan message headers. It integrates with firmware loading through `MODULE_FIRMWARE` names under `keyspan/`, and with TTY modem-control semantics via `TIOCM_*`, `CRTSCTS`, `CSTOPB`, `PARENB`, `PARODD`, and `CSIZE`.

## Risks
The driver relies on detailed per-product endpoint and message metadata; a wrong product mapping can silently route data or setup packets to the wrong endpoint. Several comments note missing locking around write-room and global control URB state, while the resend paths rely on `resend_cont` and busy URB status rather than a stronger serialized control queue. Some receive paths do not resubmit on nonzero URB status, so only expected teardown errors should reach those paths. Break handling is incomplete for some receive-side error reports. Legacy busy handling uses delays and status polling around URBs, which is sensitive to callback context and disconnect races.

## Test Signals
Useful tests include firmware-load/renumeration checks for every pre-product ID, smoke opens for one-, two-, and four-port adapters, baud setting across supported rates, DTR/RTS and `TIOCMGET`/`TIOCMSET`, close/open cycling, high-rate USA90 DMA receive, USA49WG aggregate receive demultiplexing, endpoint-flip write throughput, DCD hangup behavior, and disconnect while status/control/data URBs are active.
