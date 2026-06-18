# subset-b-004100 research

Grouped research for OmniVision V4L2 I2C sensor drivers under `sources/distributed-fs/ceph-client/drivers/media/i2c/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov7670.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov7670.c

## Purpose

`ov7670.c` is a V4L2 subdevice driver for OmniVision OV7670 and OV7675 parallel camera sensors. It exposes a single source pad, media-bus format negotiation, frame size and frame interval enumeration, legacy subdev power operations, and a set of image controls. The driver handles board-specific quirks through platform data or firmware nodes, including minimum supported window size, SMBus versus raw I2C register access, external clock speed, PLL bypass, horizontal blanking pixel-clock suppression, reset GPIO, powerdown GPIO, and media bus signal polarity.

## Important APIs, Types, And Functions

The central runtime object is `struct ov7670_info`, which embeds `struct v4l2_subdev`, one source `media_pad`, a `v4l2_ctrl_handler`, cached active `v4l2_mbus_framefmt`, current color format (`struct ov7670_format_struct`), current window (`struct ov7670_win_size`), optional `xclk`, GPIOs, clock-divider state, bus flags, and device-specific operations. `struct ov7670_devtype` selects OV7670 versus OV7675 window tables and frame-rate callbacks.

Low-level register access is split between `ov7670_read_smbus()`/`ov7670_write_smbus()` and `ov7670_read_i2c()`/`ov7670_write_i2c()`, selected by `info->use_smbus`. `ov7670_write_array()` applies sentinel-terminated register tables. `ov7670_detect()` resets/default-initializes the chip and validates manufacturer ID `0x7f/0xa2` and product ID `0x76/0x73`.

Format and timing are handled by `ov7670_try_fmt_internal()`, `ov7670_set_fmt()`, `ov7670_get_fmt()`, `ov7670_apply_fmt()`, and `ov7670_set_hw()`. Supported bus formats are YUYV, RGB444, RGB565, and 8-bit Bayer. OV7670 supports VGA, CIF, QVGA, and QCIF windows; OV7675 currently exposes only VGA. Frame-rate callbacks are either legacy divider logic (`ov7670_set_framerate_legacy()`) or OV7675 PLL-aware logic (`ov7675_set_framerate()`).

Control handling is in `ov7670_s_ctrl()` and `ov7670_g_volatile_ctrl()`. It implements brightness, contrast, saturation/hue through color-matrix rotation, H/V flip, auto/manual gain, auto/manual exposure, and sensor test patterns. Debug register access is compiled under `CONFIG_VIDEO_ADV_DEBUG`.

## Control Flow

Probe allocates `ov7670_info`, initializes the I2C subdev, parses DT or platform data, obtains optional clock and GPIOs, powers the sensor, validates clock range if an external clock is present, detects the chip, initializes default format/window/framerate, creates controls and clusters, initializes the media entity, registers the async subdev, and powers the device back off. The power-on sequence enables the clock, releases powerdown, pulses reset, then waits for the sensor. `s_power(1)` restores default registers, active format, OV7675 frame-rate state, and controls; `s_power(0)` disables the clock and asserts powerdown.

Active format changes first normalize the requested media-bus code and dimensions, cache the resulting format/window in `info`, and then write hardware only if `info->on` is true. `ov7670_apply_fmt()` writes COM7 absolutely, configures COM10 bus polarity and PCLK blanking behavior, writes the selected format table, programs the sensor crop/window registers, writes any window-specific scaling table, and finally restores the cached clock divider. Frame interval changes also update cached divider state first and defer hardware writes while powered off.

## State And Persistence

Persistent driver state is in memory only. The active `format`, `fmt`, `wsize`, `clkrc`, control values, power `on` flag, and board/fwnode flags are cached in `struct ov7670_info`. Register defaults are not persistent across power loss, so `ov7670_s_power()` and format/framerate application are responsible for replaying state after power-up. Try formats live in the V4L2 subdev state, while active formats are copied into `info->format`.

## Dependencies And Integration Points

The driver integrates with the Linux media controller, V4L2 subdev API, V4L2 controls/events, V4L2 fwnode endpoint parsing, I2C/SMBus, GPIO descriptors, and optional clocks. Device-tree integration supports `ovti,ov7670`; I2C ID matching also exposes `"ov7670"` and `"ov7675"`. Platform data comes from `<media/i2c/ov7670.h>`. The endpoint must describe a parallel media bus for DT probing.

## Risks And Edge Cases

Several register tables use vendor "magic" values and empirically chosen window coordinates. COM7 is written absolutely because read-modify-write is unsafe, so format tables must keep COM7 as their first entry. SMBus access is explicitly noted as unreliable on some hardware. The legacy `s_power` model lacks runtime PM reference counting and relies on the host bridge calling power operations correctly. `ov7670_s_power()` unconditionally calls `ov7675_apply_framerate()` even for OV7670 devdata, which currently writes common clock/PLL registers but is a coupling risk. Hue math uses a coarse sine lookup. Control setters perform multiple register writes without transaction rollback. DT matching only lists `ovti,ov7670`, so OV7675 DT users would rely on I2C IDs or need an additional compatible.

## Test Signals

Useful validation includes probe success with expected chip ID logs, async subdev registration, media graph showing one camera-sensor source pad, `v4l2-ctl --list-subdev-mbus-codes`, frame-size and frame-interval enumeration for configured minimum dimensions, format changes across YUYV/RGB/Bayer modes, power-cycle restoration of format and controls, test-pattern output, H/V flip behavior, auto/manual gain and exposure transitions, and DT/platform-data coverage for bus polarity, PCLK blanking, SMBus mode, GPIOs, and external clock frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov7670.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov772x.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov772x.c

## Purpose

`ov772x.c` is a V4L2 subdevice driver for OV7720 and OV7725 parallel/BT.656 image sensors. It replaced older soc-camera style assumptions with media-controller subdev registration, regmap/SCCB register access, fwnode endpoint parsing, and explicit controls. The driver supports VGA and QVGA windows, multiple YUV/RGB media-bus formats, 10-bit Bayer output, selectable frame intervals from 5 to 60 fps, color-bar test pattern, image flips, and band-stop filter control.

## Important APIs, Types, And Functions

`struct ov772x_priv` is the main state container. It embeds `v4l2_subdev`, `v4l2_ctrl_handler`, clock, SCCB regmap, optional platform data (`struct ov772x_camera_info`), powerdown/reset GPIOs, active color format and window pointers, flip/test/filter controls, cached fps, `mutex lock`, `power_count`, `streaming`, media pad, and bus type.

`struct ov772x_color_format` maps media-bus codes to DSP and COM register values. `struct ov772x_win_size` describes VGA/QVGA crop and output geometry. `ov772x_reset()` issues SCCB reset and soft sleep. `ov772x_select_params()` chooses a supported format/window; `ov772x_set_params()` performs the hardware reconfiguration after reset by programming crop/output registers, DSP format registers, COM3 flip/swap/test bits, COM7 resolution/output mode, pixel clock/framerate, and optional band filter. `ov772x_set_frame_rate()` derives CLKRC and COM4 PLL settings by approximating the desired pixel clock from input clock, format bytes per pixel, window blanking size, and target fps.

V4L2 operations include `ov772x_s_stream()`, `ov772x_get_fmt()`, `ov772x_set_fmt()`, `ov772x_get_selection()`, frame interval get/set/enumeration, and media-bus code enumeration. Control operations are implemented by `ov772x_s_ctrl()`. `ov772x_video_probe()` powers the device, reads PID/VER and manufacturer IDs, identifies OV7720 or OV7725, sets controls up, and powers the sensor off.

## Control Flow

Probe requires either DT or platform data, allocates state, initializes an SCCB regmap with 8-bit addresses/values, initializes the subdev and controls, obtains the input clock and optional powerdown GPIO, parses the endpoint as parallel or BT.656, probes the powered sensor, initializes one source pad, seeds default YUYV/VGA/15 fps state, and registers the async subdev.

Power is controlled through `ov772x_s_power()` and a guarded `power_count`. On the first power-on transition, the driver enables the clock, releases powerdown, temporarily requests and toggles the reset GPIO, then restores the cached active format, frame rate, and controls through `ov772x_set_params()`. On the last power-off transition, it disables the clock and asserts powerdown. The mutex protects both power and streaming state.

Streaming is separate from power. `ov772x_s_stream()` toggles BT.656 mode in COM7 when needed and clears or sets `SOFT_SLEEP_MODE` in COM2. It refuses redundant transitions. Active format and frame-interval changes are rejected with `-EBUSY` while streaming; otherwise they update cached state and apply to hardware only when powered.

## State And Persistence

The driver maintains cached active state in `cfmt`, `win`, `fps`, `test_pattern`, control values, `power_count`, `streaming`, and `bus_type`. There is no disk persistence. Register state is reconstructed after resets and power transitions by replaying cached format, rate, platform edge-control settings, flip state, test-pattern state, and band-filter control. `power_count` is intentionally constrained with warnings for negative or duplicate calls.

## Dependencies And Integration Points

The driver depends on V4L2 subdev, media entity, V4L2 controls/events, fwnode endpoint parsing, regmap SCCB, common image size constants, clocks, GPIO descriptors, and optional platform data from `<media/i2c/ov772x.h>`. Firmware compatibles are `ovti,ov7725` and `ovti,ov7720`. Endpoint parsing supports historical DTs without explicit `bus-type` by defaulting to parallel and retrying as BT.656 if parsing fails.

## Risks And Edge Cases

The reset GPIO is requested temporarily during power-on because some boards share it, which is fragile and depends on board wiring. `ov772x_parse_dt()` retry behavior can mask malformed endpoints. Frame-rate selection approximates pixel clock and may silently choose the nearest supported rate rather than exact timing. The driver relies on `clk_get()` rather than devm clock helpers and must release resources manually. `ov772x_set_params()` resets hardware on reconfiguration failure, which may leave the device in soft sleep until a later restore. Some formats use comments noting uncertain raw output behavior, especially RAW8 versus RAW10.

## Test Signals

Tests should verify PID detection for both OV7720 and OV7725, endpoint parsing for parallel and BT.656, async registration, media graph source-pad setup, all advertised media-bus codes, VGA/QVGA format negotiation, stream start/stop sleep-bit behavior, `-EBUSY` on format/rate changes while streaming, frame interval approximation across 5/10/15/20/30/60 fps, flip controls with and without platform-data inversion flags, band-stop filter programming, color-bar test pattern after a power cycle, and resource cleanup on failed probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov772x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov7740.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov7740.c

## Purpose

`ov7740.c` is a V4L2 subdevice driver for the OmniVision OV7740 VGA sensor. It exposes a single source pad with fixed VGA frame size, fixed 60 fps frame interval, YUYV and 8-bit Bayer media-bus formats, runtime-PM-managed streaming, and image controls for white balance, gain, exposure, brightness, contrast, saturation, and flips. The implementation is compact because the driver supports only one sensor size and writes one VGA register sequence.

## Important APIs, Types, And Functions

`struct ov7740` embeds the V4L2 subdev, media pad, cached active `v4l2_mbus_framefmt`, current pixel format, current frame size, SCCB regmap, sensor clock, control handler, grouped V4L2 controls, mutex, reset GPIO, and powerdown GPIO. `struct ov7740_pixfmt` maps a media-bus code to a small register sequence. `struct ov7740_framesize` maps the single VGA size to a larger tuning table.

Register access goes through regmap initialized by `devm_regmap_init_sccb()`. `ov7740_set_power()` enables/disables `xvclk`, drives powerdown, and toggles reset. `ov7740_detect()` validates manufacturer ID `0x7f/0xa2`, product high byte `0x77`, and product low byte `0x40`, `0x41`, or `0x42`.

Controls are handled by `ov7740_set_ctrl()` and `ov7740_get_volatile_ctrl()`. White balance toggles AWB and AWB gain bits and writes manual red/blue gains when AWB is disabled. Gain and exposure are split across low/high registers and disable automatic AGC/AEC when manual values are written. Brightness uses sign/magnitude register handling and disables AEC/AGC. Saturation writes U and V saturation registers together.

## Control Flow

Probe allocates state, obtains `xvclk`, reads reset and powerdown GPIOs, initializes SCCB regmap, initializes the subdev and source pad, powers the sensor, enables runtime PM as active, detects the sensor, initializes controls, seeds the default YUYV/VGA format, registers the async subdev, and then idles the runtime-PM device.

Format negotiation is simple. `ov7740_try_fmt_internal()` selects one of two media-bus codes and the only VGA frame size, fills colorspace and field, and updates the cached `ov7740->format`. `ov7740_set_fmt()` handles try state separately and for active state updates `fmt` and `frmsize` under the mutex. It does not write hardware immediately; hardware is programmed at stream start.

`ov7740_set_stream(1)` locks the mutex, resumes runtime PM, writes selected format registers and selected frame-size registers through `ov7740_start_streaming()`, then replays controls with `__v4l2_ctrl_handler_setup()`. Stream disable simply drops the runtime-PM reference. Runtime suspend and resume call `ov7740_set_power(0/1)`.

## State And Persistence

Persistent runtime state is cached in memory: active format, selected format table, frame-size table, V4L2 control values, and GPIO/clock handles. Register contents are not assumed to survive suspend; stream start writes format and VGA tables, then control setup restores user-visible control state. Control writes are skipped if `pm_runtime_get_if_in_use()` reports the device inactive, so inactive control changes are cached by the V4L2 framework and applied later.

## Dependencies And Integration Points

The driver integrates with V4L2 subdev/pad APIs, V4L2 controls/events, media entities, runtime PM, SCCB regmap, clocks via `devm_v4l2_sensor_clk_get()`, GPIO descriptors, I2C, and image-size constants. Device-tree matching uses `ovti,ov7740`; I2C ID matching uses `"ov7740"`. Unlike the other parallel drivers in this subset, this file does not parse endpoint bus flags; it assumes the board integration and receiver agree on the parallel bus details.

## Risks And Edge Cases

Only VGA and 60 fps are supported, so applications requesting other sizes/rates get coerced or rejected. `ov7740_set_power(0)` drives the powerdown GPIO low, the same visible value used in power-on, which may be intentional for this board polarity but deserves hardware validation. Probe error handling and remove both destroy/free mutex and controls in overlapping ways; the remove path calls `mutex_destroy()` and later `ov7740_free_controls()`, which also destroys the mutex. Brightness disables AEC/AGC without checking intermediate regmap errors. Runtime-PM-only control application means tests must verify control replay on next stream start.

## Test Signals

Validation should cover successful chip ID detection for accepted PIDL variants, runtime PM transitions during stream enable/disable, YUYV and SBGGR8 format negotiation, fixed VGA frame-size enumeration, fixed 1/60 interval enumeration and get/set behavior, control replay after setting controls while inactive, manual and automatic gain/exposure clusters, AWB/manual red-blue balance, brightness sign handling, flip bits, and failure cleanup when clock, GPIO, regmap, media-entity, control, detect, or async registration steps fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov7740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov8856.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov8856.c

## Purpose

`ov8856.c` is a V4L2 subdevice sensor driver for the OmniVision OV8856 MIPI CSI-2 RAW10 camera. It supports ACPI and device-tree systems, two-lane and four-lane CSI-2 configurations, lane-specific link-frequency tables, multiple full-resolution and binned/cropped modes, two Bayer order media-bus codes, runtime PM, regulators, reset GPIO, and controls for link frequency, pixel rate, blanking, exposure, analogue gain, digital gain, test pattern, and flips.

## Important APIs, Types, And Functions

`struct ov8856` is the primary state object. It stores the device pointer, subdev, media pad, control handler, `xvclk`, reset GPIO, three regulators, link-frequency/pixel-rate/vblank/hblank/exposure controls, current mode, current media-bus code index, mutex, lane count, lane configuration pointer, mode count, and an `identified` flag.

Mode description is split across `struct ov8856_lane_cfg`, `struct ov8856_mode`, `struct ov8856_link_freq_config`, and `struct ov8856_reg_list`. Two-lane mode tables include 3280x2464 and 1640x1232. Four-lane mode tables include 3280x2464, 1640x1232, 3264x2448, and 1632x1224. `bayer_offset_configs[]` adjusts register `0x3813` for SBGGR10 versus SGRBG10.

Register I/O uses explicit big-endian I2C helpers: `ov8856_read_reg()`, `ov8856_write_reg()`, and `ov8856_write_reg_list()`. `ov8856_identify_module()` reads the 24-bit chip ID and caches success. `ov8856_get_hwcfg()` obtains the clock, reset/regulators for non-ACPI firmware, parses the CSI-2 endpoint, validates 2 or 4 lanes, selects the lane config, counts modes, and verifies that all required link frequencies are present in firmware.

## Control Flow

Probe allocates state, runs hardware configuration parsing, initializes the I2C subdev, optionally powers and identifies the sensor if ACPI reports D0, initializes mutex and default mode/media-bus index, creates controls, sets subdev internal ops and media entity, registers the async sensor subdev, enables runtime PM, and idles the device.

Format setting chooses the nearest lane-supported mode with `v4l2_find_nearest_size()`, updates width/height/code/field, and for active formats updates `cur_mode`, link frequency, pixel rate, vblank limits/default, and fixed hblank. The media-bus code is constrained to SBGGR10 or SGRBG10 and falls back to the mode default if the requested code is unsupported.

Streaming resumes runtime PM, identifies the module if needed, writes the lane/link-frequency PLL register list, writes the selected mode register list, writes the selected Bayer-offset list, replays controls, and then writes `OV8856_MODE_STREAMING` to mode select. Stream disable writes standby and drops runtime PM. Runtime PM power-on enables the clock, asserts reset, enables regulators, releases reset, and waits; power-off asserts reset, disables regulators, and disables the clock. ACPI firmware nodes bypass explicit power sequencing.

## State And Persistence

The driver keeps active mode and media-bus code in `cur_mode` and `cur_mbus_index`, while active control values live in the V4L2 control framework. Hardware registers are replayed at stream start and not assumed to persist across suspend. `identified` prevents repeated chip-ID reads after a successful identification. Vblank updates dynamically alter exposure range so the maximum exposure stays below VTS by the defined margin.

## Dependencies And Integration Points

The driver depends on V4L2 subdev, fwnode endpoint parsing, V4L2 controls including fwnode properties, media entity link validation, I2C, runtime PM, regulators, clocks, GPIO descriptors, ACPI matching (`OVTI8856`), and OF matching (`ovti,ov8856`). The CSI-2 endpoint must provide either 2 or 4 data lanes and the exact link frequencies required by the selected lane configuration. The driver registers through `v4l2_async_register_subdev_sensor()`.

## Risks And Edge Cases

Firmware link-frequency validation is strict; missing one of the lane config frequencies aborts probe. The driver warns but does not fail on an unsupported external clock rate. `ov8856_get_hwcfg()` logs `cur_mode->data_lanes` before `cur_mode` is initialized, which is a latent null-pointer risk if that debug line is evaluated. Flip controls touch multiple format and option registers with separate reads/writes and no rollback. ACPI power sequencing is intentionally a no-op, so correctness depends on platform firmware keeping the sensor powered as expected. Large mode tables are opaque vendor settings, making regressions hard to review without hardware.

## Test Signals

Tests should validate DT and ACPI probe paths, 2-lane and 4-lane endpoint parsing, strict link-frequency matching, regulator/clock/reset sequencing, chip ID detection, media-bus code enumeration for SBGGR10 and SGRBG10, mode enumeration per lane count, nearest-size selection, link-frequency and pixel-rate control updates, hblank/vblank/exposure range adjustment, stream-on register write order, standby on stream-off, test pattern, analogue/digital gain, exposure fractional shift, H/V flip output orientation, and suspend/resume cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov8856.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov8858.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov8858.c

## Purpose

`ov8858.c` is a V4L2 subdevice driver for the OmniVision OV8858 MIPI CSI-2 RAW10 sensor. It supports 2-lane and 4-lane operation, two image modes (3264x2448 and 1632x1224), runtime PM with autosuspend, sensor revision detection, revision/lane-specific global register tables, per-mode register tables, and controls for link frequency, pixel rate, hblank, vblank, exposure, analogue gain, digital gain, and test pattern.

## Important APIs, Types, And Functions

`struct ov8858` stores clock, reset and powerdown GPIOs, regulators, subdev, source pad, control handler, exposure/hblank/vblank controls, selected `global_regs`, and CSI-2 lane count. `struct ov8858_mode` describes dimensions, default HTS/VTS/exposure, and separate register lists for 2-lane and 4-lane variants. `struct regval` tables use `REG_NULL` sentinels.

Register sizes are encoded in register constants by `OV8858_REG_8BIT()`, `OV8858_REG_16BIT()`, and `OV8858_REG_24BIT()`. `ov8858_write()` serializes a 16-bit register address and big-endian value of encoded length, optionally short-circuiting on a caller-provided error pointer. `ov8858_write_array()` applies sentinel-terminated 8-bit register tables. `ov8858_read()` performs a two-message I2C read. `ov8858_check_sensor_id()` validates the 24-bit chip ID, reads revision/sub-ID, and selects the correct global register table: R2A supports 2 and 4 lanes; R1A is allowed only for 2 lanes with a warning.

## Control Flow

Probe obtains `xvclk`, optional reset and powerdown GPIOs, initializes the I2C subdev, gets regulators, parses the CSI-2 endpoint for 2 or 4 lanes, initializes controls, creates the media entity, finalizes subdev state, powers the device, enables runtime PM, validates sensor ID/revision, enables autosuspend, registers the async sensor subdev, and drops the autosuspend reference.

The active subdev state owns the selected format. `ov8858_init_state()` seeds the default full-resolution format. `ov8858_set_fmt()` coerces the media-bus code to SBGGR10, picks the nearest supported mode, writes format into subdev state, and for active formats adjusts fixed hblank and vblank ranges. `ov8858_s_stream()` locks and obtains the active state, resumes runtime PM for stream-on, calls `ov8858_start_stream()`, and on stream-off writes software standby and releases runtime PM with autosuspend.

`ov8858_start_stream()` writes revision/lane-specific global registers, selects the per-mode register list based on current format dimensions and lane count, waits for PLL stabilization, replays controls, enables streaming, and waits 10 ms before returning. Control writes use the shared control/state mutex, update exposure range when vblank changes, skip hardware writes while suspended, and program exposure, analogue gain, packed digital gain, VTS, or test-pattern registers.

## State And Persistence

The active mode is represented by the V4L2 subdev active state rather than a separate current-mode pointer. Control values are cached by the V4L2 framework and replayed during stream start. The selected global register table persists in memory after sensor revision detection. Runtime PM autosuspend powers the sensor down between use; stream start always rewrites global and mode tables, so sensor register contents do not need to persist.

## Dependencies And Integration Points

The driver uses V4L2 async sensor registration, subdev active state, controls, fwnode endpoint parsing, media entities, I2C, clocks via `devm_v4l2_sensor_clk_get()`, GPIO descriptors, regulator bulk APIs, runtime PM autosuspend, and OF matching for `ovti,ov8858`. The receiver side must consume RAW10 SBGGR data at the fixed 360 MHz link frequency and the lane count described in firmware.

## Risks And Edge Cases

Only SBGGR10 is exposed even though register tables may imply more sensor flexibility. Endpoint parsing validates lane count but not link-frequency arrays, so board descriptions can be incomplete without probe failure. R1A support is explicitly partial and limited to 2 lanes. `ov8858_enable_test_pattern()` writes the pattern number directly ORed with enable, unlike some sensors that shift pattern selection; this should be confirmed against the datasheet. Digital gain has custom bit packing across the two gain registers and is easy to regress. Probe error paths must balance runtime-PM references, explicit power-on, entity cleanup, and control cleanup.

## Test Signals

Validation should cover 2-lane and 4-lane DT endpoints, R2A global table selection, R1A two-lane warning and four-lane rejection, chip ID mismatch failure, media-bus code and frame-size enumeration, default subdev state initialization, format coercion and nearest mode selection, hblank/vblank/exposure limit updates, stream-on write order for global/mode/control/streaming registers, stream-off standby, autosuspend behavior, 24 MHz clock warning, regulator/GPIO sequencing, exposure fractional shift, packed digital gain, analogue gain, and all advertised test-pattern menu entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov8858.c -->
