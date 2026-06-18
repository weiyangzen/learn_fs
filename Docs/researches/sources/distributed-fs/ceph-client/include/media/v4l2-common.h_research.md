# sources/distributed-fs/ceph-client/include/media/v4l2-common.h

## Purpose
Defines shared internal V4L2 helper APIs for logging, control query filling, I2C/SPI subdevice creation, tuner address probing, image alignment, nearest-size selection, stream parameter helpers, pixel-format metadata, link-frequency/lane discovery, sensor clock lookup, timestamp conversion, and colorimetry validation.

## Important APIs, Types, and Functions
Logging macros include `v4l_*`, `v4l2_*`, and debug-level variants. APIs include `v4l2_ctrl_query_fill()`, I2C helpers such as `v4l2_i2c_new_subdev*()`, `v4l2_i2c_subdev_init()`, tuner address lists, SPI subdev helpers, legacy `TUNER_SET_CONFIG` and `VIDIOC_INT_RESET`, `v4l_bound_align_image()`, nearest-size macros/backing function, `v4l2_g_parm_cap()`, `v4l2_s_parm_cap()`, `V4L2_FRACT_COMPARE`, `struct v4l2_format_info`, format classification helpers, `v4l2_format_info()`, pixfmt fill helpers, media-controller link frequency/lane helpers, fraction helpers, `v4l2_link_freq_to_bitmap()`, sensor clock helpers, buffer timestamp get/set, and colorimetry validity helpers.

## Control Flow
Bridge drivers use bus helpers to instantiate subdevices, format helpers to negotiate pixel layouts, alignment helpers to clamp requested dimensions, and link helpers to query transmitter pad configuration or controls. Sensor drivers use clock helpers to bridge firmware/ACPI clock description gaps.

## State and Persistence Behavior
Most helpers are stateless. Subdevice creation registers I2C/SPI client/subdev state elsewhere. Sensor clock helpers may register devm-managed fixed clocks for ACPI cases. Timestamp helpers translate between legacy timeval fields and nanoseconds.

## Dependencies and Integration Points
Depends on V4L2 dev/subdev/video types, I2C, SPI, clocks, media-controller pads, firmware properties, and V4L2 UAPI pixel/colorimetry structures. It is a broad integration header for low-level V4L2 drivers.

## Risks
Helper stubs return `NULL` or no-op when I2C/SPI/media-controller support is disabled, so callers must handle missing support. Nearest-size macros require width/height fields to be `u32`. Link-frequency fallback depends on valid transmitter controls. Timestamp conversion preserves 32-bit userspace compatibility by truncating `tv_usec` to `u32`.

## Test Signals
I2C/SPI subdevice probe/unregister, tuner address probing, image alignment edge cases, nearest-size with and without predicate, streamparm get/set through subdevs, format-info fill for planar/packed formats, link frequency from mbus config/control/pixel rate, active data lane validation, ACPI sensor clock fallback, timestamp round trips, and colorimetry validation.
