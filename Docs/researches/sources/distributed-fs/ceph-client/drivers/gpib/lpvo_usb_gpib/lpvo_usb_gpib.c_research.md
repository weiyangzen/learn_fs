# sources/distributed-fs/ceph-client/drivers/gpib/lpvo_usb_gpib/lpvo_usb_gpib.c

## Purpose

`lpvo_usb_gpib.c` supports the LPVO/Open USB-GPIB adapter by combining a linux-gpib `struct gpib_interface` implementation with a modified USB skeleton bulk I/O driver. The adapter is driven through a text/binary command protocol over an FTDI-style USB bulk device. The USB ID table is intentionally empty because the known FTDI ID is normally handled by `ftdi_sio`; users must bind devices manually or add an ID/rule.

## Important APIs, Types, and Functions

- Adapter protocol constants such as `USB_GPIB_ON`, `USB_GPIB_OFF`, `USB_GPIB_STATUS`, `USB_GPIB_READ`, `USB_GPIB_READ_1`, `USB_GPIB_DEBUG_ON`, `USB_GPIB_SET_LINES`, `USB_GPIB_UNTALK`, and `USB_GPIB_UNLISTEN` define the wire protocol.
- `struct usb_gpib_priv` stores per-board EOS byte/flags, cached timeout, and pointer to the USB skeleton `struct lpvo`.
- Global arrays `lpvo_usb_interfaces[]`, `usb_minors[]`, and `assigned_usb_minors` map USB minors to gpib attach choices under `minors_lock`.
- `send_command()`, `write_loop()`, `set_control_line()`, `one_char()`, and `set_timeout()` implement adapter command exchange and timeout programming.
- `usb_gpib_attach()` selects a USB device by sysfs path, bus/devnum, or `ibbase` minor; opens the USB object; turns the adapter on; enables debug/extended protocol; configures REN/IFC behavior; and disables first-byte timeout.
- `usb_gpib_read()` parses LPVO framed reads with `DLE STX` start, `DLE ETX ACK` end, DLE escaping, single-byte special handling, software EOS detection, and overflow flushing.
- `usb_gpib_write()` frames writes as newline, `IB`, DLE/STX, payload, DLE/ETX/newline, sends the command, and then unlistens.
- `usb_gpib_command()`, control-line callbacks, line status, parallel poll, EOS, status update, and placeholders implement the gpib callback table.
- `struct lpvo` stores USB device/interface, bulk URB/buffers, endpoint addresses, error state, read progress, kref, I/O mutex, wait queue, and write anchor/semaphore.
- `lpvo_probe()`, `lpvo_disconnect()`, suspend/resume/reset hooks, `lpvo_do_open()`, `lpvo_do_release()`, `lpvo_do_read()`, and `lpvo_do_write()` own USB lifecycle and bulk I/O.

## Control Flow

USB probe allocates `struct lpvo`, initializes kref, semaphore, mutex, spinlock, URB anchor, and read wait queue, takes a USB-device reference, discovers bulk endpoints, allocates the read buffer and URB, stores intfdata, optionally registers a raw userspace USB class device, lowers FTDI latency to 1 ms, and calls `usb_gpib_init_module()` to register the gpib interface on the first detected adapter and record the interface/minor in the global table.

GPIB attach locks the minor table, finds the requested adapter by `device_path`, bus/devnum, or USB minor, allocates `usb_gpib_priv`, opens the `struct lpvo` by USB minor, and sends a sequence of adapter setup commands. Detach sends adapter-off, waits briefly, releases the USB object, and frees private data.

Reads first set adapter timeouts if needed. Length-one reads use `USB_GPIB_READ_1` and expect one data byte plus ACK. Multi-byte reads send `USB_GPIB_READ`, require `DLE STX`, then loop through data and control escapes. Data bytes are appended until caller length, software EOS, or `DLE ETX ACK`. If the caller buffer fills before frame end, it discards up to `MAX_READ_EXCESS` bytes looking for the closing frame. Successful framed reads send UNTALK.

Writes allocate a frame buffer, copy the payload without DLE escaping, send it through `send_command()`, set `*bytes_written`, and send UNLISTEN. `send_eoi` is accepted by the signature but not explicitly encoded in the frame.

The skeleton read path serializes with `io_mutex`, waits for ongoing URBs, reports and clears stored errors, strips the two FTDI status bytes at the start of valid bulk reads, and restarts if only the two status bytes were returned. Writes use a semaphore to allow only one URB in flight, allocate coherent DMA memory, anchor the URB, and release resources in the write callback.

## State and Persistence Behavior

Per-board gpib state is in `usb_gpib_priv`, especially cached timeout and EOS software settings. Per-USB-interface state is in `struct lpvo` and persists from probe to disconnect with kref ownership shared by gpib attach and optional raw userspace opens. Global minor tables persist while devices are present and drive gpib interface registration/unregistration. Error state is latched in `dev->errors` and reported once. USB reset sets `errors = -EPIPE` in post-reset.

## Dependencies and Integration Points

The driver depends on the USB core, autosuspend APIs, URBs, USB class device registration when `USER_DEVICE` is enabled, linux-gpib private APIs, FTDI latency control request values, and the LPVO adapter protocol. It integrates with gpib-common through one `gpib_interface` named by `KBUILD_MODNAME`, with `skip_check_for_command_acceptors = 1`.

## Risks and Test Signals

The USB device ID table is empty by design, so automatic binding will not occur without external configuration. `usb_gpib_write()` explicitly notes DLE bytes are not escaped and can only safely send ASCII-like data; binary payloads containing DLE can corrupt framing. Several gpib callbacks are stubs returning success or zero (`primary_address`, `secondary_address`, serial poll response/status, T1 delay, parallel-poll configuration/response, return-to-local), which limits compliance. `send_eoi` is not meaningfully handled in write. `usb_gpib_attach()` returns errors after `lpvo_do_open()` and allocation without always releasing the opened device/private data unless detach follows. `lpvo_do_write()` copies `count` bytes into a buffer sized for `writesize`, which is `min(count, MAX_TRANSFER)`; large writes risk overflow unless callers never exceed `MAX_TRANSFER`. Test signals are manual USB binding, attach by path/bus/minor, setup command ACKs, timeout programming, framed reads including DLE escaping and overflow flush, writes with and without DLE bytes, disconnect during I/O, suspend/reset recovery, raw user-device open/read/write if enabled, and gpib-core behavior around stubbed callbacks.
