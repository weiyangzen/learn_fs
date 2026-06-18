# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.c

## Purpose
Implements IPU7 ISYS V4L2 capture video nodes, pixel-format negotiation, media link validation, firmware stream configuration/open/start/flush/close, shared stream allocation, runtime firmware open reference counting, and video device registration/cleanup.

## Important APIs, Types, and Functions
Exports `ipu7_isys_pfmts[]`, `ipu7_isys_get_isys_format()`, `ipu7_isys_video_prepare_stream()`, `ipu7_isys_put_stream()`, `ipu7_isys_query_stream_by_handle()`, `ipu7_isys_query_stream_by_source()`, `ipu7_isys_video_set_streaming()`, `ipu7_isys_fw_open()`, `ipu7_isys_fw_close()`, `ipu7_isys_setup_video()`, `ipu7_isys_video_init()`, and `ipu7_isys_video_cleanup()`. Internal V4L2 ioctls implement querycap, format enumeration, frame-size enumeration, get/try/set format, reqbufs, and create_bufs. Firmware helpers include `ipu7_isys_fw_pin_cfg()`, `start_stream_firmware()`, `stop_streaming_firmware()`, and `close_streaming_firmware()`.

## Control Flow
Format negotiation clamps geometry, aligns bytes-per-line to 64 bytes, maps V4L2 formats to media-bus codes and firmware frame formats, and adds an overshoot allowance to `sizeimage`. `ipu7_isys_setup_video()` resolves the remote CSI2 pad and external sensor, finds active route metadata, obtains CSI2 frame descriptors or falls back to media-bus-code MIPI type, starts/joins the media pipeline, and obtains a shared stream keyed by CSI source and virtual channel. `ipu7_isys_video_set_streaming(1)` opens firmware stream configuration, waits for open completion, submits the initial start-and-capture buffer set, waits for start ACK, then enables the connected subdevice stream. State 0 flushes firmware, disables the subdevice, closes the firmware stream, and drops open counts.

## State and Persistence Behavior
`struct ipu7_isys_video` stores current pixel format, capture queue, stream pointer, CSI2 pointer, current VC/DT, and `streaming` flag. Shared `struct ipu7_isys_stream` instances are allocated from the parent ISYS array with spinlock-protected refcounts and are reused by multiple queues on the same source/VC. Firmware open is reference-counted in `isys->ref_count`, protected by `isys->mutex`, and runtime PM is held while firmware is open. Completion objects in the stream persist across commands and are reinitialized before each wait.

## Dependencies and Integration Points
Depends on media-controller pipeline APIs, V4L2 ioctl/vb2 helpers, firmware ABI and command wrappers, CSI2 descriptor helpers, queue callbacks, runtime PM, PM QoS via top-level ISYS, and TSC support indirectly through queue timestamping. Firmware pin setup wires `stream->output_pins[pin].pin_ready` to `ipu7_isys_queue_buf_ready()`.

## Risks and Test Signals
Risks include `ipu7_isys_vidioc_s_fmt_vid_cap()` ignoring the return from try-format on busy queues, firmware open/stream completion timeouts leaving partially opened state, subdevice enable failure after firmware start requiring robust flush, and refcount misuse for shared streams. Test format alignment/overshoot, busy queue `S_FMT`, sensors with multi-entry frame descriptors sharing a VC, multi-video-node stream startup ordering, firmware open/start/flush/close timeout paths, runtime PM reference balance, and media link mismatch rejection.
