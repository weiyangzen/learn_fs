# subset-b-004095 research

This grouped report covers OmniVision/OmniVision-compatible V4L2 I2C camera sensor drivers under `sources/distributed-fs/ceph-client/drivers/media/i2c`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/og0ve1b.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/og0ve1b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/os05b10.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/os05b10.c

## Purpose
`os05b10.c` is a V4L2 sub-device driver for the OS05B10 5 MP Bayer sensor. It supports one 2592x1944 10-bit BGGR mode over four CSI-2 lanes at a 600 MHz link frequency, exposes native/active crop rectangles, and manages power, clocking, blanking, exposure, and analogue gain.

## Important APIs, Types, and Functions
`struct os05b10` holds device, CCI regmap, subdev, media pad, xclk, I2C client, optional reset GPIO, supplies, control handler, link/hblank/vblank/gain/exposure controls, selected link-frequency index, and data-lane count. `struct os05b10_mode` stores width, height, VTS, HTS, default exposure, and bits per pixel. The main routines are `os05b10_set_ctrl()`, `os05b10_set_framing_limits()`, `os05b10_set_pad_format()`, `os05b10_get_selection()`, `os05b10_enable_streams()`, `os05b10_disable_streams()`, `os05b10_identify_module()`, `os05b10_power_on()`, `os05b10_parse_endpoint()`, `os05b10_pixel_rate()`, `os05b10_init_controls()`, and probe/remove.

## Control Flow
Probe builds the CCI regmap, requires a 24 MHz xclk, acquires regulators, parses endpoint 0 and rejects any non-four-lane bus or missing 600 MHz link frequency, acquires optional reset, powers on, reads the 24-bit chip ID `0x530641`, creates controls, initializes a single sensor source pad, finalizes subdev state, enables runtime PM, registers with V4L2 async, and idles the sensor. Stream enable resumes runtime PM, writes the large common register table, applies current controls, and writes `OS05B10_REG_CTRL_MODE` streaming. Disable writes standby and drops the PM reference.

## State and Persistence
State lives in the active subdev format, controls, selected link-frequency index, parsed lane count, and volatile sensor registers. Control writes are skipped while the device is runtime-suspended and replayed at stream enable. Runtime PM owns regulators, xclk, and reset GPIO sequencing; no suspend register cache or persistent storage is implemented.

## Dependencies and Integration Points
The file depends on Linux I2C, CCI regmap, V4L2 subdev/media-controller APIs, V4L2 fwnode parsing, regulator/GPIO/clock frameworks, and runtime PM. It binds through OF compatible `ovti,os05b10`, exposes `MEDIA_BUS_FMT_SBGGR10_1X10`, and uses `v4l2_subdev_s_stream_helper` plus pad `enable_streams`/`disable_streams`.

## Risks and Edge Cases
The mode is fixed; requests for other sizes are forced to 2592x1944. Endpoint parsing requires exactly four data lanes and a 600 MHz link frequency, so board descriptions must be exact. `os05b10_disable_streams()` returns 0 even if the standby write fails after logging an error, which can hide stop failures from callers. Power-off disables regulators before the clock in this snapshot, so hardware sequencing should be checked against the datasheet. The active/native selection rectangles are hard-coded and should match the binding and sensor optical crop.

## Test Signals
Test probe with valid and invalid xclk, lane count, and link-frequency properties; verify chip-ID mismatch errors; check `V4L2_SEL_TGT_NATIVE_SIZE`, crop bounds, default crop, and active crop; confirm pixel-rate calculation for 600 MHz, four lanes, 10 bpp; exercise vblank-driven exposure range updates; and validate stream-on/off PM reference balance, common-register writes, gain/exposure/VTS writes, and source pad format enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/os05b10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov01a10.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov01a10.c

## Purpose
`ov01a10.c` drives the OmniVision OV01A10/OV01A1B family as an ACPI-enumerated V4L2 camera sensor. It exposes a crop-capable one-lane CSI-2 subdev with configurable output dimensions within a 1296x816 native array, handles Bayer or greyscale bus formats depending on matched model, and provides gain, exposure, digital gain, flips, blanking, link frequency, pixel rate, and test-pattern controls.

## Important APIs, Types, and Functions
`struct ov01a10_sensor_cfg` captures model-specific behavior: name, media-bus format, Bayer pattern size, border size, base format register value, and flip-window inversion rules. `struct ov01a10` owns device, regmap, selected config, subdev, media pad, controls, link-frequency index, clock, reset/powerdown GPIOs, and regulators. Important functions include `ov01a10_update_digital_gain()`, `ov01a10_set_format1()`, `ov01a10_set_hflip()`, `ov01a10_set_vflip()`, `ov01a10_set_ctrl()`, `ov01a10_init_controls()`, `ov01a10_set_mode()`, `ov01a10_start_streaming()`, `ov01a10_set_format()`, `ov01a10_get_selection()`, `ov01a10_set_selection()`, `ov01a10_get_pm_resources()`, `ov01a10_identify_module()`, `ov01a10_check_hwcfg()`, and probe/remove.

## Control Flow
Probe reads match data from ACPI IDs `OVTI01A0` or `OVTI01AB`, initializes a CCI regmap and V4L2 I2C subdev, validates a fwnode endpoint supplied by the bridge, requires one CSI-2 data lane and a supported 400 MHz link frequency, gets a 19.2 MHz clock plus optional reset/powerdown GPIOs and regulators, powers on, verifies chip ID `0x560141`, initializes controls, creates the media pad, finalizes subdev state, enables runtime PM, idles the device, and registers with V4L2 async. Streaming locks active state, resumes runtime PM, writes link-frequency PLL registers, global settings, active crop/output timing registers, applies controls, then writes mode-select streaming.

## State and Persistence
The V4L2 active state stores crop and format. Control state persists in the control framework and is written only when runtime PM says the sensor is powered. The driver dynamically updates hblank/vblank/exposure limits when crop or format changes. Hardware state is volatile and rebuilt on each stream start from PLL/global settings, selected crop/output registers, and control setup.

## Dependencies and Integration Points
The driver integrates with ACPI matching, I2C, CCI regmap, V4L2 async/media-controller, V4L2 fwnode device and endpoint parsing, runtime PM, clocks, GPIOs, and regulator bulk APIs. It uses `v4l2_i2c_subdev_set_name()` to expose the matched model and `v4l2_subdev_link_validate` for media graph validation.

## Risks and Edge Cases
The file contains duplicated declarations/lines in this snapshot, including duplicate `struct v4l2_ctrl *exposure;` and duplicated `ov01a10_update_blank_ctrls()` text, which should be checked against the actual build tree. The OV01A10 ACPI config intentionally reports BGGR to preserve compatibility with userspace that relied on an old mirroring bug; changing flip defaults or Bayer code can break existing IPU6 stacks. Crop alignment and border handling are model-specific and must remain consistent with Bayer pattern preservation. Endpoint absence returns `-EPROBE_DEFER`, so platforms rely on bridge-created graph properties.

## Test Signals
Validate both ACPI IDs and resulting subdev names/bus formats, endpoint deferral and one-lane enforcement, 19.2 MHz clock rejection, crop bounds/default/native selections, format clamping/alignment, flip controls shifting window offsets correctly for OV01A10 but not OV01A1B, runtime stream on/off sequencing, digital gain writes to all four color channels, exposure/vblank range updates, and compatibility of reported Bayer order with expected userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov01a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov02a10.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov02a10.c

## Purpose
`ov02a10.c` is a legacy-style V4L2 I2C driver for the OmniVision OV02A10 2 MP Bayer sensor. It supports a single 1600x1200 10-bit mode, one CSI-2 data lane at a 390 MHz link frequency, optional 180-degree board rotation handling, optional MIPI clock-voltage tuning, and controls for exposure, analogue gain, vblank, and test pattern.

## Important APIs, Types, and Functions
`struct ov02a10` stores the device, MIPI clock-voltage selector, eclk, powerdown/reset GPIOs, regulators, streaming flag, upside-down flag, mutex, subdev, pad, current frame format, control handler, exposure control, and current mode. Register access is direct SMBus byte access through `ov02a10_write_array()`, `i2c_smbus_write_byte_data()`, and `i2c_smbus_read_word_swapped()`, not CCI regmap. Important routines are `ov02a10_set_fmt()`, `ov02a10_get_fmt()`, `ov02a10_check_sensor_id()`, power on/off, `__ov02a10_start_stream()`, `ov02a10_s_stream()`, `ov02a10_set_exposure()`, `ov02a10_set_gain()`, `ov02a10_set_vblank()`, `ov02a10_set_test_pattern()`, `ov02a10_set_ctrl()`, `ov02a10_initialize_controls()`, `ov02a10_check_hwcfg()`, and probe/remove.

## Control Flow
Probe validates the fwnode endpoint and required link frequency, initializes the subdev, defaults the media-bus code to `SBGGR10`, optionally switches to `SRGGB10` for `rotation = 180`, obtains a legacy `eclk`, mandatory powerdown and reset GPIOs, and supplies, creates controls, initializes the media entity, enables runtime PM, optionally powers on immediately if runtime PM is disabled, and registers a subdev. Stream start resumes PM, writes the mode table, applies controls, optionally writes mirror/flip and global-effective for 180-degree rotation, applies the optional MIPI TX speed selector, and writes streaming mode. Stop writes standby and releases runtime PM.

## State and Persistence
`streaming`, `fmt`, `cur_mode`, `mipi_clock_voltage`, and `upside_down` are the main software state. A mutex serializes streaming, format, and control access. Control values persist in V4L2 and are only applied when the device is powered. Sensor state is volatile and rebuilt through the mode table and control replay at stream start.

## Dependencies and Integration Points
The driver binds to OF compatible `ovti,ov02a10`, uses V4L2 async subdev registration, media pads, fwnode endpoint parsing, runtime PM, regulator and GPIO frameworks, and the I2C SMBus byte/word API. It integrates optional device-tree properties `rotation` and `ovti,mipi-clock-voltage`.

## Risks and Edge Cases
The endpoint parser checks that the required link frequency is present but does not validate CSI-2 lane count even though the driver only supports one lane. `mipi_clock_voltage` is set to the default after `ov02a10_check_hwcfg()` in probe, so a parsed non-default property may be overwritten in this snapshot. Test-pattern control writes the streaming register after global-effective, which can restart or force stream state unexpectedly if used outside the intended active-stream path. The vblank-to-VTS calculation subtracts `OV02A10_BASE_LINES`, so timing behavior should be verified against hardware. The fixed single mode means all format requests collapse to 1600x1200.

## Test Signals
Test chip-ID read `0x2509`, power sequencing with mandatory reset/powerdown GPIOs, runtime PM enabled and disabled paths, link-frequency validation, optional rotation changing media-bus code and programming mirror/flip, optional MIPI TX speed register behavior, mutex-protected stream idempotence, exposure/gain/vblank writes through page switch and global-effective, and correct error cleanup for media entity, controls, and mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov02a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov02c10.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov02c10.c

## Purpose
`ov02c10.c` is a V4L2 sub-device driver for the OmniVision OV02C10 2 MP Bayer sensor. It supports one 1928x1092 10-bit GRBG mode, either one or two CSI-2 lanes at a 400 MHz link frequency, lane-specific register programming, ACPI/OF matching, and controls for blanking, gain, exposure, flips, and test pattern.

## Important APIs, Types, and Functions
`struct ov02c10_mode` stores width, height, HTS, minimum VTS, common mode register sequence, and per-lane register sequences. `struct ov02c10` owns the subdev, pad, control handler, CCI regmap, controls, imaging clock, reset GPIO, supplies, link-frequency index, and lane count. Important routines include `ov02c10_test_pattern()`, `ov02c10_set_ctrl()`, `ov02c10_init_controls()`, `ov02c10_enable_streams()`, `ov02c10_disable_streams()`, `ov02c10_get_pm_resources()`, power on/off, `ov02c10_set_format()`, `ov02c10_identify_module()`, `ov02c10_check_hwcfg()`, and probe/remove.

## Control Flow
Probe requires a 19.2 MHz imaging clock, initializes the subdev, parses the endpoint and accepts only one or two CSI-2 data lanes with the 400 MHz link frequency, acquires reset and regulators, initializes a 16-bit-address CCI regmap, powers on, reads chip ID `0x5602`, initializes controls with lane-dependent pixel rate and default VTS, creates the media pad, finalizes the subdev, enables runtime PM, registers the sensor, and idles it. Stream enable resumes runtime PM, writes the common 1928x1092 register sequence, writes lane-specific sequence for the parsed lane count, applies controls, and writes stream control. Disable writes stream control 0 and releases PM.

## State and Persistence
Software state consists of lane count, link-frequency index, controls, and the active subdev format. VTS default is calculated as `vts_min * mipi_lanes` to maintain default frame rate across lane counts. Control values are retained by V4L2 and replayed on stream start; hardware registers are rebuilt each stream enable and are not saved across power loss.

## Dependencies and Integration Points
The file integrates with CCI regmap, regmap multi-register writes, V4L2 pad stream helpers, V4L2 fwnode endpoint parsing, runtime PM, regulator/clock/GPIO frameworks, media-controller pads, ACPI ID `OVTI02C1`, and OF compatible `ovti,ov02c10`. It exposes `MEDIA_BUS_FMT_SGRBG10_1X10`.

## Risks and Edge Cases
The driver contains duplicated label text around the stream-enable error path in this snapshot (`out:` repeated). It accepts one or two lanes but uses a single pixel-rate menu, so timing calculations and VTS defaults are lane-sensitive and should be tested for both configurations. Flip controls write both ISP window offsets and rotate bits with asymmetric semantics; Bayer ordering and crop alignment need hardware validation. Probe error handling frees the control handler even on paths where control initialization may not have assigned `sd.ctrl_handler`, which is common but worth checking under fault injection.

## Test Signals
Exercise one-lane and two-lane endpoint descriptions, lane-specific register tables, pixel-rate and vblank defaults for both lane counts, stream-on/off with `v4l2_subdev_s_stream_helper`, chip-ID mismatch, reset and power sequencing, analogue/digital gain bit shifts, exposure and VTS writes, H/V flip behavior, test-pattern menu values, ACPI and OF matching, and PM cleanup after failed registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov02c10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov02e10.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov02e10.c

## Purpose
`ov02e10.c` is a V4L2 sub-device driver for the OmniVision OV02E10 2 MP Bayer sensor. It supports one 1928x1088 10-bit GRBG mode over two CSI-2 lanes at 360 MHz, page-based register addressing, command-hold/update semantics for grouped control writes, runtime PM, ACPI/OF matching, and controls for blanking, gain, flips, exposure, and test pattern.

## Important APIs, Types, and Functions
`struct ov02e10_mode` carries width, height, HTS, default/minimum VTS, and a `reg_sequence_list`. `struct ov02e10` stores device, 8-bit-address CCI regmap, subdev, pad, controls, imaging clock, supplies, optional reset GPIO, current mode, link-frequency index, and lane count. Key functions are `to_pixel_rate()`, `to_pixels_per_line()`, `ov02e10_test_pattern()`, `ov02e10_set_ctrl()`, `ov02e10_init_controls()`, `ov02e10_set_stream_mode()`, `ov02e10_enable_streams()`, `ov02e10_disable_streams()`, `ov02e10_get_pm_resources()`, power on/off, `ov02e10_set_format()`, `ov02e10_get_format()`, `ov02e10_identify_module()`, `ov02e10_check_hwcfg()`, and probe/remove.

## Control Flow
Probe requires a 19.2 MHz imaging clock, initializes the subdev, parses an endpoint, rejects anything other than two data lanes or missing 360 MHz link frequency, creates an 8-bit-address CCI regmap, obtains reset/regulators, powers on, selects page 0 and reads the 32-bit chip ID `0x45025610`, sets the default mode, initializes controls, creates and finalizes the media entity, enables runtime PM, registers the async sensor, and idles it. Stream enable resumes PM, writes the mode register sequence, applies controls, then writes page-0 stream mode plus a page-1 global update. Control writes first command-hold, select page 1 as needed, write the target register, and command-update.

## State and Persistence
State includes selected mode, link-frequency index, parsed lane count, control values, and active pad format. Hardware state is volatile and heavily page-dependent. V4L2 retains control state while powered down; stream enable replays controls after the base mode table. The command hold/update register is used to batch live control writes.

## Dependencies and Integration Points
The driver integrates with CCI regmap, regmap multi-register writes, V4L2 subdev/media-controller, V4L2 fwnode parsing, runtime PM, regulator/clock/GPIO frameworks, ACPI ID `OVTI02E1`, and OF compatible `ovti,ov02e10`. It exposes `MEDIA_BUS_FMT_SGRBG10_1X10` and the pad stream helper callbacks.

## Risks and Edge Cases
The snapshot shows stray duplicated text/braces and a duplicated `return ret;` in `ov02e10_set_format()`, which should be verified in build context. Page selection is critical; any missing page write can direct a control to the wrong register. `to_pixel_rate()` uses the constant two-lane count, so future lane variants would require code changes. Hblank is calculated through `to_pixels_per_line()` and the fixed `OV02E10_SCLK`; this must match sensor timing. Stream mode writes multiple pages and global-update registers, so stop/start failures can leave the sensor on an unexpected page.

## Test Signals
Validate two-lane endpoint and 360 MHz link-frequency enforcement, page-0 chip-ID read, command-hold/update around each live control, analog/digital gain, exposure, vblank, H/V flip and test-pattern writes on page 1, stream mode page switching, runtime PM balance, ACPI and OF probing, and format enumeration and hblank/vblank updates for the fixed mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov02e10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov08d10.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov08d10.c

## Purpose
`ov08d10.c` is a V4L2 I2C driver for the OmniVision OV08D10 8 MP Bayer sensor. It supports two-lane CSI-2 operation with 19.2 MHz or 24 MHz input clocks, three fixed 10-bit modes, link-frequency-specific PLL tables, runtime PM, reset-control based power sequencing, and controls for link frequency, pixel rate, blanking, analogue/digital gain, exposure, flips, and test pattern.

## Important APIs, Types, and Functions
`struct ov08d10_lane_cfg` groups link-frequency menus, per-clock PLL register lists, and supported modes. `struct ov08d10_mode` stores dimensions, HTS, default/minimum VTS, link frequency, data lanes, and mode register list. `struct ov08d10` owns clock, reset control, supplies, selected xvclk index, subdev, pad, controls, current mode, mutex, lane count, lane config, and mode count. Key functions include `ov08d10_modes_num()`, `to_rate()`, `to_pixels_per_line()`, `ov08d10_write_reg_list()`, gain/exposure/vblank/test-pattern/flip helpers, `ov08d10_set_ctrl()`, `ov08d10_init_controls()`, `ov08d10_start_streaming()`, `ov08d10_stop_streaming()`, `ov08d10_set_stream()`, format/enum/open ops, `ov08d10_power_on()`, `ov08d10_identify_module()`, `ov08d10_get_hwcfg()`, and probe/remove.

## Control Flow
Probe validates the external clock against 19.2 MHz or 24 MHz and records the index for PLL table selection, parses the fwnode endpoint and requires exactly two lanes plus both 720 MHz and 360 MHz link frequencies in the endpoint, obtains optional exclusive reset control and regulators, initializes the subdev, powers on, reads chip ID `0x5608` through page 0 byte reads, initializes the mutex and controls, creates the media pad, enables runtime PM, registers the sensor, and idles it. Stream start resumes PM, performs a page-0 soft reset sequence, writes the PLL table for the current mode link frequency and xvclk index, writes the mode table, applies controls, and writes mode-select streaming.

## State and Persistence
`cur_mode`, `xvclk_index`, `priv_lane`, `modes_size`, controls, and flip-dependent media-bus code are the main software state. The mutex serializes format, stream, and code enumeration. V4L2 controls persist while powered down and are replayed at stream start. Hardware state is page-based and volatile; power-off asserts reset, disables supplies, and stops the clock.

## Dependencies and Integration Points
The driver depends on I2C SMBus access, V4L2 subdev/media-controller APIs, V4L2 fwnode endpoint parsing, clock, regulator, runtime PM, reset-controller APIs, ACPI ID `OVTI08D1`, and OF compatible `ovti,ov08d10`. It exposes formats whose Bayer order changes with H/V flip state and validates links through media-entity operations.

## Risks and Edge Cases
The driver requires all link frequencies in the two-entry menu to be present in the endpoint, not merely the active mode's frequency. `ov08d10_get_hwcfg()` logs `cur_mode->data_lanes` before `cur_mode` is initialized in this snapshot, which is a potential null dereference if the debug statement evaluates it. Exposure programming reads HTS registers and rescales exposure with a formula tied to `ROWCLK`; this deserves sensor-level validation. The burst of mode tables and page switching uses raw SMBus byte writes, so partial write failures can leave the sensor on a non-default page. There is no `v4l2_subdev_cleanup()` call in remove in this snapshot, unlike newer-state subdev drivers.

## Test Signals
Validate both supported input clocks, rejection of non-two-lane endpoints and missing link frequencies, chip-ID reads after page selection, mode enumeration for 3280x2460, 3264x2448, and 1632x1224, link-frequency and pixel-rate changes per mode, flip-dependent media-bus code changes and grabbed flip controls during streaming, exposure/gain/vblank/test-pattern writes with global-effective, reset-control sequencing, and PM cleanup after failed registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov08d10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov08x40.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov08x40.c

## Purpose
`ov08x40.c` is a V4L2 sub-device driver for the OmniVision OV08X40 8 MP Bayer sensor. It supports both two-lane and four-lane CSI-2 configurations, multiple full-resolution and binned 10-bit GRBG modes, two link-frequency configurations, ACPI/OF matching, runtime PM, and controls for link frequency, pixel rate, blanking, exposure, analogue/digital gain, flips, and multi-pattern test output.

## Important APIs, Types, and Functions
`struct ov08x40_mode` describes each mode's dimensions, lane count, default/minimum VTS, line length pixels, link-frequency index, mode register list, and exposure calculation parameters. `struct ov08x40` stores the subdev, media pad, controls, xvclk, reset GPIO, regulators, current mode, mutex, parsed lane count, chip-identification cache, and link-frequency bitmap. Register I/O is through custom big-endian `ov08x40_read_reg()`, `ov08x40_write_reg()`, `ov08x40_write_reg_list()`, and burst-fill helpers. Important functions include `link_freq_to_pixel_rate()`, `ov08x40_update_digital_gain()`, `ov08x40_enable_test_pattern()`, flip helpers, `ov08x40_set_ctrl()`, lane filter and frame-size enumeration, pad format get/set, `ov08x40_start_streaming()`, `ov08x40_identify_module()`, `ov08x40_set_stream()`, `ov08x40_init_controls()`, `ov08x40_check_hwcfg()`, probe/remove, and runtime PM power on/off.

## Control Flow
Hardware config parsing waits for a fwnode graph endpoint, acquires optional reset GPIO, supplies, and a 19.2 MHz xvclk, accepts only two or four CSI-2 lanes, and maps endpoint link frequencies against 400 MHz and 749 MHz menu entries. Probe initializes the subdev, optionally powers and identifies the sensor immediately when ACPI says the device is already in D0, sets the default mode to the first full-resolution mode, initializes controls and mutex, creates the media pad, registers the async subdev, enables runtime PM, and idles. Stream start resumes PM, identifies the module if not already cached, writes software reset, link-frequency PLL registers, global registers, current mode registers, optionally burst-fills crosstalk tables for full-size modes, applies controls, and writes mode-select streaming. Stop writes standby and releases PM.

## State and Persistence
State includes parsed lane count, link-frequency bitmap, current mode, cached chip identification, runtime PM state, and V4L2 controls. The active mode is filtered by lane count; two-lane systems expose 3856x2176 and 1928x1088 at 749 MHz, while four-lane systems expose 3856x2416, 3856x2176, and 1928x1208 at 400 MHz. Hardware state is volatile and rebuilt on each stream start. `identified` avoids repeated chip-ID reads after a successful identification.

## Dependencies and Integration Points
The driver integrates with I2C transfer/master-send APIs, V4L2 common helpers, V4L2 subdev/media-controller, V4L2 fwnode parsing, ACPI ID `OVTI08F4`, OF compatible `ovti,ov08x40`, runtime PM, clocks, GPIOs, and regulators. It uses `I2C_DRV_ACPI_WAIVE_D0_PROBE` and `acpi_dev_state_d0()` to avoid forcing some ACPI devices through power transitions during probe.

## Risks and Edge Cases
`link_freq_to_pixel_rate()` uses the compile-time four-lane constant even when the parsed configuration is two lanes, so reported pixel rate for two-lane modes needs review. The burst-fill loop uses adapter `max_write_len` but calls the low-level helper with `last_reg` as the buffer-size argument; this snapshot should be checked for off-by-one or oversized-transfer behavior. Full-resolution modes use `exposure_shift = 1`, requiring doubled VTS/exposure math and vblank step alignment to four lines; mistakes can create invalid exposure ranges. H/V flip controls do not update the reported media-bus code, which is fixed GRBG. Probe may skip initial chip-ID read when ACPI does not report D0, deferring detection to stream start.

## Test Signals
Test two-lane and four-lane endpoints separately, link-frequency bitmap handling, frame-size enumeration filtered by lane count, pixel-rate values per mode, ACPI D0 and non-D0 probe paths, chip-ID read `0x560858`, stream-start ordering of reset/PLL/global/mode/control writes, crosstalk burst fill for full-size modes, exposure/vblank math for shifted and binned modes, digital gain byte packing, test-pattern enable across ISP and short-pattern registers, flip bit semantics, runtime PM cleanup, and register I/O error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov08x40.c -->
