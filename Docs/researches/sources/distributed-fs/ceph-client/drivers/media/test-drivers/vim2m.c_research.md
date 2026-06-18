# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vim2m.c

## Purpose
`vim2m.c` is a virtual V4L2 memory-to-memory test device. It exercises the mem2mem and videobuf2 frameworks by accepting OUTPUT buffers, transforming pixels into CAPTURE buffers, and completing jobs through delayed work that simulates hardware interrupt latency.

## Important APIs, Types, and Functions
The driver registers a platform device/driver named `"vim2m"` and a `video_device` with V4L2 M2M capabilities. Device state is `struct vim2m_dev`; per-open-instance state is `struct vim2m_ctx`; per-queue format state is `struct vim2m_q_data`; supported formats are in `formats[]`. Core processing functions are `device_process()`, `copy_line()`, and `copy_two_pixels()`, supporting RGB565/RGB565X/RGB24/BGR24 input and RGB/YUYV/Bayer capture output. Mem2mem callbacks are `device_run()`, `job_ready()`, `job_abort()`, and delayed-work `device_work()`. V4L2 ioctl handlers cover format enumeration, try/set/get format, frame sizes, streaming, buffer operations, request controls, and events.

## Control Flow
Module init registers the platform device and driver. Probe allocates the device, registers a V4L2 device, initializes `v4l2_m2m_dev`, sets up a media device and media-controller entity, registers `/dev/video0` or another free node, and registers the media device. On open, a `vim2m_ctx` is allocated, controls are created, default source and destination formats are initialized, and a mem2mem context creates vb2 queues. Users queue source and destination buffers; `job_ready()` waits until `translen` buffers are available on both sides. `device_run()` applies request controls, processes the next buffer pair immediately, completes request controls, and schedules delayed work. `device_work()` removes buffers, marks them done, and either finishes the M2M job or recursively starts the next pair in the transaction.

## State and Persistence
Global module parameters control debug level, default transaction time, and single-planar versus multiplanar operation. Per-device state tracks instance count, locks, V4L2/media objects, and the mem2mem scheduler. Per-context state tracks controls, pending transaction length/time, abort flag, H/V flip mode, colorimetry, source/destination format data, sequence counters, vb2 mutex, and delayed work. All state is volatile and released on close/remove/module unload.

## Dependencies and Integration Points
The driver uses V4L2 core, media controller, `v4l2-mem2mem`, videobuf2 vmalloc memory ops, V4L2 controls/events/requests, and platform-driver registration. It is intended for user-space V4L2 compliance tools and applications testing mem2mem scheduling, format negotiation, requests, scaling, flipping, and conversion without hardware.

## Risks and Edge Cases
Processing assumes a single memory plane in `device_process()` by accessing plane 0 even in multiplanar mode; current formats are effectively single-plane, but future multi-plane formats would need deeper handling. Format conversion processes pixels in pairs (`width >> 1`), so width alignment is critical, especially for Bayer output. `copy_line()` reverse mode assumes even widths. `stop_streaming()` cancels delayed work and returns all queued buffers as errors, but controls must be completed for every path. `job_abort()` only sets a flag, so completion waits for the delayed work path. Memory limit enforcement can reduce requested buffer counts down to zero if formats grow.

## Test Signals
Useful tests include `v4l2-compliance` in both single-planar and multiplanar modes, format enumeration and try/set/get checks, HFLIP/VFLIP controls, transaction length/time controls, request API behavior, streaming stop during delayed work, Bayer alignment, scaling between different resolutions, and conversion correctness using known pixel patterns.
