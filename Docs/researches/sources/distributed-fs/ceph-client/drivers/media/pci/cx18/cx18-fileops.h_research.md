# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-fileops.h

## Purpose
This header declares cx18 V4L2 file operation helpers and stream claim/release functions shared across stream registration, ioctl, ALSA, and capture code.

## Important APIs, Types, and Functions
Declarations cover `cx18_v4l2_open()`, `cx18_v4l2_read()`, `cx18_v4l2_write()`, `cx18_v4l2_close()`, `cx18_v4l2_enc_poll()`, `cx18_start_capture()`, `cx18_stop_capture()`, `cx18_mute()`, `cx18_unmute()`, `cx18_v4l2_mmap()`, `cx18_clear_queue()`, `cx18_vb_timeout()`, `cx18_claim_stream()`, and `cx18_release_stream()`.

## Control Flow
No executable flow lives here. It publishes entry points used when building `video_device` file operations and when other modules need to participate in stream ownership.

## State and Persistence
The functions manipulate stream flags, queues, file handles, and capture state in `struct cx18`, but the header itself stores no state.

## Dependencies and Integration Points
It depends on Linux file, poll, vm area, vb2 buffer-state, and cx18 stream/open-id types from included driver headers. The `cx18_claim_stream()` and `cx18_release_stream()` declarations are explicitly shared with `cx18-alsa`.

## Risks and Edge Cases
Several declared functions are implemented outside this source slice, so changing prototypes requires coordinated updates. `cx18_v4l2_write()` and mmap/queue helpers must match registered file/ioctl ops even though their implementation is elsewhere.

## Test Signals
Compile/link coverage catches prototype drift. Runtime signals include working open/read/poll/close on all registered V4L2 nodes and ALSA coexistence with PCM stream claims.
