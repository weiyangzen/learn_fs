# subset-b-004094 research

This grouped report covers seven Linux V4L2 I2C camera sensor drivers under `sources/distributed-fs/ceph-client/drivers/media/i2c`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m114.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m114.c

## Purpose
This driver supports the onsemi/Aptina MT9M114/MI1040 sensor as a V4L2 media-controller device. It models the chip as two subdevices: a raw Bayer pixel-array source and an Image Flow Processor sink/source block that can crop, scale, convert to YUV/RGB/Bayer, expose test patterns, and stream over either parallel or CSI-2 D-PHY output.

## Important APIs, Types, and Functions
The central state is `struct mt9m114`, holding the I2C client, CCI regmap, clock/regulator/reset resources, parsed `v4l2_fwnode_endpoint`, Aptina PLL data, runtime streaming state, and nested pixel-array and IFP subdevice/control state. Format handling is described by `struct mt9m114_format_info` and `mt9m114_format_infos[]`. Hardware helpers include `mt9m114_poll_command()`, `mt9m114_poll_state()`, `mt9m114_set_state()`, `mt9m114_initialize()`, `mt9m114_configure_pa()`, `mt9m114_configure_ifp()`, and `mt9m114_set_frame_rate()`. Probe and lifetime are handled by `mt9m114_parse_dt()`, `mt9m114_clk_init()`, `mt9m114_identify()`, `mt9m114_power_on()`, `mt9m114_power_off()`, `mt9m114_probe()`, and `mt9m114_remove()`.

## Control Flow
Probe allocates state, initializes a 16-bit CCI regmap, parses the firmware graph endpoint, obtains model data, clock, optional reset GPIO, and three supplies, computes PLL or PLL-bypass timing against the endpoint `link-frequencies`, powers the sensor, verifies chip/version registers, enables runtime PM, initializes the pixel-array subdev, initializes the IFP subdev, and registers the IFP asynchronously. The IFP `registered` callback registers the pixel-array subdev and creates an immutable pad link from pixel array to IFP. Stream-on resumes runtime PM, writes the large initialization table, configures PLL/output port/pad slew, programs IFP crop/compose/output format, programs pixel-array crop/binning, applies frame rate and both control handlers, then sends a config-change state transition. Stream-off sends suspend state and drops the runtime PM reference.

## State and Persistence
Runtime state is volatile and stored in V4L2 active subdev states plus cached fields such as `streaming`, `pixrate`, `bypass_pll`, and IFP `frame_rate`. Controls are applied only while the device is powered; volatile exposure/gain controls switch between hardware-read values and manual cached values depending on auto-exposure mode. Crop/format changes update V4L2 state first and are pushed to registers immediately only when streaming and permitted. No state persists across power loss; register programming is replayed on each stream start.

## Dependencies and Integration Points
The driver depends on V4L2 async/media-controller APIs, subdev active-state APIs, CCI regmap helpers, `aptina-pll`, runtime PM, firmware graph endpoints, clocks, regulators, reset GPIOs, and media bus formats. It binds OF compatibles `onnn,mt9m114` and `aptina,mi1040`, plus ACPI `INT33F0`. Endpoint bus type must be parallel or CSI-2 D-PHY, and the single expected link frequency must match either EXTCLK bypass or the calculated PLL pixel rate.

## Risks and Edge Cases
The driver contains several documented assumptions: undocumented minimum blanking, semi-arbitrary scaler minimums, and a FIXME for horizontal crop alignment when binning. Some state transitions depend on model-specific standby polling behavior. TRY frame interval is explicitly unsupported. Format/crop changes while streaming are partially restricted: pixel-array size changes return `-EBUSY`, while some IFP changes are only state updates until the next config-change path. Link-frequency validation is strict and can reject otherwise viable boards if firmware values are absent or computed differently.

## Test Signals
Useful tests include OF/ACPI probe with both compatibles, invalid bus/link-frequency rejection, runtime PM autosuspend/resume, stream-on/off loops, parallel versus CSI-2 output selection, scaler/crop/compose propagation, RAW10 versus processed-format border behavior, volatile exposure/gain behavior when toggling auto exposure, test-pattern controls while streaming, and media-graph validation of the immutable pixel-array-to-IFP link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9p031.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9p031.c

## Purpose
This driver supports Aptina MT9P031-family 5MP parallel-output sensors, including Bayer and monochrome variants. It exposes one V4L2 camera-sensor subdevice with a single source pad, crop and format selection, power control, PLL/pixel-clock setup, exposure/gain/mirroring/test-pattern controls, and custom black-level calibration controls.

## Important APIs, Types, and Functions
`struct mt9p031` stores the subdev, media pad, active crop and format, manual power counter, clock/regulator/reset resources, model bus code, Aptina PLL settings, cached `OUTPUT_CONTROL` and `READ_MODE_2` register values, and V4L2 controls. Low-level access is via SMBus word helpers `mt9p031_read()` and `mt9p031_write()`. Register-cache helpers `mt9p031_set_output_control()` and `mt9p031_set_mode2()` keep shadow values synchronized. Key flows are `mt9p031_clk_setup()`, `mt9p031_power_on()`, `__mt9p031_set_power()`, `mt9p031_set_params()`, `mt9p031_s_stream()`, `mt9p031_s_ctrl()`, `mt9p031_registered()`, and `mt9p031_probe()`.

## Control Flow
Probe checks SMBus word support, parses the firmware endpoint and clock-frequency properties, obtains regulators, initializes controls and media entity, sets default crop/format, acquires reset GPIO and sensor clock, calculates PLL or divider timing, and asynchronously registers the subdev. The internal `registered` callback powers the chip, reads `CHIP_VERSION`, and powers it down. Opening or `s_power` increments the manual power count; the first power-on enables supplies and clock, releases reset, resets the sensor, programs pixel-clock polarity, and applies all controls. Stream-on programs crop/window registers, row/column skip/binning, blanking, enables sensor output, restarts the frame sequencer, and enables the PLL. Stream-off pauses/restarts, disables output, and powers down the PLL.

## State and Persistence
Active crop/format live in `mt9p031->crop` and `mt9p031->format`, while TRY values live in subdev state. The power state is reference counted with `power_lock`, not runtime PM. `output_control` and `mode2` are software register caches used for read-modify-write behavior. Control values are cached by V4L2 while powered off and replayed at power-on. There is no persistent storage; all hardware state is volatile.

## Dependencies and Integration Points
The driver integrates with V4L2 async/subdev/media-entity APIs, firmware graph parsing, GPIO, regulators, clocks, and `aptina-pll`. It binds OF compatibles `aptina,mt9p006`, `aptina,mt9p031`, and `aptina,mt9p031m`, selecting Bayer `MEDIA_BUS_FMT_SGRBG12_1X12` or mono `MEDIA_BUS_FMT_Y12_1X12` output.

## Risks and Edge Cases
`mt9p031_parse_properties()` releases the endpoint handle before reading `input-clock-frequency` and `pixel-clock-frequency` from it, which is a lifetime/order risk. If the external clock exceeds PLL limits, the fallback divider path can only approximate target pixel rate. Crop/binning programming has an explicit TODO about matching start/size to skipping, binning, and mirroring. Test-pattern mode disables digital BLC and toggles related controls, so regressions can leave black-level settings inconsistent. The manual power counter warns if unbalanced but can still be driven by legacy users.

## Test Signals
Build and probe tests should cover Bayer and mono compatibles, valid and invalid chip IDs, endpoint clock-property parsing, PLL and divider-only timing paths, reset GPIO timing, stream-on/off sequencing, crop and frame-size enumeration, exposure/gain quantization, H/V flip cache writes, test-pattern/BLC interaction, and unbalanced open/close or `s_power` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9p031.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9t112.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9t112.c

## Purpose
This legacy V4L2 subdev driver supports MT9T111/MT9T112 camera sensors with an internal MCU/IFP, parallel output formats, PLL programming from board platform data, and basic frame-size/format control. It is explicitly incomplete for frame-rate control because public register documentation and test hardware were insufficient.

## Important APIs, Types, and Functions
`struct mt9t112_priv` stores the subdev, platform data, I2C client, active frame rectangle, optional clock, standby GPIO, current format, detected format count, and one-time initialization flag. `struct mt9t112_format` maps media bus codes to sensor format/order values. Low-level access is split into raw register helpers `__mt9t112_reg_read()`, `__mt9t112_reg_write()`, `__mt9t112_reg_mask_set()` and MCU logical-address helpers `__mt9t112_mcu_read()`, `__mt9t112_mcu_write()`, `__mt9t112_mcu_mask_set()`. Main setup functions are `mt9t112_reset()`, `mt9t112_init_pll()`, `mt9t112_init_setting()`, `mt9t112_auto_focus_setting()`, `mt9t112_init_camera()`, `mt9t112_s_stream()`, and `mt9t112_camera_probe()`.

## Control Flow
Probe requires `client->dev.platform_data`, allocates state, initializes the I2C subdev, obtains optional `extclk` and standby GPIO, powers the device for chip detection, then registers the subdev. Chip detection reads register `0x0000`; MT9T111 exposes only one format while MT9T112 exposes all listed YUV/RGB formats. Power-on enables the clock and releases standby. The first stream-on performs reset, PLL programming, many timing/flicker/JPEG/analog initialization writes, autofocus setup, PCLK polarity programming from platform flags, and marks `init_done`. Every stream-on programs output format/order, context-A frame size, and triggers autofocus. Stream-off does not truly stop the sensor; it programs VGA size as a thermal workaround.

## State and Persistence
State is simple and mostly active-only: selected frame rectangle, selected format, format count, and `init_done`. The initialization table is applied once per driver lifetime after first stream-on, not on every stream transition. No runtime PM or persistent storage is used. Board-specific PLL dividers and flags live in platform data supplied by the embedding board code.

## Dependencies and Integration Points
The driver depends on legacy platform data from `<media/i2c/mt9t112.h>`, V4L2 subdev APIs, optional `extclk`, optional standby GPIO, V4L2 image-size helpers, and raw I2C transfers. It uses an I2C device ID table rather than OF/ACPI match data. ADV_DEBUG optionally exposes raw register get/set.

## Risks and Edge Cases
The platform-data requirement limits use with modern firmware descriptions. Error handling uses macros that return immediately but can hide which write failed in long initialization sequences. `mt9t112_set_pll_dividers()` return value is ignored inside `mt9t112_init_pll()`, so divider programming failure may be masked until later operations. Stream-off cannot stop hardware and relies on reducing frame size. TRY state support is minimal; active-only selection is enforced. Numerous magic register values are timing-file generated or marked as secret/workaround values.

## Test Signals
Test with both chip IDs, missing platform data, optional clock absent/present, standby GPIO polarity, platform PCLK edge flag, all supported media bus codes, active crop bounds up to 2048x1536, first versus repeated stream-on behavior, VGA fallback on stream-off, and ADV_DEBUG register access when enabled. Compliance tools are expected to report frame-rate limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9t112.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v011.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v011.c

## Purpose
This driver supports the Micron MT9V011 1/4-inch VGA raw Bayer sensor. It is a small legacy I2C/V4L2 subdev driver that exposes one source pad, fixed raw `MEDIA_BUS_FMT_SGRBG8_1X8` output, crop-by-window resolution changes, frame interval adjustment through clock-speed register programming, and basic gain/exposure/color-balance/flip controls.

## Important APIs, Types, and Functions
`struct mt9v011` stores the V4L2 subdev, media pad, controls, selected width/height, crystal frequency, flip bits, and cached gain/exposure/red/blue balance values. Register I/O is through `mt9v011_read()` and `mt9v011_write()` using direct I2C send/receive. Configuration helpers include `calc_mt9v011_gain()`, `set_balance()`, `calc_fps()`, `calc_speed()`, `set_res()`, `set_read_mode()`, and `mt9v011_reset()`. V4L2 operations are `mt9v011_set_fmt()`, frame interval get/set, ADV_DEBUG register get/set, `mt9v011_s_ctrl()`, `mt9v011_probe()`, and `mt9v011_remove()`.

## Control Flow
Probe checks I2C byte functionality, allocates state, initializes the subdev and media pad, reads the chip version, initializes six controls, sets default cached values for gain/exposure/640x480/27MHz, optionally overrides the crystal from platform data, and leaves hardware programming to reset/control/format paths. Reset writes a small default register list, then reapplies balance, resolution, and read mode. Format set validates the raw code, bounds width/height, writes active dimensions immediately for ACTIVE state, and stores TRY format in subdev state otherwise. Frame interval set computes the closest speed-divider value, writes it, and reports the recalculated interval.

## State and Persistence
The driver stores all meaningful state in memory and sensor registers: selected dimensions, clock source, flips, exposure, gain, and balance offsets. There is no explicit power management, runtime PM, asynchronous registration, or persistent state. Controls immediately update hardware through I2C; read failures in helper paths are logged but not always fatal because low-level helpers return register values directly.

## Dependencies and Integration Points
The driver uses V4L2 subdev/control/media-entity APIs, optional legacy `mt9v011_platform_data`, and raw I2C master operations. It registers by I2C device ID `mt9v011`; there is no OF match table. It includes ADV_DEBUG register access when configured.

## Risks and Edge Cases
I2C helper error handling is weak: failed reads can still return converted buffer contents, and writes log mismatched transfer sizes without propagating errors. The probe error path after `media_entity_pads_init()` does not clean up the entity on later chip-ID/control failures. The advertised I2C functionality check does not exactly match the raw master-send/master-recv operations used. `set_res()` uses empirically chosen blanking equations and notes that datasheet width-minus-one behavior did not work. There is no stream-on/off callback, so bridge drivers must tolerate always-programmed output behavior.

## Test Signals
Exercise both known chip versions, invalid chip ID handling, default reset sequence, platform-data crystal override, all controls, frame interval calculation boundaries, minimum/maximum active format sizes, TRY versus ACTIVE format behavior, H/V flip register writes, and I2C error injection to expose non-propagated transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v011.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v032.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v032.c

## Purpose
This driver supports Aptina MT9V022/024/032/034 monochrome and color VGA sensors. It exposes a V4L2 media-controller camera-sensor subdev with crop, binning-derived format sizes, manual power counting, regmap-backed register access, auto exposure/gain controls, test pattern controls, optional link-frequency control, and model-specific timing limits.

## Important APIs, Types, and Functions
Model behavior is split across `enum mt9v032_model`, `struct mt9v032_model_data`, `struct mt9v032_model_info`, and `mt9v032_models[]`. Runtime state in `struct mt9v032` includes subdev/media pad, active format/crop, binning ratios, control handler, regmap, clock/reset/standby GPIOs, parsed platform data, detected chip version, cached AEC/AGC enable bits, and hblank. Key functions are `mt9v032_update_aec_agc()`, `mt9v032_update_hblank()`, `mt9v032_power_on()`, `__mt9v032_set_power()`, `mt9v032_s_stream()`, `mt9v032_set_format()`, `mt9v032_set_selection()`, `mt9v032_s_ctrl()`, `mt9v032_registered()`, `mt9v032_get_pdata()`, and `mt9v032_probe()`.

## Control Flow
Probe allocates state, initializes an 8-bit/16-bit regmap with maple cache, acquires clock and optional GPIOs, parses OF endpoint flags and optional `link-frequencies`, creates controls using model-specific ranges, initializes active crop/format based on color/mono model data, initializes subdev/media entity, and registers asynchronously. The internal `registered` callback powers the sensor, reads chip version, maps it to known revisions, powers down, and updates pixel rate. Opening powers the sensor and initializes TRY state. Stream-on programs read-mode binning, crop window, hblank, and enables sequential data output. Stream-off clears output-enable/sequential bits.

## State and Persistence
The driver uses manual `power_count` under `power_lock`; no runtime PM is used. Active crop/format and h/v binning ratios are cached in `struct mt9v032`, while TRY state lives in file-handle state. AEC/AGC bits are cached in `aec_agc` to support read-modify-write. `hblank` is cached separately because the programmed value may be clamped upward by model/revision timing requirements. Hardware state is volatile and replayed when powered or streaming.

## Dependencies and Integration Points
The driver depends on V4L2 subdev/control/media APIs, regmap over I2C, clocks, optional reset/standby GPIOs, OF graph parsing, and firmware endpoint parallel-clock polarity. OF compatibles select exact color/mono and model-family behavior, while actual chip revision is verified at registration. Optional `link-frequencies` creates clustered `LINK_FREQ`/`PIXEL_RATE` controls.

## Risks and Edge Cases
`standby_gpio` is requested but not used in power sequencing, so board-level standby wiring may not be controlled. `mt9v032_s_ctrl()` writes registers without checking whether the device is powered, relying on V4L2 control setup timing and callers. Link-frequency parsing assumes a zero-terminated allocated array but allocates exactly the property element count, so iteration over `pdata->link_freqs[i]` can read past the allocation if the property lacks a trailing zero entry. Stream control is not protected by the power mutex. Model-specific hblank clamping differs for MT9V034 and binning, making timing regressions easy.

## Test Signals
Test every OF compatible, color versus mono bus codes, unsupported chip versions, endpoint clock polarity, link-frequency menu creation, power-counted open/close, stream-on/off register programming, crop alignment to odd Bayer origins, 1x/2x/4x binning format selection, AEC/AGC and hblank/vblank controls, test-pattern cluster behavior, and DT link-frequency property edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v032.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v111.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v111.c

## Purpose
This driver supports the Aptina MT9V111 VGA sensor with an integrated Image Flow Processor. It exposes a single V4L2 camera-sensor subdev that outputs YUV byte-order permutations, uses IFP decimation for supported frame sizes, controls auto white balance and auto exposure, and approximates frame rate by programming core horizontal/vertical blanking.

## Important APIs, Types, and Functions
`struct mt9v111_dev` stores the I2C client, cached address space, subdev/media pad, controls, current output format, fps, power and stream mutexes, pending-configuration flag, clock/sysclk, and optional enable/standby/reset GPIOs. Low-level access is split into `__mt9v111_read()`, `__mt9v111_write()`, `__mt9v111_addr_space_select()`, `mt9v111_read()`, `mt9v111_write()`, and `mt9v111_update()` because the chip has core and IFP register spaces. Hardware flows are `__mt9v111_power_on()`, `__mt9v111_hw_reset()`, `__mt9v111_sw_reset()`, `mt9v111_calc_frame_rate()`, `mt9v111_hw_config()`, `mt9v111_s_stream()`, `mt9v111_s_ctrl()`, `mt9v111_chip_probe()`, and `mt9v111_probe()`.

## Control Flow
Probe obtains the sensor clock, validates `sysclk <= 27MHz`, gets optional enable/standby/reset GPIOs, initializes power/stream mutexes and controls, computes initial blanking for 640x480 at 15 fps, initializes the subdev/media entity, probes the chip by powering it and reading the core chip-version register, then asynchronously registers the subdev. Stream-on takes the stream mutex, powers the device, and if configuration is pending performs hardware or software reset, configures clock sample mode, output byte ordering, IFP pan/zoom/output size registers, applies controls, programs pixel integration, and clears pending. Stream-off powers the device down.

## State and Persistence
The driver maintains separate power and stream state. `pwr_count` is bounded for nested power calls, `streaming` avoids duplicate stream transitions, and `pending` defers format/control changes made while powered down or not yet applied. The selected register address space is cached to avoid redundant writes. Format and fps are active-state fields in the driver; TRY format is initialized through subdev state. Hardware state is not persistent and is reapplied on pending stream-on.

## Dependencies and Integration Points
The driver uses V4L2 async/subdev/control/media APIs, V4L2 image-size constants, raw I2C transfers, clocks, optional GPIOs, and OF compatible `aptina,mt9v111`. It integrates as a single source-pad sensor entity with link validation. Output is limited to four 8-bit YUV mbus codes.

## Risks and Edge Cases
The chip-ID check uses `&&` when comparing high and low bytes, so a value with one matching byte can pass unexpectedly. `mt9v111_s_stream()` powers on before hardware configuration but does not undo that power reference if configuration fails. The power counter warns outside 0..1 but still mutates state for nested calls. Frame-rate calculation brute-forces blanking and then stores requested fps, while the actual returned denominator may be only the closest achievable value. Auto exposure/white balance can alter effective frame rate, as documented. TRY frame interval is unsupported and streaming format changes return `-EBUSY`.

## Test Signals
Test chip-ID rejection, hardware reset versus software-reset fallback, optional GPIO absence, clock-rate limits, all YUV byte orders, all enumerated frame sizes and frame intervals, busy rejection for streaming format/fps changes, pending configuration after powered-off controls, AWB/AE flicker interaction, stream-on error unwinding, and address-space switching under repeated register updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9v111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/og01a1b.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/og01a1b.c

## Purpose
This driver supports the OmniVision OG01A1B 1280x1024 global-shutter sensor over two-lane CSI-2. It exposes a modern V4L2 sensor subdev with one source pad, stream enable/disable pad operations, runtime PM, CCI register-list mode programming, 8-bit or 10-bit monochrome output, exposure/gain/blanking/test-pattern controls, and OF/ACPI matching.

## Important APIs, Types, and Functions
Mode data is represented by `struct og01a1b_mode`, `struct og01a1b_reg_list`, and `struct og01a1b_link_freq_config`. `struct og01a1b` stores device resources, CCI regmap, clock/reset/regulators, V4L2 subdev/media pad/control handler, key controls, current mode, and selected media bus code. Important helpers include `to_pixel_rate()`, `to_pixels_per_line()`, `og01a1b_test_pattern()`, `og01a1b_set_ctrl()`, `og01a1b_init_controls()`, `og01a1b_enable_streams()`, `og01a1b_disable_streams()`, `og01a1b_set_format()`, `og01a1b_check_hwcfg()`, `og01a1b_power_on()`, `og01a1b_power_off()`, and `og01a1b_probe()`.

## Control Flow
Probe initializes the I2C subdev and 16-bit CCI regmap, obtains and validates a 19.2MHz external clock, checks firmware endpoint requirements, obtains optional reset GPIO and optional AVDD/DOVDD/DVDD regulators, powers the device, verifies the 24-bit chip ID, initializes default mode/code and controls, finalizes subdev state, registers the sensor subdev, enables runtime PM, and idles the device. Stream enable resumes runtime PM, writes link-frequency PLL registers, writes the mode register table, programs output bit depth, applies all controls, and writes mode-select streaming. Stream disable writes standby and drops the runtime PM autosuspend reference.

## State and Persistence
Current mode and output code are cached in `cur_mode` and `code`; controls cache link frequency, pixel rate, blanking, exposure, gain, and test pattern values. VBLANK changes dynamically adjust exposure maximum. Controls are only written when runtime PM says the device is already active; otherwise V4L2 caches values for setup on stream start. Register state is volatile and is replayed on every stream enable.

## Dependencies and Integration Points
The driver depends on V4L2 CCI helpers, V4L2 fwnode endpoint parsing, subdev active-state/finalize APIs, `v4l2_subdev_s_stream_helper`, runtime PM, clocks, GPIOs, regulators, OF compatible `ovti,og01a1b`, and ACPI ID `OVTI01AC`. Firmware must describe a CSI-2 D-PHY endpoint with exactly two data lanes and link frequency 500 MHz.

## Risks and Edge Cases
Only one sensor mode is supported, so format negotiation is nearest-size but effectively fixed at 1280x1024. `og01a1b_set_format()` does not validate `fmt->format.code` against the enumerated codes before using it; unrecognized codes fall into the 8-bit bpp path while the returned format preserves the caller's code. Optional regulators mean power sequencing may rely on board defaults. `pm_runtime_put()` in control writes does not use autosuspend, unlike stream error/disable paths. Hardware configuration validation requires every driver-supported link frequency to appear in firmware, not just the selected one.

## Test Signals
Test OF and ACPI probe, wrong xclk frequency, missing endpoint, wrong CSI-2 lane count, missing/incorrect link frequencies, optional regulator and reset-GPIO combinations, chip-ID mismatch, 8-bit versus 10-bit output format programming, vblank-driven exposure-range updates, stream-on/off loops with runtime PM, test-pattern menu values, and invalid requested media bus codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/og01a1b.c -->
