# sources/distributed-fs/ceph-client/drivers/usb/serial/mxuport.c

## Purpose

`mxuport.c` is the Linux usb-serial driver for Moxa UPort USB-to-serial adapters with 2, 4, 8, or 16 ports. It handles devices that multiplex all serial data over a shared bulk-in/bulk-out framing protocol, receive control events on a second bulk-in endpoint, and may need firmware comparison and download at probe time.

## Important APIs, Types, And Functions

`struct mxuport_port` stores per-port modem-control and modem-status snapshots. A mutex protects `mcr_state`, while a spinlock protects `msr_state`. The file defines many Moxa vendor requests for baud, line settings, flow control, open/close, purge, firmware, interface mode, and queue-status commands.

USB control helpers are `mxuport_recv_ctrl_urb()`, `mxuport_send_ctrl_data_urb()`, and `mxuport_send_ctrl_urb()`. Framing and demux are handled by `mxuport_prepare_write_buffer()`, `mxuport_process_read_urb()`, `mxuport_process_read_urb_demux_data()`, `mxuport_process_read_urb_demux_event()`, `mxuport_process_read_urb_data()`, `mxuport_msr_event()`, `mxuport_lsr_event()`, and `mxuport_process_read_urb_event()`.

TTY operations include `mxuport_open()`, `mxuport_close()`, `mxuport_set_termios()`, `mxuport_set_termios_flow()`, `mxuport_break_ctl()`, `mxuport_tx_empty()`, `mxuport_tiocmget()`, `mxuport_tiocmset()`, `mxuport_dtr_rts()`, `mxuport_throttle()`, and `mxuport_unthrottle()`. Device lifecycle is handled by `mxuport_probe()`, `mxuport_calc_num_ports()`, `mxuport_port_probe()`, `mxuport_attach()`, `mxuport_release()`, and `mxuport_resume()`.

## Control Flow

Probe first queries firmware configuration; on failure it sends a reset request and fails. It reads the running firmware version, requests `moxa/moxa-<productid>.fw`, compares embedded version bytes at `VER_ADDR_1/2/3`, and downloads the firmware if the local version is newer. The selected device feature bit from the USB ID table is stored in serial private data.

`mxuport_calc_num_ports()` converts feature bits into a port count and configures all logical bulk-out endpoints to share endpoint zero. Attach submits generic read URBs for port 0 and port 1: port 0 carries multiplexed data frames, and port 1 carries event frames. Release closes those shared read paths.

Writes use `mxuport_prepare_write_buffer()` to pop tty write FIFO bytes into a packet with a four-byte big-endian header containing logical port number and payload length. Reads demultiplex one URB into possibly multiple logical-port messages. Data messages validate header size, port number, and payload length, then push data to the target tty only if that tty port is initialized. Event messages validate fixed eight-byte records and dispatch MSR, LSR, and MCR events. MSR events update cached modem status, increment icount deltas, and wake `delta_msr_wait`; LSR events increment break/frame/parity/overrun counts.

Open enables host receive, sends device open, applies initial termios, and clears cached MSR. Close sends device close and disables host receive. Termios writes line format, software flow-control characters and enablement, DTR/RTS behavior including `B0` transitions, hardware RTS flow-control mode, and baud as a little-endian 32-bit value. Throttle/unthrottle cannot stop shared read URB submission, so they tell the device to disable or enable host receive for the logical port.

## State And Persistence

Driver state is volatile. Firmware may be downloaded into the device during probe, but the driver itself does not persist data. `mcr_state` mirrors host-requested DTR/RTS and is updated only after successful control requests. `msr_state` is event-driven and starts at zero on open because the code notes that `RQ_VENDOR_GET_MSR` is not understood. Generic usb-serial FIFOs and URBs carry write/read buffering, with shared endpoint multiplexing configured during port-count calculation.

## Dependencies And Integration Points

The driver depends on usb-serial generic helpers for read URB submission, write start, close, tiocmiwait, and icount. It uses the firmware loader (`request_firmware()`), USB control messaging, tty flip buffers, unaligned endian helpers, mutexes, spinlocks, and serial register constants. User-facing behavior appears through ttyUSB ports, modem-control ioctls, break control, `tx_empty`, flow control, and firmware files under the standard firmware search path.

## Risks And Edge Cases

The shared endpoint protocol means malformed device frames can affect all ports on the adapter; the demux code returns from the whole URB on the first invalid record. Cached MSR starts unknown until events arrive, so early `tiocmget()` can report low signals even if hardware lines are high. Firmware download assumes version offsets exist in the blob and that larger numeric version means newer. Control-message failures in close/throttle paths are not propagated to callers. Suspend handling is only resume-specific here; resume always restarts shared read URBs for ports 0 and 1 and write queues for initialized ports.

## Test Signals

Test across all supported port-count families, firmware present/missing/newer/equal/older cases, malformed data and event frames, multi-port simultaneous reads and writes, write framing lengths and endianness, open failure rollback, host receive throttle/unthrottle per logical port, software and hardware flow control, B0 drop/raise behavior, DTR/RTS ioctls, MSR delta wakeups, LSR error accounting, `tx_empty()` with queued device bytes, resume after active IO, and unplug during firmware download or shared URB operation.
