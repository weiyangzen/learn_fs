# sources/distributed-fs/ceph-client/drivers/media/i2c/t4ka3.c

## Purpose
`t4ka3.c` is a V4L2 sensor subdevice driver for the Toshiba T4KA3 8 MP Bayer camera sensor. It supports ACPI-enumerated hardware, CSI-2 endpoint validation, CCI register access, runtime power via GPIOs, crop/format selection with optional 2x binning, exposure/gain/blanking/flip/test-pattern controls, and stream start/stop sequences.

## Important APIs, Types, and Functions
- `struct t4ka3_data` stores the subdev, source pad, state mutex, controls, current calculated mode, device/regmap/GPIOs, streaming flag, and CSI-2 link metadata.
- `struct t4ka3_ctrls` groups V4L2 controls for flips, blanking, exposure, gain, test pattern, link frequency, and pixel rate.
- Register tables `t4ka3_init_config`, `t4ka3_pre_mode_set_regs`, and `t4ka3_post_mode_set_regs` program undocumented sensor setup and mode sequencing.
- `t4ka3_calc_mode()` decides 1x or 2x binning and computes centered crop-window start after binning.
- `t4ka3_set_pad_format()` clamps aligned output size to the crop rectangle, updates active state, recalculates mode, and adjusts vblank/hblank controls.
- `t4ka3_s_ctrl()` applies powered controls, including exposure range updates when vblank changes.
- `t4ka3_enable_stream()` powers the sensor, writes init/mode tables under group hold, restores controls, clears group hold, and starts streaming.
- `t4ka3_check_hwcfg()` validates the fwnode CSI-2 endpoint and requires exactly four data lanes.

## Control Flow and State
Probe checks firmware link frequencies and lane count, initializes the mutex and subdev, obtains powerdown and optional reset GPIOs, initializes a 16-bit CCI regmap, powers the sensor and verifies product ID `0x1490`, enables runtime PM, initializes media entity and active state, creates controls, registers the sensor subdev, and idles runtime PM.

Format and crop state are managed through the V4L2 subdev active state. The default crop is the active 3280x2460 area starting at row 2. Format changes are rejected while active streaming, preserve Bayer order according to flip controls, and choose 2x binning when requested dimensions fit within half the crop. Streaming state is separately tracked by `sensor->streaming` to block layout-changing flip and active format changes. Runtime PM resume deasserts GPIOs, waits, and re-detects the chip; suspend asserts powerdown and reset.

## Dependencies and Integration Points
The driver depends on ACPI ID `XMCC0003`, V4L2 subdev sensor registration, media entity source pad, CCI regmap helpers, V4L2 fwnode endpoint parsing and link-frequency matching, runtime PM, GPIO descriptors, mutex-backed control locking, and V4L2 stream helpers. Downstream bridge drivers consume its source pad, media-bus code, frame sizes, and link-frequency/pixel-rate controls.

## Risks and Edge Cases
- Many register values and timing constants are based on reverse engineering or comments without a datasheet; link frequency and vblank limits are approximations.
- `t4ka3_set_selection()` recalculates mode using the old crop pointer before assigning the new crop, so crop-size changes deserve focused review.
- Flip controls are blocked while streaming because they change Bayer order/layout.
- `t4ka3_disable_stream()` returns 0 even when the stream-off register write fails, only logging the error.
- Probe sets `sensor->sd.state_lock = sensor->ctrls.handler.lock` before controls initialize the handler lock, which should be checked against current V4L2 subdev expectations.
- Runtime resume performs chip detection every power-up, making resume dependent on I2C availability and sensor boot timing.

## Test Signals
Test ACPI probe, four-lane endpoint validation, link-frequency bitmap matching, product-ID failure and success paths, default crop/format initialization, crop and format alignment/clamping, full-size and half-size frame-size enumeration, vblank-driven exposure range changes, hblank read-only value updates, flip Bayer-order changes while stopped and `-EBUSY` while streaming, stream-on register sequence with group hold, runtime suspend/resume GPIO levels, and logged stream-off failures.
