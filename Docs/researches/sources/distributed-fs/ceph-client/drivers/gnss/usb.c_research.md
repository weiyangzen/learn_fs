# sources/distributed-fs/ceph-client/drivers/gnss/usb.c

## Purpose
`usb.c` is a generic USB GNSS receiver driver. It exposes USB bulk GNSS devices as GNSS core character devices with continuous bulk-in URB reception and synchronous bulk-out writes.

## Important APIs, Types, and Functions
Private state is `struct gnss_usb`, storing the USB device, interface, GNSS device, read URB, and write pipe. GNSS ops are `gnss_usb_open()`, `gnss_usb_close()`, and `gnss_usb_write_raw()`. USB callbacks are `gnss_usb_probe()`, `gnss_usb_disconnect()`, and `gnss_usb_rx_complete()`.

## Control Flow
Probe finds one bulk-in and one bulk-out endpoint, allocates private state and a GNSS device, sets type `GNSS_TYPE_NMEA`, allocates a bulk read URB and buffer sized to at least 512 bytes, fills the URB, registers the GNSS device, and stores interface data. Open submits the read URB; completion inserts received bytes into the GNSS FIFO and resubmits unless the URB was stopped or shut down. Write duplicates the caller buffer and sends it with `usb_bulk_msg()` and a 1000 ms timeout. Disconnect deregisters GNSS, frees the URB buffer and URB, drops the GNSS device, and frees private state.

## State and Persistence
State is in memory only: USB pointers, one reusable read URB, write pipe, and GNSS FIFO state in the core. There is no persistent configuration.

## Dependencies and Integration Points
The driver depends on USB core APIs and GNSS core APIs. The current ID table matches Sierra Wireless XM1210 (`1199:b000`).

## Risks and Test Signals
The receive path drops bytes when the GNSS FIFO is full and only logs debug. Write allocates a temporary buffer for every call. The driver relies on GNSS deregistration closing/killing the URB before freeing it. Tests should cover endpoint discovery failure, open/close URB submit and kill, disconnect while open, receive resubmit after transient URB errors, FIFO overflow, write timeout, and short or failed bulk writes.
