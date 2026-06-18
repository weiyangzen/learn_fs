# Research Report: subset-b-004097

This grouped report covers five OmniVision V4L2 I2C camera sensor drivers under `sources/distributed-fs/ceph-client/drivers/media/i2c/`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2740.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov2740.c

## Purpose

`ov2740.c` is a Linux kernel V4L2 sub-device driver for the OmniVision OV2740 raw Bayer camera sensor. It binds through ACPI (`INT3474`) as an I2C driver, exposes a single source pad media entity, and supports a 1932x1092 10-bit GRBG CSI-2 output mode selected against firmware-provided link frequencies. The driver also exposes the sensor's customer OTP area through the kernel nvmem provider API.

## Important APIs, Types, and Functions

The central state is `struct ov2740`, which owns the `v4l2_subdev`, media pad, control handler, runtime-selected mode table, reset and powerdown GPIOs, sensor clock, regulator bulk array, OTP/nvmem state, and an `identified` cache. Mode metadata is split into `struct ov2740_mode`, `struct ov2740_reg_list`, and `struct ov2740_link_freq_config`.

Register access is implemented by `ov2740_read_reg()`, `ov2740_write_reg()`, and `ov2740_write_reg_list()` using raw I2C transfers with 16-bit register addresses. `ov2740_identify_module()` reads the three-byte chip ID from `OV2740_REG_CHIP_ID` and caches success. `ov2740_update_digital_gain()` writes RGB digital gains under the sensor group-hold protocol. `ov2740_test_pattern()` maps the V4L2 menu index to the sensor test-pattern register.

Controls are initialized in `ov2740_init_controls()` and applied in `ov2740_set_ctrl()`. Exposed controls include link frequency, pixel rate, hblank, vblank, analogue gain, digital gain, exposure, test pattern, and firmware-described properties from `v4l2_fwnode_device_parse()`. Format operations are implemented by `ov2740_set_format()`, `ov2740_enum_mbus_code()`, `ov2740_enum_frame_size()`, and `ov2740_init_state()`.

Streaming is controlled by `ov2740_set_stream()`, `ov2740_start_streaming()`, and `ov2740_stop_streaming()`. Probe and lifetime are handled by `ov2740_probe()` and `ov2740_remove()`. Runtime PM is supplied through `DEFINE_RUNTIME_DEV_PM_OPS()` with `ov2740_suspend()` and `ov2740_resume()`. OTP support is implemented by `ov2740_register_nvmem()`, `ov2740_nvmem_read()`, and `ov2740_load_otp_data()`.

## Control Flow

Probe allocates `struct ov2740`, initializes the V4L2 I2C subdev, parses the firmware endpoint, and chooses either the 360 MHz or 180 MHz mode table based on endpoint link frequencies. It obtains optional reset and powerdown GPIOs, validates the required 19.2 MHz clock, fetches `AVDD`, `DOVDD`, and `DVDD` regulators, and, if ACPI reports the device in D0, powers it enough to identify the chip. It then creates controls, initializes media entity state, enables runtime PM, registers the async sensor subdev, and attempts nvmem registration.

Stream-on locks the active subdev state, resumes runtime PM, identifies the sensor if needed, lazily loads OTP data when nvmem support is present, software-resets the sensor, writes the link-frequency PLL table, writes the selected mode table, applies all controls, and finally writes `OV2740_MODE_STREAMING`. Stream-off writes standby and drops the runtime PM reference.

Format negotiation selects the nearest supported mode from the firmware-compatible mode table, fixes the media bus code to `MEDIA_BUS_FMT_SGRBG10_1X10`, updates active state, and updates read-only link-frequency, pixel-rate, hblank, vblank, and exposure ranges for active formats.

The OTP path takes the active subdev-state lock, resumes the device if needed, clears ISP bits needed to expose OTP memory, temporarily starts streaming, waits 20 ms, reads 256 bytes from `0x7010` through regmap bulk access, returns to standby, restores ISP registers, and caches the buffer for future reads.

## State and Persistence Behavior

Persistent runtime state is in `struct ov2740`: selected mode table, current mode, control values held by the V4L2 handler, `identified`, and optional cached OTP bytes in `nvm_data::nvm_buffer`. The driver does not persist settings across module unload; controls are replayed at stream-on through `__v4l2_ctrl_handler_setup()`. OTP bytes are cached in RAM after first read to avoid repeated sensor mode manipulation. Runtime PM state gates hardware register writes: control writes return success without touching hardware when the device is suspended.

## Dependencies and Integration Points

The driver depends on the V4L2 subdev, async registration, media entity, fwnode endpoint parsing, PM runtime, regulator, GPIO, clock, nvmem provider, and regmap frameworks. Firmware must provide a CSI-2 D-PHY endpoint with exactly two data lanes and at least one supported link frequency. ACPI matching uses `INT3474`, and the I2C driver sets `I2C_DRV_ACPI_WAIVE_D0_PROBE`.

## Risks and Edge Cases

The driver supports only one resolution per link-frequency table, so endpoint link-frequency data directly controls available modes. Incorrect firmware link-frequency values cause probe failure. OTP loading temporarily enters streaming and manipulates ISP control registers, making serialization through the subdev state lock important. `ov2740_start_streaming()` calls `ov2740_load_otp_data()` but ignores its return value, so OTP read failure does not block normal streaming. Control writes are skipped while suspended and rely on replay at stream-on. The 180 MHz and 360 MHz mode tables have different VTS bounds, so exposure/vblank range updates are sensitive to mode selection.

## Test Signals

Useful validation includes probe on ACPI systems with correct and incorrect link-frequency tables, runtime suspend/resume cycling, `media-ctl` topology inspection, `v4l2-ctl --list-ctrls`, `v4l2-compliance` for subdev pad and control APIs, stream-on/off at both supported link frequencies, exposure/vblank range changes after `set_fmt`, and reading the nvmem device to verify OTP serialization and caching. Kernel build coverage should include ACPI, PM runtime, nvmem, and V4L2 subdev support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov2740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov4689.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov4689.c

## Purpose

`ov4689.c` is a V4L2 I2C sub-device driver for the OmniVision OV4689 raw Bayer sensor. It targets a device-tree described four-lane MIPI CSI-2 sensor with a 24 MHz external clock, one supported 2688x1520 SBGGR10 mode, and controls for exposure, analogue and digital gain, blanking, flips, white-balance channel gains, and test patterns.

## Important APIs, Types, and Functions

The main state type is `struct ov4689`, containing the device, CCI regmap, clock, reset and powerdown GPIOs, regulators, V4L2 subdev, media pad, control handler, exposure control pointer, and current mode. Register access uses the V4L2 CCI helpers (`devm_cci_regmap_init_i2c()`, `cci_read()`, `cci_write()`, `cci_update_bits()`, and `cci_multi_reg_write()`), avoiding hand-rolled I2C register formatting.

`struct ov4689_mode` describes the single mode, including dimensions, HTS/VTS defaults, exposure default, pixel rate, and the mode register sequence. `struct ov4689_gain_range` drives `ov4689_map_gain()`, which translates logical V4L2 analogue gain values to the sensor's physical gain register encoding.

Pad and format functions are `ov4689_fill_fmt()`, `ov4689_set_fmt()`, `ov4689_enum_mbus_code()`, `ov4689_enum_frame_sizes()`, and `ov4689_get_selection()`. Streaming is implemented by `ov4689_s_stream()`, timing setup helpers `ov4689_setup_timings()` and `ov4689_setup_blc_anchors()`, and runtime PM callbacks `ov4689_power_on()` and `ov4689_power_off()`. Control setup and application are handled by `ov4689_initialize_controls()` and `ov4689_set_ctrl()`. Probe support includes `ov4689_check_hwcfg()`, `ov4689_check_link_frequency()`, `ov4689_configure_regulators()`, and `ov4689_check_sensor_id()`.

## Control Flow

Probe first validates the firmware endpoint: the bus must be CSI-2 D-PHY, use exactly four data lanes, and advertise the supported 504 MHz link frequency. It allocates state, fixes `cur_mode` to the only supported mode, acquires and validates a 24 MHz sensor clock, initializes a 16-bit CCI regmap, obtains optional reset and `pwdn` GPIOs, gets the three regulators, initializes the V4L2 subdev and controls, powers on the sensor, checks the chip ID, creates the media source pad, finalizes subdev state, enables runtime PM with autosuspend, registers the async sensor, and then autosuspends.

Stream-on locks the active state, resumes runtime PM, writes the mode register list, programs crop/output timing registers, writes black-level correction anchor registers, applies the V4L2 controls, and writes `OV4689_MODE_STREAMING`. Stream-off writes software standby and releases the runtime PM reference with autosuspend.

Control writes first update dependent ranges, especially exposure maximum after vblank changes. If the device is not currently powered, the control value is stored only in the control handler. When powered, exposure is written as a 24-bit value shifted by four fractional bits; analogue gain is mapped through the range table; vblank and hblank update VTS and HTS; flips update timing format registers; and red/blue balance write white-balance gain registers.

## State and Persistence Behavior

The driver keeps only volatile in-kernel state: current mode, control handler values, and runtime PM state. There is no nonvolatile calibration export and no cached sensor register mirror beyond the control framework. Since only one mode exists, format negotiation does not mutate `cur_mode`; it clamps requests to that mode. Hardware state is restored on every stream-on by writing the complete mode sequence and replaying controls.

## Dependencies and Integration Points

This driver integrates with the media controller, V4L2 async sensor registration, V4L2 fwnode endpoint parsing, regulator, GPIO, clock, runtime PM, and V4L2 CCI/regmap layers. It matches `of_match_table` compatible `ovti,ov4689`. Firmware endpoint correctness is essential because lane count and link frequency are hard requirements.

## Risks and Edge Cases

There is only one supported mode and one link frequency, so userspace requests are always clamped to 2688x1520 SBGGR10. The gain mapping is table-based and can reject out-of-range logical values. HBLANK writes divide `(width + hblank)` by `OV4689_HTS_DIVIDER`, so control step and bounds must stay aligned to that divider. Probe powers the device to read chip ID; failures must unwind controls, entity setup, and regulators correctly. Hardware writes in `ov4689_set_ctrl()` are skipped while suspended and depend on stream-on replay.

## Test Signals

Validate successful probe only with a four-lane endpoint and the 504 MHz link frequency; negative tests should cover missing endpoint, wrong lane count, wrong xclk, and missing regulators. Runtime tests should cover stream-on/off, autosuspend, `v4l2-compliance`, pad selection crop bounds, flip controls changing reported image orientation expectations, hblank/vblank range updates, and analogue gain mapping across each range boundary. Build coverage should include `CONFIG_VIDEO_V4L2_CCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov4689.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov5640.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov5640.c

## Purpose

`ov5640.c` is a full-featured V4L2 sub-device driver for the OmniVision OV5640 5MP sensor. It supports device-tree described parallel DVP, BT.656, and MIPI CSI-2 buses, multiple resolutions from 160x120 through 2592x1944, several media bus formats including YUV, RGB565, JPEG, and 8-bit raw Bayer, frame interval negotiation, runtime PM, and a broad set of image controls.

## Important APIs, Types, and Functions

The main state is `struct ov5640_dev`, which owns the I2C client, subdev, media pad, parsed endpoint, clock, regulators, optional reset and powerdown GPIOs, orientation flag, mutex, current format, current and last modes, frame interval, current CSI-2 link frequency, grouped controls, automatic exposure state, pending mode/format flags, and streaming state.

Formats are described by `struct ov5640_pixfmt`; per-mode geometry and bus-specific timing are described by `struct ov5640_mode_info` and `struct ov5640_timings`. The mode table provides low-resolution, 720p, 1080p, and QSXGA register sequences plus DVP and CSI-2 timing variants.

I2C register helpers include `ov5640_init_slave_id()`, `ov5640_write_reg()`, `ov5640_read_reg()`, `ov5640_read_reg16()`, `ov5640_write_reg16()`, and `ov5640_mod_reg()`. Clock programming is a major subsystem: `ov5640_calc_sys_clk()`, `ov5640_set_mipi_pclk()`, `ov5640_calc_pixel_rate()`, `ov5640_calc_pclk()`, and `ov5640_set_dvp_pclk()` derive PLL and divider registers for CSI-2 or DVP.

Mode setting flows through `ov5640_set_mode()`, `ov5640_set_mode_direct()`, `ov5640_set_mode_exposure_calc()`, `ov5640_set_timings()`, `ov5640_set_jpeg_timings()`, `ov5640_set_binning()`, `ov5640_set_bandingfilter()`, and `ov5640_set_virtual_channel()`. Power and streaming are split between common power sequencing and bus-specific setup: `ov5640_set_power_on()`, `ov5640_set_power_off()`, `ov5640_set_power_mipi()`, `ov5640_set_power_dvp()`, `ov5640_set_stream_mipi()`, `ov5640_set_stream_dvp()`, and `ov5640_s_stream()`.

The control surface is implemented by `ov5640_init_controls()`, `ov5640_s_ctrl()`, and `ov5640_g_volatile_ctrl()`, with helpers for exposure, gain, white balance, hue, contrast, saturation, test pattern, power-line frequency, hflip, vflip, and vblank.

## Control Flow

Probe establishes default VGA UYVY state, parses the first firmware endpoint, accepts parallel, BT.656, or CSI-2 D-PHY buses, selects a default format based on bus type, validates an xclk between 6 MHz and 54 MHz, acquires optional GPIOs, initializes the subdev and media entity, fetches supplies, initializes the mutex and controls, powers on and restores default mode, enables runtime PM, verifies chip ID `0x5640`, registers the async sensor, and enables autosuspend.

Power-on enables xclk and regulators, runs the hardware or software reset/powerdown sequence, optionally reprograms the sensor slave ID, loads the global initialization sequence, restores the last mode, and configures the active frame format. Bus-specific power setup then either configures MIPI LP-11/HS resources or DVP/BT.656 pad output, polarity, and embedded sync settings. Power-off reverses bus configuration, disables regulators, and disables the clock.

Format negotiation finds the nearest mode and format, constraining 8 bpp formats away from low resolutions and 24 bpp formats away from high resolutions. Active `set_fmt` is rejected while streaming, updates pending flags, stores the new media bus format, and recalculates pixel rate, link frequency, hblank, vblank, and exposure ranges. Frame interval changes similarly update current FPS and mark a pending mode change.

Stream-on resumes runtime PM, replays controls, locks the driver mutex, applies pending mode and format changes, and starts either the CSI-2 or DVP stream. Stream-off writes the bus-specific stop condition and drops the runtime PM reference. Mode changes between subsampling and scaling can run exposure recalculation to preserve approximate brightness across capture transitions; mode changes within the same downsize class load registers directly.

## State and Persistence Behavior

The driver maintains a significant volatile software model: current format, current mode, last mode, frame interval, CSI-2 link frequency, pending mode/format flags, previous sysclk/HTS for exposure calculations, AE thresholds, and streaming state. Control values persist in the V4L2 handler across runtime suspend and are replayed before streaming. Gain and exposure are marked volatile, so reads can query hardware when powered. No calibration or settings persist beyond the lifetime of the driver instance.

## Dependencies and Integration Points

The driver depends on V4L2 subdev, media controller, V4L2 async registration, fwnode endpoint parsing, runtime PM, regulators, GPIO descriptors, clocks, and I2C. It matches device-tree compatible `ovti,ov5640` and I2C ID `ov5640`. It exposes source-pad crop and native-size metadata, V4L2 events, frame interval operations, and a module parameter `virtual_channel` for CSI-2 channel selection.

## Risks and Edge Cases

This is a broad driver with many timing paths. PLL calculations are constrained by undocumented or vendor-derived assumptions, so new formats or lane counts can break clock limits. The CSI-2 link-frequency table intentionally contains duplicates, and `WARN_ON()` catches missing calculated frequencies but does not recover. DVP operation depends on physical wiring of data lines and endpoint polarity flags. Mode switching has complex exposure/gain preservation math with several divide-by-zero guards. `ov5640_set_mode()` returns success if clock programming fails because it returns `0` on `ret < 0`, which is a notable behavioral risk. Active format and frame interval changes are blocked while streaming, so userspace must stop the stream before reconfiguration.

## Test Signals

Validation should cover both CSI-2 and DVP/BT.656 device-tree endpoints, multiple xclk frequencies within and outside range, all exposed media bus formats, all supported resolutions, frame interval enumeration and setting, runtime PM autosuspend, stream-on/off after pending mode and format changes, volatile gain/exposure reads, and controls for white balance, gain, exposure, vblank, power-line frequency, flips, and test pattern. `v4l2-compliance`, `media-ctl`, and real capture tests are important because static build tests will not exercise PLL, lane, polarity, or exposure transition behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov5640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov5645.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov5645.c

## Purpose

`ov5645.c` is a V4L2 I2C sub-device driver for the OmniVision OV5645 camera sensor. It targets a device-tree described MIPI CSI-2 endpoint and exposes UYVY 8-bit-per-component output over a 16-bit media bus code, with predefined SXGA, 1080p, and full-resolution modes plus controls for saturation, flips, auto gain, auto white balance, auto exposure, and test patterns.

## Important APIs, Types, and Functions

`struct ov5645` contains the I2C client, device, V4L2 subdev, media pad, parsed endpoint, crop rectangle, xclk, regulators, current mode pointer, controls, pixel-rate and link-frequency controls, cached register values for AEC/AGC and flip registers, and mandatory enable/reset GPIOs.

Register access is implemented by `ov5645_write_reg()` and `ov5645_read_reg()` using 16-bit register addresses. Register tables use `struct reg_value`, while modes use `struct ov5645_mode_info` to pair dimensions, register arrays, pixel clocks, and link frequencies. `ov5645_set_register_array()` sequentially writes tables and delays briefly when the system-control register starts the sensor.

Power sequencing is split between `ov5645_set_power_on()`, `ov5645_set_power_off()`, and `__ov5645_set_power_off()`. Controls are implemented by `ov5645_s_ctrl()` and helpers for AEC, AGC, saturation, hflip, vflip, test pattern, and AWB. Pad operations include `ov5645_enum_mbus_code()`, `ov5645_enum_frame_size()`, `ov5645_set_format()`, `ov5645_get_selection()`, `ov5645_enable_streams()`, and `ov5645_disable_streams()`.

## Control Flow

Probe allocates state, parses the endpoint at port 0 and requires CSI-2 D-PHY, obtains a legacy xclk and checks it is within one percent of 24 MHz, gets three regulators, obtains mandatory `enable` and `reset` GPIOs, initializes controls, initializes the V4L2 I2C subdev and media entity, powers the sensor on, reads and validates high and low chip ID bytes, reads cached AEC/AGC and flip register values, finalizes subdev state, enables runtime PM, registers the async sensor, and enables autosuspend.

Power-on enables regulators, prepares the clock, asserts enable, deasserts reset, waits for the sensor, and writes the global initialization table. Stream-on resumes runtime PM, writes the selected mode table, replays controls, enables the MIPI interface, and writes system-control start. Stream-off disables MIPI output, writes system-control stop, and autosuspends.

Format setting finds the nearest supported mode, updates crop dimensions and active controls for pixel clock and link frequency, stores the current mode, and fixes the frame format to `MEDIA_BUS_FMT_UYVY8_1X16` with sRGB colorspace. The initial state picks mode index 1 from the mode table.

## State and Persistence Behavior

The driver caches `aec_pk_manual`, `timing_tc_reg20`, and `timing_tc_reg21` so control helpers can update individual bits without rereading every time. Current mode, crop, control values, and runtime PM state are volatile. Hardware state is restored on power-on through global initialization and on stream-on through the mode table and control replay. There is no persistent calibration or nvmem export.

## Dependencies and Integration Points

The driver integrates with V4L2 subdev and stream helpers, media entity pads, device-tree endpoint parsing, regulator bulk APIs, GPIO descriptors, runtime PM, and the legacy sensor clock helper. It matches `ovti,ov5645` and I2C ID `ov5645`. It uses modern pad-level `.enable_streams` and `.disable_streams` while retaining `.s_stream = v4l2_subdev_s_stream_helper`.

## Risks and Edge Cases

The driver requires both enable and reset GPIOs; boards that omit either will fail probe. Endpoint validation requires CSI-2 but does not deeply validate lane count or link frequencies against the mode table. The mode-control relationship uses the mode's `link_freq` as an index into the integer menu, so table consistency is critical. Cached register values must match hardware after global initialization and probe reads; failed cache initialization aborts probe. Controls are ignored while suspended and depend on replay at stream-on.

## Test Signals

Tests should validate probe with correct and incorrect xclk tolerance, missing GPIOs, CSI-2 endpoint parsing, chip ID mismatch handling, `media-ctl` topology, `v4l2-compliance`, stream-on/off for all modes, pixel-rate/link-frequency control updates after `set_fmt`, and cached flip/AEC/AGC behavior across runtime suspend. Real capture tests should verify UYVY ordering, saturation changes, test pattern output, and autosuspend after stream-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov5645.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov5647.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov5647.c

## Purpose

`ov5647.c` is a V4L2 I2C sub-device driver for OmniVision OV5647 raw Bayer sensors. It targets device-tree described MIPI CSI-2 hardware, supports multiple 10-bit raw modes from VGA through full 2592x1944 resolution, exposes crop/native-size metadata, handles mode-dependent link frequencies and pixel rates, and supports common sensor controls such as exposure, gain, blanking, flips, AWB/AGC/AEC, and test patterns.

## Important APIs, Types, and Functions

The primary state is `struct ov5647`, containing the V4L2 subdev, CCI regmap, media pad, xclk, optional powerdown GPIO, regulators, non-continuous-clock flag, control handler, current mode, and pointers to key controls. Each `struct ov5647_mode` holds the media bus format, crop rectangle, pixel rate, link-frequency index, HTS/VTS, and register list.

Register access uses CCI/regmap helpers. `ov5647_set_virtual_channel()` writes the CSI-2 virtual-channel bits. `ov5647_set_mode()` writes common registers, the selected mode sequence, virtual channel zero, and ensures the device leaves software standby. `ov5647_stream_stop()` gates the MIPI clock lane, requests frame-off behavior, and disables pad output. Runtime PM callbacks are `ov5647_power_on()` and `ov5647_power_off()`.

Pad operations include `ov5647_enum_mbus_code()`, `ov5647_enum_frame_size()`, `ov5647_get_pad_fmt()`, `ov5647_set_pad_fmt()`, and `ov5647_get_selection()`. Stream operations use pad-level `ov5647_enable_streams()` and `ov5647_disable_streams()` with the subdev stream helper. Controls are initialized by `ov5647_init_controls()` and applied by `ov5647_s_ctrl()`. Probe support includes `ov5647_parse_dt()`, `ov5647_configure_regulators()`, and `ov5647_detect()`.

## Control Flow

Probe parses the endpoint, records whether the CSI-2 clock is non-continuous, obtains a 25 MHz xclk, requests optional `pwdn`, obtains regulators, sets the default VGA mode, initializes the subdev, creates controls, initializes the media entity, initializes a 16-bit CCI regmap, powers the device, detects chip ID `0x5647`, finalizes subdev state, enables runtime PM, registers the async sensor, and idles the device.

Power-on enables regulators, deasserts powerdown, waits the datasheet-required 20 ms, enables xclk, enables sensor output pads, and stops streaming to place MIPI lanes in LP-11. Power-off disables output pads, enters software standby, disables xclk, asserts powerdown, and disables regulators.

Stream-on resumes runtime PM, writes common and mode-specific registers, replays controls, configures MIPI control according to the non-continuous-clock endpoint flag, clears frame-off, and enables pad output. Stream-off calls `ov5647_stream_stop()` and drops the runtime PM reference.

Format setting chooses the nearest mode, updates active mode and controls for pixel rate, hblank, vblank, exposure, and link frequency, and returns a media bus code derived from the current hflip/vflip values. This dynamic Bayer-code mapping is important: the sensor reports a different Bayer order when flips are active. Selection queries expose active crop, native size, default crop, and crop bounds.

## State and Persistence Behavior

The current mode pointer, control values, non-continuous-clock flag, and runtime PM state are volatile. The driver stores no persistent calibration. Controls set while powered off remain in the V4L2 handler and are replayed on stream-on. Link frequency and pixel rate are updated when the active mode changes. The default state is 640x480 raw 10-bit full-FOV binned/subsampled mode.

## Dependencies and Integration Points

The driver integrates with V4L2 subdev, media controller, V4L2 event subscription, fwnode endpoint parsing, CCI/regmap, runtime PM, clocks, GPIOs, and regulator bulk APIs. It matches `ovti,ov5647` and I2C ID `ov5647`. With `CONFIG_VIDEO_ADV_DEBUG`, it exposes debug register get/set callbacks.

## Risks and Edge Cases

Probe enforces exactly 25 MHz xclk but does not reject missing regulators after `ov5647_configure_regulators()` logs an error, so downstream failures may surface later. Dynamic Bayer code reporting depends on control values, so userspace and bridge drivers must re-check format after flips. Stream-on failure after runtime resume must release PM; the implementation does so only on the failure path before a successful stream. The MIPI LP-11 coaxing sequence is hardware-sensitive. The debug register callbacks mask the register address to 8 bits despite 16-bit register definitions, so advanced debug access is limited.

## Test Signals

Validation should cover endpoint parsing with continuous and non-continuous clock flags, exact 25 MHz clock enforcement, chip ID detection, `media-ctl` crop/native-size reporting, all four supported modes, link-frequency and pixel-rate updates, flip-dependent media bus code changes, blanking/exposure range updates, stream-on/off under runtime PM, and test-pattern/AWB/AGC/AEC controls. `v4l2-compliance` and real raw capture tests are important for Bayer order and mode timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov5647.c -->
