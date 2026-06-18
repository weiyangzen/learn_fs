# sources/distributed-fs/ceph-client/drivers/usb/usb-skeleton.c

## Purpose

`usb-skeleton.c` is a sample USB bulk device driver that demonstrates matching a USB device, exposing a minor-backed character device, and safely performing bulk IN/OUT I/O with URBs, autosuspend, disconnect handling, and reset handling.

## Important APIs, Types, and Functions

`struct usb_skel` stores USB device/interface references, a write limit semaphore, submitted-URB anchor, one reusable bulk-in URB/buffer, endpoint addresses, error state, read waitqueue, kref, and I/O mutex. File operations are `skel_open()`, `skel_release()`, `skel_flush()`, `skel_read()`, and `skel_write()`. `skel_do_read_io()` submits the bulk-in URB; callbacks record errors or completion length. `skel_probe()` discovers endpoints and registers `skel%d`; `skel_disconnect()` deregisters and kills URBs.

## Control Flow

Open resolves the USB interface from the minor, resumes the device via autosuspend, and increments the kref. Reads serialize through `io_mutex`, wait for any ongoing read, consume cached bulk-in bytes, or submit a new read. Writes throttle concurrent URBs with `limit_sem`, allocate coherent buffers, anchor the URB, and submit bulk OUT. Flush and suspend call `skel_draw_down()` to wait for or kill outstanding writes and the read URB.

## State and Persistence Behavior

State is per connected interface and reference-counted. Errors are latched and reported once to userspace; `disconnected` prevents new submissions after unplug. No data persists beyond runtime buffers.

## Dependencies and Integration Points

It integrates with USB core device matching, USB class minor registration, userspace char-device I/O, autosuspend PM, URB anchoring, wait queues, krefs, and reset callbacks.

## Risks and Test Signals

Risks include single-reader design, partial read caching edge cases, user-triggered memory pressure despite `WRITES_IN_FLIGHT`, disconnect races, and using placeholder vendor/product IDs. Test signals include probe endpoint validation, blocking and nonblocking read/write behavior, error propagation from URB callbacks, unplug during active I/O, suspend/reset drawdown, and kref release after last close.
