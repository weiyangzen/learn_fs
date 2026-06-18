
# sources/distributed-fs/ceph-client/drivers/media/usb/siano/smsusb.c

## Purpose
`smsusb.c` implements the USB transport for Siano SMS1xxx MDTV receivers. It binds many Siano and branded USB IDs, loads cold-state firmware for Stellar devices, allocates bulk URBs, translates Siano message endian format, registers with the common `smscore` layer, and handles suspend/resume.

## Important APIs, Types, and Functions
`enum smsusb_state` tracks disconnected, suspended, and active device states. `struct smsusb_device_t` stores the USB device, smscore device, endpoint numbers, response alignment, buffer size, and an array of `struct smsusb_urb_t`. Important functions are `smsusb_probe()`, `smsusb_disconnect()`, `smsusb_suspend()`, `smsusb_resume()`, `smsusb_init_device()`, `smsusb_term_device()`, `smsusb_start_streaming()`, `smsusb_stop_streaming()`, `smsusb_submit_urb()`, `smsusb_onresponse()`, `smsusb_sendrequest()`, `smsusb1_load_firmware()`, `smsusb1_detectmode()`, and `smsusb1_setmode()`.

## Control Flow
Probe first filters for the board's expected interface number, clears endpoint stalls, and ignores ROM interface 0 on two-interface devices. For cold Stellar ROM IDs, it loads mode-specific firmware with `smsusb1_load_firmware()` and lets the device re-enumerate. Warm devices call `smsusb_init_device()`, which discovers bulk endpoints, chooses USB1 or USB2 buffer sizes, registers a media controller device when enabled, registers with `smscore`, allocates up to ten receive URBs, submits them, marks the device active, and starts the core device. Each URB completion validates the Siano message header, handles split-message alignment, endian-converts RX data, passes the buffer to `smscore_onresponse()`, and schedules a work item to resubmit the URB from process context. Outbound messages are copied, endian-converted, and sent with `usb_bulk_msg()`. Suspend kills URBs and sets suspended state; resume clears stalls, resets the interface, and restarts streaming.

## State and Persistence
Device state is runtime-only: endpoints, response alignment, buffer pool ownership, URBs, smscore core pointer, and active/suspended/disconnected state. Firmware files are externally persisted, with board-specific names coming from `sms_get_board(board_id)->fw` or fallback `smsusb1_fw_lkup`. No driver configuration is persisted beyond smscore registry mode lookup for cold firmware choice.

## Dependencies and Integration Points
The driver depends on Linux USB bulk APIs, firmware loader, workqueues, media controller optional support, and the shared Siano `smscore`/board/endian APIs. It integrates with board descriptors via `driver_info`, calls `sms_board_load_modules()` after probe, and exposes send/detect/set-mode callbacks to smscore.

## Risks and Edge Cases
URB completion cannot sleep, so resubmission is deferred; teardown must cancel work after killing URBs to avoid use-after-free. Split-message alignment adjusts buffer offsets and copies the header; bad length or offset calculations can corrupt message delivery. `smsusb_sendrequest()` rejects non-active devices, so resume ordering matters. Cold firmware load intentionally returns after upload because the device resets and re-enumerates. Resume restarts streaming but does not explicitly set `state = SMSUSB_ACTIVE`, so behavior depends on higher-layer expectations after suspend.

## Test Signals
Test cold-to-warm Stellar firmware upload, board/interface filtering, endpoint halt clearing, USB1 and USB2 family buffer sizes, split-message reception, smscore buffer return on stop, media-controller registration cleanup, suspend/resume with live DVB applications, disconnect during queued work, and outbound request rejection while suspended or disconnected.
