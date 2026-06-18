# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-scaler.c

## Purpose
`vimc-scaler.c` implements a two-pad VIMC scaler subdevice. It accepts non-Bayer frames, supports sink cropping and source scaling, and produces a resized frame for downstream capture.

## Important APIs, Types, and Functions
`struct vimc_scaler_device` embeds entity/subdev/pads, a stream-time source frame, and virtual hardware snapshots of sink/source formats, crop rectangle, and bytes per pixel. Key callbacks are `vimc_scaler_init_state()`, `vimc_scaler_enum_mbus_code()`, `vimc_scaler_set_fmt()`, `vimc_scaler_get_selection()`, `vimc_scaler_set_selection()`, `vimc_scaler_s_stream()`, and `vimc_scaler_process_frame()`. The entity export is `vimc_scaler_type`.

## Control Flow
Default active state sets both pads to 640x480 RGB888 and crop to the full sink. The scaler enumerates only non-Bayer bus codes. Sink format changes update code/colorimetry, clamp dimensions, reset crop, and propagate to source; source format changes can adjust dimensions but inherit code/colorimetry. Crop selection is allowed only on the sink and is clamped inside sink bounds with minimum size. Stream-on snapshots formats and crop, computes frame size, and allocates `src_frame`. Frame processing uses nearest-neighbor mapping from each output pixel to a cropped input pixel and copies one pixel of `bpp` bytes.

## State and Persistence
Negotiated formats and crop live in V4L2 subdev state. The `hw` snapshot and `src_frame` exist while streaming. State is freed on stream-off and release.

## Dependencies and Integration Points
The scaler depends on media-bus formats, V4L2 rectangle helpers, subdev active-state APIs, vmalloc, and common pixel-map helpers. It sits between debayer/input and RGB/YUV capture in the hard-coded topology.

## Risks and Edge Cases
The scaler rejects Bayer formats, so links from raw Bayer sources must pass through debayer or raw capture instead. Active format/crop changes are blocked while `src_frame` exists. The scaling algorithm is simple nearest-neighbor and does not handle multi-plane formats. It assumes `vimc_pix_map_by_code(format->code)` succeeds for active formats.

## Test Signals
Tests should enumerate only non-Bayer codes, verify crop bounds/minimums, confirm source propagation from sink, stream scaling up/down with known patterns, and validate link failures when formats do not match downstream capture.
