# subset-b-004089 Research

Grouped research report for the V4L2 I2C camera sensor drivers requested by subset B work item `subset-b-004089`. Each section is bounded by the reconciliation markers required by the research cron.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/hi846.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/hi846.c

## Purpose

`hi846.c` is a Linux V4L2 sub-device driver for the Hynix HI846 raw Bayer camera sensor. It exposes the sensor as an I2C-backed media-controller camera entity with one source pad, selectable sensor modes, CSI-2 lane validation, runtime power management, and V4L2 controls for link frequency, pixel rate, blanking, exposure, analogue/digital gain, and test pattern generation. The driver supports three output modes, 640x480, 1280x720, and 1632x1224, backed by large static register tables and separate MIPI register lists for two-lane and four-lane boards.

## Important APIs, Types, and Functions

The main state container is `struct hi846`, which owns reset and shutdown GPIOs, three regulators, the sensor clock, the current `struct hi846_mode`, V4L2 subdev/media pad/control objects, lane count, and a mutex protecting `cur_mode`, `streaming`, and sensor register access. `struct hi846_mode` describes width, height, line length, link-frequency index, nominal fps, frame length, per-mode register lists, lane-specific register lists, and crop rectangle. `struct hi846_reg` and `struct hi846_reg_list` represent raw 16-bit register table entries.

The low-level I2C helpers are `hi846_read_reg()`, `hi846_write_reg()`, `hi846_write_reg_16()`, and `hi846_write_reg_list()`. Control handling lives in `hi846_set_ctrl()` and `hi846_init_controls()`. Mode and pad operations are implemented by `hi846_set_format()`, `hi846_get_format()`, `hi846_enum_mbus_code()`, `hi846_enum_frame_size()`, `hi846_get_selection()`, and `hi846_init_state()`. Streaming and power sequencing are handled by `hi846_start_streaming()`, `hi846_stop_streaming()`, `hi846_set_stream()`, `hi846_power_on()`, `hi846_power_off()`, `hi846_suspend()`, and `hi846_resume()`. Probe/remove and integration entry points are `hi846_parse_dt()`, `hi846_identify_module()`, `hi846_probe()`, `hi846_remove()`, `hi846_pm_ops`, `hi846_of_match`, and `hi846_i2c_driver`.

## Control Flow

Probe allocates `struct hi846`, parses the firmware graph endpoint, validates a two- or four-lane CSI-2 bus and all advertised link frequencies, obtains optional reset/shutdown GPIOs, obtains the sensor clock and three supplies, initializes the V4L2 I2C subdev, powers on the hardware, reads the split chip ID bytes from `0x0f16` and `0x0f17`, initializes controls, creates the media source pad, registers the async sensor subdev, and enables runtime PM.

Format selection chooses the nearest supported mode, rejects active modes that have no register list for the detected lane count, refuses active changes while streaming, updates `cur_mode`, and recalculates read-only link frequency, pixel rate, hblank, and vblank ranges. Streaming first writes the global two-lane or four-lane initialization table, writes the mode configuration table, writes the mode's lane-specific MIPI table, programs frame length and line length through `hi846_set_video_mode()`, applies all active controls with `__v4l2_ctrl_handler_setup()`, optionally logs a diagnostic if undocumented register `0x0034` lacks `BIT(2)`, and finally writes `HI846_REG_MODE_SELECT` to streaming. Stop streaming writes standby and clears the software `streaming` flag.

## State and Persistence Behavior

Persistent in-kernel state is limited to `struct hi846`: current mode, selected format descriptor, runtime lane count, control values held by the V4L2 control framework, and whether streaming is active. The driver does not persist state to disk or firmware. Hardware state is reconstructed on every stream start from static register tables plus current controls. Runtime PM controls the powered state; `hi846_set_ctrl()` updates control ranges even while off, but only writes hardware if `pm_runtime_get_if_in_use()` succeeds.

## Dependencies and Integration Points

The driver depends on Linux I2C, GPIO descriptors, clocks, regulator bulk APIs, runtime PM, V4L2 subdev/control/fwnode helpers, and media-controller entity registration. Firmware integration is through OF compatible `hynix,hi846`, a graph endpoint with CSI-2 bus settings and link-frequency values, optional `reset` and `shutdown` GPIOs, a V4L2 sensor clock expected to be 25 MHz, and supplies named `vddio`, `vdda`, and `vddd`. Its media entity exposes `MEDIA_ENT_F_CAM_SENSOR`, one source pad, and uses `v4l2_subdev_link_validate`.

## Risks and Edge Cases

The driver contains many undocumented `UNKNOWN_*` register writes, so table correctness is board- and sensor-revision-sensitive. `hi846_set_format()` checks lane support before assigning the nearest mode, using the previous `cur_mode` for the lane-register-list validation; this deserves review because the intended validation likely belongs after mode selection. The exposure register is documented as 20 bits but only 16 bits are used, limiting long exposure behavior. `hi846_test_pattern()` enables the ISP test-pattern bit when a pattern is selected but does not explicitly clear that ISP bit when pattern zero is selected. Power sequencing assumes the GPIO polarities encoded by `GPIOD_OUT_LOW` and subsequent values. Error handling in stream enable powers down through the common disable path, but stop errors are logged and ignored.

## Test Signals

Useful validation signals are successful module probe with chip ID `08 46`, correct media graph registration, `v4l2-ctl --list-subdev-mbus-codes`, frame size enumeration for the three modes, lane-specific start streaming on two-lane and four-lane hardware, read-only link frequency and hblank values after mode changes, exposure max updates after vblank changes, runtime suspend/resume around streaming, and visible frames for each supported mode. Test pattern controls should verify both enabling patterns and returning to disabled output. Negative tests should cover missing endpoint, invalid lane count, missing link frequencies, and unsupported link frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/hi846.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/hi847.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/hi847.c

## Purpose

`hi847.c` is a Linux V4L2 I2C sub-device driver for the Hynix HI847 raw camera sensor, aimed at ACPI-described Intel platforms. It exposes two 10-bit Bayer modes, 3264x2448 and 1632x1224, over a fixed four-lane CSI-2 interface with link frequencies of 400 MHz and 200 MHz. The file is dominated by sensor initialization and mode register tables, then wraps them with V4L2 controls, format negotiation, streaming, chip identification, and hardware-configuration validation.

## Important APIs, Types, and Functions

`struct hi847` stores the device pointer, clock, V4L2 subdev and media pad, control handler and controls, current mode, and a mutex. `struct hi847_mode` carries dimensions, line length, default/min frame length, link-frequency index, and a mode register list. `struct hi847_link_freq_config` maps a link-frequency menu index to a PLL/MIPI register list. `struct hi847_reg` and `struct hi847_reg_list` represent 16-bit register writes.

Register access is implemented by `hi847_read_reg()`, `hi847_write_reg()`, and `hi847_write_reg_list()`. Control handlers include `hi847_update_digital_gain()`, `hi847_test_pattern()`, `hi847_grbg_shift()`, `hi847_set_ctrl_hflip()`, `hi847_set_ctrl_vflip()`, `hi847_set_ctrl()`, and `hi847_init_controls()`. Subdev operations are `hi847_set_stream()`, `hi847_set_format()`, `hi847_get_format()`, `hi847_enum_mbus_code()`, `hi847_enum_frame_size()`, and `hi847_open()`. Platform integration goes through `hi847_identify_module()`, `hi847_check_hwcfg()`, `hi847_probe()`, `hi847_remove()`, ACPI ID `HYV0847`, and `hi847_i2c_driver`.

## Control Flow

Probe allocates `struct hi847`, obtains a V4L2 sensor clock, enforces the 19.2 MHz external clock, checks the fwnode graph endpoint for exactly four CSI-2 data lanes and both required link frequencies, initializes the V4L2 I2C subdev, reads `HI847_REG_CHIP_ID`, initializes the mutex and controls, sets the default full-resolution mode, registers the media entity and async subdev, and enables runtime PM. Unlike several OF-oriented sensor drivers, this file has no explicit regulator or GPIO power sequence; platform/ACPI power resources are expected to make the device accessible.

On active format set, the nearest mode is selected, pad format is assigned as `MEDIA_BUS_FMT_SGRBG10_1X10`, and link frequency, pixel rate, vblank, and hblank controls are adjusted to the mode. Stream start writes the link-frequency register list, writes the current mode table, applies all controls, enables the timing generator through `HI847_REG_MODE_TG`, and writes streaming mode. Stream stop disables the timing generator and sets standby. Control writes are skipped unless runtime PM reports the device is in use.

## State and Persistence Behavior

The driver keeps runtime state in `struct hi847` and V4L2 control values only. It has no persistent storage. Sensor register state is reprogrammed on every stream start from static register tables plus current controls. Hflip and vflip are ordinary controls; the driver compensates Bayer sampling offsets by programming `HI847_REG_FORMAT_X` and `HI847_REG_FORMAT_Y` through `hi847_grbg_shift()` before updating mirror/flip bits. Runtime PM is enabled, but no runtime PM callbacks are declared in this file, so power-state effects are platform-dependent.

## Dependencies and Integration Points

Dependencies include Linux ACPI, fwnode graph parsing, clocks, I2C, runtime PM, V4L2 controls/devices/fwnode helpers, and media entity APIs. The ACPI match table exposes `HYV0847`. Hardware configuration depends on a CSI-2 DPHY endpoint with exactly four data lanes and link-frequency properties containing both 400 MHz and 200 MHz. The driver registers a camera sensor entity with one source pad and link validation.

## Risks and Edge Cases

The driver does not manage regulators, GPIO reset, or explicit clock enable/disable around streaming beyond validating `clk_get_rate()`, so it relies heavily on ACPI/platform power behavior. `hi847_set_ctrl()` ignores return values from `hi847_set_ctrl_hflip()` and `hi847_set_ctrl_vflip()`, leaving `ret` as success even if orientation writes fail. `hi847_test_pattern()` ORs the requested pattern into the current test-pattern register value, which may leave stale bits when switching or disabling patterns. The link-frequency configs for both menu entries point to the same `mipi_data_rate_lane_4` table, so mode-specific link-rate differences are mostly represented by the mode table and control metadata. Runtime PM has no callbacks in the driver structure, making `pm_runtime_get_if_in_use()` mostly a gating mechanism rather than a full hardware transition.

## Test Signals

Validation should include chip ID `0x0847`, ACPI enumeration through `HYV0847`, correct rejection of non-19.2 MHz clocks, endpoint validation for exactly four lanes and both link frequencies, enumeration of the two frame sizes, format changes updating pixel/link-rate controls, successful streaming in both modes, and Bayer order correctness under hflip/vflip. Control tests should exercise analogue gain, digital gain on all color channels, vblank/exposure interaction, test-pattern enable/disable, and start/stop error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/hi847.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx111.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx111.c

## Purpose

`imx111.c` is a V4L2 media-controller driver for the Sony IMX111 CMOS raw image sensor. It supports OF-described boards, one or two CSI-2 lanes, multiple external clock rates, RAW8 and RAW10 media bus formats, a broad set of crop/binning output sizes, runtime PM with autosuspend, and CCI/regmap-based register access. The driver exposes a modern pad stream API through `enable_streams` and `disable_streams` while using V4L2 helper compatibility for `.s_stream`.

## Important APIs, Types, and Functions

`struct imx111` is the main state object. It stores the CCI regmap, external clock, reset GPIO, supplies, parsed CSI-2 endpoint, V4L2 subdev and pad, control handler and controls, current mode, selected PLL entry, data depth, raw pixel clock, and default link frequency. `struct imx111_mode` defines width, height, default vertical/horizontal total length, and a CCI register sequence. `struct imx111_pll` maps supported external clock rates to PLL pre-divider and multiplier values.

Key helpers include `to_settle_delay()`, `imx111_get_format_code()`, `imx111_get_format_bpp()`, `imx111_update_digital_gain()`, `imx111_set_ctrl()`, `imx111_init_controls()`, `imx111_enable_streams()`, `imx111_disable_streams()`, and `imx111_initialize()`. Pad and media operations are `imx111_enum_mbus_code()`, `imx111_enum_frame_size()`, `imx111_set_format()`, `imx111_init_state()`, `imx111_init_subdev()`, and `imx111_subdev_entity_ops`. Platform lifecycle is implemented by `imx111_power_on()`, `imx111_power_off()`, runtime PM callbacks, `imx111_identify_module()`, `imx111_clk_init()`, `imx111_parse_dt()`, `imx111_probe()`, and `imx111_remove()`.

## Control Flow

Probe creates a CCI regmap, obtains the external clock, optional reset GPIO, and `iovdd`/`dvdd`/`avdd` regulators, parses the fwnode endpoint, validates lane count, computes the PLL and default link frequency from the external clock and lane count, powers on the sensor, reads product/revision/manufacturer registers, initializes global sensor registers, initializes subdev/media/control state, finalizes subdev active state, enables runtime PM, registers the async sensor, and enables autosuspend.

Format negotiation finds the nearest mode, updates active data depth from the selected media bus code, recalculates pixel rate as `pixel_clk_raw / (2 * data_depth)`, and updates blanking ranges. `imx111_get_format_code()` maps hflip/vflip controls to Bayer order; hflip and vflip carry `V4L2_CTRL_FLAG_MODIFY_LAYOUT`. Stream enable resumes runtime PM, writes the current mode table, writes RAW8/RAW10 data depth with group hold, applies all current controls, sets streaming mode, grabs flip controls, and waits 30 ms. Stream disable writes standby, releases flip controls, and autosuspends.

## State and Persistence Behavior

State persists only in memory: parsed endpoint data, PLL selection, current mode, current data depth, V4L2 controls, and active subdev format state. Hardware configuration is rebuilt from `imx111_global_init`, mode tables, data depth, and controls whenever runtime PM resumes and streaming starts. The driver uses group-write (`IMX111_GROUP_WRITE`) around multi-register exposure, gain, and timing updates so related values latch consistently. No nonvolatile data is written.

## Dependencies and Integration Points

The driver depends on CCI/regmap, clocks, GPIO descriptors, regulator bulk APIs, runtime PM, V4L2 async/subdev/control/fwnode helpers, media entity helpers, and the OF match string `sony,imx111`. Firmware must provide a graph endpoint, link-frequency matching the driver-computed default, valid CSI-2 lane count no greater than two, a usable sensor clock, optional reset GPIO, and three named supplies. The media entity is `MEDIA_ENT_F_CAM_SENSOR` with one source pad.

## Risks and Edge Cases

PLL and link-frequency validation are strict: endpoint link-frequency must exactly match the computed default, which can reject otherwise functional board descriptions. The endpoint parse accepts lane counts up to two and does not explicitly reject zero lanes before clock math, so invalid firmware could produce a bad computed link frequency. Several nominal modes reuse larger register tables while exposing smaller dimensions, so crop/scaler behavior must match the intended sensor configuration. Flip controls are grabbed only after stream start succeeds, but layout-modifying format codes depend on current flip values. The driver relies on CCI group writes for atomic updates; failures in a sequence can leave group hold cleanup dependent on accumulated `ret`.

## Test Signals

Good test coverage includes probe with supported external clock rates, rejection of unsupported clocks/link frequencies, chip ID `0x0111`, media bus code enumeration for RAW10 and RAW8 families with flip-dependent Bayer order, all listed frame sizes, runtime PM autosuspend/resume, stream enable/disable through both pad stream APIs and legacy helper path, hblank/vblank/exposure range updates on mode changes, and test pattern color-channel controls. Hardware tests should verify real frame timing after hblank/vblank changes and that flip controls are blocked during streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx208.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx208.c

## Purpose

`imx208.c` is a V4L2 I2C sub-device driver for the Sony IMX208 raw image sensor, targeted at ACPI platforms. It supports two 10-bit Bayer modes, 1936x1096 and 968x548, fixed two-lane CSI-2 timing metadata, direct I2C register access, V4L2 controls for gain/exposure/blanking/orientation/test patterns, runtime PM, and a read-only sysfs binary attribute exposing 40 bytes of OTP data.

## Important APIs, Types, and Functions

`struct imx208` holds the device, clock, subdev, pad, control handler and controls, current mode, mutex, cached OTP state/data, and a cached `identified` flag. `struct imx208_mode` stores dimensions, default/min VTS, link-frequency index, and a mode register list. `struct imx208_link_freq_config` maps link frequencies to pixels-per-line and PLL registers. `struct imx208_reg` and `struct imx208_reg_list` describe one-byte register tables.

Important helpers are `link_freq_to_pixel_rate()`, `imx208_get_format_code()`, `imx208_read_reg()`, `imx208_write_reg()`, `imx208_write_regs()`, `imx208_update_digital_gain()`, `imx208_set_ctrl()`, `imx208_set_pad_format()`, `imx208_identify_module()`, `imx208_start_streaming()`, `imx208_stop_streaming()`, `imx208_set_stream()`, `imx208_read_otp()`, `otp_read()`, `imx208_init_controls()`, `imx208_probe()`, and `imx208_remove()`. The sysfs attribute is declared with `BIN_ATTR_RO(otp, IMX208_OTP_SIZE)`.

## Control Flow

Probe allocates state, obtains a V4L2 sensor clock, enforces a 19.2 MHz external clock, initializes the I2C subdev, optionally reads the chip ID immediately if ACPI reports D0 power state, sets the default full-resolution mode, creates controls and the mutex, initializes media entity and async subdev registration, creates the OTP sysfs binary file, and enables runtime PM. The driver uses `I2C_DRV_ACPI_WAIVE_D0_PROBE`, so it can avoid forcing ACPI devices into D0 just to probe.

Format negotiation chooses the nearest mode, updates link frequency, pixel rate, vblank range, and read-only hblank. Bayer order changes according to hflip/vflip values through a static code matrix. Stream start resumes runtime PM, identifies the module if not already cached, writes PLL registers, writes the selected mode table, applies controls, and writes streaming mode. Stream stop writes standby, releases runtime PM, and grabs/ungrabs hflip and vflip around streaming.

OTP access is lazy. The first sysfs read takes the mutex, resumes runtime PM, identifies the module, reads 40 bytes starting at `0x3500` via a two-message I2C transfer, caches the data, sets `otp_read`, and returns slices from the cached buffer for subsequent reads.

## State and Persistence Behavior

Runtime state includes the current mode, control values, cached chip-identification status, and cached OTP data. The OTP data is read from sensor memory once per driver instance and not refreshed unless the device is reprobed. Register state is rebuilt on each stream start from PLL and mode tables plus current controls. There is no disk persistence and no writable sysfs attribute. The mutex serializes pad format, stream transitions, control access, and OTP reads.

## Dependencies and Integration Points

Dependencies include Linux ACPI, clock, I2C, runtime PM, V4L2 subdev/control/device helpers, and media entity APIs. ACPI match ID is `INT3478`; the I2C driver uses `I2C_DRV_ACPI_WAIVE_D0_PROBE`. It registers a camera sensor media entity with one source pad and a read-only `otp` binary sysfs file on the I2C device. Unlike OF/fwnode drivers, this file does not parse a graph endpoint and hardcodes link-frequency metadata for two lanes.

## Risks and Edge Cases

The `imx208_update_digital_gain()` signature accepts a `len` argument that is unused, which is harmless but misleading. Digital gain is an integer menu index into five discrete values, so callers must not treat the raw control value as a register value. Exposure max is initialized from VTS minus eight, but `imx208_set_ctrl()` does not dynamically shrink exposure range when VBLANK changes, unlike several peer drivers. OTP reads cache the first successful result permanently; transient corruption during the first read would persist until reprobe. Because no endpoint is parsed, board-level lane/frequency mismatches are not validated here. Runtime PM behavior depends on ACPI power state and platform integration.

## Test Signals

Tests should confirm ACPI enumeration through `INT3478`, successful operation with D0-waived probing, chip ID `0x0208`, creation and stable reads of `/sys/.../otp`, frame size enumeration for both modes, Bayer code changes under hflip/vflip, control writes during active streaming, and correct mode-dependent pixel-rate/link-frequency/hblank/vblank metadata. Negative tests should include wrong clock rate, chip ID mismatch, OTP read while suspended, invalid digital gain index protection by the V4L2 control core, and stream start failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx208.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx214.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx214.c

## Purpose

`imx214.c` is a V4L2 I2C sub-device driver for the Sony IMX214 raw camera sensor. It supports OF-described four-lane CSI-2 hardware, CCI/regmap register access, runtime PM, PLL calculation through the shared CCS PLL helper, two modes, test patterns with color controls, flip-dependent Bayer ordering, crop/selection reporting, and legacy frame-interval compatibility operations. It is a larger sensor driver with substantial reverse-engineered register tables and explicit power sequencing.

## Important APIs, Types, and Functions

`struct imx214` owns the device, xclk, CCI regmap, calculated `struct ccs_pll`, parsed endpoint, V4L2 subdev/pad/control handler, controls, regulator array, and enable GPIO. `struct imx214_mode` stores width, height, default VTS, and a mode register table. The register constants cover chip ID, streaming, frame length, exposure, analogue and digital gains, orientation, CSI format/lane mode, PLL, crop/output geometry, binning, noise/statistics, test pattern, and active pixel array geometry.

Core helpers include `imx214_power_on()`, `imx214_power_off()`, `imx214_get_format_code()`, `imx214_update_pad_format()`, `imx214_set_format()`, `imx214_get_selection()`, `imx214_entity_init_state()`, `imx214_configure_pll()`, `imx214_update_digital_gain()`, `imx214_set_ctrl()`, `imx214_pll_calculate()`, `imx214_pll_update()`, `imx214_ctrls_init()`, `imx214_start_streaming()`, `imx214_stop_streaming()`, `imx214_s_stream()`, `imx214_parse_fwnode()`, `imx214_identify_module()`, `imx214_probe()`, and `imx214_remove()`. Optional advanced debug register access is present under `CONFIG_VIDEO_ADV_DEBUG`.

## Control Flow

Probe obtains xclk, regulators `vdda`/`vddd`/`vdddo`, a required `enable` GPIO, and a CCI regmap, parses the fwnode endpoint, validates exactly four CSI-2 lanes, normalizes the legacy 480 MHz link frequency to 600 MHz, and accepts a link frequency only if `imx214_pll_calculate()` succeeds. It initializes the V4L2 subdev, powers on the sensor, verifies chip ID `0x0214`, initializes controls and PLL-derived pixel rate, creates the media entity and active state, enables runtime PM, registers the async sensor subdev, and idles the device.

Active format setting chooses the nearest mode, updates pad format and crop, and recalculates vblank, exposure, and hblank ranges. Stream start writes the common register table, configures PLL registers, writes requested CSI link bit rate, configures four-lane mode, finds the active mode from the locked subdev state, writes the mode table, enables the temperature sensor, applies all controls, and writes streaming mode. Stream stop writes standby and releases runtime PM. Legacy frame-interval operations always report 30 fps for compatibility while warning users to use blanking controls for real timing.

## State and Persistence Behavior

State is in memory and in V4L2 active state: endpoint data, calculated PLL, current active format/crop, control values, power state, and regulator/GPIO handles. The driver does not persist data externally. PLL state is recalculated from selected link frequency and xclk, then written during stream start. Runtime control writes use `pm_runtime_get_if_in_use()` so controls may be changed while off and synchronized later through `__v4l2_ctrl_handler_setup()`. Hflip and vflip are clustered and marked layout-modifying so Bayer code and format behavior stay coupled.

## Dependencies and Integration Points

The driver depends on CCI/regmap, the shared `ccs-pll.h` helper, clocks, GPIO descriptors, regulators, runtime PM, V4L2 controls/fwnode/subdev helpers, and media entity APIs. It binds to OF compatible `sony,imx214`. Firmware must provide one graph endpoint, four CSI-2 data lanes, at least one usable link frequency, an xclk in the CCS PLL limits, a required enable GPIO, and the three named supplies. The media entity is a one-pad `MEDIA_ENT_F_CAM_SENSOR`.

## Risks and Edge Cases

Many PLL limits and register sequences are explicitly reverse-engineered, so timing assumptions may be fragile across boards. The code warns but continues when the endpoint advertises more than one link frequency, and transparently rewrites legacy 480 MHz to 600 MHz for backward compatibility. `imx214_start_streaming()` always writes `IMX214_CSI_4_LANE_MODE`, matching current validation but limiting future two-lane support. The test-pattern menu order differs from raw register values and is translated through `imx214_test_pattern_val`; tests should not assume menu index equals hardware value. Legacy frame-interval operations intentionally report an unreliable fixed value. Power-on contains a comment about avoiding clock-disable warnings, indicating sequencing sensitivity.

## Test Signals

Validation should cover OF probe with `sony,imx214`, regulator/GPIO/clock sequencing, chip ID `0x0214`, endpoint rejection for non-four-lane hardware, PLL calculation for accepted link frequencies, legacy 480 MHz normalization, mode enumeration for 4096x2304 and 1920x1080, crop/native-size selections, active format changes updating control ranges, streaming with common and per-mode tables, test patterns and solid-color channels, hflip/vflip Bayer-code changes, runtime suspend/resume, and the compatibility frame-interval warning path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx214.c -->
