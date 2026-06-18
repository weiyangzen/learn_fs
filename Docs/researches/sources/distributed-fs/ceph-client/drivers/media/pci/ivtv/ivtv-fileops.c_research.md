# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.c

## Purpose
`ivtv-fileops.c` implements V4L2 file operations and stream lifetime management for ivtv capture, VBI, radio, MPEG decode, YUV decode, and VBI output devices. It handles open/close/read/write/poll, stream claiming, start/stop, buffer copying, MPEG VBI insertion, radio switching, and audio mute helpers.

## Important APIs, Types, and Functions
Exported or externally used functions include `ivtv_claim_stream()`, `ivtv_release_stream()`, `ivtv_start_capture()`, `ivtv_stop_capture()`, `ivtv_start_decoding()`, `ivtv_v4l2_open()`, `ivtv_v4l2_close()`, `ivtv_v4l2_read()`, `ivtv_v4l2_write()`, `ivtv_v4l2_enc_poll()`, `ivtv_v4l2_dec_poll()`, `ivtv_mute()`, and `ivtv_unmute()`. Internal helpers include `ivtv_get_buffer()`, `ivtv_copy_buf_to_user()`, `ivtv_update_pgm_info()`, `ivtv_dualwatch()`, `ivtv_schedule()`, and `ivtv_schedule_dma()`.

## Control Flow
Open performs first-open firmware initialization, checks firmware health, rejects incompatible simultaneous MPEG/YUV decode opens, allocates a per-file `ivtv_open_id`, and performs radio or YUV setup. Read serializes on `serialize_lock`, starts capture on demand, then drains full/io buffers or injected VBI MPEG buffers to userspace. Write claims decoder streams, fixes output mode, starts decode, copies userspace data into buffers or performs YUV UDMA frame transfers, and schedules DMA when firmware asks for data. Close stops capture or decode, unwinds radio mode, releases V4L2 file handles, clears stream flags, and releases claimed streams.

## State and Persistence
State lives in `ivtv_stream` flags and queues, per-open `ivtv_open_id`, atomics for capturing/decoding, VBI insertion counters, program index cache, output mode, radio-user flag, speed flags, and wait queues. Nothing persists across device removal.

## Dependencies and Integration Points
The file depends on queue helpers, stream firmware start/stop helpers, IRQ/DMA/UDMA, VBI processing, routing/ioctl helpers, YUV support, firmware health checks, V4L2 events, and tuner/subdevice calls.

## Risks and Edge Cases
Automatic VBI stream claiming must not conflict with application VBI reads. Blocking paths temporarily drop `serialize_lock`, so wakeups and flags must be correct. MPEG VBI insertion scans packet boundaries and can return partial buffers. Decoder output mode is exclusive across MPEG/YUV/UDMA paths. Radio open is rejected during capture. Nonblocking read/write must return `-EAGAIN` without leaking claimed state.

## Test Signals
Validate blocking and nonblocking reads/writes, poll-triggered capture start, close during active capture/decode, embedded sliced VBI insertion, standalone VBI capture, radio open/close switching, simultaneous decoder stream exclusion, YUV frame-sized writes and UDMA, firmware-dead open rejection, stream queue flushes, and poll event behavior for old and new V4L2 event APIs.
