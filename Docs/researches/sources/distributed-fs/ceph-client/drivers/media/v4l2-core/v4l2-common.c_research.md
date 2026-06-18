# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-common.c

## Purpose
`v4l2-common.c` contains generic exported V4L2 helper APIs shared by many media drivers. It covers legacy query-control filling, image dimension alignment, nearest-size lookup, subdev frame interval get/set helpers, a large pixel-format information table, single- and multi-planar format filling, media-controller link frequency helpers, active CSI-2 lane discovery, fraction/frame interval conversion, firmware-vs-driver link-frequency bitmap creation, and sensor clock acquisition/fallback.

## Important APIs, types, and functions
Exported helpers include `v4l2_ctrl_query_fill()`, `v4l_bound_align_image()`, `__v4l2_find_nearest_size_conditional()`, `v4l2_g_parm_cap()`, `v4l2_s_parm_cap()`, `v4l2_format_info()`, `v4l2_apply_frmsize_constraints()`, `v4l2_fill_pixfmt_mp()`, `v4l2_fill_pixfmt()`, `v4l2_get_link_freq()`, `v4l2_get_active_data_lanes()`, `v4l2_simplify_fraction()`, `v4l2_fraction_to_interval()`, `v4l2_link_freq_to_bitmap()`, and `__devm_v4l2_sensor_clk_get()`. Internal helpers compute block width/height, plane stride, plane height, and plane size from `struct v4l2_format_info`.

## Control flow
Control fill delegates to `v4l2_ctrl_fill()` and copies the resolved metadata into legacy queryctrl fields. Image alignment clamps dimensions and increases width/height alignment to satisfy combined size alignment. Format lookup linearly scans a static table of RGB, YUV, tiled, multiplanar, Bayer, and raw formats. Pixel-format filling computes bytesperline and sizeimage differently for single-memory-plane and multi-memory-plane formats. Link frequency first asks the subdev pad for `get_mbus_config`, then falls back to `V4L2_CID_LINK_FREQ` or an estimate from pixel rate. Sensor clock acquisition tries `devm_clk_get_optional()`, optional `clock-frequency`, optional rate setting, and finally a dummy fixed-rate clock on supported non-OF or legacy paths.

## State and persistence behavior
Most helpers are stateless. The static format table is read-only. `v4l2_simplify_fraction()` temporarily allocates continued-fraction terms. `__devm_v4l2_sensor_clk_get()` may register a devm-managed fixed clock whose lifetime follows the device. Link-frequency and lane helpers read live subdev control or media bus state but do not store it.

## Dependencies and integration points
The file integrates V4L2 controls, subdev pad operations, media controller pads, videodev2 pixel formats, common clock framework, firmware properties, and device logging. UVC code uses `v4l2_simplify_fraction()` and `v4l2_fraction_to_interval()` for frame interval conversions, and many camera/codec drivers use the format and link helpers.

## Risks and edge cases
The pixel-format table is central: wrong bpp, divisor, plane count, subsampling, or block dimensions will miscompute buffer sizes across drivers. `v4l2_simplify_fraction()` silently returns unchanged values if allocation fails. `v4l2_fraction_to_interval()` saturates on overflow and must handle denominator zero. Link frequency fallback from pixel rate is explicitly approximate and warns once. Sensor clock fallback behavior differs for OF, non-OF, and legacy callers, so dependency changes can alter probe timing.

## Test signals
Test format size calculations for representative RGB, packed YUV, planar, multiplanar, tiled, Bayer, and packed raw formats. Check nearest-size selection with predicates, alignment constraints, frame interval conversions, link-frequency matching against firmware arrays, active lane validation, and sensor clock paths with provided clocks, `clock-frequency`, missing clocks, fixed-rate requests, and deferred probe.
