# sources/distributed-fs/ceph-client/drivers/usb/serial/garmin_gps.c

## Purpose

This file implements the USB serial driver for Garmin GPS devices using vendor ID `0x091E` and product ID `3`. It exposes one tty port and bridges between user space and Garmin's USB packet protocol. The driver supports two modes: native mode, where user space exchanges Garmin USB packets directly, and Garmin serial protocol mode, where the driver converts DLE/ETX-framed serial packets to and from USB packet headers.

## Important APIs, Types, And Functions

`struct garmin_data` is the per-port state container. It stores the state machine value, flags, current mode, serial number, timer, input/output buffers, private control packet buffer, queued receive packets, write URB anchor, sequence counter, and spinlock. `struct garmin_packet` is a flexible-array list item used for queued device-to-tty packets.

Important functions include `garmin_port_probe`, `garmin_init_session`, `garmin_open`, `garmin_close`, `garmin_write`, `garmin_write_bulk`, `garmin_read_int_callback`, `garmin_read_bulk_callback`, `garmin_read_process`, `nat_receive`, `gsp_receive`, `gsp_rec_packet`, `gsp_send`, `gsp_next_packet`, `pkt_add`, `pkt_pop`, `pkt_clear`, `garmin_throttle`, `garmin_unthrottle`, `timeout_handler`, and `process_resetdev_request`. Private protocol packet IDs such as `PRIV_PKTID_SET_MODE`, `PRIV_PKTID_INFO_REQ`, `PRIV_PKTID_RESET_REQ`, and `PRIV_PKTID_SET_DEF_MODE` allow user space to query or adjust driver behavior.

## Control Flow

Probe allocates `garmin_data`, initializes the queue, timer, lock, write anchor, and starts a Garmin session. Session setup kills any old interrupt URB, submits the interrupt URB, marks the driver active, and sends the start-session request three times. Interrupt callbacks detect bulk-data-available notices and start bulk reads, or parse start-session replies to capture the device serial number. Bulk callbacks pass received USB packets to `garmin_read_process` and keep reading until a zero-length transfer or throttling stops the loop.

Writes first inspect the buffer for private driver packets. Private requests clear pending data, then change current mode, report version/mode/serial information, reset the USB device, or change the global `initial_mode`. Non-private writes are dispatched by mode. Native mode accumulates full Garmin USB packets in `inbuffer` and writes complete packets to bulk OUT. Garmin serial mode parses DLE-stuffed framed records, validates size and checksum, builds the 12-byte Garmin USB packet header in-place, writes the USB packet, and handles ACK/NAK by sending the next queued packet.

Read-side conversion also depends on mode. In native mode, application-layer packets can be sent directly to the tty unless throttled. In serial mode, USB application packets are queued and converted by `gsp_send` to DLE-framed serial packets, with checksum generation, DLE stuffing, and a wait for tty ACK before the next queued packet is sent.

## State And Persistence

Per-port state persists from `port_probe` to `port_remove`. `state` distinguishes reset, disconnected, active, waiting-for-tty-ack, and waiting-for-data conditions. `flags` track active bulk reads, restart requests, throttling, queueing, application request/response sightings, data dropping after abort commands, and serial parser skip/DLE state. The module parameter `initial_mode` is global and can be changed through a private packet for future opens. Queued packets are volatile and cleared on close, private control requests, abort-transfer commands, and mode changes. The device serial number is cached after the session reply.

## Dependencies And Integration Points

The driver integrates with the USB serial core through `struct usb_serial_driver garmin_device`, registering open/close/read/write/throttle callbacks and one port. It uses tty flip buffers, timers, USB interrupt and bulk URBs, anchored write URBs, little-endian helpers, and module parameters. User space sees a tty plus the private packet layer in native Garmin USB-packet format.

## Risks

The parser is stateful and accepts partial records, so DLE/ETX handling, checksum validation, and buffer limits are high-risk. `GPS_IN_BUFSIZ` and `GPS_OUT_BUFSIZ` bound protocol assumptions; larger future Garmin packets would be rejected or truncated by design. State and flags are partly protected by a spinlock but some mode and state assignments occur outside locks, so concurrency with callbacks, writes, close, reset, and throttle paths needs care. Reset kills interrupt URBs and calls `usb_reset_device`, which can race with open/close behavior if not serialized by the USB serial core. The write callback sends serial-mode ACKs based on the submitted application packet, so write failures with dismissed acknowledgements must not confuse user-space protocol state.

## Test Signals

Test signals include successful probe and session initialization, interrupt handling of bulk-available and session-reply packets, native-mode packet forwarding including partial writes, serial-mode DLE stuffing/unstuffing and checksum rejection, ACK/NAK pacing through queued packets, abort-transfer queue clearing, private info/mode/reset/default-mode requests, throttled queue behavior, close cleanup of timers/URBs/queued packets, and disconnect/reset under active reads and writes.
