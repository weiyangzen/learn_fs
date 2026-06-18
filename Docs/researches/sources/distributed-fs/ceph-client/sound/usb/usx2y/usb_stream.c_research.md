<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.c

## Purpose
Generic low-latency full-duplex USB isochronous streaming helper used by US-X2Y-style mmap/raw USB paths. It allocates shared read/write buffers, packet metadata, URBs, and synchronizes input and output isochronous completions.

## APIs, Types, and Functions
Exports `usb_stream_new()`, `usb_stream_free()`, `usb_stream_start()`, and `usb_stream_stop()`. Key internals include packet-size calculation (`usb_stream_next_packet_size()`, `playback_prep_freqn()`), URB setup (`init_urbs()`), startup/idle completion pairs, `stream_start()`, `stream_idle()`, `usb_stream_prepare_playback()`, and `submit_urbs()`.

## Control Flow, State, and Persistence
Allocation computes packets per period from rate and USB frame rate, allocates one `struct usb_stream` read area with packet descriptors and one write area, initializes four IN and four OUT URBs, and stores rate in Q16.16-style `freqn`. Start submits paired IN/OUT URBs on matching start frames, retries if frames differ, waits for sync states to reach ready, then switches callbacks to idle mode. Completion balancing waits until matching capture/playback URBs have completed, records input packet offsets in shared memory, prepares output packet descriptors either from captured packet lengths or nominal frequency, submits the next pair, increments `periods_done`, and wakes waiters.

## Dependencies and Integration
Depends on USB isochronous APIs and UAPI `sound/usb_stream.h` shared structures that userspace can mmap/read. It is independent of ALSA PCM ops but designed for audio period transport.

## Risks and Test Signals
Risks include fragile sync heuristics, fixed `USB_STREAM_NURBS`/depth assumptions, read/write allocation limits, start-frame retry timing, xrun state on zero-length/status packets, and shared-memory ABI compatibility. Test signals are start/stop at full/high speed, period wakeups, mmap clients reading packet tables, underrun injection, and long-running drift checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usb_stream.c -->
