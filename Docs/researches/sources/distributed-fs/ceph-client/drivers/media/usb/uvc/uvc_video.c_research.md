# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/uvc_video.c

## Purpose
`uvc_video.c` implements UVC video transport. It performs USB class control transactions for video probe/commit, fixes known device-specific descriptor/control defects, converts payload timestamps, decodes capture payloads, encodes output payloads, captures metadata headers, allocates and submits video URBs, and starts/stops streaming across normal operation and suspend/resume.

## Important APIs, types, and functions
Public entry points include `uvc_query_ctrl()`, `uvc_probe_video()`, `uvc_video_clock_update()`, `uvc_video_stats_dump()`, `uvc_video_init()`, `uvc_video_suspend()`, `uvc_video_resume()`, `uvc_video_start_streaming()`, and `uvc_video_stop_streaming()`. Probe/commit helpers include `__uvc_query_ctrl()`, `uvc_get_video_ctrl()`, `uvc_set_video_ctrl()`, `uvc_fixup_video_ctrl()`, and `uvc_commit_video()`. Streaming data flow uses `uvc_video_complete()`, `uvc_video_decode_isoc()`, `uvc_video_decode_bulk()`, `uvc_video_encode_bulk()`, `uvc_video_decode_start()`, `uvc_video_decode_data()`, `uvc_video_decode_end()`, and `uvc_video_next_buffers()`. URB memory management is handled by `uvc_alloc_urb_buffers()`, `uvc_init_video_isoc()`, `uvc_init_video_bulk()`, `uvc_video_start_transfer()`, and `uvc_video_stop_transfer()`.

## Control flow
Initialization resets the streaming interface to alternate setting 0, retrieves default/current probe controls, selects default/current format and frame descriptors, chooses the decode or encode function, and initializes async copy work. Starting streaming initializes the timestamp clock, commits negotiated controls, selects an isochronous alternate setting or bulk endpoint, allocates URBs and noncoherent buffers, submits all URBs, and optionally restores controls for affected devices. Completion fetches current video and metadata buffers, decodes or encodes payloads, queues async memcpy work if needed, and resubmits the URB. Stop poisons URBs, flushes the async workqueue, frees URBs and optionally buffers, resets the interface or clears bulk halt, and releases clock samples.

## State and persistence behavior
All state is volatile and stream-scoped. `struct uvc_streaming` stores negotiated `ctrl`, current format/frame, `sequence`, `last_fid`, bulk payload accumulator state, URB contexts, async workqueue, metadata queue configuration, statistics, and the timestamp clock ring buffer. `struct uvc_buffer` tracks bytes used, sequence, error state, PTS, and async reference count. No data persists beyond device/stream lifetime, but quirk behavior encodes long-lived compatibility policy for known devices.

## Dependencies and integration points
This file integrates with USB control and data paths, videobuf2 queues, UVC descriptor-derived format/frame tables, UVC control restore logic, JPEG marker helpers, debugfs statistics consumers, and V4L2 buffer timestamp semantics. It consumes module parameters such as `uvc_timeout_param`, `uvc_clock_param`, `uvc_hw_timestamps_param`, and quirk flags from `struct uvc_device`.

## Risks and edge cases
The main risks are concurrency and malformed device behavior. URBs can complete during teardown; poisoning plus workqueue flushing prevents resubmission after stop. Async memcpy takes buffer references and must release them exactly once. Payload parsing must handle missing EOF, missing/toggling FID, short headers, error bits, empty packets, bulk payloads spanning URBs, overflow, and queue cancellation with `buf == NULL`. Timestamp interpolation depends on enough SCR samples, SOF wrap handling, and device clock quality. Probe/commit code contains many workarounds; changing them can regress real hardware.

## Test signals
Test with isochronous and bulk cameras, capture and output devices, suspend/resume while streaming, unplug during active URBs, autosuspend wake quirks, multiple resolutions/intervals, metadata capture, hardware timestamps enabled/disabled, MJPEG streams with lost EOF, malformed short packets, and low-memory URB allocation fallback. Debug categories `VIDEO`, `FRAME`, `STATS`, and `CLOCK` provide strong runtime signals.
