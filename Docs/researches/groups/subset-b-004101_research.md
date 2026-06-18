# subset-b-004101 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov8865.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov8865.c

## Purpose
`ov8865.c` is a V4L2 sub-device driver for the OmniVision OV8865 raw Bayer CSI-2 image sensor. It exposes one media source pad, negotiates a small fixed set of 10-bit SBGGR modes, configures the sensor's PLL, MIPI transmitter, timing, binning, black-level correction, ISP gain, and runtime power sequencing, and registers as an I2C camera sensor for OF and ACPI systems.

## Important APIs, types, and functions
- `struct ov8865_sensor` is the device aggregate: I2C client, optional reset/powerdown GPIOs, `dvdd`/`dovdd`/`avdd` regulators, external clock, parsed CSI-2 endpoint, subdev, media pad, mutex, current state, and controls.
- `struct ov8865_state` persists the active mode, media bus code, and a software `streaming` flag across runtime PM suspend/resume.
- `struct ov8865_mode` describes mode-specific geometry, blanking, auto-size settings, binning/variopixel flags, black-level windows, PLL2 choice, and extra register tables.
- `ov8865_read()`, `ov8865_write()`, `ov8865_update_bits()`, and `ov8865_write_sequence()` are raw 16-bit-register/8-bit-value I2C helpers used throughout the driver.
- `ov8865_sensor_init()` performs reset, standby, chip-ID validation, global initialization, charge-pump/MIPI/ISP/BLC setup, and current-mode programming.
- `ov8865_mode_configure()` writes output sizes, HTS/VTS, crop or auto-size, VFIFO, ABLC/zline, binning, BLC anchors, PLL1/PLL2/SCLK, and per-mode tuning registers.
- `ov8865_ctrls_init()` creates exposure, analog gain, red/blue balance, flips, test pattern, hblank/vblank, link frequency, pixel rate, and fwnode controls.
- `ov8865_s_stream()`, `ov8865_suspend()`, and `ov8865_resume()` connect the subdev stream state to runtime PM and hardware standby.
- Pad operations include `enum_mbus_code`, `get_fmt`, `set_fmt`, `enum_frame_size`, selection reporting, and frame interval reporting.

## Control flow
Probe allocates `struct ov8865_sensor`, obtains regulators, parses the graph endpoint as CSI-2 D-PHY, gets optional GPIOs and the external sensor clock, accepts only supported external clock rates, initializes the V4L2 subdev/media entity, creates controls, initializes default state, enables runtime PM in suspended state, and registers the sensor subdev. The probe path does not power the sensor or validate chip ID immediately; hardware programming is deferred to runtime resume.

Runtime resume powers rails and clock, deasserts reset/powerdown, waits for power timing, calls `ov8865_sensor_init()`, applies all cached V4L2 controls through `__v4l2_ctrl_handler_setup()`, and, if software state says streaming was active, exits standby. Runtime suspend enters standby when streaming, powers the sensor down, and attempts to restore streaming if power-down fails.

Format negotiation is mode-table driven. `set_fmt()` rejects active changes while streaming, chooses the requested or default media bus code, finds the nearest mode by output size, updates TRY state or active state, and recalculates vblank, hblank, exposure range, link frequency, and pixel rate. Active state changes only alter software state; registers are written on the next runtime resume/init sequence.

Streaming is lightweight: enabling calls `pm_runtime_resume_and_get()` and writes the standby register to stream on; disabling writes standby and drops the runtime PM reference. The heavy global and mode programming happens on resume.

## State and persistence behavior
The persistent state is in memory only: current mode, bus code, streaming flag, and V4L2 control values. Hardware state is treated as volatile across runtime PM and rebuilt in `ov8865_sensor_init()`. `state.streaming` intentionally survives suspend/resume so resume can restart the stream after reinitialization. The controls handler caches user values while powered off; `ov8865_s_ctrl()` returns success without I2C writes when the device is runtime suspended, and resume replays the handler.

## Dependencies and integration points
The driver depends on Linux I2C, regulator, GPIO descriptor, clock, runtime PM, media controller, V4L2 subdev/control/fwnode APIs, and endpoint link-frequency metadata. It integrates with device tree compatible `ovti,ov8865` and ACPI ID `INT347A`. The external endpoint must describe MIPI CSI-2 data lanes and link frequencies matching the driver's calculated 360 MHz link frequency. It registers as `MEDIA_ENT_F_CAM_SENSOR` through `v4l2_async_register_subdev_sensor()`.

## Risks and edge cases
- PLL, black-level, MIPI, and mode tables encode sensor-specific magic values; mistakes typically appear as no image, corrupted CSI-2 packets, or unstable exposure rather than compile failures.
- Only two external clock rates are supported. Boards with another clock rate fail probe.
- `ov8865_state_mipi_configure()` logs if link frequency is absent from the endpoint but only returns an error for invalid mbus code; unsupported endpoint frequency may leave link-frequency control stale while still setting pixel rate.
- The stream state is a plain flag protected by the driver mutex in most paths, but PM and stream transitions still depend on correct runtime PM reference ordering.
- Control writes are skipped while powered off, so bugs in resume control replay can make cached userspace settings diverge from hardware.
- Selection and frame interval TRY support is incomplete; `get_frame_interval()` explicitly rejects TRY state.

## Test signals
Useful validation signals include successful probe and async subdev registration, chip ID reads during first runtime resume, link-frequency/pixel-rate control values matching the endpoint, mode enumeration for 3264x2448, 3264x1836, 1632x1224, and 800x600, stream-on/off without PM imbalance warnings, vblank-driven exposure range changes, flip/test-pattern register effects, and CSI-2 receiver lock at the expected 10-bit Bayer format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov8865.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9282.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov9282.c

## Purpose
`ov9282.c` is a V4L2 sub-device driver for the OmniVision OV9281/OV9282 monochrome global-shutter CSI-2 sensors. It supports 1280x800, 1280x720, and 640x400 modes, both 10-bit and 8-bit monochrome mbus formats, runtime PM, CCI/regmap access, exposure/gain clustering, horizontal and vertical blanking controls, flips, and flash/strobe timing controls.

## Important APIs, types, and functions
- `struct ov9282` stores the V4L2 subdev, CCI regmap, pad, reset GPIO, input clock, regulators, controls, current mode, current mbus code, vblank cache, and CSI-2 noncontinuous-clock choice.
- `struct ov9282_mode` carries width/height, separate minimum hblank values for continuous and noncontinuous CSI-2 clocking, vblank limits, crop rectangle, link-frequency index, and mode register list.
- `common_regs`, per-mode register arrays, and `bitdepth_regs` drive the hardware programming sequence used when streams are enabled.
- `ov9282_update_controls()` synchronizes link frequency, pixel rate, hblank range, and vblank range after mode or bit-depth changes.
- `ov9282_update_exp_gain()` writes exposure and analogue gain under group hold and updates the flash-duration range based on exposure time.
- `ov9282_try_ctrl()` snaps requested flash duration to the nearest representable strobe span.
- `ov9282_enable_streams()` and `ov9282_disable_streams()` implement the pad stream API; the legacy video `s_stream` operation is provided by `v4l2_subdev_s_stream_helper`.
- `ov9282_parse_hw_config()`, `ov9282_power_on()`, `ov9282_detect()`, and `ov9282_probe()` implement hardware validation and registration.

## Control flow
Probe initializes the subdev, parses hardware configuration, initializes a 16-bit CCI regmap, powers the sensor, reads the ID, selects the default 1280x720 Y10 mode, creates controls, initializes the media entity and finalized subdev state, enables runtime PM, registers the sensor subdev, then idles the device.

Hardware configuration parsing requires a fwnode, optional reset GPIO, 24 MHz input clock, named regulators, exactly two CSI-2 data lanes, and link-frequency metadata containing 400 MHz. It records whether the endpoint requests noncontinuous CSI-2 clocking because that changes the hblank minimum.

Stream enable resumes the device, writes common registers, writes RAW10 or RAW8 bit-depth-specific PLL/analog-core registers, writes the current mode table, replays the V4L2 control handler so exposure/gain/blanking/flash settings reach hardware, then writes mode select streaming. Any failure drops the runtime PM reference. Stream disable writes standby and releases PM.

Format negotiation enumerates Y10 and Y8 codes, nearest supported frame sizes, and crop rectangles. Active `set_fmt()` changes current mode and code only after `ov9282_update_controls()` succeeds. TRY format uses subdev state. Crop reporting returns mode-specific crop for active state and standard pixel-array bounds for native/default/bounds targets.

## State and persistence behavior
Current mode, current mbus code, vblank, noncontinuous-clock mode, and control values are in-memory state. Register state is reconstructed each stream enable rather than kept live during runtime suspend. Exposure and analogue gain are clustered so they are updated together. Flash duration is stored as a V4L2 control in microseconds but written as sensor strobe-frame-span units after `try_ctrl()` quantization.

## Dependencies and integration points
The driver uses V4L2 CCI helpers (`devm_cci_regmap_init_i2c`, `cci_read`, `cci_write`, `cci_multi_reg_write`), runtime PM, regulator bulk APIs, a sensor input clock, fwnode endpoint parsing, media controller subdev registration, V4L2 events, and the new subdev stream pad operations. It binds to OF compatibles `ovti,ov9281` and `ovti,ov9282`.

## Risks and edge cases
- The chip ID constant is `0x9281`, so both OV9281 and OV9282 compatibles depend on that shared identity behavior.
- Flash/strobe span conversion is empirical and integer-rounded; unusual hblank/framerate values may produce approximate rather than exact flash durations.
- Hblank writes divide total line length by two before writing HTS, which is sensor-specific and easy to break if timing units are changed.
- The common register table must not include software reset because power-on writes MIPI clock behavior first; reintroducing reset there would erase earlier state.
- `ov9282_init_controls()` returns `ctrl_hdlr->error` when either that or fwnode parsing failed; if fwnode parsing fails without setting handler error, error reporting can be misleading.
- Runtime PM is central to control writes. Controls set while powered off are cached and rely on stream-enable handler setup.

## Test signals
Test by probing with valid two-lane 400 MHz endpoint metadata, confirming ID detection, enumerating Y10/Y8 codes and all three frame sizes, switching between 8-bit and 10-bit formats, verifying hblank minimum changes for noncontinuous clock endpoints, streaming on/off repeatedly, checking exposure/gain group updates, and validating flash duration quantization through `VIDIOC_TRY_EXT_CTRLS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9282.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9640.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov9640.c

## Purpose
`ov9640.c` is an older V4L2 sub-device driver for the OmniVision OV9640/OV96xx parallel-bus camera sensor. It supports fixed discrete resolutions from QQCIF through SXGA, UYVY/RGB555/RGB565 output encodings, basic horizontal and vertical flip controls, manual power sequencing with GPIOs and an `mclk`, and direct SCCB-style I2C register programming.

## Important APIs, types, and functions
- `struct ov9640_priv` is defined in `ov9640.h` and stores the subdev, control handler, clock, power/reset GPIOs, model, and revision.
- `ov9640_regs_dflt`, resolution-specific register arrays, and YUV/RGB matrix arrays are static programming tables.
- `ov9640_reg_read()`, `ov9640_reg_write()`, and `ov9640_reg_rmw()` implement byte-register I2C access. Writes perform a readback because the source notes a suspected hardware quirk.
- `ov9640_s_power()` asserts/deasserts camera power and reset GPIOs and prepares/enables or disables `mclk`.
- `ov9640_res_roundup()` rounds requested dimensions up to the nearest supported resolution.
- `ov9640_alter_regs()` derives color-encoding deltas for COM registers.
- `ov9640_write_regs()` selects the resolution table, merges color deltas into key registers, then writes the color matrix table.
- `ov9640_set_fmt()` validates pad 0, rounds dimensions, chooses color space/code, and programs hardware for active formats.
- `ov9640_video_probe()` powers the device, reads product/manufacturer IDs, records revision, applies controls, and powers off again.

## Control flow
Probe allocates the private state, gets required named GPIOs for camera power and reset, initializes the I2C subdev, creates hflip/vflip controls, obtains the `mclk`, probes the powered sensor identity, and registers the subdev. No media pad entity is initialized in this driver, unlike newer sensor drivers.

Power-on drives the power GPIO high, enables `mclk`, waits, and releases reset. Power-off asserts reset, disables the clock, and drops power. The driver exposes `.s_power` rather than runtime PM.

Active format setting performs a soft reset through COM7, writes default gamma/system registers, waits 150 ms, then writes resolution and color-matrix registers. TRY format only normalizes the requested frame format. Streaming operation is a stub returning success; the sensor effectively becomes configured by format/power rather than stream state.

## State and persistence behavior
The driver stores revision/model and control handler state only. It does not cache active frame format in `struct ov9640_priv`; `set_fmt()` programs the hardware directly for active formats. Because hardware registers are reset and reprogrammed during active format changes, userspace format state is not recoverable from driver memory after power loss except through the next `set_fmt()`.

## Dependencies and integration points
The file depends on Linux I2C transfers, GPIO descriptors, sensor clock acquisition, V4L2 async subdev registration, V4L2 controls, and V4L2 parallel bus configuration. `ov9640_get_mbus_config()` reports a parallel bus with rising PCLK, master mode, active-high sync and data. The driver binds through the I2C ID table `ov9640`.

## Risks and edge cases
- `.s_stream` is a no-op, so bridge drivers must tolerate stream state not being explicitly reflected in sensor registers.
- Format state is not cached, which limits accurate `get_fmt()` behavior; this driver only implements `set_fmt`, enumeration, selection, and bus config.
- GPIO names use legacy strings with spaces (`"Camera power"`, `"Camera reset"`), which are fragile for fwnode descriptions.
- Register programming is direct and table-driven; failures partway through can leave the sensor partially configured.
- The readback after every write hides the original write result if readback fails: `ov9640_reg_write()` logs readback failure but returns success after a successful write.
- The driver is not media-controller complete compared with newer sensors; integration may depend on older host drivers.

## Test signals
Useful signals are successful power-on ID reads for OV9640 V2/V3, correct manufacturer ID logging, hflip/vflip register changes in `MVFP`, active format programming for each supported resolution and code, parallel mbus configuration reported to the host, and image capture after `set_fmt()` despite no-op stream calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9640.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9640.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov9640.h

## Purpose
`ov9640.h` is the private companion header for `ov9640.c`. It defines the OV9640 register map, bit masks, known chip revisions, supported resolution constants, small register-table structures, and the driver's private state structure.

## Important APIs, types, and definitions
- Register macros cover sensor gain, color gains, COM registers, timing/crop registers, manufacturer/product IDs, matrix registers, lens correction registers, gamma tables, and clock/reset/pixel-format controls.
- Bit masks define clock divider behavior (`OV9640_CLKRC_*`), mirror/flip bits, COM1/COM2/COM3/COM4/COM5/COM6/COM7 mode flags, YUV byte order, gamma/matrix options, RGB output range, and RGB555/RGB565 selection.
- `OV9640_V2`, `OV9640_V3`, and `VERSION(pid, ver)` are used by the C file to validate the detected sensor revision.
- The anonymous resolution enum defines supported widths from QQCIF through SXGA; `H_SXGA` defines the maximum height.
- `struct ov9640_reg_alt` holds per-format deltas for COM7/COM12/COM13/COM15.
- `struct ov9640_reg` represents one byte register write.
- `struct ov9640_priv` is the driver's state container: subdev, control handler, clock, power/reset GPIOs, model, and revision.

## Control flow
The header has no executable control flow. Its constants drive the C file's format-selection path: requested output code is translated into `ov9640_reg_alt`, selected resolution chooses a `struct ov9640_reg` table, and COM register values are ORed with the alteration fields before writing to hardware.

## State and persistence behavior
The header defines state layout but does not persist anything itself. `struct ov9640_priv` stores only software state that lives for the bound I2C device. Register definitions are stateless constants used to rebuild hardware configuration.

## Dependencies and integration points
This header is included only by `ov9640.c` in this subset and relies on V4L2 types being included before use for `struct v4l2_subdev`, `struct v4l2_ctrl_handler`, and GPIO/clock pointer types. It is tightly coupled to the OV9640 driver's register-table programming style and is not a generic public API.

## Risks and edge cases
- Many register and bit definitions are sensor-specific magic values with limited inline documentation; incorrect reuse can produce silent image corruption.
- The resolution enum defines widths only, with only SXGA height named separately; callers must keep width/height tables synchronized elsewhere.
- The include guard name still references an old `media/video` path, which is harmless but signals legacy origin.
- Since the private state struct is in the header, unrelated changes to state layout require recompiling all include users, though currently the include scope appears narrow.

## Test signals
The header is indirectly validated by compiling `ov9640.c`, detecting OV9640 V2/V3 IDs, selecting all output formats, checking flip bits, and verifying that each register macro produces expected bus writes during active `set_fmt()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9640.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9650.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov9650.c

## Purpose
`ov9650.c` is a V4L2 sub-device driver for OV9650 and OV9652 parallel/SCCB CMOS sensors. It supports SXGA, VGA, and QVGA output sizes, multiple YUV byte orders, selectable frame intervals, auto/manual exposure, auto/manual gain, auto/manual white balance, brightness, saturation, sharpness, flips, banding filter, and test pattern control.

## Important APIs, types, and functions
- `struct ov965x` is the main state: subdev, media pad, bus type, optional powerdown/reset GPIOs, clock and frequency, mutex, regmap, exposure row interval, detected ID, current frame size, TSLB byte-order value, current format, control cluster state, frame interval, streaming count, power count, and pending format flag.
- `struct ov965x_ctrls` groups controls into V4L2 auto clusters for white balance, gain, exposure, flips, and other image controls.
- `ov965x_init_regs`, `frame_size_reg_addr`, per-resolution format arrays, `ov965x_framesizes`, `ov965x_formats`, and `ov965x_intervals` encode sensor setup, geometry, byte ordering, and frame-rate choices.
- `ov965x_read()`, `ov965x_write()`, and `ov965x_write_array()` use an SCCB regmap.
- `ov965x_s_power()` reference-counts power, controls clock/GPIOs, writes initial registers on power-on, and marks frame format and controls for later application.
- `ov965x_s_ctrl()` dispatches to white balance, brightness, exposure, gain, flip, banding, saturation, sharpness, and test-pattern helpers; volatile getters read hardware auto exposure/gain.
- `ov965x_set_fmt()` chooses nearest frame size and supported mbus code, updates active or TRY format, resets frame interval, and recalculates exposure range.
- `ov965x_s_stream()` applies pending frame/timing parameters, replays cached controls, and writes COM2 soft-sleep/active state.
- `ov965x_detect_sensor()` powers the device temporarily and validates OV9650/OV9652 product IDs.

## Control flow
Probe initializes SCCB regmap, requires fwnode-backed clock/GPIO properties, initializes the mutex/subdev/media entity, creates controls, sets default format/frame size/frame interval, powers the sensor long enough to detect its ID, updates exposure control limits, and registers the async subdev.

Power-on is reference-counted: the first transition enables the clock, deasserts powerdown/reset, waits, writes the initialization table, and marks `apply_frame_fmt` and `ctrls.update`. Power-off asserts reset and powerdown and disables the clock. Stream-on applies frame format if pending, writes gamma and color matrix, configures banding filter for the current interval, replays controls if pending, then clears soft sleep. Stream-off writes COM2 sleep.

Format and frame-interval control are linked. Active format changes are rejected while streaming, update current frame size and TSLB byte-order register value, set `apply_frame_fmt`, and reset frame interval to the minimum available for that size. Frame-interval requests choose the supported interval with smallest error for the current size.

## State and persistence behavior
The driver maintains software copies of current format, frame size, frame interval, power count, streaming count, pending format flag, and exposure row interval. Many controls are cached while powered off; `ov965x_s_ctrl()` returns success without writing hardware when `power == 0`. On the next stream-on, pending controls are replayed by `v4l2_ctrl_handler_setup()`. Auto exposure and auto gain controls are volatile and read sensor registers when queried while powered.

## Dependencies and integration points
The file depends on regmap SCCB support, V4L2 subdev/control/event/media APIs, GPIO descriptors, sensor clock APIs, and fwnode properties. It registers a media source pad and supports OF compatibles `ovti,ov9650` and `ovti,ov9652` plus I2C IDs `OV9650` and `OV9652`. It is a parallel-bus style sensor driver rather than a CSI-2 driver.

## Risks and edge cases
- Power and streaming are integer reference counts; imbalance can leave the device powered or streaming unexpectedly, though negative counts are warned.
- `ov965x_set_white_balance()` appears to use `REG_COM8` as a bit mask instead of `COM8_AWB`, which is a likely bug because `REG_COM8` is the register address.
- `ov965x_set_sharpness()` decrements unsigned `value`, so value 0 underflows before range logic; this relies on later masking behavior and is fragile.
- Controls changed while powered off are not applied until stream-on handler setup, so stream paths must remain correct for cached control persistence.
- Timing math assumes known 24 MHz-derived divider defaults for intervals; alternate clock frequencies may need careful validation.
- Register tables and empirical QVGA values are hardware-tuned and difficult to verify without image capture.

## Test signals
Validation should cover ID detection for both OV9650 and OV9652, media pad registration, supported YUV code enumeration, SXGA/VGA/QVGA size enumeration, frame interval selection per size, power/stream reference count warnings, cached control replay after power cycling, volatile auto-gain/exposure reads, and visible effects for brightness, saturation, sharpness, banding, flips, and test pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9734.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ov9734.c

## Purpose
`ov9734.c` is a V4L2 sub-device driver for the OmniVision OV9734 1-lane CSI-2 raw Bayer sensor. It exposes one fixed 1296x734 10-bit SGRBG mode, configures PLL/link timing, controls exposure, analogue and digital gain, vblank/hblank, test pattern, and registers through ACPI.

## Important APIs, types, and functions
- `struct ov9734` stores device, clock, subdev, media pad, control handler, control pointers, current mode, and mutex.
- `struct ov9734_mode` describes width, height, HTS, default/min VTS, link-frequency index, and the mode register table.
- `struct ov9734_link_freq_config` connects the 180 MHz link-frequency menu entry to a PLL register list.
- `ov9734_read_reg()` and `ov9734_write_reg()` implement 16-bit register I2C transfers with variable 1-4 byte values using unaligned big-endian helpers.
- `ov9734_write_reg_list()` writes register tables with ratelimited diagnostics.
- `ov9734_update_digital_gain()` uses sensor group access to update red, green, and blue digital gains atomically.
- `ov9734_set_ctrl()` applies analogue gain, digital gain, exposure, vblank/VTS, and test pattern when runtime PM says the device is active.
- `ov9734_start_streaming()` writes PLL registers, mode registers, cached controls, then mode-select streaming.
- `ov9734_check_hwcfg()` validates endpoint link-frequency metadata; `ov9734_probe()` validates 19.2 MHz clock, identifies the chip, initializes controls/media entity/runtime PM, and registers the subdev.

## Control flow
Probe first checks the fwnode endpoint and required link frequency, allocates state, acquires the clock, validates that it is 19.2 MHz, initializes the subdev, reads the chip ID, initializes mutex and controls, sets up media entity/source pad, enables runtime PM as already active under ACPI PM, idles the device, and registers the sensor.

Streaming is protected by the mutex. Enable resumes runtime PM, writes the data-rate register list, writes the sole mode table, replays controls, and writes mode-select streaming. On failure it stops streaming and releases PM. Disable writes standby and releases PM.

Format handling is minimal because there is one mode and one mbus code. `set_format()` finds nearest mode, fills SGRBG10 format, updates active mode and controls for active requests, and stores TRY state for TRY requests. Hblank is read-only and derived from HTS, link frequency, data lanes, and SCLK. Vblank changes update exposure max before writing VTS.

## State and persistence behavior
Current mode and controls live in memory. Register state is rebuilt at stream start and not preserved across runtime PM transitions. Control writes are skipped when the device is not active and are later replayed during stream start. Digital gain uses group hold/launch to keep color channels synchronized.

## Dependencies and integration points
The driver uses Linux I2C, ACPI matching, sensor clocks, runtime PM, V4L2 controls/subdev/fwnode helpers, and media entity APIs. It requires endpoint link frequencies containing 180 MHz and binds to ACPI ID `OVTI9734`. It exposes `MEDIA_ENT_F_CAM_SENSOR` and uses `v4l2_async_register_subdev_sensor()`.

## Risks and edge cases
- The driver checks endpoint link frequencies but not the number of data lanes in `ov9734_check_hwcfg()`, despite the hardware constant saying one lane.
- Probe identifies the module before explicit clock enable in this file, relying on ACPI/i2c-core power-domain behavior noted in comments.
- `ov9734_set_stream()` contains a duplicated unreachable `return ret;`, harmless but a code-quality signal.
- Only one hard-coded mode exists; any board needing a different crop/timing requires table work.
- Register tables contain many opaque tuning values and a duplicate-looking `0x380f` write, so table ordering matters.
- Controls set while runtime suspended rely on handler replay at stream start.

## Test signals
Key signals are successful ACPI probe, 19.2 MHz clock validation, chip ID `0x9734`, link-frequency validation at 180 MHz, enumeration of SGRBG10 1296x734 only, correct read-only hblank and pixel-rate controls, vblank/exposure range coupling, digital gain group update behavior, test pattern output, and repeated runtime PM stream cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ov9734.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm20.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm20.c

## Purpose
`rdacm20.c` is a V4L2 sub-device driver for the IMI RDACM20 GMSL camera module, which combines an OmniVision OV10635 sensor with a Maxim MAX9271 serializer. It initializes the serializer, resets and readdresses the remote sensor, writes a large OV10635 configuration table, exposes a fixed 1280x800 UYVY 16-bit parallel-style media bus format, and toggles the GMSL serial link for streaming.

## Important APIs, types, and functions
- `struct rdacm20_device` stores the parent device, embedded `struct max9271_device`, dummy I2C client for the remote OV10635, V4L2 subdev, media pad, pixel-rate control handler, and two firmware-provided addresses.
- `ov10635_regs_wizard` is the large static initialization sequence for sensor timing, ISP, FIFO, embedded MCU/configuration blocks, FSIN, and output behavior.
- `ov10635_read16()`, `__ov10635_write()`, `ov10635_write()`, and `ov10635_set_regs()` implement 16-bit sensor register access through the remote I2C path.
- `rdacm20_initialize()` is the core hardware bring-up sequence for MAX9271 and OV10635.
- `rdacm20_s_stream()` maps stream enable/disable directly to `max9271_set_serial_link()`.
- `rdacm20_get_fmt()` exposes fixed width, height, UYVY8_1X16 code, RAW colorspace, 601 encoding, full range, and no transfer function.
- `rdacm20_probe()`, `rdacm20_remove()`, and `rdacm20_shutdown()` manage dummy client lifetime, subdev registration, and shutdown stream-off.

## Control flow
Probe reads a two-entry `reg` firmware property for serializer and translated sensor addresses, creates a dummy OV10635 client at the default address, initializes hardware, creates the V4L2 subdev and fixed pixel-rate control, initializes the media source pad, and registers the async subdev.

Initialization wakes the serializer, disables the serial link while no valid pixel clock exists, configures MAX9271 reverse-channel I2C timing, asserts the remote sensor reset via serializer GPIO, configures the GMSL link, verifies serializer ID, changes serializer address, releases sensor reset, retries OV10635 ID reads, changes the sensor I2C address, writes the large sensor register table, logs identification, and raises the serializer reverse-channel threshold.

Streaming does not touch the sensor mode; it only enables or disables the MAX9271 serial link. Shutdown explicitly disables the serial link to avoid transmitting during reset/reboot.

## State and persistence behavior
The driver stores only fixed module state and rewritten I2C addresses. The OV10635 configuration is programmed once during probe; there is no runtime PM, mode switching, or cached format state. If the remote module loses power after probe, the driver has no automatic reinitialization path except reprobe. The serial link state is delegated to `max9271_set_serial_link()`.

## Dependencies and integration points
The driver depends on I2C, firmware properties, V4L2 async subdev/media/control APIs, and the local `max9271.h` serializer helper API. It binds to OF compatible `imi,rdacm20`. It creates an extra dummy I2C client for the remote OV10635 and depends on the serializer's I2C translation/reverse channel being configured before sensor access.

## Risks and edge cases
- The sensor register table is very large, opaque, and includes MCU/configuration writes; partial failure leaves hardware in unknown state.
- Probe-time-only initialization means power glitches or deserializer resets after probe are not recovered.
- The `reg` firmware property must contain exactly the expected two addresses; incorrect values break address reassignment or translation.
- `__ov10635_write()` contains duplicated debug logging, harmless but noisy at high debug levels.
- The fixed format uses `V4L2_COLORSPACE_RAW` with UYVY/YCBCR metadata, which may be surprising to consumers.
- TODO comments flag possible conflicts with embedded MCU startup and reverse-channel threshold assumptions.

## Test signals
Validation signals include successful MAX9271 ID verification, OV10635 ID `0xa635` after retries, successful sensor address change, completion of the full register table, fixed format enumeration, pixel-rate control at 44 MHz, stream enable/disable toggling the serial link, and shutdown forcing stream off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm21.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm21.c

## Purpose
`rdacm21.c` is a V4L2 sub-device driver for the IMI RDACM21 GMSL camera module, built around a MAX9271 serializer, an OV490 ISP, and an OV10640 sensor. It configures the serializer, maps the OV490 over remote I2C, powers and checks the OV10640 through OV490 SCCB proxy registers, applies OV490 firmware/workaround registers, reads the active ISP output size, and exposes a fixed YUYV8_1X16 source format.

## Important APIs, types, and functions
- `struct rdacm21_device` contains the parent device, MAX9271 serializer, dummy OV490 I2C client, V4L2 subdev, media pad, current frame format, pixel-rate control handler, address pair, and cached OV490 page.
- `ov490_regs_wizard` is the static OV490 configuration sequence for DVP, embedded lines, PCLK workaround, FSIN timing, OV10640 FSIN/HFLIP behavior, and host commands.
- `ov490_read()`, `ov490_write()`, `ov490_set_page()`, `ov490_read_reg()`, and `ov490_write_reg()` implement paged 32-bit OV490 register access through 16-bit page registers plus 16-bit offsets.
- `ov10640_power_up()` controls OV490 GPIO registers to power and reset the OV10640.
- `ov10640_check_id()` uses OV490 SCCB slave proxy registers and host command triggering to read the OV10640 ID.
- `ov490_initialize()` validates the OV490 ID, waits for firmware output enable, checks OV10640 ID, writes OV490 configuration, reads firmware-provided output dimensions, and sets DVP bus width/order.
- `rdacm21_initialize()` sequences MAX9271 setup, address translation, reset release, OV490 initialization, and reverse-channel threshold configuration.
- `rdacm21_s_stream()` enables/disables the MAX9271 serial link.

## Control flow
Probe reads the two-address `reg` property, creates a dummy OV490 I2C client at the default address, initializes the module, sets up the subdev and fixed pixel-rate control, initializes the source pad, and registers the async subdev.

Module initialization wakes MAX9271, disables the serial link, configures reverse-channel I2C, verifies serializer ID, holds OV490 in reset via serializer GPIO, configures GMSL, readdresses the serializer, installs I2C translation for the OV490, releases OV490 reset, and runs OV490 initialization. OV490 initialization powers the OV10640 via OV490 GPIOs, retries OV490 ID reads until firmware exits reset, waits up to 300 ms for frame output enable, checks OV10640 communication through SCCB proxy registers, writes the OV490 wizard table with inter-write delays, reads output width/height from ISP registers, and sets DVP control.

Streaming only gates the MAX9271 serial link after the ISP is expected to provide a valid pixel clock. Format get/set both return the current fixed format derived from the OV490 firmware.

## State and persistence behavior
`last_page` caches the selected OV490 high/low page to avoid redundant page writes. `fmt.width` and `fmt.height` persist the output size read from OV490 firmware during probe. There is no runtime PM or reinitialization state machine. Hardware setup is one-shot at probe, while stream state is held by the serializer helper.

## Dependencies and integration points
The driver depends on I2C, firmware properties, V4L2 async subdev/media/control APIs, and `max9271.h`. It binds to OF compatible `imi,rdacm21`, creates a dummy client for the remote OV490, and depends on MAX9271 address translation for access to the ISP. It exposes a camera-sensor media entity with a single source pad and a fixed 55 MHz pixel-rate control.

## Risks and edge cases
- `rdacm21_subdev_ops` initializes `.pad` twice; this is harmless duplicate assignment but should be cleaned if the file is touched.
- One-shot probe initialization cannot recover if the remote ISP/sensor or serializer resets later.
- OV490 SCCB proxy handling is explicitly undocumented in comments; register names are arbitrary and fragile.
- Firmware readiness and output dimensions are inferred from OV490 registers, so firmware changes can alter exposed format without driver table changes.
- Large opaque register sequences and fixed delays make failures timing-sensitive.
- Remove unregisters controls and dummy client but does not call `media_entity_cleanup()`, unlike most media entity users.

## Test signals
Useful validation includes MAX9271 verification, successful address translation to the OV490, OV490 ID `0x0490`, firmware output-enable within timeout, OV10640 high ID `0xa6`, completion of OV490 register writes, nonzero width/height read from ISP registers, fixed YUYV8_1X16 format reporting, 55 MHz pixel-rate control, and serial-link toggling on stream start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm21.c -->
