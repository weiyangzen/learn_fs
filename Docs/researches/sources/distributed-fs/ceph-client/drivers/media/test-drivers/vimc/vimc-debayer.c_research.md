# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-debayer.c

## Purpose
`vimc-debayer.c` implements a VIMC subdevice that converts Bayer-pattern sink frames to RGB-like source frames. It is a virtual pixel conversion stage used between sensors and the scaler/capture pipeline.

## Important APIs, Types, and Functions
`struct vimc_debayer_device` embeds entity/subdev/control/pad state, a source frame buffer, conversion callback, and virtual hardware configuration. Static maps describe Bayer code color ordering and supported RGB source bus codes. Key callbacks are `vimc_debayer_init_state()`, `vimc_debayer_enum_mbus_code()`, `vimc_debayer_set_fmt()`, `vimc_debayer_s_stream()`, `vimc_debayer_process_frame()`, and `vimc_debayer_s_ctrl()`. The entity export is `vimc_debayer_type`.

## Control Flow
Active state initializes sink pad to SRGGB8 and source pad to RGB888. Format setting is allowed only on the sink when not streaming; the source follows dimensions/colorimetry with RGB output code. Stream-on snapshots active formats into `hw`, determines sink bytes per pixel, source code, Bayer map, dimensions, and allocates a source frame. For each incoming frame, `vimc_debayer_process_frame()` iterates over every pixel, computes RGB values by averaging same-color samples in the configured odd-sized mean window, and writes RGB/BGR bytes to the source frame.

## State and Persistence
State is per subdevice. Active V4L2 subdev state stores negotiated formats. `hw` is a stream-time snapshot plus mean-window control value. `src_frame` exists only while streaming and is freed on stream-off. There is no persistent storage.

## Dependencies and Integration Points
The file depends on V4L2 subdev active-state APIs, controls/events, vmalloc, media-bus formats, and common VIMC pixel maps. It integrates with the streamer through `ved.process_frame` and with user space through V4L2 subdev format and control ioctls.

## Risks and Edge Cases
The per-pixel mean-window algorithm is intentionally simple but expensive, especially at large resolutions and window sizes. `vimc_debayer_process_rgb_frame()` handles RGB24 and BGR24 pixelformats; other valid source bus codes mapped to RGB24 are okay through `vimc_pix_map_by_code()`, but unsupported fourcc cases silently write nothing. `set_fmt()` blocks active changes when `src_frame` exists, so stream state must be correct. The control handler stores mean-window changes directly into `hw`, including while streaming.

## Test Signals
Tests should enumerate sink Bayer and source RGB codes, verify source format propagation, change mean-window control, stream known Bayer patterns through the pipeline, and validate stream-on/off buffer allocation cleanup. Performance tests at maximum resolution can expose excessive CPU use.
