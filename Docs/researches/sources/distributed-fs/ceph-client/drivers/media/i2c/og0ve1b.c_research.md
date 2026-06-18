# sources/distributed-fs/ceph-client/drivers/media/i2c/og0ve1b.c

## Purpose
`og0ve1b.c` is a V4L2 sub-device driver for the OmniVision OG0VE1B monochrome/greyscale image sensor. It exposes one CSI-2 source pad, a single 640x480 120 fps 8-bit mode, runtime power management, and the usual camera controls for link frequency, pixel rate, blanking, analogue gain, exposure, and a vertical color-bar test pattern.

## Important APIs, Types, and Functions
The central state is `struct og0ve1b`, which owns the CCI regmap, xvclk, optional reset GPIO, three regulators, media pad, V4L2 subdev, control handler, `vblank`/`exposure` controls, and a cached `pre_isp` register value used to preserve unrelated bits while toggling test pattern output. `struct og0ve1b_mode` describes the fixed mode and its `cci_reg_sequence` list. Key operations are `og0ve1b_set_ctrl()`, `og0ve1b_enable_streams()`, `og0ve1b_disable_streams()`, `og0ve1b_set_pad_format()`, `og0ve1b_identify_sensor()`, `og0ve1b_check_hwcfg()`, `og0ve1b_power_on()`, `og0ve1b_power_off()`, `og0ve1b_probe()`, and `og0ve1b_remove()`.

## Control Flow
Probe initializes the subdev, builds a 16-bit-address CCI regmap, validates a 24 MHz xvclk, validates the fwnode endpoint link frequency against the 500 MHz menu, acquires reset and `avdd`/`dovdd`/`dvdd`, powers the sensor, reads the 24-bit chip ID and `PRE_ISP`, registers controls and a single source pad, finalizes the subdev state, enables runtime PM, registers asynchronously, and idles the device. Streaming resumes runtime PM, issues a software reset, writes the 640x480 mode table, applies active controls, then writes mode-select streaming. Stop writes standby and releases the runtime PM reference through autosuspend.

## State and Persistence
Persistent state is hardware-backed register state plus the software `pre_isp` cache read during identification. V4L2 control values are retained by the control framework while the sensor is powered down; writes are skipped unless `pm_runtime_get_if_active()` succeeds and are replayed by `__v4l2_ctrl_handler_setup()` at stream start. Runtime PM controls clock, reset, and regulators; there is no filesystem persistence.

## Dependencies and Integration Points
The driver integrates with the I2C core, OF matching for `ovti,og0ve1b`, V4L2 async sensor registration, media-controller pads, V4L2 subdev state, V4L2 fwnode endpoint parsing, `v4l2_subdev_s_stream_helper`, the CCI regmap helpers, the regulator and GPIO frameworks, and runtime PM. The output media-bus code is fixed to `MEDIA_BUS_FMT_Y8_1X8`.

## Risks and Edge Cases
The driver only checks that the endpoint contains a supported link frequency; it does not enforce the number of CSI-2 data lanes. Pixel-rate computation is `link_freq / bpp`, which omits lane and DDR factors used by many Bayer drivers and should be checked against the binding and hardware timing. `og0ve1b_enum_frame_size()` contains a duplicated `if (fse->index >= ARRAY_SIZE(supported_modes))` line in this snapshot. Test-pattern writes depend on a cached `PRE_ISP` value, so any hardware-side change to other bits after probe can be overwritten when the test pattern toggles.

## Test Signals
Useful signals include successful probe with a 24 MHz xvclk and matching chip ID `0xc75645`, endpoint rejection when the 500 MHz link frequency is absent, correct single `Y8_1X8` format enumeration, stream start/stop register writes around runtime PM transitions, exposure limit updates when `V4L2_CID_VBLANK` changes, analogue gain and exposure programming while streaming, test-pattern toggling without losing unrelated `PRE_ISP` bits, and remove/error paths leaving reset asserted and regulators disabled.
