# subset-b-004105 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6420.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tea6420.c

Purpose: Implements a small V4L2 I2C subdevice driver for the SGS Thomson TEA6420 audio matrix. The chip routes one of five stereo inputs, or a mute input, to one of four stereo outputs and supports per-output gain encoded in the routing output argument.

Important APIs, types, and functions: `tea6420_s_routing()` is the only behavioral V4L2 operation. It receives `input`, `output`, and `config` through `v4l2_subdev_audio_ops.s_routing`, extracts gain from the high nibble of `output`, validates input 1..6, output 1..4, and even gain 0/2/4/6, then builds the single command byte expected by the chip. `tea6420_probe()` checks `I2C_FUNC_SMBUS_WRITE_BYTE`, allocates a devm-managed `v4l2_subdev`, initializes it with `v4l2_i2c_subdev_init()`, and mutes all four outputs. `tea6420_remove()` unregisters the subdev. The module is bound through the `"tea6420"` I2C device id.

Control flow: probe is adapter capability check, subdev registration, then four initial `tea6420_s_routing(sd, 6, output, 0)` calls. Runtime routing is direct: validate parameters, encode output bits, input bits, and the inverted gain code, write one byte with `i2c_smbus_write_byte()`, and return `-EIO` on any nonzero SMBus result.

State and persistence: The driver keeps no software route cache beyond the device's hardware state. All routing state persists only in the TEA6420 until overwritten or power-cycled. Allocation is devm-managed, and removal only unregisters the V4L2 subdev.

Dependencies and integration points: Depends on Linux I2C SMBus byte write support and V4L2 subdev audio routing. The companion header supplies routing constants to board or bridge drivers. Logging uses `v4l2_dbg()` and the module `debug` parameter.

Risks: The routing API overloads the output parameter with gain bits, so callers must OR output constants with `TEA6420_GAIN*` values exactly. The initialization error path sums return codes from four writes, which is enough to detect failure but loses the first precise error. There is no locking or shadow state, so concurrent routing calls rely on upper layers to serialize if needed.

Test signals: Useful tests are probe failure on missing `I2C_FUNC_SMBUS_WRITE_BYTE`, valid routing byte generation for all input/output/gain combinations, rejection of invalid input/output/gain values, and initialization issuing four mute writes. Hardware or I2C mock tests should verify an SMBus write failure returns `-EIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6420.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6420.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tea6420.h

Purpose: Defines the public constants used by TEA6420 users to request audio matrix routes through the V4L2 subdev routing callback.

Important APIs, types, and functions: This header has no functions or types. It exposes four output pin constants `TEA6420_OUTPUT1` through `TEA6420_OUTPUT4`, six input pin constants `TEA6420_INPUT1` through `TEA6420_INPUT6`, and four gain encodings `TEA6420_GAIN0`, `TEA6420_GAIN2`, `TEA6420_GAIN4`, and `TEA6420_GAIN6`.

Control flow: None. Consumers combine one output constant with one gain constant in the `output` argument of `.s_routing`, and pass one input constant as the `input` argument.

State and persistence: None. The header only defines compile-time constants. Hardware state is owned by `tea6420.c`.

Dependencies and integration points: Included by `tea6420.c` and intended for bridge drivers that need readable names for route setup. The gain constants are already shifted into the high bits expected by `tea6420_s_routing()` when it extracts `(output >> 4) & 0xf`.

Risks: The comments label the output constants under "input pins" and input constants under "output pins", which is misleading even though the macro names are clear. `TEA6420_INPUT6` represents the mute input according to the driver, not a normal external source. The header contract relies on callers knowing that gain is encoded into the output argument rather than a separate configuration field.

Test signals: Compile-time users should be checked for correct argument placement, especially that `TEA6420_OUTPUTn | TEA6420_GAINx` is passed as output and `TEA6420_INPUTn` as input. Static checks can catch invalid constants only if bridge code uses these names instead of raw integers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6420.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/thp7312.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/thp7312.c

Purpose: Implements a modern V4L2 subdevice driver for the THine THP7312 MIPI camera ISP, including normal camera streaming, runtime PM, CSI-2 lane remapping, sensor description parsing, V4L2 controls, and a firmware-upload path for 2-wire slave boot mode.

Important APIs, types, and functions: `struct thp7312_device` is the central state container, holding the V4L2 subdev, media pad, CCI regmap, regulators, input clock, reset GPIO, parsed lane remaps, sensor model data, controls, focus state, firmware-upload state, and firmware version. Mode support is described by `struct thp7312_mode_info` and `struct thp7312_frame_rate`; the driver supports YUYV output and fixed 1080p, 2048x1536, 4K, and 4160x3120 modes with per-mode frame rates and link frequencies. Key functions are `thp7312_parse_dt()`, `thp7312_power_on()`, `thp7312_set_mipi_lanes()`, `thp7312_set_fmt()`, `thp7312_set_frame_interval()`, `thp7312_s_stream()`, `thp7312_s_ctrl()`, `thp7312_init_controls()`, and the `thp7312_fw_*` firmware upload callbacks.

Control flow: probe allocates state, initializes the CCI I2C regmap, parses OF endpoint and child sensor nodes, gets regulators, clock, and reset GPIO, then branches by boot mode. In flash-upload mode it powers the chip enough to register `firmware_upload_register()`. In normal SPI-master mode it initializes a source-pad camera subdev, powers on, reads firmware version, creates controls, finalizes active subdev state, enables runtime PM with autosuspend, and registers asynchronously. Streaming takes the active-state lock. Disable writes output disable and drops PM usage. Enable resumes PM, programs color format and mode/rate registers, applies controls once after resume, then enables output.

State and persistence: Software state includes active subdev format/interval, `link_freq`, `ctrls_applied`, `focus_state`, firmware version, and upload cancellation flag. Runtime suspend powers off regulators and clock and clears `ctrls_applied`, forcing controls to be replayed on next stream enable. Hardware mode, controls, and lane remap are register state and are not persistent across power loss. Firmware upload writes to external flash and is persistent.

Dependencies and integration points: Integrates with V4L2 async subdev registration, media controller as `MEDIA_ENT_F_CAM_SENSOR`, V4L2 fwnode parsing, CCI regmap helpers, runtime PM, regulator/clock/GPIO frameworks, Linux firmware-upload APIs, SPI NOR command constants, and custom uAPI controls from `<uapi/linux/thp7312.h>`.

Risks: The focus-state logic is subtle, and the local `continuous` variable is set true for manual and oneshot states despite selecting `CONTINUOUS_*` register values, which deserves hardware-focused validation. Firmware upload has long erase/write sleeps, limited cancellation checkpoints, and a TODO to erase only necessary blocks. Device-tree parsing supports one sensor and requires complete four-lane arrays. Control writes are skipped when the device is suspended, so replay through `ctrls_applied` is essential. Firmware version 40.03 has a power-line-frequency special case that should not regress.

Test signals: Probe tests should cover invalid endpoints, duplicate or unsupported sensors, invalid lane maps, missing supplies/clock/reset, both boot modes, and runtime PM disabled behavior. Streaming tests should verify PM reference balancing, mode/rate register writes, control replay after suspend, and output disable on stop. Control tests should cover focus transitions, noise-reduction clustering, flips, manual white balance, exposure bias, firmware-version-specific flicker handling, and read-only link frequency updates. Firmware upload tests should cover invalid sizes, cancel paths, erase timeout, SRAM bank/chunk splitting, flash verify failure, CRC mismatch, and unregister/power-off on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/thp7312.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ths7303.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ths7303.c

Purpose: Provides a V4L2 I2C subdevice driver for TI THS7303/THS7353 video amplifiers. It programs the per-channel low-pass filter and input/bias bits based on analog standard or digital video timings and gates the channels with stream state.

Important APIs, types, and functions: `struct ths7303_state` stores the subdev, platform channel configuration, current BT timings, standard-id flag, and stream state. `enum ths7303_filter_mode` represents SD interlaced, ED progressive, 720p/1080i, 1080p, and disabled modes. `ths7303_setval()` writes all three channel registers from the selected filter mode and platform-data channel masks. `ths7303_s_std_output()`, `ths7303_s_dv_timings()`, and `ths7303_s_stream()` update state and call `ths7303_config()`. `ths7303_log_status()` reads back registers and decodes bit fields. Advanced debug optionally exposes raw register get/set.

Control flow: probe requires platform data and `I2C_FUNC_SMBUS_BYTE_DATA`, allocates state, initializes the subdev, and programs the default 480i/576i filter. Standard selection marks `std_id`, clears pixel clock, and selects SD filtering for all non-SECAM analog standards, otherwise disables channels. DV timing selection validates BT.656/1120 timings, stores `bt`, clears `std_id`, and reconfigures. Stream disable clears low three channel bits while preserving filter bits; stream enable selects the filter by pixel clock thresholds over 120 MHz, over 70 MHz, over 20 MHz, analog-standard fallback, or disable.

State and persistence: Driver-private state tracks stream, last timings, and whether an analog standard was selected. Hardware register values persist until rewritten. There is no runtime PM or software register cache beyond state fields.

Dependencies and integration points: Depends on board-supplied `struct ths7303_platform_data` from `<media/i2c/ths7303.h>` for channel settings. Integrates as a V4L2 subdev with core log status, video stream/std operations, and pad timing operation. Uses SMBus byte data with a three-attempt write retry loop.

Risks: Platform data is mandatory, so OF-only systems need board glue. `ths7303_config()` does not check errors from the channel-disable read/modify/write sequence when stream is off. Read failures in log paths are stored in `u8`, losing negative error information. Filter selection is purely pixel-clock-threshold based and may be too coarse for unusual timings.

Test signals: Tests should validate probe failure without platform data or SMBus support, default filter programming, exact three-channel values for each filter mode and platform channel masks, stream-off bit clearing, timing validation, threshold boundaries, analog SECAM disable behavior, and error propagation from `ths7303_setval()` writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ths7303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ths8200.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ths8200.c

Purpose: Implements a V4L2 I2C subdevice driver for the TI THS8200 video encoder. It powers, resets, streams, validates DV timings, and programs the encoder display timing generator for progressive RGB output.

Important APIs, types, and functions: `struct ths8200_state` stores the subdev, chip version, power state, and current DV timings. `ths8200_timings_cap` limits accepted timings to BT.656/1120 progressive CEA-861 style ranges from 640..1920 by 350..1080 and 25 MHz..148.5 MHz. `ths8200_s_power()` controls power bits in `THS8200_CHIP_CTL`; `ths8200_s_stream()` asserts/deasserts reset/streaming; `ths8200_core_init()` programs fixed data path and sync defaults; `ths8200_setup()` translates `v4l2_bt_timings` into many DTG1/DTG2 registers; pad ops expose set/get/enum/cap DV timings.

Control flow: probe checks SMBus byte-data support, allocates state, initializes the V4L2 subdev, reads chip version, applies core init, and registers asynchronously. Setting DV timings validates pad 0, validates against the cap, finds a matching timing, clears reduced-FPS flags, caches the timing, and calls `ths8200_setup()`. Setup disables streaming while programming horizontal/vertical timing registers, breakpoint line types, sync widths/delays, polarities, RGB mode, and then re-enables streaming. Remove powers down and unregisters the async subdev.

State and persistence: The driver caches `power_on` and the most recent `v4l2_dv_timings`. Hardware registers are programmed directly with no regmap cache and persist only while the device remains powered. There is no runtime PM integration.

Dependencies and integration points: Uses V4L2 subdev core/video/pad ops, async registration, I2C SMBus byte data, OF matching for `"ti,ths8200"`, and register offsets from `ths8200_regs.h`. Advanced debug optionally exposes raw register access.

Risks: `ths8200_write_and_or()` ignores read and write errors, so many setup failures can be silent. `ths8200_s_stream()` always returns 0 even if writes fail. Setup comments and code target progressive formats; interlaced handling is effectively unsupported by the cap but should stay guarded. Register field packing is dense and easy to regress around MSB/LSB split fields and polarity bits. Power state is software-only and may desynchronize if writes fail.

Test signals: Tests should cover timing validation rejection for bad pad, unsupported resolution, interlaced modes, and out-of-range clocks. Register-write traces for known 720p/1080p timings should validate DTG field packing, h/v totals, sync widths, line breakpoint values, and polarity bits. Remove should write power-down bits and unregister. Fault-injection should show current gaps where write errors are not propagated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ths8200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ths8200_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ths8200_regs.h

Purpose: Provides symbolic register offsets for the THS8200 video encoder. It is the register-map contract consumed by `ths8200.c`.

Important APIs, types, and functions: There are no functions or data types. The header defines offsets for chip control/version, color-space conversion coefficients, data control, display timing generator groups DTG1 and DTG2, DAC controls, clipping/scaling/matrix registers, CGMS registers, and miscellaneous pixel-per-line/filter controls.

Control flow: None. Runtime code uses the macros as addresses passed to SMBus byte-data read/write helpers.

State and persistence: None in the header. Each macro corresponds to a hardware register whose state is managed by the encoder.

Dependencies and integration points: Included by `ths8200.c`. The offsets are tightly coupled to helper code that performs read/modify/write on bit-packed fields, especially combined MSB registers such as `THS8200_DTG1_SPEC_DEH_MSB`, `THS8200_DTG2_HLENGTH_LSB_HDLY_MSB`, and `THS8200_DTG2_VLENGTH1_MSB_VDLY1_MSB`.

Risks: The header contains a duplicate `THS8200_CSM_MULT_RCR_LSB` define at the same value, harmless for compilation but a maintenance smell. It only names offsets, not masks or shifts, so call sites must hand-code bit operations and are vulnerable to field-packing mistakes. No comments document valid bit values beyond broad grouping.

Test signals: Build coverage catches missing include guards or macro spelling. Higher-value tests are generated register-write traces from `ths8200.c`, since this header's correctness is validated by using the offsets to program a known timing and comparing against the THS8200 datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ths8200_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tlv320aic23b.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tlv320aic23b.c

Purpose: Implements a V4L2 I2C subdevice driver for the TLV320AIC23B audio codec in a video-capture context. It initializes codec registers, exposes audio mute as a V4L2 control, and supports setting sample clock frequency.

Important APIs, types, and functions: `struct tlv320aic23b_state` holds the subdev and a V4L2 control handler. `tlv320aic23b_write()` validates codec register numbers, encodes the 7-bit register plus top data bit into the SMBus command byte, retries writes three times, and logs failures. `tlv320aic23b_s_clock_freq()` maps 32 kHz, 44.1 kHz, and 48 kHz to sample-rate register values. `tlv320aic23b_s_ctrl()` implements `V4L2_CID_AUDIO_MUTE`; unmute restores +3.0 dB gain after first writing mute. Probe initializes reset, power, interface format, gain, sample rate, digital activation, and controls.

Control flow: probe checks `I2C_FUNC_SMBUS_BYTE_DATA`, allocates state, initializes subdev ops, writes a fixed codec initialization sequence, creates the mute control, attaches the handler, and applies defaults. Runtime control changes go through the V4L2 control handler. Remove unregisters the subdev and frees controls.

State and persistence: The driver tracks only control-handler state. Register contents are not cached. Codec configuration persists in hardware until reset or power loss. Devm manages state allocation.

Dependencies and integration points: Integrates with V4L2 subdev core log-status and audio `s_clock_freq`; uses V4L2 controls for mute; depends on I2C SMBus byte-data writes. The driver has only an I2C id table and no OF table.

Risks: Initialization write return values are ignored, so probe can succeed with a partially configured codec. `tlv320aic23b_write()` returns `-1` rather than standard negative errno values for invalid register and write failure. Mute handling always writes register 0 first and only restores left-channel register 0, relying on codec semantics for both channels; this should be checked against hardware expectations. Only three fixed sample rates are supported.

Test signals: Tests should verify register encoding for 9-bit codec values, supported/unsupported clock frequencies, mute and unmute write sequences, control-handler error cleanup, and probe behavior under I2C write failures. A useful improvement test would expose ignored initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tlv320aic23b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvaudio.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tvaudio.c

Purpose: Implements a legacy multi-chip V4L2 I2C subdevice driver for simple TV sound decoders and audio mux/processors. It detects many possible chips at shared address ranges, initializes the selected chip from a descriptor table, exposes volume/balance/bass/treble/mute controls when supported, routes audio inputs, and optionally runs a kernel thread to follow detected mono/stereo/language modes.

Important APIs, types, and functions: `struct CHIPDESC` describes each supported chip: name, address range, register count, module enable option, detection callback, initialization callback or command sequence, feature flags, control register mappings, conversion callbacks, audio-mode callbacks, and input maps. `struct CHIPSTATE` stores the subdev, controls, descriptor, shadow register command buffer, mute/radio/input/audio-mode state, timer, and optional kthread. Core helpers are `chip_write()`, `chip_write_masked()`, `chip_read()`, `chip_read2()`, and `chip_cmd()`. Chip-specific sections implement TDA9840, TDA985x, TDA9873, TDA9874, TDA9875, TEA6300/6320/6420, TDA8425, PIC16C54, and TA8874Z behavior.

Control flow: probe allocates state and scans `chiplist` for an enabled descriptor whose address range matches and whose optional `checkit()` passes. It initializes the chip, creates controls based on feature flags, applies default controls, sets up a timer, and starts a thread for descriptors marked `CHIP_NEED_CHECKMODE`. Control writes update the hardware through descriptor register maps and conversion functions. Tuner frequency changes reset audio mode to mono and arm a two-second timer; the thread wakes, reads detected subchannels, chooses the best requested mode still available, writes the audio mode, and re-arms itself. Remove deletes the timer, stops the thread, unregisters the subdev, and frees controls.

State and persistence: `chip->shadow` is a software register mirror used for masked writes and audio-mode updates, but comments note it may be wrong for `chip_cmd()`. `muted`, `input`, `radio`, `audmode`, and `prevmode` are software state. Hardware register state persists until changed or reset. Module parameters globally alter detection and TDA9874 defaults.

Dependencies and integration points: Depends on V4L2 subdev core/tuner/audio/video ops, V4L2 controls, Linux I2C `i2c_master_send`, `i2c_master_recv`, and combined transfers, timers, kthreads, and freezer support. Address constants come from `<media/i2c/tvaudio.h>`.

Risks: The driver is broad and descriptor-driven, so address clashes and false detection are real risks; several chips are disabled by default for that reason. Global module parameters and global TDA9874 state can affect all instances. Shadow-register correctness is explicitly questioned in a FIXME. Some descriptor entries rely on callbacks being present and mutate descriptor flags at runtime if not. Thread/timer behavior must be carefully torn down to avoid wakeups after remove. Some I2C failures are logged but not always propagated through higher-level operations.

Test signals: Tests should cover descriptor matching order, disabled module parameters, each detection callback, masked writes using `inputmask`, control creation by feature flags, volume/balance left/right conversion, mute and route interactions, tuner mode validation, thread wake/selection behavior for mono/stereo/language changes, timer cleanup on remove, and I2C error propagation. Regression tests should include TEA6420 input register `-1` single-byte writes and chips sharing address ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvaudio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp514x.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp514x.c

Purpose: Implements a V4L2 I2C subdevice driver for TI TVP5146/TVP5147 analog video decoders. It detects chip variants, applies variant-specific power-on sequences, configures decoder registers, exposes standard/input/output/control operations, and registers a source-pad media entity for UYVY interlaced analog video.

Important APIs, types, and functions: `struct tvp514x_decoder` stores the subdev, control handler, cached register list, platform data, version, streaming flag, current pixel/mbus formats, supported formats and standards, route selections, media pad, and init sequence. `tvp514x_reg_list_default` is the default register script. `tvp514x_read_reg()` and `tvp514x_write_reg()` perform SMBus byte-data I/O with retries. `tvp514x_write_regs()` executes tokenized register scripts. `tvp514x_detect()` verifies chip IDs. V4L2 operations include `tvp514x_s_std()`, `tvp514x_querystd()`, `tvp514x_s_routing()`, `tvp514x_s_ctrl()`, `tvp514x_s_stream()`, and pad format/frame-interval callbacks.

Control flow: probe obtains platform data from legacy platform data or OF endpoint flags, validates SMBus support, copies `tvp514x_dev` defaults and the register script, selects an init sequence from I2C/OF match data, folds bus polarity into cached registers, sets video standard to auto, initializes the subdev and optional media pad, creates brightness/contrast/saturation/hue/autogain controls, applies defaults, and registers asynchronously. Stream enable writes the variant init sequence, detects the chip, writes cached configuration, and marks streaming. Stream disable writes operation mode power-down. Standard query temporarily powers the ADCs if not streaming, reads current standard/status registers, checks lock bits based on input type, and returns NTSC/PAL or unknown.

State and persistence: The driver keeps a cached register list for controls, standard, routing, and platform polarity. `streaming`, `current_std`, `input`, `output`, and `format` are software state. Hardware state is rebuilt from the cached list on stream enable. No runtime PM is used.

Dependencies and integration points: Integrates with V4L2 async subdev registration, media controller source pad, OF graph/fwnode endpoint parsing, legacy `struct tvp514x_platform_data`, V4L2 controls, and register/token definitions from `tvp514x_regs.h`. I2C and OF match tables map variants to init sequences.

Risks: `decoder->int_seq = i2c_get_match_data(client)` assumes match data is available for all instantiation paths; legacy I2C id `driver_data` may not be returned by that helper on all kernels, so stream enable could dereference NULL if not handled by the core. Register cache indexing assumes register numbers map into the 0x40-entry default array; current writeback uses low registers only, but future high-register caching would overflow. `querystd()` powers the decoder to query but does not restore the previous off state. Try-format support is limited, with FIXME notes around active-state API use. Hue maps only exact +/-180 endpoints specially.

Test signals: Tests should cover OF and platform-data parsing, bus polarity register bits, missing platform data, missing SMBus capability, variant init sequence selection, stream enable failure at init/detect/configure stages, NTSC/PAL standard selection and query lock masks for CVBS/S-Video inputs, routing input/output validation, control writes and cache updates, pad format rejection for unsupported code/field/colorspace/size, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp514x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp514x_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp514x_regs.h

Purpose: Defines the TVP5146/TVP5147 register offsets, status bits, video-standard encodings, register-script tokens, and `struct tvp514x_reg` used by the TVP514x decoder driver.

Important APIs, types, and functions: The header exports macros for analog front-end, video standard, luma/chroma controls, timing windows, formatter controls, status, chip ID, VDP, VBUS, FIFO, and interrupt registers. It defines expected chip IDs `TVP514X_CHIP_ID_MSB`, `TVP5146_CHIP_ID_LSB`, and `TVP5147_CHIP_ID_LSB`; video-standard bits for auto, NTSC, PAL variants, SECAM, and PAL60; status lock bits used by standard query; token constants `TOK_WRITE`, `TOK_TERM`, `TOK_DELAY`, and `TOK_SKIP`; and `struct tvp514x_reg { u8 token; u8 reg; u32 val; }`.

Control flow: None directly. `tvp514x.c` iterates arrays of `struct tvp514x_reg`, using token values to write, skip, delay, or terminate scripts.

State and persistence: None. The definitions describe hardware register state but do not store state themselves.

Dependencies and integration points: Included by `tvp514x.c`. The token structure is shared by the default configuration table and variant init sequences. Status and standard macros are used by the driver's autodetection and lock checking paths.

Risks: The header is broad and primarily offset-based, with few masks beyond standard/status fields, so call sites must manually encode register values. Some comments preserve spelling mistakes from older code, which is harmless but can confuse searches. The token ABI is local to this driver; if new token values are added, `tvp514x_write_regs()` must be extended in lockstep.

Test signals: Build coverage validates macro availability. Functional validation should execute token scripts containing write, skip, delay, and term entries, verify chip ID comparisons, and test status lock-bit combinations for CVBS and S-Video standard detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp514x_regs.h -->
