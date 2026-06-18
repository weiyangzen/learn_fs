
# sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc.h

## Purpose
`pwc.h` is the shared internal header for the Philips/NXP USB webcam driver. It defines device limits, Philips vendor-control request selectors, frame and USB isochronous buffer sizing, codec family predicates, the central `struct pwc_device`, and prototypes used by the interface, V4L2, control, and decompression implementation files.

## Important APIs, Types, and Functions
Important constants include `PWC_VERSION`, `MAX_WIDTH`, `MAX_HEIGHT`, `MAX_ISO_BUFS`, `ISO_FRAMES_PER_DESC`, `ISO_MAX_FRAME_SIZE`, `PWC_FRAME_SIZE`, and supported size identifiers `PSZ_*`. Vendor-control selectors are grouped around luminance, chrominance, status, stream, and motorized pan/tilt requests. `struct pwc_raw_frame` describes compressed camera data, `struct pwc_frame_buf` embeds `vb2_v4l2_buffer`, and `struct pwc_device` aggregates USB state, V4L2/vb2 queues, controls, frame assembly state, decompressor private data, and optional snapshot-button input state. Declared cross-file APIs include `pwc_set_video_mode()`, `send_control_msg()`, `pwc_get_u8_ctrl()`/`pwc_set_u8_ctrl()`, `pwc_init_controls()`, `pwc_camera_power()`, `pwc_ioctl_ops`, and `pwc_decompress()`.

## Control Flow
The header itself has no executable flow, but it defines the data path used by the driver: USB isochronous completion fills `fill_buf`, raw camera payload is tracked with header/trailer sizes and `vbandlength`, then `pwc_decompress()` expands or passes data into user buffers managed by vb2. Control flow for userspace settings is routed through V4L2 control objects in `struct pwc_device`, through the `pwc_get_*_ctrl`/`pwc_set_*_ctrl` helpers, and finally through Philips vendor control transfers.

## State and Persistence
Runtime state is per camera in `struct pwc_device`: USB identity and endpoint selection, current video mode, current frame counters, isochronous URBs, queued vb2 buffers, decompressor state, cached auto white-balance/gain/exposure values with jiffies timestamps, and optional input-device state. The only durable device behavior exposed here is the camera's own save/restore user defaults and factory defaults control selectors; the Linux driver has no filesystem persistence.

## Dependencies and Integration Points
The header integrates Linux USB, V4L2 device/ioctl/control/event APIs, videobuf2-v4l2/vmalloc memory ops, wait queues, mutexes, spinlocks, and optional input evdev support. It also depends on the local codec headers `pwc-dec1.h` and `pwc-dec23.h`. Consumers of this header must respect the lock ordering comment: `vb_queue_lock` before `v4l2_lock` when both are needed.

## Risks and Edge Cases
The single large `struct pwc_device` mixes USB disconnect state, queue state, and control caches, so teardown paths must hold the documented locks before setting `udev` to NULL. Frame-size constants assume worst-case VGA YUV420 plus ToUCam header/trailer overhead; mismatched sizes can cause decompressor or vb2 payload errors. Codec-family macros depend on model-number ranges. Vendor-control cache timestamps can return stale gain/exposure/white-balance readings if invalidation is missed.

## Test Signals
Useful signals include successful probe for codec1/codec2/codec3 cameras, V4L2 format enumeration for compressed and decompressed modes, mmap/read streaming through vb2, isochronous error recovery after startup low-watermark frames, correct control get/set traffic for luminance/chrominance/status selectors, optional snapshot-button events, and clean behavior when a device is unplugged while buffers or controls are active.
