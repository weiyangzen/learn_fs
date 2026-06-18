# sources/distributed-fs/ceph-client/drivers/greybus/gb-beagleplay.c

## Purpose

`gb-beagleplay.c` is a serdev Greybus host driver for BeaglePlay boards using a TI CC1352P7 as a Greybus bridge. It transports Greybus messages over UART using HDLC framing, starts/stops the remote SVC with control frames, and exposes Linux firmware-upload operations to flash the CC1352 bootloader firmware while temporarily tearing down Greybus.

## Important APIs, Types, and Functions

- `struct gb_beagleplay` stores serdev, Greybus host, TX work/circular buffer, RX HDLC parser state, firmware upload state, bootloader GPIOs, completions, and CRC bookkeeping.
- HDLC TX helpers `hdlc_tx_frames()`, `hdlc_append_tx_*()`, and `hdlc_transmit()` encode complete frames into a circular buffer and drain them through `serdev_device_write_buf()`.
- HDLC RX helpers `hdlc_rx()`, `hdlc_rx_frame()`, `hdlc_rx_greybus_frame()`, and `hdlc_rx_dbg_frame()` unescape frames, validate CRC-CCITT, ACK I-frames, and dispatch Greybus/debug payloads.
- `gb_message_send()` implements the `gb_hd_driver` send callback by framing CPort, Greybus header, and payload under address `ADDRESS_GREYBUS`.
- `gb_beagleplay_start_svc()` and `gb_beagleplay_stop_svc()` emit control frames.
- Bootloader helpers implement sync, ACK/NACK waits, status, bank erase, reset, CRC32, download, and send-data commands.
- Firmware-upload callbacks `cc1352_prepare()`, `cc1352_write()`, `cc1352_poll_complete()`, `cc1352_cancel()`, and `cc1352_cleanup()` manage flashing.
- `gb_beagleplay_probe()` initializes serdev, HDLC, firmware upload, Greybus host, then starts SVC.

## Control Flow

During probe, the driver allocates state, opens and configures the serial device at 115200 baud, initializes HDLC TX/RX state, registers firmware upload support, creates/adds a Greybus host with up to 32 CPorts, and sends a control frame to start the remote SVC. Incoming serial data is routed to the bootloader parser when `flashing_mode` is true; otherwise it is parsed as HDLC.

Greybus send constructs an HDLC frame containing a little-endian CPort, operation header, and payload. The TX path waits for enough circular-buffer space outside the producer spinlock, then enqueues the full frame atomically and schedules the consumer work. RX validates the frame FCS against `0xf0b8`, ACKs I-frames, and passes Greybus payloads to `greybus_data_rcvd()`.

Firmware upload stops normal Greybus, enters bootloader mode via GPIO reset/backdoor sequencing, syncs with the CC1352 bootloader, optionally skips if CRCs match, erases, streams non-empty packets with download-address resets around skipped `0xff` regions, verifies CRC, resets the controller, recreates Greybus, and restarts SVC.

## State and Persistence Behavior

The per-device state persists for the serdev device lifetime. The TX circular buffer is shared by Greybus, control, and bootloader-stop/start paths; producer and consumer locks plus release/acquire ordering protect head/tail. `flashing_mode` is the key mode switch for RX parsing and write wakeups. Firmware upload state tracks ACKs, command response values, computed image CRC, and whether a new download command is needed after skipped empty flash regions.

## Dependencies and Integration Points

The file integrates with serdev, Greybus host-device APIs, firmware-upload core, GPIO descriptors, CRC32, CRC-CCITT, circular buffers, completions, and device tree compatible `ti,cc1352p7`. It relies on the Greybus core for SVC/module enumeration once the remote SVC starts.

## Risks and Edge Cases

- `hdlc_rx_greybus_frame()` trusts that the decoded frame is long enough for `struct hdlc_greybus_frame` and that the embedded Greybus size fits the HDLC payload.
- `gb_message_send()` rejects messages whose Greybus header size exceeds `RX_HDLC_PAYLOAD`, tying the usable MTU to the RX payload constant despite the TX circular buffer being larger.
- `cc1352_bootloader_rx()` contains two identical overflow checks with different log levels; this is harmless but suggests defensive code drift.
- Firmware prepare deinitializes Greybus before all subsequent bootloader steps; failures before cleanup/reinit can leave the remote bridge in flashing mode until higher layers recover.
- `gb_message_cancel()` is empty, so operation cancellation cannot retract already queued HDLC frames.
- `hdlc_tx_frames()` waits for space with retries; under sustained backpressure frames are dropped with `-EAGAIN`.

## Test Signals

Exercise HDLC escaping/FCS/ACK behavior, unknown address handling, circular-buffer full paths, Greybus message size rejection, serdev wakeup scheduling, SVC start/stop frames, firmware upload same-image skip, erase/write/verify/reset success, bootloader ACK/NACK/timeout paths, GPIO sequencing, probe unwind at each init stage, and remove during active or failed flashing.
