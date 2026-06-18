# subset-b-004091 research

This grouped report covers the assigned Sony image-sensor V4L2 I2C drivers. Each section is wrapped with the reconciliation markers required for source-tree-aligned split output.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx319.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx319.c research

## Purpose

`imx319.c` is a Linux V4L2 subdevice driver for the Sony IMX319 camera sensor on I2C. It exposes the sensor as a single-source-pad media entity, supports ACPI discovery through `SONY319A`, validates a fixed 19.2 MHz input clock and CSI-2 link-frequency firmware data, programs large static register tables for supported image modes, and controls streaming through runtime PM.

## Important APIs, Types, and Data

The central state is `struct imx319`, which owns the `v4l2_subdev`, media pad, V4L2 controls, current mode pointer, firmware-derived hardware config, mutex, and an `identified` cache bit. Mode description is split between `struct imx319_reg`, `struct imx319_reg_list`, and `struct imx319_mode`. `supported_modes[]` includes full-resolution, cropped, and binned 10-bit Bayer modes from 3280x2464 down to 1280x720. `imx319_global_regs[]` holds sensor-wide tuning writes, and each mode table supplies timing, crop/binning, PLL, and output-size registers.

The driver uses direct I2C helpers instead of CCI regmap: `imx319_read_reg()` performs a two-message big-endian register read up to four bytes, `imx319_write_reg()` sends a two-byte register address plus up to four bytes of big-endian payload, and `imx319_write_regs()` iterates one-byte table writes with ratelimited diagnostics.

The V4L2 surface is implemented by `imx319_subdev_ops`: pad operations enumerate one dynamic Bayer code, enumerate exact frame sizes, get/set pad format, and video ops use `.s_stream = imx319_set_stream`. Internal `.open` initializes try format. Control ops route through `imx319_set_ctrl()`.

## Control Flow

Probe allocates state, initializes the mutex, acquires and verifies the 19.2 MHz sensor clock, initializes the I2C subdevice, optionally identifies the chip immediately when ACPI reports D0, parses the first fwnode endpoint with `v4l2_fwnode_endpoint_alloc_parse()`, validates the fixed link-frequency menu through `v4l2_link_freq_to_bitmap()`, sets the default mode to the largest supported mode, initializes controls, initializes the media entity pad, enables runtime PM, registers the async sensor subdevice, and idles the device.

Format setting is serialized by `imx319->mutex`. Active `set_fmt` clamps the requested dimensions to the nearest supported mode, updates `cur_mode`, recalculates read-only pixel rate, adjusts vertical blanking range/default, updates exposure max through the vblank control path, and fixes hblank to `llp - width`. The media bus code is computed by `imx319_get_format_code()` from current hflip/vflip controls, so flips modify reported Bayer order.

Streaming enable resumes runtime PM, calls `imx319_start_streaming()`, writes global settings, writes current mode registers, selects global digital gain mode, applies all current controls with `__v4l2_ctrl_handler_setup()`, and finally writes `IMX319_MODE_STREAMING`. Streaming disable writes standby and drops runtime PM. Flip controls are grabbed while streaming to prevent Bayer-order changes mid-stream.

## State, Persistence, and Dependencies

Persistent software state is limited to `cur_mode`, control values in the V4L2 handler, the `identified` flag, and endpoint-derived `link_freq_bitmap`. Hardware state is reconstructed on every stream start from static tables plus current controls, so no register cache is maintained. Runtime PM gates all register writes that come from controls: controls update software state while suspended and are replayed on the next stream start.

Dependencies include Linux I2C, runtime PM, ACPI, V4L2 subdev/media controller APIs, V4L2 fwnode endpoint parsing, sensor clock helpers, and unaligned big-endian helpers. Integration requires firmware to provide a CSI-2 endpoint with the expected link frequency and a 19.2 MHz input clock. There is no regulator or GPIO handling in this driver.

## Risks and Edge Cases

The mode tables are large opaque sensor-programming data; small transcription errors can silently affect timing or image quality. The endpoint parser only checks link frequency, not lane count, so platform data must still match the assumed four-lane pixel-rate calculation. `imx319_set_ctrl()` returns success without hardware writes when the device is suspended; this is intended, but correctness depends on handler replay before streaming. The chip-id read is cached after success; a later power-cycle identity failure will not be rechecked. Error paths during streaming correctly put runtime PM, but `imx319_stop_streaming()` return value is ignored on disable.

## Test Signals

Useful validation includes successful probe with `SONY319A`, correct rejection of non-19.2 MHz clocks or missing link frequency, `v4l2-ctl --list-subdev-mbus-codes` showing Bayer order changes with flips before streaming, enumerated frame sizes matching `supported_modes[]`, active format requests clamping to nearest mode, runtime PM suspend/resume around stream on/off, chip-id mismatch diagnostics, and visible test-pattern output for all menu entries. Exposure/vblank tests should verify that exposure max tracks `height + vblank - 18` and that control values survive suspend before streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx319.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx334.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx334.c research

## Purpose

`imx334.c` is a V4L2 subdevice driver for the Sony IMX334 CSI-2 image sensor. It supports device-tree probing via `sony,imx334`, uses the V4L2 CCI regmap helpers for register access, validates a 24 MHz input clock and a four-lane CSI-2 endpoint, exposes RAW10 and RAW12 Bayer formats, and supports four fixed image sizes from 3840x2160 down to 640x480.

## Important APIs, Types, and Data

`struct imx334` stores the device, CCI regmap, I2C client, subdevice, media pad, optional reset GPIO, input clock, controls, current vblank, current mode, link-frequency bitmap, and current media-bus code. `struct imx334_mode` captures dimensions, hblank/vblank limits, pixel clock, link-frequency menu index, and a mode-specific CCI register list. `common_mode_regs[]` supplies baseline sensor configuration, while `mode_3840x2160_regs[]`, `mode_1920x1080_regs[]`, `mode_1280x720_regs[]`, and `mode_640x480_regs[]` adjust crop/windowing and timing. `raw10_framefmt_regs[]` and `raw12_framefmt_regs[]` configure output bit depth.

The driver uses `cci_write()`, `cci_read()`, and `cci_multi_reg_write()` throughout. Control clustering joins exposure and analogue gain. The subdevice uses modern pad `.enable_streams` and `.disable_streams` operations, with `.s_stream = v4l2_subdev_s_stream_helper`.

## Control Flow

Probe initializes the CCI regmap, subdev, hardware config, powers on the sensor, detects chip ID from `IMX334_REG_ID`, chooses a default mode based on the first supported link frequency bit, initializes controls, creates the media pad, finalizes subdev state, enables runtime PM, registers the sensor asynchronously, and idles it.

`imx334_parse_hw_config()` acquires optional reset GPIO, clock, and endpoint data. It enforces `IMX334_INCLK_RATE` and exactly four CSI-2 data lanes, then converts firmware link frequencies to the driver's two-entry link-frequency bitmap. `imx334_init_state()` seeds the default active or try format and masks unsupported link-frequency menu entries.

Active format changes select the nearest supported size and validate the requested bus code through `imx334_get_format_code()`. If mode or code changed, `imx334_update_controls()` updates link frequency, read-only pixel rate, fixed hblank, vblank range/default, and current vblank. Streaming enable resumes runtime PM, writes common registers, writes mode registers, configures four-lane mode, programs RAW10/RAW12 format registers, replays controls, and writes streaming mode. Streaming disable writes standby and releases runtime PM.

## State, Persistence, and Dependencies

Software state is `cur_mode`, `cur_code`, `vblank`, and the V4L2 control handler. Hardware state is not cached; stream startup reconstructs sensor state from common/mode/frame-format tables plus current controls. Exposure and gain are written atomically under group hold by `imx334_update_exp_gain()`, which also writes `VMAX` when vblank changes.

Dependencies include V4L2 subdev active-state APIs, V4L2 fwnode endpoint parsing, CCI regmap, runtime PM, GPIO, clocks, media entity pads, and device-tree matching. The link between mode and bandwidth is explicit through `link_freq_idx`, pixel clock, and mode-specific timing registers.

## Risks and Edge Cases

The default mode is selected by `supported_modes[__ffs(link_freq_bitmap)]`; this assumes the order of `supported_modes[]` lines up with link-frequency bit positions, which is true for the current table but fragile if modes are rearranged. `imx334_set_ctrl()` performs several test-pattern CCI writes with `NULL` error accumulation and returns success, so partial test-pattern programming failures can be hidden. The code defines an eight-lane lane-mode constant but only accepts four lanes. The power-on reset comment explicitly warns that reset polarity handling is historically confused and should not be copied. Stream-off errors are reported but runtime PM is still put.

## Test Signals

Probe tests should cover missing endpoints, wrong clock rate, non-four-lane endpoints, unsupported link frequencies, and chip-id mismatch. Media tests should enumerate RAW12 and RAW10 codes, all four sizes, and correct clamping to nearest mode. Streaming tests should verify common plus mode registers are written before mode select, RAW10/RAW12 register differences are applied, link frequency and pixel-rate controls update with mode, exposure max tracks `vblank + height - 5`, grouped exposure/gain writes release hold, and test-pattern enable/disable produces expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx334.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx335.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx335.c research

## Purpose

`imx335.c` drives the Sony IMX335 image sensor as a V4L2 CSI-2 subdevice. It supports device-tree match `sony,imx335`, CCI regmap register access, two scan modes, selectable RAW10/RAW12 output, two-lane or four-lane CSI-2 wiring, regulator-backed power sequencing, vertical flip with mode-specific correction registers, crop selection reporting, and runtime PM controlled streaming.

## Important APIs, Types, and Data

`struct imx335` owns device and I2C identity, the CCI regmap, clock, reset GPIO, three supplies (`avdd`, `ovdd`, `dvdd`), subdev/pad, controls, current vblank, lane mode, current mode, link-frequency bitmap, and current media-bus code. `struct imx335_mode` includes scan mode (`IMX335_ALL_PIXEL` or `IMX335_2_2_BINNING`), dimensions, timing, pixel clock, mode registers, and separate vflip-normal/vflip-inverted register lists.

The main static data sets are `mode_2592x1944_regs[]`, `mode_1312x972_regs[]`, `imx335_common_regs[]`, mode-specific vertical-flip tables, PLL/MIPI tables for 1188 Mbps and 891 Mbps lane rates, and `supported_modes[]`. `imx335_native_area` and `imx335_active_area` provide selection API bounds.

## Control Flow

Probe initializes CCI, subdev, hardware config, powers on regulators/clock/reset, reads the chip ID, sets full-resolution RAW12 as default, initializes controls, initializes and finalizes media state, registers the async sensor, enables runtime PM, and idles the device.

Hardware config parsing collects reset GPIO, regulators, clock, and fwnode endpoint. It requires a 24 MHz input clock, accepts either two or four CSI-2 data lanes, maps lane count to the sensor `LANEMODE` register value, and validates firmware link frequencies against the driver's menu.

Format setting uses nearest-mode selection and updates `cur_mbus_code` if the requested code is RAW10 or RAW12. It writes the frame format into subdev state, updates crop state to account for binned modes by doubling crop dimensions, centers the crop within the native array, and for active formats updates link frequency, hblank, and vblank ranges before changing `cur_mode`. Selection get returns current crop, native size, and default/bounds active area.

Streaming enable resumes runtime PM, writes the selected PLL table, writes mode registers, writes common registers, configures frame bit depth through `imx335_set_framefmt()`, sets the selected lane mode, replays controls, starts streaming, then waits for stabilization. Streaming disable writes standby and puts runtime PM.

## State, Persistence, and Dependencies

State persists in V4L2 controls, active subdev state, `cur_mode`, `cur_mbus_code`, `lane_mode`, and `vblank`. Hardware state is rebuilt on each stream start. Runtime control writes are skipped while suspended and replayed on stream start. Exposure and gain use group hold in `imx335_update_exp_gain()`; vblank updates also modify exposure range based on a scan-mode-dependent shutter minimum.

Dependencies include CCI regmap, V4L2 subdev state and selection APIs, fwnode endpoint parsing, regulators, GPIO, clocks, runtime PM, and device-tree match. It also consumes firmware properties through `v4l2_fwnode_device_parse()` / `v4l2_ctrl_new_fwnode_properties()`.

## Risks and Edge Cases

`imx335_update_controls()` always selects `__ffs(link_freq_bitmap)` rather than a per-mode link-frequency index, so if firmware exposes multiple supported frequencies the first bit governs all modes. RAW12 output in binned mode forces 10-bit AD conversion while keeping output width handling separate, a subtle sensor-specific rule. Vertical flip depends on opaque undocumented register tables; missing a table update can corrupt image geometry. The chip ID value is `0x00`, so detection relies on a register whose default-looking value may be less discriminating than larger IDs. Stream-start writes PLL, mode, common, frame format, lanes, and controls; ordering regressions are likely visible as no-stream or bad frames.

## Test Signals

Tests should validate regulator and reset sequencing, both accepted lane counts, link-frequency bitmap rejection, wrong clock rejection, chip-id mismatch, RAW10/RAW12 enumeration, crop state for full and binned modes, exposure max formulas for all-pixel and binned modes, vflip register programming in both modes, test-pattern enable/disable side effects on black level and WRJ/open registers, and runtime PM balance across stream on/off and failed stream setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx335.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx355.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx355.c research

## Purpose

`imx355.c` is a V4L2 I2C subdevice driver for the Sony IMX355 camera sensor. It supports ACPI match `SONY355A` and OF match `sony,imx355`, validates a 19.2 MHz clock, requires four CSI-2 data lanes and a fixed 360 MHz link frequency, manages reset GPIO and three regulators, provides many 10-bit Bayer modes from 3280x2464 down to 820x616, and controls streaming through runtime PM.

## Important APIs, Types, and Data

The main state is `struct imx355`, containing device and clock handles, subdev/pad, controls, current mode, firmware hardware config, mutex, reset GPIO, and regulator bulk data. Mode structures mirror `imx319`: `struct imx355_reg`, `struct imx355_reg_list`, and `struct imx355_mode`. `imx355_global_regs[]` supplies common tuning. `supported_modes[]` references many mode tables covering full readout, slight width variants, cropped 1080p-style modes, binned 1640/1300/1296/1280 sizes, and 820x616.

Register I/O is direct I2C with 16-bit big-endian register addresses and up to four-byte values. V4L2 integration uses old-style `.s_stream`, pad format ops, media entity link validation, event subscription support, and an internal `.open` handler. Controls include link frequency, pixel rate, vblank, read-only hblank, exposure, hflip/vflip, analogue gain, digital gain, test pattern, and fwnode-provided controls.

## Control Flow

Probe allocates and initializes the driver state, validates the external clock, gets regulators and optional reset GPIO, initializes the I2C subdevice, parses endpoint hardware config, powers on, identifies the chip, selects the largest mode, initializes controls, creates the media pad, enables runtime PM, registers the async sensor, and leaves the device idle.

Endpoint parsing requires a firmware node, a CSI-2 endpoint, exactly four lanes, and a link frequency matching the single menu item. Power-on enables the clock, enables regulators, waits, deasserts reset, and waits again. Power-off asserts reset, disables regulators, and disables the clock.

Active format setting is mutex-protected and clamps to nearest mode. It updates `cur_mode`, recomputes pixel rate from fixed link frequency and four lanes divided by 10 bits per sample, updates vblank and exposure constraints, and fixes hblank. Media bus code is computed from current hflip/vflip state using the Bayer-order lookup.

Streaming enable resumes runtime PM, writes global registers, writes current mode registers, enables global digital gain mode, replays controls, and writes streaming mode. Disable writes standby and releases runtime PM. Flip controls are grabbed while streaming.

## State, Persistence, and Dependencies

Software state persists in `cur_mode`, controls, endpoint-derived link-frequency bitmap, and runtime PM state. The driver reconstructs sensor registers on stream start rather than caching them. Control writes are skipped while suspended and replayed before streaming. Unlike `imx319`, chip identity is not cached and is checked during probe only, not on every stream start.

Dependencies include direct Linux I2C helpers, V4L2 subdev/media/event/fwnode APIs, ACPI and OF matching, sensor clock helper, GPIO, regulators, runtime PM, and unaligned big-endian helpers.

## Risks and Edge Cases

The large mode table contains many near-duplicate widths and crops; nearest-size behavior can select subtly different sensor windows than a caller expects. The driver assumes four CSI-2 lanes in pixel-rate math and endpoint validation, so board descriptions must be exact. `imx355_stop_streaming()` return is ignored during disable. Control changes while suspended only update V4L2 state; successful replay depends on `__v4l2_ctrl_handler_setup()` ordering. The fwnode property controls are added after explicit controls, so control-handler sizing and error handling must remain correct if more controls are introduced.

## Test Signals

Test coverage should include ACPI and OF match probing, wrong clock rejection, missing regulators/GPIO tolerance, endpoint lane/link-frequency validation, chip-id mismatch, all supported frame-size enumeration, Bayer code changes from hflip/vflip before streaming, hblank/vblank/exposure range updates on mode changes, stream-on register order, runtime PM balance on stream failure, fwnode orientation/rotation controls, and visible test-pattern output. Power sequencing should be checked with reset and regulator timing on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx355.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx412.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx412.c research

## Purpose

`imx412.c` drives Sony IMX412 and compatible IMX577 sensors as a V4L2 I2C subdevice. It supports OF matches `sony,imx412` and `sony,imx577`, exposes a single 4056x3040 RAW10 mode, validates 24 MHz input clock, requires four CSI-2 lanes and a 600 MHz link frequency, handles reset/regulator/clock power sequencing, and implements exposure/gain/vblank controls around runtime-PM streaming.

## Important APIs, Types, and Data

`struct imx412` stores device, client, subdev, pad, reset GPIO, input clock, three regulators, controls, current vblank, current mode, and a mutex. `struct imx412_mode` captures the single mode's dimensions, media-bus code, hblank/vblank limits, pixel clock, link-frequency index, and register list. `mode_4056x3040_regs[]` is the complete mode programming table, including clock, crop/output size, PLL, timing, gain defaults, and sensor tuning registers. `supported_mode` wraps this table and fixed mode metadata.

Direct I2C helpers `imx412_read_reg()`, `imx412_write_reg()`, and `imx412_write_regs()` use 16-bit register addresses and up to four-byte big-endian values. The V4L2 API exposes one mbus code, one frame size, old-style `.s_stream`, `.get_fmt`, `.set_fmt`, and internal `.init_state`.

## Control Flow

Probe gets match data, initializes the subdev, parses hardware config, initializes the mutex, powers on the sensor, detects the chip ID (`0x0577`), selects the only supported mode, initializes controls, names the subdevice with the matched compatible data, creates the media pad, registers the async sensor, and enables runtime PM.

Hardware parsing obtains optional reset GPIO, the 24 MHz clock, three regulators, and CSI-2 endpoint data. It rejects non-four-lane endpoints and requires at least one firmware link frequency equal to 600 MHz. Power-on enables regulators, deasserts reset, enables the clock, and waits 10-12 ms for module startup; the longer delay is documented as needed by some Arducam IMX577 variants.

Format set always returns the single supported mode. Active format setting updates link frequency, hblank, and vblank ranges and assigns `cur_mode`. Streaming enable resumes runtime PM, writes all mode registers, replays controls, waits 7.4-8 ms, then writes streaming mode. Disable writes standby and puts runtime PM.

## State, Persistence, and Dependencies

Persistent software state is small: one mode pointer, current vblank, V4L2 controls, mutex, and power resources. Hardware state is rebuilt at stream start from the mode table and control replay. `imx412_update_exp_gain()` uses group hold to write LPFR, coarse integration time, and analogue gain together, then releases hold even on intermediate failure.

Dependencies include direct I2C transfers, V4L2 subdev/fwnode/media APIs, runtime PM, clocks, GPIO, regulators, and OF matching. Integration is intentionally narrow: a board must provide the expected 24 MHz clock, four CSI-2 lanes, and 600 MHz link frequency.

## Risks and Edge Cases

`imx412_set_ctrl()` handles vblank range changes even while suspended, but only the exposure control path writes hardware; changing analogue gain alone is part of the exposure/gain cluster and relies on clustered control behavior to invoke the right path. The default exposure control maximum uses `lpfr - 22`, so mode or vblank changes must keep the offset consistent with sensor requirements. The mode table is monolithic and opaque. Stream disable ignores the return value in the caller. Since only one mode and one code are exposed, applications asking for different sizes will silently receive 4056x3040.

## Test Signals

Tests should verify probe with both compatible strings, subdevice naming as `imx412` or `imx577`, rejection of wrong clock/lane/link-frequency configurations, regulator and reset sequencing, chip-id mismatch behavior, single-code and single-size enumeration, active and try format behavior, exposure range updates when vblank changes, grouped LPFR/exposure/gain writes, stream-on delay and mode-select order, and runtime PM cleanup on probe and stream failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx412.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx415.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/imx415.c research

## Purpose

`imx415.c` is a V4L2 subdevice driver for the Sony IMX415 CMOS image sensor. It supports OF match `sony,imx415`, CCI regmap access, fixed full-array 3864x2192 RAW10 output, two- or four-lane CSI-2 wiring, multiple lane-rate/input-clock combinations, regulator/reset/clock power sequencing, autosuspend runtime PM, hblank/vblank/exposure/gain/flip/test-pattern controls, and model identification through the sensor-info register.

## Important APIs, Types, and Data

`struct imx415` stores device, clock, selected pixel rate, regulators, reset GPIO, CCI regmap, selected clock-parameter table, subdev/pad, controls, current mode index, and number of data lanes. `struct imx415_clk_params` maps lane rate plus input clock to eleven INCK/clock registers. `supported_modes[]` maps supported lane rates to minimum HMAX values for two-lane and four-lane operation plus CSI timing register lists. `imx415_init_table[]` contains fixed setup and undocumented tuning registers. `link_freq_menu_items[]` exposes V4L2 link frequencies as half of sensor lane rates.

The V4L2 interface uses `.s_stream`, active subdev state locking, `.get_fmt = v4l2_subdev_get_fmt`, custom `.set_fmt`, selection get for crop bounds, and internal `.init_state`. Control handling is centralized in `imx415_s_ctrl()`.

## Control Flow

Probe parses hardware first, initializes CCI regmap, manually powers on the device, wakes the sensor to read model ID, initializes subdev/controls/media pad, marks runtime PM active with a usage count, registers the async sensor, then enables autosuspend and drops the usage count so the sensor powers down after delay.

Hardware parsing obtains regulators, optional reset GPIO, clock, and endpoint data. It accepts only two or four lanes, requires firmware link frequencies, then searches for a link frequency that is compatible with both the input clock and one of the driver's supported lane-rate modes. It sets `cur_mode`, `pixel_rate`, and `clk_params` based on this match.

Stream enable locks active state, resumes runtime PM, writes the init table, applies the selected lane-rate CSI timing and INCK clock parameter tables, writes lane mode, replays controls, wakes the sensor out of standby with an 80 ms delay, and starts master streaming with `XMSTA`. Stream disable writes `XMSTA_STOP`, puts the device into standby, and uses autosuspend.

Controls update exposure limits when vblank changes. Hardware writes are skipped while suspended. Vblank writes `VMAX` and then falls through to reprogram exposure because exposure is expressed as `SHR0 = VMAX - exposure`. Hblank writes `HMAX` from `(width + hblank) / 12`. Flip writes the combined reverse register. Test-pattern control programs black level, pattern select, test clock, digital clip, and WRJ-open registers.

## State, Persistence, and Dependencies

Persistent software state includes active subdev format, selected mode index, clock parameter pointer, lane count, pixel rate, and controls. The sensor is fully reprogrammed on each stream start; controls persist in V4L2 state and are replayed after setup. Runtime PM uses autosuspend, so power-off may be delayed after stream stop.

Dependencies include V4L2 CCI regmap, fwnode endpoint parsing, V4L2 subdev active state, media pads, controls including fwnode properties, runtime PM with autosuspend, regulators, GPIO, clocks, OF matching, and standard kernel min/clamp helpers.

## Risks and Edge Cases

`imx415_set_testpattern()` accumulates CCI write errors but returns `0`, hiding failures. In `imx415_s_ctrl()`, early returns after failed vblank writes can bypass `pm_runtime_put()`, which is a runtime-PM leak risk if `cci_write(VMAX)` fails. `IMX415_VREVERSE_SHIFT` is defined as `BIT(0)` rather than a numeric shift count; using `sensor->vflip->val << IMX415_VREVERSE_SHIFT` shifts by 1 because `BIT(0)` is 1, but the name is misleading. `imx415_set_format()` copies requested width/height instead of clamping to the fixed pixel array, while enumeration reports only the fixed size; callers may observe inconsistent active state if they set another size. Mode selection depends on matching firmware link frequencies, input clock, lane-rate tables, and lane count.

## Test Signals

Validation should cover all supported input-clock/link-frequency combinations, two-lane and four-lane HMAX minima, invalid endpoint rejection, model ID read after wakeup, autosuspend behavior, stream-on register order, recovery on stream setup failures, fixed code/size enumeration, format-setting behavior for non-native requests, vblank/exposure fallthrough writes, hblank-to-HMAX calculation, flip register values, test-pattern enable/disable side effects, and runtime PM reference balance when CCI writes fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/imx415.c -->
