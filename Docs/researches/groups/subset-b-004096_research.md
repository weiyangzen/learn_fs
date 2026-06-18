# subset-b-004096 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov13858.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov13858.c

## Purpose
This file is a V4L2 I2C subdevice driver for the OmniVision OV13858 raw Bayer MIPI CSI-2 camera sensor. It exposes one source pad, fixed 10-bit GRBG media-bus output, four discrete modes from 4224x3136 down to 1056x784, two MIPI link rates, and standard camera controls for exposure, analogue gain, digital gain, blanking, pixel rate, link frequency, test pattern, and fwnode-provided orientation/rotation properties.

## Important APIs, types, and functions
The central state is `struct ov13858`, containing the device, sensor clock, V4L2 subdev, media pad, control handler/control pointers, current mode, and a mutex. Mode data is split between `struct ov13858_mode` for resolution/VTS/mode register lists and `struct ov13858_link_freq_config` for PLL/link-rate register lists plus pixels-per-line. Register access uses custom big-endian helpers `ov13858_read_reg()`, `ov13858_write_reg()`, `ov13858_write_regs()`, and `ov13858_write_reg_list()` over raw I2C transfers. V4L2 pad operations are `ov13858_enum_mbus_code()`, `ov13858_enum_frame_size()`, `ov13858_get_pad_format()`, and `ov13858_set_pad_format()`. Streaming is driven by `ov13858_set_stream()`, `ov13858_start_streaming()`, and `ov13858_stop_streaming()`. Probe/remove are `ov13858_probe()` and `ov13858_remove()`, bound through `module_i2c_driver()`.

## Control flow
Probe allocates state, obtains the sensor clock with `devm_v4l2_sensor_clk_get()`, rejects non-19.2 MHz clocks, initializes the I2C subdev, reads the 24-bit chip ID, selects the maximum-resolution default mode, initializes controls, creates a single source media pad, registers the subdevice as a sensor, and enables runtime PM. Format negotiation clamps all requested bus codes to `MEDIA_BUS_FMT_SGRBG10_1X10` and chooses the nearest supported mode. For active formats, it updates `cur_mode`, read-only link frequency and pixel rate, VBLANK range/default, and read-only HBLANK. Stream-on resumes runtime PM, writes software reset, applies the link-frequency PLL register list, applies the selected mode list, restores all controls via `__v4l2_ctrl_handler_setup()`, then writes mode-select streaming. Stream-off writes standby and drops the runtime PM reference.

## State and persistence
Persistent runtime state is in memory only: `cur_mode`, control values cached by the V4L2 control framework, and runtime PM state. Hardware programming is not persistent across power/runtime suspend, so stream-on rewrites PLL, mode, and control registers. VBLANK control changes dynamically modify the exposure maximum. Digital gain is persisted as one logical control but written into blue, green, and red manual white-balance gain registers.

## Dependencies and integration points
The driver integrates with I2C, V4L2 subdev/media-controller APIs, ACPI matching (`OVTID858`), runtime PM, fwnode control properties, and a platform-provided clock. It uses `v4l2_async_register_subdev_sensor()` and `v4l2_subdev_link_validate` for media graph integration. There is no device-tree endpoint parsing in this file; lane count and link setup are fixed by the built-in mode/link tables.

## Risks
The probe path identifies the sensor before enabling explicit runtime PM and depends on firmware/ACPI power state having the device accessible. Only a 19.2 MHz input clock and hard-coded 4-lane pixel-rate calculation are supported. Register tables are large opaque sensor sequences, so mode correctness depends on vendor values and hardware testing. Controls are skipped while the device is runtime-suspended, which is intentional, but any control whose cached value is not restored by `__v4l2_ctrl_handler_setup()` would diverge from hardware. Error handling during stream-off ignores the return from `ov13858_stop_streaming()` in the caller path.

## Test signals
Useful validation is successful probe with matching `0x00d855` chip ID, correct media graph source pad registration, `v4l2-ctl --list-subdev-mbus-codes` showing only GRBG10, frame-size enumeration for all four modes, link-frequency/pixel-rate changes when selecting full-resolution versus binned modes, stream-on/off I2C traces showing reset/PLL/mode/control/mode-select writes, and test-pattern frames for each menu item. Runtime PM balance should be checked across failed stream-on paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov13858.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov13b10.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov13b10.c

## Purpose
This file implements an OmniVision OV13B10 V4L2 I2C subdevice driver for a 13 MP raw Bayer MIPI CSI-2 sensor. It exposes 10-bit GRBG output, supports different mode tables for 4-lane and 2-lane CSI-2 wiring, and provides runtime controls for exposure, analogue/digital gain, blanking, link frequency, pixel rate, test pattern, and horizontal/vertical flip.

## Important APIs, types, and functions
`struct ov13b10` holds the subdevice, media pad, controls, clock/regulator/reset resources, selected mode table, current mode, lane count, mutex, and an `identified` cache. `struct ov13b10_mode` captures mode dimensions, VTS defaults/minima, link-frequency index, pixels-per-line, and register list. `ov13b10_check_hwcfg()` parses the firmware endpoint and selects either `supported_4_lanes_modes` or `supported_2_lanes_modes`. Register I/O uses `ov13b10_read_reg()`, `ov13b10_write_reg()`, and list helpers. Control handlers include `ov13b10_update_digital_gain()`, `ov13b10_enable_test_pattern()`, `ov13b10_set_ctrl_hflip()`, `ov13b10_set_ctrl_vflip()`, and `ov13b10_set_ctrl()`. PM and lifecycle functions include `ov13b10_power_on()`, `ov13b10_power_off()`, `ov13b10_start_streaming()`, `ov13b10_set_stream()`, `ov13b10_probe()`, and `ov13b10_remove()`.

## Control flow
Probe parses the CSI-2 endpoint, validates lane count and advertised link frequencies, initializes the subdev, obtains optional reset GPIO, clock, and optional `avdd`, and handles ACPI D0 probing. If firmware reports the device already in D0, the driver powers the chip and reads the 24-bit ID immediately; otherwise identification is deferred and cached at first stream-on. Control initialization sets read-only link frequency, read-only HBLANK, pixel rate derived from lane count, VBLANK/exposure coupling, gains, test pattern, flips, and fwnode orientation properties. Active format selection finds the nearest mode from the lane-specific table and updates VBLANK, HBLANK, pixel rate, and link frequency. Stream-on resumes runtime PM, identifies the chip if needed, resets it, applies link and mode register lists, restores controls, and writes streaming mode. Stream-off writes standby and drops runtime PM.

## State and persistence
The selected mode table and lane count are immutable after endpoint parsing. `cur_mode`, cached control values, `identified`, and runtime PM state are in-memory state. Hardware register state is reconstructed on each stream-on. Digital gain is decomposed into three registers using bit shifts/masks, while flips manipulate format/crop offset registers to preserve Bayer order. VBLANK updates exposure range so exposure tracks frame length.

## Dependencies and integration points
The driver integrates with ACPI IDs `OVTIDB10`, `OVTI13B1`, and `OMNI13B1`, runtime PM (`DEFINE_RUNTIME_DEV_PM_OPS`), the firmware graph via `v4l2_fwnode_endpoint_alloc_parse()`, V4L2 controls/subdev/media entity APIs, GPIO, regulator, and clock frameworks. It uses `I2C_DRV_ACPI_WAIVE_D0_PROBE`, allowing probe when ACPI firmware has not left the sensor powered.

## Risks
The HFLIP and VFLIP cases call their helper functions but do not assign their return values to `ret`, so I2C failures in those paths can be hidden from userspace. Endpoint validation requires every internal link-frequency menu item to be present in firmware, which is strict but avoids unsupported boards. Non-D0 probe defers chip-ID verification until streaming, moving hardware failures later in the user workflow. Mode tables are fixed and opaque, and only one link frequency is accepted. Flip helpers increment/decrement crop-offset registers relative to current hardware contents, so repeated failures or unexpected defaults could affect Bayer alignment.

## Test signals
Test by probing both 4-lane and 2-lane firmware descriptions, checking selected mode counts, validating rejection of unsupported lane counts/link frequencies, confirming chip ID `0x560d42`, enumerating all lane-specific frame sizes, and streaming each mode. Exercise analogue gain, digital gain, exposure, VBLANK, test pattern, HFLIP, and VFLIP with I2C error injection if possible, because flip error propagation is a specific risk. Runtime PM reference balance should be verified through failed stream-on and stream-off paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov13b10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2640.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov2640.c

## Purpose
This is a legacy-style V4L2 I2C subdevice driver for the OmniVision OV2640 parallel/DVP camera sensor. It supports multiple DSP-scaled output sizes from QCIF through UXGA and several 8-bit media-bus formats, including YUV422 byte orders and RGB565. Unlike the newer MIPI drivers in this group, it uses SMBus byte accesses, manual power counting, and explicit sensor/DSP register banks.

## Important APIs, types, and functions
`struct ov2640_priv` stores the subdev, media pad, controls, current media-bus code, clock, selected window, optional reset/powerdown GPIOs, lock, streaming flag, and `power_count`. `struct regval_list` defines 8-bit register/value tables with an `ENDMARKER`; `struct ov2640_win_size` maps named resolutions to register sequences. Register helpers include `ov2640_write_array()`, `ov2640_mask_set()`, and `ov2640_reset()`. Format and size setup is centralized in `ov2640_set_params()`, called by `ov2640_s_stream()`. V4L2 operations include `ov2640_get_fmt()`, `ov2640_set_fmt()`, `ov2640_enum_mbus_code()`, `ov2640_get_selection()`, `ov2640_s_power()`, and optional advanced debug register access under `CONFIG_VIDEO_ADV_DEBUG`.

## Control flow
Probe checks the adapter for SMBus byte-data support, allocates state, optionally enables the `xvclk` clock for OF devices, obtains optional `resetb` and `pwdn` GPIOs, initializes default SVGA/UYVY state, registers controls for HFLIP, VFLIP, and test pattern, initializes a single source pad, powers the sensor briefly to read PID/VER/MID registers, and registers the subdevice. Format negotiation selects the nearest equal-or-larger supported window, normalizes unsupported codes to UYVY, and refuses active format changes while streaming. Stream-on, when transitioning from off to on, calls `ov2640_set_params()`: reset, write global init table, write size preamble and selected size table, write format preamble and format table, set byte-order control, then restore controls. Stream-off only flips the software `streaming` flag; there is no explicit hardware standby write in this path.

## State and persistence
The driver maintains software `win`, `cfmt_code`, `streaming`, and `power_count`. Hardware state is rebuilt on every stream-on from the selected tables and V4L2 controls. Control writes are deferred while `power_count` is zero and are replayed during stream-on. Power state is reference-counted through `.s_power`; GPIO direction/value updates assert/deassert reset and powerdown pins.

## Dependencies and integration points
The driver integrates with I2C SMBus byte data, V4L2 subdev/media-controller, V4L2 controls/events, optional GPIOs, optional OF clock `xvclk`, and OF compatible `ovti,ov2640`. It does not parse endpoint bus parameters, does not use runtime PM, and uses `v4l2_async_register_subdev()` rather than the newer sensor-specific helper.

## Risks
Power management relies on callers using `.s_power()` correctly; streaming does not automatically power the device. The power counter can go negative, only guarded by `WARN_ON()`. Stream-off does not program a hardware standby sequence, so board-level power control may be needed to stop output fully. Format tables and bank switching are opaque and easy to regress. There is no endpoint validation for bus width/polarity. The probe path reads manufacturer IDs but only validates product ID/version, and several I2C reads are stored in `u8` despite negative SMBus errors being possible before assignment.

## Test signals
Test signals include SMBus functionality failure handling, successful PID `0x2642` detection, media-bus code enumeration for all supported YUV/RGB byte orders, format selection for every supported size, `-EBUSY` on active format changes while streaming, control replay after stream-on, GPIO sequencing through `.s_power()`, and visible test-pattern/color-bar output. Regression tests should include power-count edge cases and stream-on after changing format while powered down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2659.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov2659.c

## Purpose
This file implements a V4L2 I2C subdevice driver for the OmniVision OV2659 CMOS image sensor. It supports several discrete frame sizes from QVGA to UXGA, YUV422/RGB565/raw BGGR output formats, runtime PM, programmable PLL calculation from platform or firmware link frequency, and a simple vertical color-bar test pattern.

## Important APIs, types, and functions
Core state is `struct ov2659`, containing the subdev, media pad, active format, clock, platform data, controls, selected frame size, format register table, calculated PLL registers, streaming flag, and optional powerdown/reset GPIOs. `struct ov2659_framesize` binds dimensions to mode register tables and max exposure lines. `struct ov2659_pixfmt` maps media-bus codes to format-control register tables. Low-level I/O uses `ov2659_write()`, `ov2659_read()`, and `ov2659_write_array()` with 16-bit register addresses and 8-bit values. PLL setup is handled by `ov2659_pll_calc_params()` and `ov2659_set_pixel_clock()`. Subdev operations include `ov2659_set_fmt()`, `ov2659_s_stream()`, `ov2659_set_test_pattern()`, `ov2659_power_on()`, `ov2659_power_off()`, and `ov2659_detect()`.

## Control flow
Probe obtains platform data either directly or by parsing the OF endpoint link frequency, gets and validates `xvclk` in the 6-27 MHz range, grabs optional GPIOs, initializes controls, marks the I2C client as SCCB, initializes the subdevice and media pad, sets default SVGA/YUYV state, powers the device, soft-resets and checks the OV2659 ID, calculates PLL register fields nearest to the requested link frequency, registers the subdevice, and enables runtime PM. Active format setting chooses the closest frame size by absolute width/height error, validates/normalizes media-bus code, refuses changes while streaming, stores the selected frame size and format table, and updates the pixel-rate/link-frequency control value according to raw versus non-raw output. Stream-on resumes runtime PM, writes global initialization, calculated PLL registers, selected frame-size registers, selected format registers, then writes software standby with streaming enabled. Stream-off writes standby off and releases runtime PM.

## State and persistence
The persistent software state is the active `format`, `frame_size`, `format_ctrl_regs`, calculated `pll`, and `streaming` flag. Register state is rewritten on stream-on. Runtime PM owns clock/GPIO power after registration. The test-pattern control is applied only while the device is runtime-active; otherwise the cached V4L2 value is expected to be restored during stream setup if included in handler setup, though this driver only sets up controls through direct control path for test pattern.

## Dependencies and integration points
The driver uses V4L2 subdev/media-controller/control/event APIs, OF graph endpoint parsing, legacy platform data fallback, runtime PM, GPIO, clock, and I2C/SCCB transport. It exposes compatible `ovti,ov2659` and I2C ID `ov2659`. The pixel-rate control is named in code as `link_frequency` but created as `V4L2_CID_PIXEL_RATE`, which matters for readers and test tooling.

## Risks
`ov2659_s_ctrl()` returns directly from the test-pattern case without `pm_runtime_put()`, leaking a runtime PM reference whenever the active test-pattern control is applied successfully. Stream-on error paths after `pm_runtime_resume_and_get()` do not obviously release runtime PM before returning, which can also unbalance PM. The PLL search uses `u32 bestdelta = -1` and computes absolute deltas from unsigned arithmetic; it works as a large initial value but is fragile. Firmware parsing accepts the first link frequency only. The driver does not expose exposure/gain controls despite frame-size metadata carrying max exposure lines.

## Test signals
Validation should include probe with platform-data and OF endpoint paths, ID detection for `0x2656`, PLL register calculation for representative xclk/link-frequency combinations, media-bus code and frame-size enumeration, format changes rejected while streaming, stream-on I2C order for init/PLL/frame/format/standby, and stream-off runtime PM release. Runtime PM leak tests around `V4L2_CID_TEST_PATTERN` are especially important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2659.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2680.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov2680.c

## Purpose
This file is a V4L2 CCI/regmap-based I2C subdevice driver for the OmniVision OV2680 2 MP raw Bayer MIPI CSI-2 sensor. It supports dynamic crop/format selection within the native 1616x1216 array, optional 2x binning, 30 fps timing, h/v flip-aware Bayer order, analogue gain, exposure, blanking, test patterns, regulators, GPIO powerdown, and runtime PM autosuspend.

## Important APIs, types, and functions
`struct ov2680_dev` stores device/regmap/subdev/media pad, clock and PLL data, single-entry link-frequency menu, pixel rate, regulators, optional powerdown GPIO, mutex, streaming flag, controls, and current `struct ov2680_mode`. `struct ov2680_mode` combines crop rectangle, frame format, frame interval, binning flag, and calculated sensor window/output registers. Register access uses `devm_cci_regmap_init_i2c()`, `cci_write()`, `cci_read()`, `cci_update_bits()`, and `regmap_multi_reg_write()`. Key functions are `ov2680_calc_mode()`, `ov2680_set_mode()`, `ov2680_stream_enable()`, `ov2680_s_stream()`, `ov2680_set_fmt()`, `ov2680_set_selection()`, `ov2680_s_ctrl()`, `ov2680_parse_dt()`, and `ov2680_check_id()`.

## Control flow
Probe initializes a 16-bit CCI regmap, parses the firmware endpoint, obtains powerdown/reset-compatible GPIO, validates the xclk as either 19.2 MHz or 24 MHz, calculates PLL multiplier/link frequency/pixel rate, initializes default 800x600 mode within the active crop, gets regulators, powers the sensor, verifies chip ID/revision, enables runtime PM, registers the V4L2 subdev and controls, and enables autosuspend. Crop selection clamps requested rectangles to even coordinates/sizes within the native array and resets output size if crop dimensions change. Format selection clamps even output dimensions to the current crop, chooses binning when requested output is no larger than half the crop dimensions, recalculates sensor window registers, and updates VBLANK/HBLANK/exposure ranges. Stream-on writes PLL multiplier, global settings, calculated mode registers, restores controls, then starts streaming. Stream-off writes stream control off and drops runtime PM.

## State and persistence
The current crop/format/mode calculations live in `sensor->mode`; controls are cached in `sensor->ctrls`; streaming state is `is_streaming`. Hardware state is rebuilt from global settings plus calculated mode and controls each stream-on. H/V flip controls update the media-bus code according to the four possible Bayer orders and are rejected while streaming. VBLANK changes modify exposure range and program VTS when powered.

## Dependencies and integration points
The driver integrates with CCI/regmap, V4L2 controls/subdev/media APIs, firmware graph parsing, regulator bulk APIs (`DOVDD`, `DVDD`, `AVDD`), GPIO, sensor clock helpers, runtime PM autosuspend, OF compatible `ovti,ov2680`, and ACPI ID `OVTI2680`. Endpoint link-frequency validation is optional but warns if the property is missing.

## Risks
The driver is more dynamic than table-only sensors, so crop/format/binning math is a key risk; off-by-one errors can disrupt Bayer order or sensor boundaries. `ov2680_power_on()` performs a soft reset before enabling xclk when no GPIO exists, which may rely on board-specific clock behavior. `ov2680_s_ctrl()` updates Bayer order even when the device is powered off, which is intentional for format reporting but should be checked with control locking. The pad ops wire `.set_frame_interval` to `ov2680_get_frame_interval`, making set-frame-interval a no-op getter. Only one frame interval is supported.

## Test signals
Test crop and format combinations across full-size and binned outputs, verifying even alignment and expected Bayer media-bus code under all H/V flip combinations. Probe should validate both supported xclk frequencies, computed link frequency, optional link-frequency firmware property, regulators, and chip ID `0x2680`. Stream tests should trace PLL/global/mode/control writes and confirm autosuspend behavior. VBLANK/exposure range coupling and rejection of flip/format changes while streaming are important regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2680.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2685.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov2685.c

## Purpose
This file is a V4L2 I2C subdevice driver for the OmniVision OV2685 raw Bayer MIPI CSI-2 sensor. It currently exposes a single 1600x1200 10-bit SBGGR mode over one CSI-2 lane, standard controls for exposure, analogue gain, VBLANK, read-only HBLANK/link frequency/pixel rate, test patterns, regulator/clock/reset sequencing, and runtime PM.

## Important APIs, types, and functions
`struct ov2685` stores the I2C client, xvclk, reset GPIO, supplies, mutex, subdev, pad, controls, handler, and current mode. `struct ov2685_mode` captures dimensions, default exposure/HTS/VTS, analog crop, and register list. Register helpers are `ov2685_write_reg()`, `ov2685_write_array()`, and `ov2685_read_reg()` with 16-bit register addresses and variable-width values. Format/pad functions include `ov2685_fill_fmt()`, `ov2685_set_fmt()`, `ov2685_get_fmt()`, frame-size/code enumeration, and `ov2685_get_selection()`. Runtime and lifecycle functions include `__ov2685_power_on()`, `__ov2685_power_off()`, `ov2685_s_stream()`, `ov2685_set_ctrl()`, `ov2685_initialize_controls()`, `ov2685_check_sensor_id()`, `ov2685_probe()`, and `ov2685_remove()`.

## Control flow
Probe allocates state, selects the only supported mode, obtains a legacy-compatible 24 MHz xvclk, warns if the actual clock differs, obtains optional reset GPIO and regulators, initializes the mutex/subdev/controls, powers the sensor, checks chip ID `0x2685`, initializes the media pad/entity, registers the subdevice, and enables runtime PM. Power-on enables clock, asserts reset, enables regulators, releases reset, waits 8192 xclk cycles, and writes the mode register table as a workaround for bad data after reset. Format operations always return the fixed SBGGR10 1600x1200 mode. Stream-on resumes runtime PM, restores controls, and writes streaming mode; stream-off writes standby and drops runtime PM.

## State and persistence
The selected mode is fixed for the device lifetime. V4L2 controls cache exposure/gain/VBLANK/test-pattern values, and hardware controls are only written while runtime-active. VBLANK changes update exposure maximum. Hardware register programming is partly done at power-on via the workaround mode table write and partly at stream-on via control restoration and mode-select. There is no explicit `is_streaming` flag in the driver.

## Dependencies and integration points
The driver uses V4L2 subdev/media-controller/control APIs, I2C, regulator bulk supplies (`DOVDD`, `AVDD`, `DVDD`), GPIO reset, runtime PM, and OF compatible `ovti,ov2685`. The link frequency is hard-coded to 330 MHz and pixel rate derives from one lane and 10 bits per sample. It uses `devm_v4l2_sensor_clk_get_legacy()` for compatibility with older clock descriptions.

## Risks
`ov2685_check_sensor_id()` returns `ret` when the ID mismatches; if the read succeeded but returned the wrong ID, `ret` may be zero, so a mismatched chip can be reported without failing probe. The driver does not parse or validate the firmware endpoint lane count/link frequency, despite hard-coding one lane. Format and selection support are minimal and `.set_selection` is wired to the getter, making crop setting ineffective. Because stream state is not tracked, repeated stream-on/off calls rely on callers and runtime PM behavior. The power-on workaround writes mode registers before normal stream setup, so failures there block probe/runtime resume.

## Test signals
Tests should cover wrong-chip-ID behavior, because the mismatch return path is suspicious. Probe should verify regulator/clock/reset ordering and ID `0x2685`. Media enumeration should show one SBGGR10 1600x1200 mode and crop bounds/default matching the 1600x1200 active crop inside 1616x1216 native size. Stream-on/off should validate runtime PM balance, control writes, test-pattern values, and standby/streaming register writes. Firmware endpoint mismatch tests would expose the absence of lane validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2685.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2732.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov2732.c

## Purpose
This file implements a modern V4L2 CCI/regmap I2C subdevice driver for the OmniVision OV2732 raw Bayer MIPI CSI-2 sensor. It supports one 1920x1080 SBGGR10 mode over two CSI-2 lanes, common sensor initialization registers, exposure/analogue gain/digital gain/blanking/test-pattern controls, runtime PM autosuspend, and the newer subdev streams API.

## Important APIs, types, and functions
`struct ov2732` stores device/regmap, media pad, subdev, controls, xclk, GPIOs, and three regulators. `struct ov2732_mode` defines width, height, and VTS for the single mode. Register access uses `devm_cci_regmap_init_i2c()`, `cci_read()`, `cci_write()`, and `cci_multi_reg_write()`. Important functions are `ov2732_power_on()`, `ov2732_power_off()`, `ov2732_identify_chip()`, `ov2732_set_fmt()`, `ov2732_enable_streams()`, `ov2732_disable_streams()`, `ov2732_set_ctrl()`, `ov2732_init_controls()`, `ov2632_probe_dt()` (name typo but OV2732 behavior), and `ov2732_probe()`.

## Control flow
Probe parses endpoint 0/port 0 and requires exactly two CSI-2 data lanes, obtains and validates a 24 MHz xvclk, gets optional powerdown/reset GPIOs, initializes the CCI regmap and regulators, initializes the I2C subdev, powers the device, enables runtime PM, reads the 24-bit chip ID `0x002732`, initializes controls, creates the media entity, finalizes active subdev state using `v4l2_subdev_init_finalize()`, registers the sensor subdevice, and enables autosuspend. Format setting selects the nearest supported mode, forces SBGGR10/raw colorimetry, stores the state format, and adjusts VBLANK range for active formats. Stream enable resumes runtime PM, forces standby, writes common registers, restores controls, then writes streaming. Stream disable writes standby, waits the datasheet power-down delay, and autosuspends.

## State and persistence
The active subdev state stores the current format/crop and is locked with the control handler lock. Controls cache timing/gain/test-pattern values and are restored on stream enable. VBLANK changes update exposure range based on active format height. Hardware state does not persist across runtime suspend and is rebuilt from common registers and controls each stream enable.

## Dependencies and integration points
The driver uses V4L2 CCI, V4L2 subdev active-state and streams helpers, fwnode endpoint parsing, regulator bulk supplies (`avdd`, `dovdd`, `dvdd`), GPIO, sensor clock helpers, runtime PM autosuspend, and OF compatible `ovti,ov2732`. It registers with `v4l2_async_register_subdev_sensor()` and uses `v4l2_subdev_s_stream_helper` to bridge legacy `.s_stream` to stream ops.

## Risks
`ov2632_probe_dt()` has a typo in the function name, which is harmless at compile time but confusing for maintenance. The endpoint parser does not check for a missing endpoint before passing it to `v4l2_fwnode_endpoint_alloc_parse()`. Only lane count is validated; link frequency is fixed by the driver and not checked against firmware. The single supported mode means set_fmt is mostly normalization. In `ov2732_set_ctrl()`, the active state is fetched without an obvious NULL check; correctness depends on subdev finalization and lock wiring.

## Test signals
Probe tests should validate missing/malformed endpoint handling, rejection of non-2-lane endpoints, 24 MHz clock enforcement, chip ID `0x002732`, regulator/GPIO sequencing, and autosuspend. Media tests should check one SBGGR10 1920x1080 frame size, raw colorimetry, crop/native selection, and stream-helper compatibility. Runtime tests should trace standby/common-register/control/streaming writes and verify VBLANK/exposure coupling plus analogue/digital gain and all test-pattern menu values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2732.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2735.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov2735.c

## Purpose
This file is a V4L2 CCI/regmap I2C subdevice driver for the OmniVision OV2735 1080p raw Bayer MIPI CSI-2 sensor. It supports one 1920x1080 SGRBG10 mode over two lanes at 420 MHz link frequency, page-addressed register access, common analog/MIPI/BLC initialization, frame-format programming, exposure/gain/blanking/test-pattern controls, regulator/GPIO/clock power sequencing, runtime PM, and the subdev streams API.

## Important APIs, types, and functions
`struct ov2735` stores device, CCI regmap, subdev, media pad, clock, reset/enable GPIOs, regulators, controls, selected link-frequency index, cached current register page, and `page_lock`. `struct ov2735_mode` stores dimensions, default exposure/HTS/VTS, and crop. Register constants encode page number in CCI private bits via `OV2735_PAGE_REG8()` and `OV2735_PAGE_REG16()`. Access goes through `ov2735_page_access()`, `ov2735_read()`, `ov2735_write()`, and `ov2735_multi_reg_write()`, which select register pages before CCI I/O. Functional paths include `ov2735_set_ctrl()`, `ov2735_init_controls()`, `ov2735_set_pll_ctrl()`, `ov2735_set_framefmt()`, `ov2735_enable_streams()`, `ov2735_disable_streams()`, `ov2735_set_pad_format()`, `ov2735_power_on()`, `ov2735_identify_module()`, `ov2735_parse_endpoint()`, and `ov2735_probe()`.

## Control flow
Probe initializes the I2C subdev and 8-bit CCI regmap, initializes the page lock/cache, obtains and validates a 24 MHz xclk, gets regulators, parses the firmware endpoint requiring two data lanes and one supported 420 MHz link frequency, obtains reset and enable GPIOs, powers the device, reads chip ID `0x2735`, initializes controls, creates the media entity/source pad, finalizes subdev active state, enables runtime PM through devm helpers, and registers the sensor subdevice. Format setting normalizes requests to the nearest supported mode, raw colorimetry, updates active HBLANK/VBLANK ranges, stores format, and resets crop to the mode crop. Stream enable resumes runtime PM, programs PLL fields, writes common page-addressed register tables, programs frame/crop dimensions and MIPI line/column counts, restores controls, and writes stream-on. Stream disable writes stream-off and releases runtime PM.

## State and persistence
The driver keeps a cached current page to avoid redundant page-select writes; access is serialized by `page_lock`. Active format/crop are held in subdev state. Control values are cached by V4L2 and restored on stream enable. VBLANK changes update exposure range and write frame-length/frame-sync registers when powered. Hardware state is reconstructed on each stream enable after runtime resume.

## Dependencies and integration points
The driver depends on V4L2 CCI, subdev active-state/streams APIs, fwnode endpoint parsing and `v4l2_link_freq_to_bitmap()`, regulators (`avdd`, `dovdd`, `dvdd`), reset/enable GPIOs, clock framework, runtime PM, and OF compatible `ovti,ov2735`. It uses `v4l2_subdev_s_stream_helper` for legacy stream callers and `v4l2_async_register_subdev_sensor()` for sensor registration.

## Risks
Page selection is a central correctness risk: all register definitions must encode the right page and all accesses must go through the wrappers. `ov2735_page_access()` locks only around page selection, not the following read/write, so concurrent accesses on different pages could interleave page select and data access unless higher-level serialization prevents it. The test-pattern register shares the same address as one MIPI control definition (`0x01b2`), so changing test-pattern bits must not corrupt unrelated MIPI configuration. `HBLANK` is writable and writes hardware, unlike many sensor drivers that expose fixed HBLANK read-only; verify userspace expectations. Remove relies on devm runtime PM cleanup and does not explicitly power off.

## Test signals
Validation should include endpoint rejection for non-2-lane or missing 420 MHz link frequency, 24 MHz xclk enforcement, chip ID `0x2735`, page-select traces for common registers spanning pages 0/1/2, and stream-on order of PLL/common/frame/control/stream writes. Media tests should show one SGRBG10 1920x1080 mode, native 1936x1096 and active 1920x1080 crop signals, and correct raw colorimetry. Concurrency or lockdep-style tests around controls during streaming are useful because of the page-selection cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2735.c -->
