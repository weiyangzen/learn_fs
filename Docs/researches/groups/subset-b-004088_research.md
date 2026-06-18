# subset-b-004088 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_mode.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_mode.c

## Purpose
`et8ek8_mode.c` is a static mode-table companion for the Toshiba/Nokia ET8EK8 sensor driver. It does not implement I2C, V4L2, or PM logic directly; instead it exports `meta_reglist`, a versioned list of `struct et8ek8_reglist` objects consumed by the main ET8EK8 driver to program power-on and streaming modes.

## Important APIs, Types, and Data
- Includes only `et8ek8_reg.h`; all public contracts come from that header.
- Defines nine `static struct et8ek8_reglist` mode objects, one of which has type `ET8EK8_REGLIST_POWERON` and the rest `ET8EK8_REGLIST_MODE`.
- Each reglist embeds `struct et8ek8_mode` metadata: physical sensor dimensions, crop/window dimensions, output frame geometry, pixel clock, frame interval, maximum exposure, media-bus format, and 16.16 sensitivity.
- Register sequences are `struct et8ek8_reg` flexible arrays terminated by `{ ET8EK8_REG_TERM, 0, 0 }`.
- The exported `struct et8ek8_meta_reglist meta_reglist` has version `"V14 03-June-2008"` and a NULL-terminated pointer table in mode order.

## Control Flow
There is no executable control flow in this file beyond static initialization. Runtime flow is data-driven: the ET8EK8 driver selects a `meta_reglist.reglist[i].ptr`, inspects its `type` and `mode`, then iterates `regs` until `ET8EK8_REG_TERM`. The first list is a power-on/full-resolution setup with additional analog/CCP2/ISP initialization, while subsequent lists adjust timing, scaling/binning, bus format, and frame rate.

## State and Persistence
All state is immutable kernel data after module load. Persistence is limited to the compiled-in mode table. The table stores sensor timing assumptions such as SPCK/CCP2/VCO, HCOUNT/VCOUNT, divisors, maximum exposure, and output bus format. There is no dynamic allocation, locking, or per-device state here.

## Dependencies and Integration Points
- Depends on Linux media bus format constants via the header include path.
- Consumed by the ET8EK8 sensor driver through the external `meta_reglist` symbol.
- Register type constants (`ET8EK8_REG_8BIT`, `ET8EK8_REG_TERM`) and list type constants come from `et8ek8_reg.h`.
- Integration risk is mainly ABI-like: the order and metadata in `meta_reglist` must match the driver's selection and enumeration expectations.

## Risks
- Register values are opaque vendor tuning values; accidental edits can break PLL, CCP2/LVDS output, frame timing, exposure limits, or image quality.
- Some comments and values disagree slightly, for example denominator naming around 13.12 fps, so reviewers should validate effective timing rather than trusting comments alone.
- The flexible-array mode objects are static and non-const, which permits accidental writes by driver code even though the intended data is read-only.
- Any missing `ET8EK8_REG_TERM` would make the consumer walk past the register array.
- Mode metadata must stay consistent with register programming; mismatched width, height, pixel clock, or bus format can cause bad V4L2 negotiation.

## Test Signals
- Build/link should confirm `meta_reglist` resolves and `et8ek8_reg.h` contracts match the main driver.
- Runtime probe/stream tests should exercise each advertised mode, verify frame size and bus code negotiation, and check no register-list walk errors.
- Sensor capture should confirm frame interval, exposure limits, and compressed vs uncompressed bus formats for DPCM modes.
- Regression checks should compare the version and pointer ordering when changing tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_reg.h

## Purpose
`et8ek8_reg.h` defines the data contract shared between the ET8EK8 sensor driver and the compiled register/mode tables in `et8ek8_mode.c`. It provides mode metadata, register sequence element formats, reglist type identifiers, and the external `meta_reglist` symbol.

## Important APIs, Types, and Data
- `struct et8ek8_mode` describes sensor array dimensions, active sensor window, output dimensions, output window, `pixel_clock`, `timeperframe`, `max_exp`, `bus_format`, and fixed-point `sensitivity`.
- Register entry type constants are `ET8EK8_REG_8BIT`, `ET8EK8_REG_16BIT`, `ET8EK8_REG_DELAY`, and `ET8EK8_REG_TERM`.
- `struct et8ek8_reg` carries a register operation type, 16-bit register offset, and up-to-32-bit value.
- Reglist type constants divide sensor lifecycle and feature lists: standby, power-on, resume, stream on/off, disabled, mode, lens-shading enable/disable, and auto-noise-reduction enable/disable.
- `struct et8ek8_reglist` combines a type, a mode descriptor, and a flexible `regs[]` array.
- `struct et8ek8_meta_reglist` carries a version string and a flexible table of reglist pointers; `meta_reglist` is declared `extern`.

## Control Flow
The header has no runtime logic. It shapes the consumer driver's control flow by defining the sentinel-based register walk (`ET8EK8_REG_TERM`) and the list classification (`ET8EK8_REGLIST_*`) that tells the driver whether a sequence is a mode, power-on sequence, stream transition, or feature toggle.

## State and Persistence
The structures are storage definitions for persistent compiled-in mode/register data. The header itself owns no device state. Values such as `timeperframe`, `max_exp`, and `sensitivity` become the initial truth used by V4L2 enumeration and control setup in the main driver.

## Dependencies and Integration Points
- Includes Linux I2C and V4L2 type headers plus `linux/types.h`.
- Forward-declares V4L2 media-bus structs for compatibility with the main ET8EK8 code.
- Integrated directly with `et8ek8_mode.c` through the `meta_reglist` declaration.
- The flexible-array layout requires static initializers to be defined carefully in C files.

## Risks
- This is a shared ABI within the driver; changing field order, type widths, constants, or sentinel values requires synchronized changes in every consumer and mode table.
- `struct et8ek8_reglist` and `struct et8ek8_meta_reglist` use flexible arrays; misuse with stack allocation or wrong terminators can cause memory overruns.
- `ET8EK8_MAX_LEN` bounds the version string; longer version text in a table initializer would be truncated or rejected depending on initializer form.
- The comment says "smia_reglist" although the symbols are ET8EK8, suggesting inherited code and a need for cautious semantic review.

## Test Signals
- Compile coverage should catch mismatched field names and initializer shape between mode table and header.
- Static analysis should focus on consumers walking `regs[]` and `reglist[]` sentinels.
- Runtime media enumeration should confirm `struct et8ek8_mode` fields produce coherent formats, frame sizes, and control ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc0308.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/gc0308.c

## Purpose
`gc0308.c` is a V4L2 sub-device driver for the GalaxyCore GC0308 parallel camera sensor. It exposes media-bus format and frame-size negotiation, image controls, runtime power management, register programming through regmap/CCI helpers, and OF binding for `"galaxycore,gc0308"`.

## Important APIs, Types, and Functions
- Register constants cover page-0/page-1 analog, ISP, AWB, AEC, gamma, crop, subsample, and output modules using `CCI_REG8/16`.
- `struct gc0308` is the per-device state: `v4l2_subdev`, control handler, media pad, clock, regulator, GPIOs, regmap, bus flags, current output mode, and clustered flip/blanking controls.
- `gc0308_regmap_config` uses regmap ranges with page selector `0xfe`; the driver avoids `devm_cci_regmap_init_i2c()` because it needs regmap pagination.
- Static tables include exposure bias presets, AWB gains, output formats, frame sizes, default sensor programming, and color-effect register groups.
- Power and PM: `gc0308_power_on()`, `gc0308_power_off()`, runtime PM ops, autosuspend in probe.
- V4L2 controls: `_gc0308_s_ctrl()` applies controls, while `gc0308_s_ctrl()` only applies live I2C writes when runtime PM says the device is active.
- Format and stream ops: `gc0308_enum_mbus_code()`, `gc0308_enum_frame_size()`, `gc0308_set_format()`, `gc0308_init_state()`, `gc0308_start_stream()`, `gc0308_stop_stream()`, `gc0308_s_stream()`.
- Probe/remove wire together fwnode parallel-bus parsing, resources, chip-ID read, media entity setup, subdev registration, and runtime PM.

## Control Flow
Probe allocates state, parses the endpoint as `V4L2_MBUS_PARALLEL`, acquires optional clock, `vdd28`, powerdown/reset GPIOs, initializes paged regmap, subdev, controls, media entity, and subdev state. It powers the sensor, optionally warns if the clock is not 24 MHz, reads `GC0308_CHIP_ID`, then enables autosuspended runtime PM and registers the subdev.

Streaming locks the active subdev state, resumes power, writes the large `sensor_default_regs` table, applies selected output format and resolution/subsampling registers, replays controls through `__v4l2_ctrl_handler_setup()`, and finally writes sync polarity from parsed parallel bus flags. There is no explicit stream-enable register; stop streaming releases runtime PM and lets autosuspend power down the sensor.

Control flow is split so controls update cached V4L2 values while suspended, and are replayed at stream start. Live controls write blanking, mirror bits, AWB, power-line anti-flicker tables, color effects, test pattern bits, and exposure bias registers.

## State and Persistence
Persistent per-device state includes the chosen `gc0308->mode` fields (`out_format`, `subsample`, width, height), control values in the handler, and parsed `mbus_config`. Hardware state is volatile: `sensor_default_regs` are rewritten on every stream start, then cached controls are replayed. Runtime PM usage count represents active streaming; autosuspend powers the chip down after use.

## Dependencies and Integration Points
- Linux subsystems: I2C, regmap, regulators, GPIO descriptors, optional clock, runtime PM, media entity, V4L2 controls/subdev/fwnode, and CCI helpers.
- Device-tree compatible is `"galaxycore,gc0308"`.
- Requires a parallel endpoint and uses endpoint flags for HSYNC/VSYNC polarity.
- Exposes one source pad with selectable UYVY/VYUY/YUYV/YVYU/RGB formats and 640x480, 320x240, 160x120 sizes.

## Risks
- `gc0308_regmap_config.disable_locking = true`; correctness relies on V4L2 state/control locking and single-threaded CCI access patterns.
- The driver comments say frame rate depends strongly on exposure/AEC and is not fully understood, so FPS reporting is approximate.
- Stop stream only drops runtime PM; if future hardware requires an explicit stream-off register, this path would need extension.
- Large undocumented default-register values are hard to audit and can regress image quality or timing.
- Control arrays index directly by V4L2 enum values; menu masks must continue to exclude unsupported holes.
- Probe powers the device before chip-ID read; unwind paths must keep regulator/clock/GPIO ordering correct.

## Test Signals
- `v4l2-compliance` for subdev pad ops, controls, and media graph registration.
- Probe tests should cover missing endpoint, bad regulator/GPIO, wrong chip ID, and optional clock rate warnings.
- Capture tests should verify all advertised formats/frame sizes, HSYNC/VSYNC polarity handling, runtime suspend/resume, and autosuspend after stop.
- Control tests should verify h/v flip clustering, blanking register split, power-line frequency tables, AWB presets, color effects, and test patterns before and during streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc0308.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc0310.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/gc0310.c

## Purpose
`gc0310.c` is a V4L2 sub-device driver for the GalaxyCore GC0310 VGA CSI-2 camera sensor, primarily matched through ACPI ID `"INT0310"`. It supports one fixed raw 8-bit 656x496 mode, runtime PM, exposure/gain/blanking controls, and CSI-2 stream enable/disable through modern pad stream operations.

## Important APIs, Types, and Functions
- Constants define native geometry, an inferred pixel rate, fixed link frequency, 19.2 MHz MCLK requirement, one-lane CSI-2, chip ID, page select values, stream register, exposure/gain/blanking registers, and timing offsets.
- `struct gc0310_device` stores `v4l2_subdev`, source pad, CCI regmap, reset/powerdown GPIOs, and a nested control group for exposure, gain, link frequency, pixel rate, vblank, and hblank.
- Register tables: `gc0310_reset_register[]` performs system/MIPI/CISCTL/ISP/gain tuning and `gc0310_VGA_30fps[]` applies fixed VGA-size/crop details.
- `gc0310_gain_set()` maps the 0..95 V4L2 gain range into analog gain selection and digital gain.
- `gc0310_s_ctrl()` updates exposure range on vblank changes and applies live writes only when powered.
- Pad operations expose fixed format/size/selection and implement `.enable_streams`/`.disable_streams`; legacy `.s_stream` delegates to `v4l2_subdev_s_stream_helper`.
- `gc0310_check_hwcfg()` waits for graph endpoint creation, validates `clock-frequency`, parses CSI-2 endpoint and link frequencies, and requires exactly one data lane.

## Control Flow
Probe validates hardware configuration before allocation, obtains reset and powerdown GPIOs asserted high, initializes the subdev and CCI regmap, powers the sensor, enables runtime PM, detects chip ID, initializes controls/media entity/state, registers the sensor subdev, then enables autosuspend and drops the PM reference.

Stream enable resumes runtime PM, writes reset and fixed VGA tables, replays all controls, toggles reset-related page/stream registers to enable per-frame MIPI and start streaming from page 3, then returns with the PM reference held. Stream disable writes page 3 stream stop, returns to page 0, and puts runtime PM.

## State and Persistence
There is no selectable mode state; format, crop, and frame size are fixed. V4L2 control values persist in the handler and are replayed on stream start. Hardware register contents are treated as volatile and fully initialized at each enable. Runtime PM, reset GPIO, and powerdown GPIO preserve low-power state across idle periods.

## Dependencies and Integration Points
- Uses ACPI matching, fwnode graph parsing, V4L2 fwnode endpoint helpers, CCI regmap, runtime PM, media entity, and GPIO descriptors.
- Requires bridge-provided or firmware-provided graph endpoint, `clock-frequency = 19200000`, supported link frequency, and one CSI-2 lane.
- Exposes raw `MEDIA_BUS_FMT_SGRBG8_1X8`, one source pad, and sensor registration through `v4l2_async_register_subdev_sensor()`.

## Risks
- The driver relies on bridge drivers possibly creating the fwnode graph and GPIO mappings asynchronously; `-EPROBE_DEFER` is expected when the endpoint is absent.
- `gc0310_probe()` calls `gc0310_remove()` in its error path after partial setup; this is concise but sensitive to initialization ordering of controls, media entity, and PM.
- Pixel rate is inferred from datasheet timing comments rather than a known PLL output.
- Fixed-format `.set_fmt = v4l2_subdev_get_fmt` is intentional but leaves no negotiation flexibility.
- Register tables contain many vendor values and page switches; missing page restoration can make later CCI writes hit the wrong page.

## Test Signals
- ACPI probe on an INT0310 platform with bridge-created endpoint and GPIO mappings.
- Negative probe tests for wrong MCLK, missing link frequency, wrong lane count, missing endpoint, and chip-ID mismatch.
- Stream tests should validate page switching, start/stop register writes, runtime PM balance, and no stale page after disable.
- Control tests should verify vblank changes update exposure range and that exposure/gain/vblank writes are replayed when streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc0310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc05a2.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/gc05a2.c

## Purpose
`gc05a2.c` is a V4L2 I2C sub-device driver for the GalaxyCore GC05A2 5MP raw Bayer CSI-2 sensor. It supports two 10-bit SGRBG modes, runtime PM, regulators/clock/reset sequencing, CCI register programming, basic image controls, and OF matching for `"galaxycore,gc05a2"`.

## Important APIs, Types, and Functions
- Register constants define test-pattern, stream, flip, exposure, gain, frame length, and chip-ID registers.
- `struct gc05a2` stores device resources, V4L2 subdev/media pad, controls, CCI regmap, link-frequency bitmap, identification cache, and current mode pointer.
- `struct gc05a2_mode` defines width, height, register list, horizontal timing size, default/min vertical timing size.
- Static register tables include `mode_2592x1944[]`, `mode_1280x720[]`, and large `mode_table_common[]` for shared sensor/ISP/DPHY setup.
- Power functions enable three supplies (`avdd`, `dvdd`, `dovdd`), enable the 24 MHz xclk, deassert reset, and reverse that order on power off.
- Format ops enumerate one media-bus code, enumerate two frame sizes, select nearest mode, update crop, and refresh vblank/hblank/exposure ranges.
- Controls write exposure, analogue gain, frame length, h/v flip bits, and test-pattern registers when the device is runtime-active.
- `gc05a2_identify_module()` reads chip ID lazily once and caches `identified`.

## Control Flow
Probe parses the CSI-2 fwnode and link-frequency bitmap, initializes 16-bit CCI regmap, obtains a legacy 24 MHz sensor clock, gets regulators and reset GPIO, initializes subdev and controls, sets default mode, initializes entity/state, enables autosuspended runtime PM, and registers the sensor. Unlike GC08A3, chip identification is deferred until stream start.

Stream start resumes runtime PM, identifies the module if not already identified, writes shared `mode_table_common`, writes the current mode register list, replays V4L2 controls, and sets `GC05A2_STREAMING_REG` to 1. Stream stop writes the stream register to 0 and releases runtime PM.

## State and Persistence
Persistent software state is the current mode pointer, control handler values, parsed link-frequency bitmap, and `identified` boolean. Hardware state is reloaded from common and mode tables on every stream start. Vblank updates dynamically modify exposure maximum using active format height, while mode switches recalculate hblank/vblank/exposure ranges.

## Dependencies and Integration Points
- Linux I2C, CCI regmap, clock, regulators, GPIO, runtime PM, V4L2 controls/subdev/fwnode, and media entity APIs.
- Device-tree endpoint must provide compatible link frequencies; the file records the bitmap but always creates link-frequency control with menu index 0 as default.
- Two-lane CSI-2 is implied by constants and pixel-rate math.
- Exposes `MEDIA_BUS_FMT_SGRBG10_1X10` with 2592x1944 at 30 fps and 1280x720 at 60 fps comments.

## Risks
- `gc05a2_update_pad_format()` names its first parameter `gc08a3`, a harmless copy-paste artifact but a readability risk.
- Fwnode parsing validates link frequencies but does not explicitly validate number of data lanes against `GC05A2_DATA_LANES`.
- Deferred chip ID means bad hardware may register successfully and fail only on first stream.
- Control code reads the flip register before `cci_update_bits()` but discards the read value; this only validates access and adds an extra I2C transaction.
- Large opaque common/mode register tables are difficult to review and highly timing-sensitive.
- Runtime PM uses `pm_runtime_get_if_active()` for controls, so controls set while suspended rely entirely on handler replay at stream start.

## Test Signals
- Probe tests with valid/invalid endpoint link frequencies, missing reset/regulators/clock, and first-stream chip-ID mismatch.
- `v4l2-compliance` for pad format selection, crop reporting, read-only hblank/link-freq behavior, and controls.
- Capture tests for both modes, exposure limits after vblank changes, stream start/stop PM balance, and test patterns.
- Power sequencing tests should verify regulators/clock/reset order and autosuspend after stopping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc05a2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc08a3.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/gc08a3.c

## Purpose
`gc08a3.c` is a V4L2 I2C sub-device driver for the GalaxyCore GC08A3 8MP raw Bayer CSI-2 sensor. It supports two 10-bit SRGGB modes, runtime PM, regulator/clock/reset sequencing, CCI register programming, image controls, chip identification, and OF matching for `"galaxycore,gc08a3"`.

## Important APIs, Types, and Functions
- Register constants define test-pattern, streaming, flip, exposure, analogue gain, frame length, and chip-ID access.
- `struct gc08a3` stores device resources, subdev/media pad, controls, CCI regmap, link-frequency bitmap, and current mode pointer.
- `struct gc08a3_mode` describes width, height, mode register list, HTS, default VTS, and minimum VTS.
- Static tables include `mode_3264x2448[]`, `mode_1920x1080[]`, and `mode_table_common[]` for shared system/analog/ISP/DPHY tuning.
- Power sequencing enables `avdd`, `dvdd`, and `dovdd`, enables xclk, then deasserts reset.
- Format/control/stream operations mirror the GC05A2 driver pattern with GC08A3-specific modes, link frequencies, and test-pattern mapping.
- `gc08a3_identify_module()` reads `GC08A3_REG_CHIP_ID` and is called during probe, not delayed until first stream.

## Control Flow
Probe parses the fwnode endpoint and link frequencies, initializes CCI regmap, obtains the legacy 24 MHz xclk, gets regulators and reset GPIO, initializes subdev/default mode, powers on the sensor, verifies chip ID, initializes controls and media entity, finalizes subdev state, enables autosuspended runtime PM, idles the device, and registers the subdev.

Stream start resumes runtime PM, writes the common register table, writes the selected mode table, replays controls, and writes `GC08A3_STREAMING_REG` to start output. Stop writes the stream register to zero and releases PM. Format changes select the nearest supported mode and update crop plus hblank/vblank/exposure ranges.

## State and Persistence
Persistent software state is the current mode pointer, control values, parsed link-frequency bitmap, and resources. The sensor's volatile register state is fully rebuilt on every stream start. Runtime PM controls whether live control writes occur; suspended controls are applied later by `__v4l2_ctrl_handler_setup()`.

## Dependencies and Integration Points
- Uses Linux I2C, V4L2 CCI, fwnode endpoint parsing, media entity, V4L2 controls/subdev, runtime PM, regulators, GPIO, and clock APIs.
- Requires a DT endpoint with link frequencies matching the internal menu; four CSI-2 lanes are implied by constants and pixel-rate math.
- Exposes `MEDIA_BUS_FMT_SRGGB10_1X10` with 3264x2448 at 30 fps and 1920x1080 at 60 fps comments.

## Risks
- Fwnode parsing validates link frequency but does not explicitly reject an endpoint with a different lane count than `GC08A3_DATA_LANES`.
- The driver powers on and identifies during probe; failures unwind through several labels and must maintain resource ordering.
- Like GC05A2, flip helpers perform a read whose value is not used before update-bits.
- Large register arrays include many opaque vendor settings; data-entry mistakes can break stream timing, MIPI output, or image quality.
- Link-frequency bitmap is stored but not used to select an alternate link-frequency default.
- Controls set while suspended are not written immediately and depend on stream-start replay.

## Test Signals
- Probe tests should cover missing endpoint, invalid link frequency, missing resources, chip-ID mismatch, and runtime-PM idle transition.
- Streaming tests for both modes should verify frame dimensions, raw Bayer order, MIPI stability, and PM reference balance.
- Control tests should cover exposure/vblank coupling, analogue gain, h/v flip, all test patterns, and replay after controls are changed while stopped.
- Media graph and pad tests should confirm crop bounds and nearest-size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc08a3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc2145.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/gc2145.c

## Purpose
`gc2145.c` is a V4L2 sub-device driver for the GalaxyCore GC2145 camera sensor. It supports multiple output formats (YUV, RGB565, and RAW8 Bayer orders), three frame modes, CSI-2 MIPI configuration, test patterns, flip/blanking controls, runtime PM, and OF matching for `"galaxycore,gc2145"`.

## Important APIs, Types, and Functions
- Register constants cover page 0 sensor/ISP registers and page 3 DPHY/FIFO/CSI-2 registers.
- `struct gc2145_mode` captures dimensions, per-mode register table, pixel rate, crop rectangle, hblank/vblank, and link-frequency index.
- `struct gc2145_format` maps media-bus codes to V4L2 colorspace, MIPI CSI-2 datatype, sensor output format, bypass switch, and row/column switch bits.
- `struct gc2145` stores subdev, pad, CCI regmap, xclk, optional reset/powerdown GPIOs, regulator bulk supplies, controls, and current mode.
- Static register tables include a large `gc2145_common_regs[]`, per-mode tables for 640x480, 1280x720, and 1600x1200, and `gc2145_common_mipi_regs[]`.
- Pad ops implement code/size enumeration, format selection, crop selection, and stream enable/disable.
- `gc2145_config_mipi_mode()` programs page-3 DPHY/FIFO/MIPI datatype details based on selected mode and format.
- Control handling covers hblank, vblank, test pattern, hflip, and vflip when runtime PM says the device is in use.

## Control Flow
Probe initializes the subdev early, validates DT hardware configuration, obtains and validates a 24 MHz xclk, gets regulators and optional GPIOs, initializes CCI regmap, powers the device, verifies chip ID, sets the default mode, creates controls, initializes media entity/state, enables runtime PM with an initial active reference, schedules autosuspend, and registers the sensor subdev.

Format selection chooses the nearest mode and requested format; RAW output disallows VGA and forces at least 1280x720. Active format updates current mode and read-only pixel-rate/link-frequency/hblank/vblank controls. Stream enable resumes PM, writes current mode registers and common registers, writes output format/bypass/sync bits on page 0, replays controls, configures MIPI page-3 details, and leaves the device streaming. Stream disable clears MIPI enable bits on page 3, returns to page 0, and autosuspends.

## State and Persistence
The selected `mode` pointer and active pad format/crop persist in software; controls persist in the handler. Hardware state is reprogrammed at stream enable. Page selection is explicit and important because normal sensor, common, MIPI, and test-pattern writes span pages 0, 1, 2, 3, and reset-style page values.

## Dependencies and Integration Points
- Uses Linux clock, GPIO, regulator, runtime PM, I2C, V4L2 CCI, V4L2 fwnode, media entity, and MIPI CSI-2 datatype constants.
- DT endpoint must provide exactly two CSI-2 lanes and exactly three link frequencies in the expected order: 120, 192, and 240 MHz.
- Exposes one source pad and registers through `v4l2_async_register_subdev_sensor()`.
- Supports multiple media-bus codes and maps them into MIPI datatypes and sensor output format registers.

## Risks
- `gc2145_update_pad_format()` ignores its `colorspace` argument and always sets `V4L2_COLORSPACE_SRGB`; RAW formats are described as RAW in `supported_formats`, so this may be a behavioral bug or at least confusing metadata.
- Stream enable writes mode-specific registers before common registers; this order is intentional in code but should be validated against the datasheet because common values may override mode defaults.
- `gc2145_remove()` calls `v4l2_subdev_cleanup()` before `v4l2_async_unregister_subdev()`, while many drivers unregister first; this ordering deserves review for lifetime assumptions.
- Hardware configuration validation requires link frequencies in exact count and order, which is strict for DT authors.
- Page switching is pervasive; a failed intermediate write can leave the sensor on page 3 before later control operations.
- Opaque vendor tables and MIPI FIFO heuristics are high risk for mode/format regressions.

## Test Signals
- `v4l2-compliance` across all media-bus formats and frame sizes, especially RAW mode forcing 720p instead of VGA.
- DT validation/probe tests for lane count, link-frequency order, clock rate, missing optional GPIOs, and chip-ID mismatch.
- Capture tests for each mode and format family, checking MIPI datatype, line word count, FIFO level, Bayer order, and colorimetry metadata.
- Runtime PM tests should verify autosuspend after stream stop and live control writes while streaming.
- Test-pattern and flip controls should be checked per output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/gc2145.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/hi556.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/hi556.c

## Purpose
`hi556.c` is a V4L2 I2C sub-device driver for the Hynix HI556 raw Bayer CSI-2 sensor, matched through ACPI ID `"INT3537"`. It supports four 10-bit SGRBG modes, manual I2C register access, runtime PM, ACPI D0 probe handling, exposure/gain/test-pattern controls, and media-subdev integration.

## Important APIs, Types, and Functions
- Constants define register value widths, 437 MHz link frequency, 19.2 MHz MCLK, two data lanes, 10-bit depth, chip ID, streaming mode register, FLL/LLP timing registers, exposure/gain limits, digital gain channel registers, and pixel-array bounds.
- `struct hi556_reg`, `hi556_reg_list`, `hi556_link_freq_config`, and `hi556_mode` describe register tables, PLL/link settings, mode geometry/crop, timing, and per-mode register lists.
- `struct hi556` stores device/subdev/media pad, control handler, controls, reset GPIO, clock, regulators, current mode, mutex, and identification cache.
- Register tables include a large `mipi_data_rate_874mbps[]` PLL/initialization sequence and per-mode tables for 2592x1944, 2592x1444, 1296x972, and 1296x722.
- `hi556_read_reg()` and `hi556_write_reg()` implement big-endian 16-bit register addressing and 1..4 byte value transfer directly with I2C messages rather than regmap/CCI.
- Controls write analogue gain, digital gain to all four manual white-balance gain registers, exposure, FLL for vblank, and test-pattern state.
- PM callbacks are `hi556_suspend()` and `hi556_resume()` through `DEFINE_RUNTIME_DEV_PM_OPS`.

## Control Flow
Probe first validates fwnode hardware: endpoint availability, two CSI-2 lanes, and advertised 437 MHz link frequency. It allocates state, initializes I2C subdev, obtains optional reset, clock, and regulators, validates 19.2 MHz clock, then checks whether ACPI reports the device already in D0. If full power is present, it resumes non-ACPI-managed resources and verifies chip ID. It initializes mutex, default mode, controls, media entity, async sensor registration, and runtime PM.

Streaming locks the mutex. Enabling resumes runtime PM, identifies the chip if needed, writes link-frequency PLL registers, writes the current mode table, replays controls, then writes `HI556_MODE_STREAMING`. On failure it attempts standby and drops PM. Disabling writes standby and releases PM. Format changes select nearest mode, update link frequency/pixel rate, vblank range/default, and hblank range under the same mutex.

## State and Persistence
The current mode pointer, cached controls, mutex-protected active format/crop, and `identified` flag are persistent software state. Hardware register state is volatile and is reloaded on stream start. The driver handles ACPI D0 probe cases specially: if firmware left the device powered, it reads chip ID during probe and marks runtime PM active; otherwise identification can be delayed until stream start.

## Dependencies and Integration Points
- Uses I2C core directly, V4L2 controls/device/fwnode/subdev, media entity ops, runtime PM, ACPI, GPIO, clock, regulators, and unaligned endian helpers.
- ACPI match table exposes `"INT3537"` and the I2C driver sets `I2C_DRV_ACPI_WAIVE_D0_PROBE`.
- Requires fwnode endpoint with two CSI-2 lanes and matching link frequency.
- Exposes `MEDIA_BUS_FMT_SGRBG10_1X10`, source pad, link validation via `v4l2_subdev_link_validate`, and standard sensor async registration.

## Risks
- Direct I2C helpers return `-EIO` when `i2c_transfer()` or `i2c_master_send()` returns a short positive count; diagnostics lose the exact adapter error.
- `hi556_remove()` does not call `v4l2_subdev_cleanup()`, unlike several newer drivers; confirm whether the older internal-ops/open usage needs cleanup in this tree.
- Runtime PM control writes use `pm_runtime_get_if_in_use()`, so controls changed while suspended depend on stream-start replay.
- ACPI full-power detection and `I2C_DRV_ACPI_WAIVE_D0_PROBE` make probe behavior platform-sensitive.
- Large PLL and mode tables are opaque and critical for MIPI timing; errors can cause non-obvious stream failures.
- Digital gain writes four channel registers sequentially; partial failure can leave channel gains inconsistent.

## Test Signals
- ACPI probe tests for both D0 and non-D0 startup paths, including missing endpoint, lane mismatch, link-frequency mismatch, and wrong clock rate.
- Stream tests for all four modes, verifying FLL/LLP-derived blanking, crop rectangles, pixel rate, and mode-switch control updates.
- Control tests for exposure/vblank coupling, analogue gain, digital gain channel consistency, and test-pattern enable/index mapping.
- Runtime PM tests should check reset/regulator/clock sequencing on suspend/resume and failure unwind from stream start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/hi556.c -->
