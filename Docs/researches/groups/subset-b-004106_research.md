# subset-b-004106 Research

This grouped report covers the requested media I2C source files. Each section is source-tree aligned and is delimited for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp5150.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp5150.c

## Purpose

This file implements the V4L2 I2C subdevice driver for Texas Instruments TVP5150A, TVP5150AM1, and TVP5151 analog video decoders. It exposes an analog TV decoder as a V4L2 subdev with optional media-controller connector entities, standard detection, input routing, cropping, VBI sliced/raw support, runtime PM, and optional lock-change IRQ events. It uses `tvp5150_reg.h` for the chip register map and programs the decoder through a regmap-backed SMBus interface.

## Important APIs, Types, And Functions

The central state object is `struct tvp5150`, which embeds `struct v4l2_subdev`, input and output media pads, connector entities, a V4L2 control handler, the active crop rectangle, regmap, IRQ state, current and detected standards, selected input/output route, output-enable mask, device ID/ROM version, and bus type. `struct tvp5150_connector` wraps parsed fwnode connector metadata with a media entity and source pad. `tvp5150_read()`, `tvp5150_write_inittab()`, and direct `regmap_write()`/`regmap_update_bits()` calls form the register access layer.

Key control and video entry points are `tvp5150_s_ctrl()`, `tvp5150_s_std()`, `tvp5150_g_std()`, `tvp5150_querystd()`, `tvp5150_s_stream()`, and `tvp5150_s_routing()`. Pad operations are implemented by `tvp5150_fill_fmt()`, `tvp5150_enum_mbus_code()`, `tvp5150_enum_frame_size()`, `tvp5150_get_selection()`, `tvp5150_set_selection()`, and `tvp5150_get_mbus_config()`. VBI support is concentrated in `tvp5150_vdp_init()`, `tvp5150_g_sliced_vbi_cap()`, `tvp5150_set_vbi()`, `tvp5150_get_vbi()`, `tvp5150_s_raw_fmt()`, `tvp5150_s_sliced_fmt()`, and `tvp5150_g_sliced_fmt()`. Probe/remove are `tvp5150_probe()` and `tvp5150_remove()`, with runtime PM callbacks `tvp5150_runtime_suspend()` and `tvp5150_runtime_resume()`.

## Control Flow

Probe validates I2C functionality, toggles optional `pdn` and `reset` GPIOs, allocates driver state, creates a regmap with readable and volatile register tables, initializes the V4L2 subdev, parses device tree connector and bus endpoints when present, initializes media pads, reads the chip ID and ROM version, creates V4L2 controls, sets the default crop from the detected standard, resets the chip, requests an IRQ when available, registers the async subdev, and enables runtime PM. Reset writes `tvp5150_init_default`, configures shared pins and interrupt polarity depending on whether an IRQ exists, initializes the VDP RAM and line modes, selects the current mux route, and pushes default control values.

Streaming calls `pm_runtime_resume_and_get()`, writes stream-enable defaults, chooses the programmed standard, derives output-enable bits from the media bus type, and enables outputs immediately or only after signal lock when IRQ mode is used. Stream-off clears output bits and drops runtime PM. If IRQ mode is enabled, `tvp5150_isr()` acknowledges interrupt status, updates the cached `lock` boolean, sends `V4L2_EVENT_SOURCE_CHANGE`, and toggles output enable bits based on lock state. Without IRQ, lock is polled through `TVP5150_STATUS_REG_1`.

Input routing flows through either media-controller link setup or legacy `.s_routing`. Media-controller link setup disables active input links before enabling a new connector, handles S-Video as a dual-link input to AIP1A/AIP1B, updates `cur_connector`, and constrains the active TV standard to the connector's supported SDTV set. `tvp5150_selmux()` translates `decoder->input`, `decoder->enable`, and chip revision into `TVP5150_OP_MODE_CTL`, `TVP5150_VD_IN_SRC_SEL_1`, and shared-pin mode bits.

## State And Persistence

Persistent runtime state is in `struct tvp5150`; hardware state is mirrored only selectively. `norm`, `detected_norm`, `rect`, `input`, `output`, `enable`, `oe`, `lock`, `mbus_type`, and connector metadata are the driver-side source of truth between register programming steps. Regmap uses `REGCACHE_MAPLE`, with volatile status, interrupt, line count, FIFO, and VBI read registers excluded from caching. There is no filesystem persistence. State is reset on probe/remove and chip reset, and partially re-applied on stream-on through init tables, controls, standard selection, crop programming, and VBI setup.

## Dependencies And Integration Points

The driver integrates with Linux I2C, regmap, GPIO descriptors, runtime PM, V4L2 async subdev registration, V4L2 controls, V4L2 events, media controller entities and links, fwnode/of-graph connector parsing, and VBI APIs. The output format is fixed to `MEDIA_BUS_FMT_UYVY8_2X8`, alternate fields, and SMPTE170M colorspace. Device-tree integration validates input/output endpoint counts, composite and S-Video connector topology, analog SDTV standard masks, and parallel/BT.656 bus constraints.

## Risks

The file has several hardware-specific edge cases: S-Video link setup must keep two input links consistent; VBI line programming depends on `norm` and returns success-like zero for unsupported line ranges; IRQ mode suppresses outputs until lock, so incorrect lock polarity or interrupt setup can appear as no video; and standard changes affect crop height limits. Some I2C/regmap writes ignore return values in init paths, so partial hardware programming can be hard to diagnose. Device-tree connector validation is strict and may reject boards with nonstandard endpoint layouts. Test-pattern support depends on specific dev_id/ROM combinations and reuses the input mux path.

## Test Signals

Useful test signals are probe logs showing chip ID and ROM version, async subdev registration, media graph links for composite/S-Video connectors, V4L2 standard set/query behavior for NTSC/PAL/SECAM variants, stream-on/off register side effects on output-enable bits, IRQ or poll-based lock transitions, `V4L2_EVENT_SOURCE_CHANGE` delivery, crop bounds for 525/60 and 625/50 standards, VBI capability and line-mode programming, runtime suspend/resume interrupt masking, and debug register/status dumps when `debug` or `CONFIG_VIDEO_ADV_DEBUG` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp5150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp5150_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp5150_reg.h

## Purpose

This header defines the TVP5150 register map and key bit encodings consumed by `tvp5150.c`. It is not a standalone module; it is the symbolic contract between the driver and the TVP5150 hardware register layout.

## Important APIs, Types, And Functions

The file contains only preprocessor definitions. Important groups include input, analog, operation, miscellaneous, autoswitch, luma/chroma, brightness/saturation/hue/contrast, crop, genlock, interrupt, video-standard, device ID, ROM version, status, closed-caption/WSS/VPS/VITC data, teletext filter, VDP configuration RAM, FIFO, line mode, and full-field registers. Bit helpers include `TVP5150_MISC_CTL_*`, `TVP5150_INT_A_LOCK_STATUS`, `TVP5150_INT_A_LOCK`, and `TVP5150_VDPOE`. Video standard constants encode fixed and autoswitch modes for NTSC, PAL variants, NTSC 4.43, and SECAM.

## Control Flow

There is no executable control flow. The register constants are used by the driver init tables, status logging, standard selection and detection, VBI programming, crop programming, IRQ handling, runtime PM, regmap access tables, and debug register operations.

## State And Persistence

The header declares symbolic register addresses, not state. Persistence is entirely in hardware registers and the driver's `struct tvp5150` fields.

## Dependencies And Integration Points

The header expects Linux `BIT()` to be available through included kernel headers in the C file. Its integration point is the TVP5150 driver; external users should not rely on it as a public UAPI.

## Risks

Incorrect constants directly corrupt hardware programming. The `VIDEO_STD_MASK` definition is unusual and should be treated carefully if reused. Reserved ranges are documented only by comments; future writes outside declared readable ranges in the driver may require coordinated updates in both files.

## Test Signals

Validation is indirect: successful chip initialization, correct standard selection/detection, readable debug status dumps, VBI configuration, interrupt lock events, and crop register behavior indicate that the symbolic addresses and bit definitions match the hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp5150_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp7002.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp7002.c

## Purpose

This file implements the V4L2 I2C subdevice driver for the Texas Instruments TVP7002 triple 8/10-bit video and graphics digitizer. It converts analog component/RGB-style video into a digital YUYV 10-bit media bus output and exposes supported DV timings, gain control, format reporting, streaming, and device-tree/platform bus polarity configuration.

## Important APIs, Types, And Functions

`struct tvp7002` stores the V4L2 subdev, control handler, platform configuration, chip revision, streaming flag, current DV timing definition, and optional media source pad. `struct i2c_reg_value` describes register scripts with read/write/reserved type tags. `struct tvp7002_timings_definition` couples V4L2 BT timings with per-mode register scripts, colorspace, field mode, progressive flag, lines-per-frame, and clocks-per-line detection windows.

Register access uses `tvp7002_read()`, `tvp7002_write()`, `tvp7002_read_err()`, `tvp7002_write_err()`, and `tvp7002_write_inittab()` with five SMBus retry attempts. Format and timing APIs include `tvp7002_s_dv_timings()`, `tvp7002_g_dv_timings()`, `tvp7002_query_dv()`, `tvp7002_query_dv_timings()`, `tvp7002_enum_dv_timings()`, `tvp7002_enum_mbus_code()`, `tvp7002_get_pad_format()`, and `tvp7002_set_pad_format()`. The primary control hook is `tvp7002_s_ctrl()` for RGB fine gain registers. Probe/remove are `tvp7002_probe()` and `tvp7002_remove()`.

## Control Flow

Probe obtains platform data from legacy `client->dev.platform_data` or parses an OF endpoint into `struct tvp7002_config`, validates SMBus byte access, allocates state, initializes the V4L2 subdev, reads the chip revision, writes the default register table, applies bus polarity to sync and miscellaneous control registers, programs the default DV timing, initializes a media source entity when enabled, creates a gain control, and registers the async subdev.

The timing path is table-driven. `tvp7002_s_dv_timings()` rejects non-pad-zero and non-BT timings, compares the requested BT timing fields against known timing entries, caches the matching definition, and writes the matching register script. `tvp7002_query_dv()` reads line-frame and clock-line status registers, derives progressive/interlaced state, and finds a matching table entry by lines per frame and optional clocks-per-line range. Streaming is a small impedance switch: `tvp7002_s_stream()` writes `TVP7002_MISC_CTL_2` to low impedance when enabled and high impedance when disabled, then updates the cached `streaming` flag.

## State And Persistence

The durable in-kernel state is the selected `current_timings`, `streaming`, revision, platform bus configuration, and gain control state. Hardware state is initialized by fixed scripts and later mutated by timing selection, gain control, polarity setup, and stream impedance. There is no runtime PM or persistent storage.

## Dependencies And Integration Points

The driver integrates with V4L2 subdev core/video/pad operations, V4L2 DV timings helpers, V4L2 controls, media controller pads, OF graph endpoint parsing, `media/i2c/tvp7002.h` platform configuration, and the local `tvp7002_reg.h` register map. It reports `MEDIA_BUS_FMT_YUYV10_1X20` and supports a finite set of CEA timings such as 720p, 1080i, 1080p, 480p, and 576p.

## Risks

Timing matching uses a `memcmp()` over a subset of `struct v4l2_bt_timings`; future structure changes or fields outside that range may cause surprising acceptance/rejection. The driver does not serialize all I2C operations with a mutex. Default scripts include reserved entries that are intentionally skipped, so edits must preserve `TVP7002_WRITE` tags. Probe currently stores `error = tvp7002_s_dv_timings(...)` and later reuses `error` for media/control setup; failure handling around the default timing path should be checked carefully if modified.

## Test Signals

Test by probing with valid endpoint polarity data, reading revision logs, enumerating all DV timings, setting and querying each supported timing, verifying `query_dv_timings()` under known analog inputs, checking reported pad format fields, toggling stream impedance, changing gain and observing writes to R/G/B fine gain registers, and using advanced debug register access when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp7002.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp7002_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp7002_reg.h

## Purpose

This header defines symbolic register addresses for the TI TVP7002 digitizer. It is used by `tvp7002.c` to build default and per-timing register scripts and to read timing-detection status.

## Important APIs, Types, And Functions

The file has no functions or types. It maps register names from `TVP7002_CHIP_REV` through `TVP7002_YUV_V_R_COEF_MSBS`. Covered groups include HPLL feedback/control/phase, clamp timing, sync thresholds, input mux, RGB gain/offset, output formatter, power/ADC setup, auto level control, status registers for line and clock counts, sync widths, AVID/VBLK/FBIT timing, and YUV coefficient registers.

## Control Flow

There is no executable flow. The C driver uses these constants in fixed initialization arrays, timing-specific parameter arrays, status reads, polarity programming, stream toggling, gain control, and advanced debug access.

## State And Persistence

The header holds no state. Hardware persistence is embodied in the TVP7002's registers, while selected timing and streaming state live in `struct tvp7002`.

## Dependencies And Integration Points

The header is private to the TVP7002 driver and follows naming conventions documented in comments. It relies on no custom includes beyond what the including C file provides.

## Risks

Incorrect address definitions would affect many scripts at once. Reserved gaps are intentionally omitted or referenced numerically in `tvp7002.c`; adding symbolic names should be coordinated with the register script type tags so reserved registers are not accidentally written.

## Test Signals

Correctness is observed indirectly through successful default initialization, stable DV timing detection from line/clock status registers, proper gain writes, stream toggling via miscellaneous control, and optional advanced debug register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tvp7002_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw2804.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tw2804.c

## Purpose

This file implements a V4L2 I2C subdevice driver for Techwell TW2804/TW2802 multi-channel analog video decoder hardware. It exposes standard selection, channel/input routing, logging, and image controls for brightness, contrast, saturation, hue, color killer, autogain, global gain, chroma gain, and color balance.

## Important APIs, Types, And Functions

`struct tw2804` stores the subdev, control handler, selected channel, input, and TV norm. `global_registers` and `channel_registers` are initialization scripts. `write_reg()`, `write_regs()`, and `read_reg()` encode the channel into the upper register address bits with `reg | (channel << 6)`. V4L2 hooks are `tw2804_s_std()`, `tw2804_s_video_routing()`, `tw2804_s_ctrl()`, `tw2804_g_volatile_ctrl()`, and `tw2804_log_status()`.

## Control Flow

Probe validates SMBus byte-data support, allocates state, initializes the subdev, sets `channel` to an invalid sentinel and `norm` to NTSC, creates controls, marks global controls as volatile, and leaves actual channel programming to routing. `tw2804_s_video_routing()` optionally selects and initializes a channel based on `config` values 1 through 4; channel 0 also initializes global registers. It validates `input <= 1`, updates register `0x22` bit 2 for input selection, and caches the input. `tw2804_s_std()` writes a small standard-specific script for 525/60 or 625/50 timing and updates `norm`.

## State And Persistence

The driver caches the current channel, input, and norm per subdev instance. Some hardware controls are global across four channels but exposed through separate logical instances, so the driver marks those controls volatile and reads them back from channel 0 whenever queried. There is no runtime PM or persistent storage.

## Dependencies And Integration Points

It uses Linux I2C SMBus byte-data, V4L2 subdev core/video ops, and V4L2 controls. The driver is designed for board designs where one physical TW2804 may appear as four logical I2C-adapter-backed instances.

## Risks

`channel` is a two-bit field but initialized with `-1`, relying on truncation to a sentinel-like value. Cross-channel global state cannot be synchronized across instances except through volatile reads. `tw2804_s_std()` ignores `write_regs()` errors. Routing with `config == 0` assumes the previously selected channel is valid. Hardware write failures during control changes are propagated for most controls but not all initialization paths.

## Test Signals

Test channel initialization for all four channels, global register initialization only on channel 0, input selection on register `0x22`, 50/60 Hz standard scripts, volatile global control reads after changing another instance, and normal probe/remove cleanup of the V4L2 control handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw2804.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9900.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tw9900.c

## Purpose

This file implements a modern V4L2 I2C subdevice driver for the Techwell TW9900 multi-standard analog video decoder. It supports NTSC and PAL modes, UYVY 8-bit output, runtime PM with regulator/reset sequencing, source-change and control events, signal status, standard autodetection, and brightness/contrast controls.

## Important APIs, Types, And Functions

`struct tw9900` holds the I2C client, optional reset GPIO, regulator, subdev, control handler, media source pad, mutex, streaming flag, and current mode. `struct tw9900_mode` ties width, height, V4L2 standard, and register script. Important register helpers are `tw9900_write_reg()`, `tw9900_write_array()`, and `tw9900_read_reg()`. Format and pad functions are `tw9900_fill_fmt()`, `tw9900_get_fmt()`, `tw9900_set_fmt()`, and `tw9900_enum_mbus_code()`. Video operations include `tw9900_s_std()`, `tw9900_g_std()`, `tw9900_querystd()`, `tw9900_g_tvnorms()`, `tw9900_g_input_status()`, and `tw9900_s_stream()`.

## Control Flow

Probe allocates state, gets optional reset GPIO and mandatory `vdd` regulator, initializes the subdev with device-node/events flags, sets up a mutex and two controls, initializes a media source pad, enables runtime PM, powers the device briefly via `tw9900_check_id()`, verifies chip ID, and registers the subdev. Runtime resume asserts reset, enables the regulator, waits, deasserts reset, writes `tw9900_init_regs`, and waits for HPLL lock. Runtime suspend asserts reset and disables the regulator.

Streaming is serialized by the mutex. Stream-on resumes runtime PM, applies controls, writes the current mode's register list, writes streaming output format control, and caches `streaming = true`. Stream-off writes standby output format control, clears the flag, and drops runtime PM. Standard autodetection is disallowed while streaming, powers the chip, writes the autodetect masks, waits for the auto-progress bit to clear, then decodes current standard from `TW9900_REG_STD`.

## State And Persistence

The current selected mode and streaming flag are cached in memory. Hardware state is lost across runtime suspend and reinitialized on resume; mode-specific registers and controls are applied again on stream-on. The mutex is the main consistency boundary for hardware access and control state.

## Dependencies And Integration Points

The driver integrates with V4L2 async subdev, V4L2 controls/events, media entity pads, runtime PM, GPIO descriptors, regulators, I2C SMBus, and device tree matching (`techwell,tw9900`). It reports a single `MEDIA_BUS_FMT_UYVY8_2X8` source pad and supports NTSC/PAL SDTV norms.

## Risks

Queries for standard and input status return `-EBUSY` while streaming, which userspace must handle. Runtime resume has long sleeps, including a 300 ms HPLL lock wait. Control writes are ignored while runtime suspended and are later applied at stream-on, so tests must verify delayed control application. Autodetect only recognizes NTSC-M and PAL-BDGHI register encodings. The device ID constant is zero, so detection relies on matching a register value of zero rather than a distinctive nonzero signature.

## Test Signals

Test successful regulator/reset sequencing, chip ID validation, runtime suspend/resume, NTSC/PAL `s_std()` and reported formats, stream-on/off standby and streaming register writes, brightness/contrast control persistence across power cycles, `querystd()` timeout and success paths, signal status from HLOCK, and V4L2 event subscription behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9903.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tw9903.c

## Purpose

This file implements a compact V4L2 I2C subdevice driver for the Techwell TW9903 video decoder. It programs a fixed composite-input initialization script, supports input routing, NTSC/PAL-style 60/50 Hz timing changes, basic image controls, and status logging.

## Important APIs, Types, And Functions

`struct tw9903` stores the V4L2 subdev, control handler, and current norm. `initial_registers` contains the startup register script, terminated by register `0x00`. `write_reg()` and `write_regs()` perform SMBus byte writes. V4L2 hooks are `tw9903_s_video_routing()`, `tw9903_s_std()`, `tw9903_s_ctrl()`, and `tw9903_log_status()`.

## Control Flow

Probe checks SMBus byte-data support, allocates state, initializes the subdev, creates brightness/contrast/hue controls, sets default NTSC norm, writes the initial register table, and returns without async registration because this older subdev style relies on parent V4L2 device registration. Routing writes register `0x02` with `0x40 | (input << 1)`. Standard selection writes one of two small scripts for 60 Hz or 50 Hz window timing and caches `norm`.

## State And Persistence

The only cached state is `norm` plus V4L2 control values. Hardware register state is set at probe and then modified by routing, standard selection, and controls. There is no locking, runtime PM, media entity, or persistent storage.

## Dependencies And Integration Points

The driver integrates with I2C SMBus byte-data and legacy V4L2 subdev core/video/control operations. It is derived from older go7007 staging code, and comments mention unimplemented saturation/scaling ideas.

## Risks

Register writes in routing and controls ignore errors. `write_regs()` returns `-1` instead of a specific errno. The input value is not range checked before shifting. There is no format enumeration or media-controller pad model, so parent drivers must know the output format and topology.

## Test Signals

Test probe initialization table writes, routing register values for expected inputs, 50/60 Hz script selection, brightness/contrast/hue control writes, status logging of cached norm, and cleanup of the control handler on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9903.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9906.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tw9906.c

## Purpose

This file implements a simple V4L2 I2C subdevice driver for the Techwell TW9906 video decoder. It is structurally similar to `tw9903.c`: fixed startup programming, input routing, NTSC/PAL-style timing changes, and brightness/contrast/hue controls.

## Important APIs, Types, And Functions

`struct tw9906` contains the subdev, control handler, and current norm. `initial_registers` defines the default composite input, digital format, window, scaling, color, VBI, and miscellaneous chip setup. `write_reg()` and `write_regs()` are SMBus byte-data helpers. V4L2 entry points are `tw9906_s_video_routing()`, `tw9906_s_std()`, `tw9906_s_ctrl()`, and `tw9906_log_status()`.

## Control Flow

Probe checks SMBus support, allocates and initializes state, creates three controls, sets default NTSC norm, writes the initial register table, and leaves the subdev available to the parent V4L2 device. Routing writes register `0x02` using `0x40 | (input << 1)`. Standard selection chooses between small 60 Hz and 50 Hz scripts and updates the cached norm. Remove unregisters the subdev and frees controls.

## State And Persistence

State is limited to cached `norm` and control values. Hardware state is volatile and driven by probe initialization and later register writes. There is no runtime PM, media-controller entity, async registration, or persistent storage.

## Dependencies And Integration Points

The driver depends on I2C SMBus byte-data and V4L2 subdev/control helpers. It exposes only core and video subdev operations and expects board-specific parent code to handle topology and capture format assumptions.

## Risks

Routing and control writes ignore SMBus errors. The input parameter is not validated. `write_regs()` returns `-1`, losing errno detail. There is no explicit format/pad API and no lock protecting concurrent control/standard/routing writes.

## Test Signals

Test probe register script execution, route register writes, 50/60 Hz standard script behavior, brightness/contrast/hue writes, status logging of current norm, and remove-path control cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9906.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9910.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/tw9910.c

## Purpose

This file implements a V4L2 I2C subdevice driver for the Techwell TW9910 video decoder. It supports NTSC/PAL selection, scaling among full/CIF/QCIF-like modes, UYVY output, power control through clock and GPIOs, platform-data-driven bus width and MPOUT configuration, and optional advanced debug register access.

## Important APIs, Types, And Functions

`struct tw9910_priv` stores the subdev, external clock, board/platform info, optional power-down and reset GPIOs, selected scale, current norm, and chip revision. `struct tw9910_scale_ctrl` defines named width/height/hscale/vscale choices, with separate NTSC and PAL tables. Register helpers include `tw9910_mask_set()`, `tw9910_set_scale()`, `tw9910_set_hsync()`, `tw9910_reset()`, and `tw9910_power()`. V4L2 hooks include `tw9910_s_power()`, `tw9910_s_stream()`, `tw9910_s_std()`, `tw9910_g_std()`, `tw9910_get_selection()`, `tw9910_get_fmt()`, `tw9910_set_fmt()`, `tw9910_enum_mbus_code()`, and `tw9910_g_tvnorms()`.

## Control Flow

Probe requires legacy platform data, validates SMBus byte-data support, allocates state, initializes the subdev, obtains the optional `xti` clock and `pdn` GPIO, then calls `tw9910_video_probe()`. Video probe validates 8- or 16-bit bus width, powers on the chip, reads product ID and revision, accepts only product ID `0x0b` revisions 0 or 1, initializes NTSC and the default scale, and powers off. The subdev is then registered asynchronously.

Format setting selects the nearest scale from NTSC or PAL tables, resets hardware, programs bus width, MPOUT behavior, scaling registers, and HSYNC timing, then updates the requested dimensions to the selected scale. Standard selection updates VBI polarity/window registers for 525/60 versus 625/50. Streaming enables or tri-states outputs based on chip revision and powers the ADC/PLL blocks on or off through register masks. The explicit `.s_power` path controls the external clock, power-down GPIO, and a temporarily requested shared reset GPIO.

## State And Persistence

The selected norm and scale are cached in `struct tw9910_priv`. Hardware state is reset and reprogrammed during active format changes. Power state is not reference-counted in this driver beyond V4L2 core calls; the clock and GPIO state follow `.s_power`, while internal ADC/PLL power and output enable follow `.s_stream`.

## Dependencies And Integration Points

The driver depends on I2C SMBus byte-data, V4L2 subdev core/video/pad APIs, legacy `media/i2c/tw9910.h` platform data, clocks, GPIO descriptors, and optional advanced debug. It reports `MEDIA_BUS_FMT_UYVY8_2X8`, `V4L2_COLORSPACE_SMPTE170M`, and interlaced bottom-top field order.

## Risks

The driver requires platform data and does not parse device tree. Reset GPIO handling is explicitly a workaround for shared GPIO platforms and requests/releases the line during power-on. There is no mutex around register operations. Stream-on fails if no scale has been selected. Revision-specific output tri-state values only support revisions 0 and 1. `tw9910_set_frame()` resets the chip on error and clears scale, which can surprise callers after a failed format attempt.

## Test Signals

Test platform-data validation for bus width and MPOUT, clock/GPIO sequencing in `.s_power`, product ID and revision rejection, NTSC/PAL crop and VBI register changes, format negotiation to nearest scale for each supported size, 8-bit versus 16-bit bus width programming, stream output enable/disable values for each revision, and advanced debug register read/write when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tw9910.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/uda1342.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/uda1342.c

## Purpose

This file implements a minimal V4L2 I2C subdevice driver for the Philips UDA1342 audio codec. It provides audio input routing between two inputs and performs basic reset/default input setup at probe.

## Important APIs, Types, And Functions

There is no private state structure beyond a dynamically allocated `struct v4l2_subdev`. `write_reg()` writes 16-bit codec values using SMBus word writes after `swab16()` because the device expects MSB first while SMBus sends LSB first. `uda1342_s_routing()` handles `UDA1342_IN1` and `UDA1342_IN2` by writing selector values to register `0x00`. Audio integration is through `v4l2_subdev_audio_ops`.

## Control Flow

Probe checks `I2C_FUNC_SMBUS_WORD_DATA`, allocates a subdev, initializes it, writes a reset command, selects input 1, and logs the device. Routing later switches between input 1 and input 2. Remove unregisters the subdev.

## State And Persistence

The driver does not cache selected input or any codec state. The selected route persists only in the hardware until reset or power loss. There are no controls, runtime PM hooks, or persistent files.

## Dependencies And Integration Points

It depends on Linux I2C SMBus word-data, V4L2 subdev audio ops, and public input constants from `media/i2c/uda1342.h`. Parent bridge drivers are expected to instantiate and route the codec.

## Risks

`write_reg()` ignores SMBus return values and always returns success. Unsupported routing inputs log an error but still return zero. No state cache means users cannot query current routing through this driver.

## Test Signals

Test probe on adapters with word-data support, reset and default input writes, routing writes for `UDA1342_IN1` and `UDA1342_IN2`, unsupported input logging, and remove-path subdev unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/uda1342.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/upd64031a.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/upd64031a.c

## Purpose

This file implements a V4L2 I2C subdevice driver for the NEC uPD64031A ghost-reduction chip used for Japanese NTSC video paths. It initializes the chip, supports routing modes that select ghost-reduction and sync behavior, pulses a frequency/input-change bit, and exposes status/debug register access.

## Important APIs, Types, And Functions

`struct upd64031a_state` stores the subdev, a software copy of initialized registers, and cached mode bitfields for ghost reduction, direct 3D Y/C connection, external composite sync, and external vertical sync. `upd64031a_read()` reads status bytes with `i2c_master_recv()`. `upd64031a_write()` writes two-byte register/value messages. V4L2 hooks are `upd64031a_s_frequency()`, `upd64031a_s_routing()`, `upd64031a_log_status()`, and optional advanced debug get/set register functions.

## Control Flow

Probe validates SMBus byte-data functionality, allocates state, initializes the V4L2 subdev, copies `upd64031a_init` into the register cache, sets default mode bitfields, and writes all cached registers. Routing decodes the input bitmask into mode fields, combines them with cached register defaults, writes registers R00, R05, and R08, then calls `upd64031a_s_frequency()` to toggle bit `0x10` in R00 as an input/channel-change notification. Frequency changes alone also pulse that bit.

## State And Persistence

The driver keeps an initial register cache and separate cached bitfields, but it does not update `state->regs[]` after route writes. The actual route persists in hardware registers. No runtime PM or persistent storage is present.

## Dependencies And Integration Points

It depends on V4L2 subdev core/tuner/video ops, I2C master send/receive, and public route bit definitions from `media/i2c/upd64031a.h`. It is intended to sit in an analog video processing chain before or beside decoder/Y-C separation components.

## Risks

`upd64031a_read()` checks `reg >= sizeof(buf)` where `buf` is only two bytes, so advanced debug reads beyond status byte 1 return `0xff` regardless of valid register count. `upd64031a_s_routing()` computes `r05` from `state->regs[R00]` instead of `state->regs[R05]`, which is suspicious and worth preserving only if hardware behavior depends on it. I2C send/receive errors are logged but mostly not propagated. The cached register array can diverge from hardware.

## Test Signals

Test full probe initialization writes, routing combinations for ghost-reduction and external sync flags, R00 frequency pulse behavior after routing and tuner frequency changes, status logging of SA00/SA01, advanced debug register access when configured, and remove-path subdev unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/upd64031a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/upd64083.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/upd64083.c

## Purpose

This file implements a V4L2 I2C subdevice driver for NEC uPD64083/uPD6408x 3D Y/C separation hardware. It initializes the chip for use with a uPD64031A ghost-reduction chip and allows video routing modes to switch Y/C separation mode and external Y ADC usage.

## Important APIs, Types, And Functions

`struct upd64083_state` stores the subdev, selected mode bits, external Y ADC bit, and an initialization register cache. `upd64083_write()` sends register/value pairs with `i2c_master_send()`. Optional `upd64083_read()` reads status/debug bytes with `i2c_master_recv()`. V4L2 hooks are `upd64083_s_routing()`, `upd64083_log_status()`, and optional advanced debug get/set register functions.

## Control Flow

Probe validates SMBus byte-data support, allocates state, initializes the subdev, sets default YCS mode and external Y ADC state, copies the 23-byte initialization table, and writes every register. Routing validates the input encoding, rejects values above 7 and the invalid `(input & 6) == 6` combination, derives mode bits for R00 and external Y ADC for R02, combines them with cached defaults, and writes the two affected registers.

## State And Persistence

The driver caches initial register values plus the most recent routing-derived mode bits. It does not update the full register cache after writes. Hardware state persists only in the device. There is no runtime PM, lock, control handler, media pad, or persistent storage.

## Dependencies And Integration Points

It uses V4L2 subdev core/video ops, I2C master send/receive, and public route constants from `media/i2c/upd64083.h`. It is part of a legacy analog processing chain and may be paired with the uPD64031A.

## Risks

I2C write errors are logged but not propagated from routing. Status reads assume a seven-byte receive without checking the return count. Cached registers can diverge from hardware. The accepted input bit encoding is compact and easy to misuse without the public header constants.

## Test Signals

Test probe initialization writes, valid and invalid routing encodings, R00/R02 bit updates for mode and external Y ADC, status logging of SA00-SA06, advanced debug access when enabled, and remove-path subdev unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/upd64083.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vd55g1.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/vd55g1.c

## Purpose

This file implements a V4L2 subdevice driver for STMicroelectronics VD55G1 and VD65G4 global-shutter image sensors. It supports CCI/regmap access, runtime power management, firmware patching for VD55G1, MIPI CSI-2 output setup, mono or Bayer media-bus formats, crop/format negotiation, streaming through the multi-stream subdev API, auto/manual exposure and gain controls, test pattern generation, HDR internal-subtraction mode, GPIO strobe configuration, and device-tree parsing.

## Important APIs, Types, And Functions

`struct vd55g1` is the main state object. It stores device identity, subdev, media pad, regulators, reset GPIO, external clock, regmap, clock/link/pixel-rate calculations, output interface control, GPIO modes, optional external LED mask, V4L2 control handler, and all control pointers. Format tables distinguish mono VD55G1 (`Y8`, `Y10`) from Bayer VD65G4 formats whose Bayer order changes with h/v flip. `struct vd55g1_mode` lists supported output sizes, and `struct vd55g1_vblank_limits` carries dynamic vertical blanking bounds.

Key helpers include `vd55g1_get_fmt_bpp()`, `vd55g1_get_fmt_data_type()`, `vd55g1_get_fmt_code()`, `vd55g1_get_pixel_rate()`, `vd55g1_get_hblank_min()`, `vd55g1_write_array()`, `vd55g1_poll_reg()`, `vd55g1_wait_state()`, `vd55g1_prepare_clock_tree()`, `vd55g1_patch()`, `vd55g1_set_framefmt()`, `vd55g1_update_hdr_mode()`, and `vd55g1_update_gpios()`. Streaming is handled by `vd55g1_enable_streams()` and `vd55g1_disable_streams()`. Pad/control/probe functions include `vd55g1_set_pad_fmt()`, `vd55g1_init_state()`, `vd55g1_enum_mbus_code()`, `vd55g1_enum_frame_size()`, `vd55g1_s_ctrl()`, `vd55g1_g_volatile_ctrl()`, `vd55g1_init_ctrls()`, `vd55g1_detect()`, `vd55g1_power_on()`, `vd55g1_power_off()`, `vd55g1_parse_dt()`, `vd55g1_subdev_init()`, `vd55g1_probe()`, and `vd55g1_remove()`.

## Control Flow

Probe allocates state, initializes the I2C subdev, parses the CSI-2 endpoint and optional `st,leds` GPIO list, gets regulators, sensor clock, reset GPIO, and CCI regmap, calculates the clock tree, powers the sensor on for detection and boot/patch, enables runtime PM with autosuspend, finalizes subdev state, creates controls, and registers the async subdev. Device-tree validation requires a single CSI-2 data lane, clock lane 0, exactly one link frequency, and valid optional LED GPIO indices.

Power-on enables regulators and clock, releases reset, waits for the hardware FSM to report ready-to-boot, verifies model ID against compatible data and revision, writes the external clock register, applies the VD55G1 patch or boots VD65G4, and waits for software standby. Power-off asserts reset, disables the clock, and disables regulators. The patch path writes a large firmware patch in chunks to avoid bulk-write timeout risk, commands patch-and-boot, polls completion, and verifies patch revision 2.9.

Format negotiation chooses the nearest supported mode, adapts Bayer order to h/v flip, computes a centered crop rectangle with up to 2x digital binning, stores format/crop in subdev state, and updates VBLANK, exposure max, pixel rate, and fixed HBLANK ranges for active changes. Streaming resumes runtime PM, writes MIPI rate, output interface control, frame format/crop/binning for both contexts, default GPIOs, cold-start exposure, V4L2 controls, line length, then commands standby-to-streaming and waits for FSM streaming state. Stream disable reads applied exposure/gain back for future cold-start, commands stop, waits for standby, releases grabbed controls, and autosuspends.

## State And Persistence

Driver state is in `struct vd55g1`, active subdev state, and V4L2 controls. Control state persists across runtime suspend in memory and is re-applied on stream enable. Hardware state is considered volatile across power cycles and is reconstructed by power-on, patch/boot, stream setup, and control setup. Exposure/gain applied by auto-exposure is read back on stream disable to seed cold-start behavior on the next stream. There is no filesystem persistence.

## Dependencies And Integration Points

The driver integrates with regulators, clocks, reset GPIO, runtime PM autosuspend, CCI/regmap, V4L2 controls, V4L2 fwnode properties, media controller, V4L2 async registration, MIPI CSI-2 data type constants, subdev active state/routing, and device tree compatibles `st,vd55g1` and `st,vd65g4`. It uses `devm_v4l2_sensor_clk_get()`, `devm_cci_regmap_init_i2c()`, `v4l2_subdev_init_finalize()`, and stream enable/disable pad ops.

## Risks

The probe path powers the sensor before subdev finalization and then relies on runtime PM state transitions; error paths must keep PM references balanced. The firmware patch blob and expected patch revision are critical for VD55G1. Clock-tree limits are strict: xclk must be 6-27 MHz and MIPI rate 250-1200 Mbps. HBLANK is read-only but dynamically recomputed from format, MIPI rate, crop, and HDR mode. HDR mode changes context programming and exposure limits. `vd55g1_update_gpios()` conditionally writes context-1 GPIOs only in strobe/LED-off/HDR-sub cases, so LED and HDR interactions require careful testing. `vd55g1_enable_streams()` returns `-EINVAL` for any stream setup failure, which can hide the original errno.

## Test Signals

Test DT rejection for invalid lane count, clock lane, missing/multiple link frequencies, and invalid LED GPIOs. Probe tests should cover regulator/clock/reset sequencing, model-compatible mismatch, unsupported revision, patch version mismatch, and VD65G4 no-patch boot. Format tests should enumerate mono and Bayer codes, verify Bayer order changes with flip controls, check supported frame sizes, and confirm crop/binning/HBLANK/VBLANK/exposure range updates. Streaming tests should verify FSM transitions, MIPI/data-type register programming, control grabbing, test-pattern duster disable/restore, auto/manual exposure and gain writes, exposure lock, EV bias target writes, HDR context setup, GPIO strobe behavior, readback of applied exposure on stop, and runtime autosuspend after stream disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/vd55g1.c -->
