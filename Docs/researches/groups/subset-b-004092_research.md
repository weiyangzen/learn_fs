# Research: subset-b-004092

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ir-kbd-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ir-kbd-i2c.c

## Purpose
`ir-kbd-i2c.c` is a Linux media I2C remote-control driver for several IR receiver chips used by TV/video capture hardware, plus optional Hauppauge/Zilog IR transmitter support. It binds as `ir-kbd-i2c`, creates an `rc_dev` input device, polls receiver chips through I2C, decodes vendor-specific key formats into rc-core scancodes, and exposes raw IR transmit callbacks when a Zilog blaster is present.

## Important APIs, Types, And Functions
The driver depends on `media/rc-core.h` and the platform data contract from `media/i2c/ir-kbd-i2c.h`. The central runtime object is `struct IR_i2c` from that header; this file fills its I2C clients, `rc_dev`, delayed work, protocol/keymap metadata, polling interval, lock, optional TX client, carrier, and duty cycle. Receiver decoders include `get_key_haup_common()`, `get_key_haup()`, `get_key_haup_xvr()`, `get_key_pixelview()`, `get_key_fusionhdtv()`, `get_key_knc1()`, `get_key_geniatech()`, and `get_key_avermedia_cardbus()`. Polling flows through `ir_key_poll()`, `ir_work()`, `ir_open()`, and `ir_close()`. Zilog TX uses packed `struct code_block`, `send_data_block()`, `zilog_init()`, `zilog_ir_format()`, `zilog_tx()`, `zilog_tx_carrier()`, and `zilog_tx_duty_cycle()`.

## Control Flow
`ir_probe()` rejects HDPVR unless `enable_hdpvr` is set, allocates `struct IR_i2c`, chooses a decoder/keymap/protocol set by I2C address, then lets platform data override name, keymap, `rc_dev`, protocol mask, polling interval, and key decoder. It allocates an `rc_dev` if needed, initializes rc-core fields, delayed work, and optional Zilog TX at dummy address `0x70`, then registers the rc device. Open schedules immediate delayed work. The worker takes `ir->lock` opportunistically, polls one key, reports via `rc_keydown()`, and reschedules itself. Remove cancels work, unregisters the optional TX client, and unregisters/frees the rc device.

For TX, `zilog_tx()` formats a pulse/space buffer into the Zilog table-limited encoding, transfers the packed code block in small I2C chunks, commands the chip to send, retries readiness for up to about one second, then returns the transmitted sample count on success.

## State And Persistence
State is volatile kernel/device state only. The delayed work loop persists while the rc device is open. `ir->old` suppresses Geniatech repeats. `ir->lock` serializes polling with transmit. Carrier and duty cycle are cached in memory. There is no nonvolatile persistence; device registers and TX RAM are programmed as needed.

## Dependencies And Integration Points
The driver integrates with the I2C core, rc-core keymaps/protocols, bridge-driver platform data, delayed workqueues, module parameters, and optional Zilog I2C dummy clients. `i2c_device_id` entries include generic `ir_video`, `ir_z8f0811_haup`, and HDPVR-specific Zilog support.

## Risks
Address-based autodetection is fragile and relies on board topology or platform overrides. Polling uses `mutex_trylock()`, so receive events may be skipped during long transmit operations. Zilog encoding has strict limits on pulse/space cardinality and maximum duration; recorded IR can fail with `-EINVAL`. Error handling around optional `tx_c` should be regression-tested because the client is only created for TX-capable paths but unregistered on remove/error cleanup. The worker unregisters/frees the rc device on `-ENODEV`, which is an unusual lifetime path that needs careful race coverage with remove/close.

## Test Signals
Useful tests include probing all known addresses with and without platform data, validating open/close cancellation, injecting I2C short reads/errors for each decoder, checking rc-core protocol/scancode output for RC5/RC6/vendor formats, and exercising Zilog transmit with too many distinct pulse/space lengths, excessive durations, carrier bounds, duty changes, and I2C NAK retries. Module parameter coverage should confirm HDPVR is disabled by default and enabled only when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ir-kbd-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/isl7998x.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/isl7998x.c

## Purpose
`isl7998x.c` is a V4L2 subdevice driver for the Intersil/Renesas ISL79987 analog video decoder, converting up to four analog inputs to MIPI CSI-2 or BT.656-style video. It manages register-page access, video standard selection/detection, test-pattern controls, runtime power, media pads, and V4L2 streaming operations.

## Important APIs, Types, And Functions
The main state is `struct isl7998x`, containing the subdev, paged `regmap`, optional powerdown/reset GPIOs, MIPI lane/input counts, active format/norm, media pads, stream state, locks, and V4L2 controls. Register constants define page 0 global, pages 1-4 decoder/ACA channels, and page 5 line-interleaving/MIPI engine registers. Key functions are `isl7998x_get_nr_inputs()`, `isl7998x_wait_power_on()`, `isl7998x_set_standard()`, `isl7998x_init()`, `isl7998x_set_test_pattern()`, `isl7998x_s_std()`, `isl7998x_querystd()`, `isl7998x_g_input_status()`, `isl7998x_s_stream()`, `isl7998x_pre_streamon()`, `isl7998x_post_streamoff()`, format enumeration/get/set handlers, control setup, probe/remove, and runtime PM callbacks.

## Control Flow
Probe verifies SMBus word support, obtains optional GPIOs, creates the paged regmap, parses the source endpoint for one or two CSI-2 lanes, validates that enabled input ports are exactly VID1, VID1-2, or VID1-4, initializes the media entity pads, defaults to UYVY NTSC and disabled streaming, creates a read-only link-frequency control plus ISL7998X-specific test-pattern controls, registers the subdev, and enables runtime PM. Runtime resume toggles reset/powerdown GPIOs, polls the product ID, then applies two large register patches plus lane/input-specific settings and current standard programming. `pre_streamon()` powers the chip; `s_stream()` toggles bit 7 of the line-interleaving engine and applies test pattern state on enable; `post_streamoff()` releases runtime PM.

## State And Persistence
The cached state is `norm`, `fmt`, `enabled`, test-pattern fields, lane/input topology, and regmap cache. Hardware programming is reapplied on every runtime resume, so register state is treated as volatile across suspend. `lock` protects format/norm/enabled, and `ctrl_mutex` protects V4L2 control handler access.

## Dependencies And Integration Points
The driver depends on I2C, regmap with range windows, GPIO descriptors, runtime PM, OF graph/fwnode parsing, V4L2 subdev/video/pad/control APIs, media controller pads, and async subdev registration. It exposes sink pads for VIN1-VIN4 and one source pad.

## Risks
The input topology is intentionally constrained and cannot remap sparse input ports. `s_std()` and `querystd()` reject changes while streaming, but callers must still coordinate stream state correctly. Runtime PM gating means test-pattern changes while powered down only update cached fields and are applied later. Standard detection assumes all active inputs share the same video standard and only warns on mismatch. Large magic register patches make hardware regressions hard to localize.

## Test Signals
Tests should cover invalid lane counts, invalid/sparse input ports, runtime resume GPIO sequencing, product ID timeout, register-patch failures, standard set/query for PAL/NTSC/SECAM variants, no-power input status, stream enable/disable bit programming, test-pattern control writes both powered and suspended, and media pad format enumeration for 720x480 and 720x576 modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/isl7998x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ks0127.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ks0127.c

## Purpose
`ks0127.c` is a legacy V4L2 I2C subdevice driver for the KS0127/KS0127B/KS0122S video decoder used on Matrox capture hardware. It initializes decoder registers, routes composite/S-Video/YUV656 inputs, selects analog video standards, gates output streaming, and reports signal/status information.

## Important APIs, Types, And Functions
`struct ks0127` stores the subdev, current V4L2 norm, and a 256-byte software register cache. `init_reg_defaults()` builds a static default table. `ks0127_read()` performs a custom two-message I2C read using `I2C_M_NO_RD_ACK` for a KS0127 read quirk. `ks0127_write()` updates hardware and the cache. `ks0127_and_or()` performs cached read-modify-write. Higher-level operations are `ks0127_init()`, `ks0127_s_routing()`, `ks0127_s_std()`, `ks0127_s_stream()`, `ks0127_status()`, `ks0127_querystd()`, `ks0127_g_input_status()`, probe, and remove.

## Control Flow
Probe allocates `struct ks0127`, initializes the V4L2 I2C subdev, calls `init_reg_defaults()`, powers the chip by writing `KS_CMDA`, waits, and runs `ks0127_init()` to write known defaults excluding read-only/test/reserved ranges. Routing programs different register groups for composite, S-Video, and digital YUV656 input, including input selection, freerun/non-freerun mode, chroma demodulation, luma/chroma filtering, and gain/offset defaults. Standard selection adjusts chroma/demodulation for NTSC/PAL/PAL-M/PAL-N/SECAM and probes SECAM autodetection before forcing it. Stream on/off gates output pins and the OEN behavior. Remove unregisters the subdev, tristates output, and powers down.

## State And Persistence
The driver relies on the in-memory `regs[]` cache for bit updates; it is initialized from defaults and updated on every write. There is no runtime PM or persistent storage. `norm` affects YUV656 routing and standard-dependent format decisions.

## Dependencies And Integration Points
The file integrates with the I2C core, V4L2 subdev video ops, `ks0127.h` input/output constants, and old bridge drivers that call subdev routing/standard/stream methods.

## Risks
`ks0127_write()` updates the register cache even if the I2C write fails, so cache and hardware can diverge. Unknown inputs are logged but still return success. The custom read path is adapter-sensitive due to `I2C_M_NO_RD_ACK`. Many register values are fixed legacy magic constants and comments note some standards as fixme. There is no locking around cached registers, so callers must serialize subdev operations externally.

## Test Signals
Coverage should inject I2C read/write failures, verify cache behavior, check initialization register ranges, exercise all routing constants from `ks0127.h`, validate stream output gating, test PAL/NTSC/SECAM status interpretation, and confirm remove powers down/tristates even after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ks0127.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ks0127.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ks0127.h

## Purpose
`ks0127.h` is the small public constants header for the KS0127 decoder driver and its bridge-driver callers. It names supported input routes, output routes, and two nonstandard standard identifiers used by legacy capture code.

## Important APIs, Types, And Functions
The header defines composite inputs `KS_INPUT_COMPOSITE_1` through `KS_INPUT_COMPOSITE_6`, S-Video inputs `KS_INPUT_SVIDEO_1` through `KS_INPUT_SVIDEO_3`, digital `KS_INPUT_YUV656`, and `KS_INPUT_COUNT`. It also defines output selectors `KS_OUTPUT_YUV656E` and `KS_OUTPUT_EXV`, plus legacy standard constants `KS_STD_NTSC_N` and `KS_STD_PAL_M`. There are no functions or types.

## Control Flow
There is no executable control flow. The values are consumed by `ks0127_s_routing()` in `ks0127.c` and by external bridge drivers when invoking V4L2 subdev routing.

## State And Persistence
The header contains compile-time constants only. No runtime state or persistence is introduced.

## Dependencies And Integration Points
The integration point is the V4L2 subdev routing API. Numeric input values are not dense: composite input 4 starts at value 4, S-Video starts at 8, and YUV656 is 15, matching the decoder register bit layout expected by `ks0127.c`.

## Risks
Changing these values would silently break hardware routing because the driver writes them directly into register fields. `KS_INPUT_COUNT` is not a simple maximum-plus-one sentinel for the sparse namespace, so consumers should not iterate `0..KS_INPUT_COUNT-1` assuming all values are valid.

## Test Signals
Tests should validate that each exported route value maps to the intended `ks0127_s_routing()` case and that callers do not treat `KS_INPUT_COUNT` as a dense valid-route count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ks0127.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/lm3560.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/lm3560.c

## Purpose
`lm3560.c` is a V4L2 flash LED subdevice driver for TI LM3559/LM3560 dual flash LED controllers. It exposes one flash media entity per LED, maps V4L2 flash controls to regmap writes, reads hardware fault flags, and initializes platform-data-defined current/timeout limits.

## Important APIs, Types, And Functions
`struct lm3560_flash` holds the device, platform data, regmap, mutex, shared LED mode, two V4L2 control handlers, and two V4L2 subdevs. Register helpers include `lm3560_mode_ctrl()`, `lm3560_enable_ctrl()`, `lm3560_torch_brt_ctrl()`, and `lm3560_flash_brt_ctrl()`. Control entry points are per-LED wrappers around `lm3560_get_ctrl()` and `lm3560_set_ctrl()`. Setup flows through `lm3560_init_controls()`, `lm3560_subdev_init()`, `lm3560_init_device()`, probe, and remove.

## Control Flow
Probe allocates state, creates an 8-bit regmap, supplies default platform data if none was provided, initializes the lock, creates LED0 and LED1 subdevs/control handlers, initializes the hardware peak current, disables output, clears faults by reading `REG_FLAG`, and stores client data. Each control operation locks `flash->lock`, updates cached `led_mode` where needed, and writes the relevant enable, strobe source, timeout, flash brightness, or torch brightness bits. Brightness below the documented minimum disables the addressed LED. Remove unregisters both subdevs, frees both control handlers, and cleans up media entities.

## State And Persistence
The driver caches only `led_mode`, platform limits, and control/subdev objects. Hardware registers hold current mode, LED enables, brightness, timeout, and strobe source. Faults are volatile and read from `REG_FLAG`. There is no runtime PM, nonvolatile state, or suspend/resume reprogramming.

## Dependencies And Integration Points
Dependencies include I2C, regmap, V4L2 controls, V4L2 subdevs, media entities, and `media/i2c/lm3560.h` conversion macros/platform data. Integration is through flash-class V4L2 controls such as `V4L2_CID_FLASH_LED_MODE`, `STROBE`, `STROBE_STOP`, `TIMEOUT`, `INTENSITY`, `TORCH_INTENSITY`, and volatile `FAULT`.

## Risks
`led_mode` is shared by both LED subdevs, so per-LED operations are not fully independent. Several helpers overwrite `rval` after an enable write, potentially masking an earlier enable failure if the later brightness write succeeds. Probe cleanup after LED1 or hardware init failure does not unwind LED0 resources through a centralized path. Default platform data hides missing board constraints, which can overstate safe currents if board design differs.

## Test Signals
Tests should cover default and supplied platform data, per-LED brightness min/max conversions, disabling below minimum, strobe start/stop only in flash mode, strobe-source bit programming, volatile fault mapping for timeout/overtemperature/short, failure injection for each regmap operation, and probe/remove cleanup after partial subdev initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/lm3560.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/lm3646.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/lm3646.c

## Purpose
`lm3646.c` is a V4L2 flash LED driver for the TI LM3646 dual flash LED controller. Unlike LM3560, it exposes a single combined flash subdevice where total flash/torch intensity and LED1 split values are programmed through the chip registers.

## Important APIs, Types, And Functions
`struct lm3646_flash` stores platform data, regmap, a single control handler/subdev, and `mode_reg`, the cached upper bits of `REG_ENABLE`. Key functions are `lm3646_mode_ctrl()`, `lm3646_get_ctrl()`, `lm3646_set_ctrl()`, `lm3646_init_controls()`, `lm3646_subdev_init()`, `lm3646_init_device()`, probe, and remove. The driver uses conversion macros and constants from `media/i2c/lm3646.h`.

## Control Flow
Probe allocates state, creates an 8-bit regmap, supplies default platform data if absent, initializes the V4L2 flash subdev/control handler, reads `REG_ENABLE` to preserve non-mode bits in `mode_reg`, disables output, programs LED1 flash and torch current split, resets faults by reading `REG_FLAG`, and stores client data. Control handling maps LED mode to shutdown/torch/flash writes. Selecting flash mode first forces shutdown; `V4L2_CID_FLASH_STROBE` only starts flash if the chip is currently in shutdown; `STROBE_STOP` shuts down only if currently flashing. Timeout and total brightness controls update the appropriate masks.

## State And Persistence
State is limited to platform data, regmap state, V4L2 controls, and cached `mode_reg`. Fault state is volatile in `REG_FLAG`. There is no explicit mutex, runtime PM, persistent storage, or suspend/resume path.

## Dependencies And Integration Points
The file integrates with I2C, regmap, V4L2 flash controls, V4L2 subdev/media entity registration, and LM3646 platform data. Userspace observes standard flash controls plus a flash media entity.

## Risks
There is no control serialization lock beyond V4L2 handler locking, so hardware sequencing relies on the control framework. The fault control advertises only a subset of faults even though `lm3646_get_ctrl()` maps under-voltage, input-voltage, over-current, LED over-temperature, and over-voltage bits. If `REG_ENABLE` read succeeds with unexpected upper bits, `mode_reg` preserves them in all mode writes. Probe error cleanup is minimal after subdev init succeeds but hardware init fails.

## Test Signals
Tests should cover mode transitions, strobe refusal when not shutdown, stop behavior after timeout/shutdown, fault-bit mapping, brightness/timeout conversion boundaries, preservation of upper enable bits, platform defaulting, regmap failure paths, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/lm3646.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/lt6911uxe.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/lt6911uxe.c

## Purpose
`lt6911uxe.c` is a V4L2 subdevice driver for the Lontium LT6911UXE HDMI-to-MIPI CSI-2 bridge. It detects HDMI timing changes through an HPD IRQ, exposes DV timing and pad-format operations, controls CSI-2 TX streaming, and reports a pixel-rate control derived from the detected mode.

## Important APIs, Types, And Functions
`struct lt6911uxe` holds the subdev, source pad, control handler, pixel-rate control, current DV timings, current mode, CCI/regmap, reset GPIO, and HPD IRQ GPIO. Important functions include `get_pixel_rate()`, `lt6911uxe_get_detected_timings()`, `lt6911uxe_s_dv_timings()`, `lt6911uxe_g_dv_timings()`, `lt6911uxe_query_dv_timings()`, `lt6911uxe_status_update()`, `lt6911uxe_init_controls()`, `lt6911uxe_enable_streams()`, `lt6911uxe_disable_streams()`, `lt6911uxe_set_format()`, `lt6911uxe_get_mbus_config()`, `lt6911uxe_fwnode_parse()`, `lt6911uxe_identify_module()`, `lt6911uxe_threaded_irq_fn()`, probe, and remove.

## Control Flow
Probe creates a paged CCI regmap, initializes the subdev, obtains reset and HPD GPIOs, requires exactly four CSI-2 data lanes from firmware, identifies the chip by temporarily enabling I2C access, creates the pixel-rate control, initializes the source pad/media entity, enables runtime PM, finalizes the subdev state, requests a threaded HPD IRQ on both edges, and registers as a sensor subdev. The IRQ handler reads event/status registers; on video-ready it validates clocks, totals, active size, max 60 fps, and YUV422 8-bit MIPI format, then updates `cur_mode`, raises a source-change event, and refreshes the active pad format. Video-disappear disables MIPI TX and clears mode dimensions. Stream enable resumes runtime PM and writes `REG_MIPI_TX_CTRL = 1`; disable writes zero and drops runtime PM.

## State And Persistence
`cur_mode`, `timings`, and the pixel-rate control are cached in memory and updated from hardware interrupts or pad operations. No nonvolatile state exists. Runtime PM state controls whether the device is active for streaming. Active subdev state locks protect timing/format access.

## Dependencies And Integration Points
The driver uses ACPI matching (`INTC10C5`), GPIO descriptors, IRQs, runtime PM, V4L2 CCI register helpers, V4L2 DV timings, source-change events, fwnode CSI-2 parsing, media entity pads, and async sensor subdev registration.

## Risks
`get_pixel_rate()` divides by lane count and assumes firmware parsing has already populated lanes; early control initialization depends on that ordering. The driver only supports four lanes and YUV422 8-bit, rejecting other valid hardware possibilities. IRQ status updates can fail on transient invalid clocks/totals and leave stale cached timings. Remove must match the IRQ dev_id and runtime PM cleanup sequence. EDID is intentionally unsupported because the chip requires flash updates.

## Test Signals
Tests should cover missing GPIOs/endpoints, non-four-lane firmware rejection, chip-ID mismatch, IRQ ready/disappear/default events, invalid timing register values, pixel-rate range updates after format changes, stream enable/disable runtime PM balancing, source-change event delivery, and DV timing validation against the 4Kp30 cap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/lt6911uxe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/m52790.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/m52790.c

## Purpose
`m52790.c` is a small V4L2 I2C subdevice driver for the Mitsubishi M52790SP/FP A/V source switch. It routes linked audio/video inputs to outputs by writing a two-byte switch value over SMBus.

## Important APIs, Types, And Functions
`struct m52790_state` contains the V4L2 subdev plus cached 16-bit `input` and `output` masks. `m52790_write()` combines those masks and writes them with `i2c_smbus_write_byte_data()`. `m52790_s_routing()` is shared by audio and video ops. Optional advanced-debug handlers expose the combined register through `g_register` and `s_register`. `m52790_log_status()`, probe, and remove complete the driver.

## Control Flow
Probe verifies `I2C_FUNC_SMBUS_BYTE_DATA`, allocates state, initializes the subdev, sets default route `M52790_IN_TUNER` to `M52790_OUT_STEREO`, and writes it. Audio and video `s_routing` calls simply cache the requested input/output and write the combined state to the chip. Remove unregisters the subdev.

## State And Persistence
The only runtime state is the cached input/output bit masks. Hardware switch state persists only until reprogrammed or power-cycled. There is no runtime PM, locking, nonvolatile persistence, or register cache beyond those masks.

## Dependencies And Integration Points
The driver depends on I2C SMBus byte-data support, V4L2 subdev core/audio/video ops, and route constants from `media/i2c/m52790.h`. It is intended for bridge drivers that need simple external A/V mux routing.

## Risks
`m52790_s_routing()` ignores the return value from `m52790_write()`, so route calls report success even on I2C failure. Audio and video are inseparable; users expecting independent mute or A/V switching will not get it. Advanced debug register writes split `reg->val` using hard-coded masks, so invalid values can still create unsupported switch states.

## Test Signals
Tests should cover adapter functionality rejection, default route programming, audio/video route equivalence, I2C write failure visibility, advanced-debug register get/set, and log_status output for both switch bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/m52790.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max2175.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/max2175.c

## Purpose
`max2175.c` is a V4L2 RF tuner subdevice driver for the Maxim MAX2175 RF-to-bits tuner. It loads reference register presets, calibrates ADC/power-management state machines, applies ROM trim values, programs FIR coefficients, exposes tuner frequency operations, and provides private controls for I2S output, HSLS LO polarity, and RX mode.

## Important APIs, Types, And Functions
`struct max2175` stores the subdev, I2C client, V4L2 controls, regmap, cached frequency, region-specific RX modes/frequency bands, clock frequency, decimation ratio, master/slave and AM Hi-Z flags, ROM trim fields, and `mode_resolved`. Helper layers include bitfield read/write wrappers, `max2175_poll_timeout()`, `max2175_set_filter_coeffs()`, preset loaders, `max2175_set_bbfilter()`, CSM helpers, LO/NCO/RF tuning functions, RX mode selection, ADC/ROM/core initialization, V4L2 control handlers, tuner ops, DT parsing in probe, and remove.

## Control Flow
Probe parses `maxim,master`, `maxim,am-hiz-filter`, and optional `maxim,refout-load`, obtains the reference clock, chooses EU or NA behavior based on clock rate, initializes controls, registers the async subdev, runs `max2175_core_init()`, and applies default controls. Core init loads a full FM preset, configures REFOUT, resets ADC, loads ADC presets, runs power-manager init, recalibrates ADC, reads ROM trims, and loads region-specific filter coefficients. Frequency setting clamps to the region band, picks or validates an RX mode, loads mode-specific register maps, programs LO/NCO values, triggers a channel state-machine preset tune, and caches `ctx->freq`.

## State And Persistence
The driver caches the tuned frequency, selected RX mode control value, mode-resolution state, decimation ratio, clock-derived region, ROM trim values, and control values. Regmap uses `REGCACHE_MAPLE` with explicit volatile ranges. Hardware settings are programmed during probe and on control/frequency changes; there is no runtime PM or persistent storage.

## Dependencies And Integration Points
Dependencies include I2C, regmap, `clk_get_rate()`, OF/fwnode properties, V4L2 subdev tuner ops, V4L2 controls, custom control IDs from `linux/max2175.h`, and local public enums/constants from `max2175.h`.

## Risks
Region selection is based solely on exact crystal frequency, so unsupported clocks silently fall into NA settings. Many write helpers log errors but higher-level preset loops ignore per-register failures. Control callbacks return success even if lower-level programming fails in some paths. Tuning math is sensitive to overflow/range assumptions and clock/decimation values. Register maps and FIR coefficients are large magic tables from reference code, making changes high risk.

## Test Signals
Tests should cover EU/NA clock selection, invalid refout load, missing clock/regmap failures, frequency clamping, RX mode selection for AM/FM/VHF, CSM timeout handling, LO/NCO calculations, volatile LNA/IF/PLL controls, I2S/HSLS controls, master/slave and AM Hi-Z programming, ROM read defaults, and failure injection for bulk preset writes and calibration polls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max2175.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max2175.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/max2175.h

## Purpose
`max2175.h` is the local companion header for the MAX2175 tuner driver. It defines crystal frequencies, region/band/mode enums, I2S mode identifiers, coefficient table selectors, LO polarity values, and channel state-machine actions consumed by `max2175.c`.

## Important APIs, Types, And Functions
Important definitions include `MAX2175_EU_XTAL_FREQ`, `MAX2175_NA_XTAL_FREQ`, `enum max2175_region`, `enum max2175_band`, `enum max2175_eu_mode`, `enum max2175_na_mode`, anonymous I2S mode constants, coefficient group constants `MAX2175_CH_MSEL`, `MAX2175_EQ_MSEL`, `MAX2175_AA_MSEL`, LO polarity constants, and `enum max2175_csm_mode`. There are no functions.

## Control Flow
There is no runtime control flow. `max2175.c` uses the enums to index RX mode arrays, select band-specific tuning math, program FIR coefficient memory, set HSLS polarity, and issue channel state-machine commands.

## State And Persistence
The header contributes compile-time constants only. Runtime state lives in `struct max2175` in the C file and in hardware registers.

## Dependencies And Integration Points
This header is included by `max2175.c`; public userspace-facing control IDs come from `linux/max2175.h`, not this local file. Numeric enum values are part of the driver's internal table indexing contract.

## Risks
Reordering enum values would break static array indexes and hardware mode selection. Several modes are documented as possible future additions but not implemented; exposing them without register maps and tests would create invalid tuning paths.

## Test Signals
Tests should assert EU/NA RX mode enum values match array positions, CSM mode values match register programming expectations, and new enum additions include matching preset data, control menus, and mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max2175.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max9271.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/max9271.c

## Purpose
`max9271.c` is a helper library for controlling Maxim MAX9271 GMSL serializers embedded in camera modules. It is not a standalone I2C driver; camera module drivers call its exported functions to wake, identify, configure links, set GPIOs, and program address translation through an existing I2C client.

## Important APIs, Types, And Functions
The file uses `struct max9271_device` from `max9271.h`, wrapping an I2C client. Internal helpers are `max9271_read()`, `max9271_write()`, and `max9271_pclk_detect()`. Exported APIs are `max9271_wake_up()`, `max9271_set_serial_link()`, `max9271_configure_i2c()`, `max9271_set_high_threshold()`, `max9271_configure_gmsl_link()`, GPIO set/clear/enable/disable helpers, `max9271_verify_id()`, `max9271_set_address()`, `max9271_set_deserializer_address()`, and `max9271_set_translation()`.

## Control Flow
Callers wake the chip at the default address, verify ID, optionally readdress serializer/deserializer or set translation, configure I2C timing and GMSL link parameters, and then enable/disable the serial link. Enabling the serial link first polls for a valid pixel clock. GPIO operations read-modify-write serializer GPIO registers. Most configuration changes add conservative sleeps to allow reverse/forward control channel and link timing to settle.

## State And Persistence
No driver-owned persistent state exists beyond the caller-supplied `i2c_client`. `max9271_wake_up()` mutates `dev->client->addr` to the default address, and `max9271_set_address()` only writes the chip register; callers must update the I2C client address themselves afterward. Hardware register state persists until reset or reprogramming.

## Dependencies And Integration Points
The library depends on I2C SMBus operations, delay helpers, module symbol exports, and constants/prototypes from `max9271.h`. It is integrated by remote camera module drivers such as GMSL sensor modules, often in conjunction with MAX9286 deserializers.

## Risks
Several GPIO helpers return success when the initial read fails (`return 0`), which can hide bus errors. The GMSL link configuration is hard-coded and marked FIXME. Address changes require strict caller sequencing or later I2C accesses go to the wrong address. Pixel-clock detection before enabling the serial link can fail if the upstream sensor has not started its clock. Timing delays are empirical and may be board-sensitive.

## Test Signals
Tests should cover SMBus read/write errors, pixel-clock timeout, wake/readdress sequencing, GPIO read failure behavior, ID mismatch, serial link enable/disable register values, high-threshold toggling, I2C timing configuration delays, and address translation programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max9271.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max9271.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/max9271.h

## Purpose
`max9271.h` declares the public helper interface and register bit definitions for MAX9271 serializer support. It allows camera module drivers to configure a serializer without embedding duplicated register constants and control routines.

## Important APIs, Types, And Functions
The header defines `MAX9271_DEFAULT_ADDR`, register bitfields for spread spectrum, serial/control link enable, input type, reverse/forward control, data bus mode, HS/VS encoding, I2C timing, GPIO output bits, pixel-clock detect, and ID values. It defines `struct max9271_device { struct i2c_client *client; }` and prototypes for all exported functions implemented in `max9271.c`.

## Control Flow
The header has no executable flow. It documents expected caller sequencing for key APIs: wake up before other interaction, configure I2C using `MAX9271_I2C*` masks, then use link/GPIO/address helpers as needed.

## State And Persistence
No runtime state is stored here. The only state container is the caller-owned `struct max9271_device`, which points to the active I2C client.

## Dependencies And Integration Points
The header depends on `linux/i2c.h` and is intended for in-kernel GMSL camera module drivers. Its constants are also conceptually paired with MAX9286 deserializer configuration.

## Risks
Macros expose raw register encodings, so invalid combinations are possible. Function comments note limitations: GMSL link configuration is hard-coded, address translation supports only one mapping despite hardware supporting two, and callers must update the I2C client after changing the serializer address.

## Test Signals
Tests should verify exported prototype coverage against `max9271.c`, valid bitmask composition for I2C/GPIO/GMSL setup, caller sequencing around address changes, and documentation updates when additional translation or link modes are implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max9271.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max9286.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/max9286.c

## Purpose
`max9286.c` is a V4L2 media-controller driver for the Maxim MAX9286 GMSL deserializer. It aggregates up to four remote camera links, exposes an I2C mux for reverse-channel access, controls PoC power and GPIOs, binds remote sensors through async notifiers, configures CSI-2 output, and coordinates synchronized streaming.

## Important APIs, Types, And Functions
`struct max9286_priv` holds the I2C client, powerdown GPIO, subdev, pads, PoC regulators/GPIO state, GPIO chip, I2C mux, reverse-channel and I2C timing settings, V4L2 controls, source masks, CSI lane count, source descriptors, and notifier. Key functions include I2C helpers, mux open/close/select/init, `max9286_configure_i2c()`, `max9286_reverse_channel_setup()`, link checks, video-format and fsync programming, pixel-rate aggregation, async bound/unbind handlers, notifier register/unregister, `max9286_s_stream()`, pad format/interval ops, V4L2 register/unregister, hardware setup, GPIO/PoC helpers, DT parsing, probe, and remove.

## Control Flow
Probe parses DT for enabled `i2c-mux` channels, graph endpoints, CSI-2 lane count, bus width, remote I2C speed, reverse-channel amplitude, and PoC method. It enables the chip, closes all mux channels early, disables local auto-ack, sets up GPIO or regulators, powers cameras, configures links/order/masks/video defaults, registers V4L2 subdev and async notifiers, initializes the I2C mux adapters, and leaves mux channels closed. As each remote source binds, the driver creates immutable media links; when all sources are bound, it raises reverse-channel amplitude, checks configuration links, disables local ack, and computes aggregate pixel rate from mandatory source pixel-rate controls.

Stream enable programs video format and framesync, opens all mux channels for shared sync GPIO, starts each source, checks video detect/lock, waits for framesync lock, then enables CSI output in line-interleaved mode. Stream disable disables CSI output, stops all sources, and closes the mux.

## State And Persistence
Runtime state includes source/bound masks, current mux channel/open state, GPIO output cache, reverse-channel amplitude, pixel rate, DT-derived route mask, and active subdev state for formats/frame interval. Hardware state is volatile and reprogrammed during probe/setup and streaming. Fwnode references are held until cleanup. There is no runtime PM.

## Dependencies And Integration Points
The driver depends on I2C SMBus, I2C mux core, OF graph, fwnode APIs, regulators, GPIO descriptors and gpiochip, V4L2 async notifier/subdev/control APIs, media controller links, and remote camera subdevs with pixel-rate controls. It often integrates with MAX9271 serializers and image sensor drivers behind the mux.

## Risks
DT topology is complex: mux channel availability, graph ports, source masks, and PoC supplies must agree. `max9286_notify_bound()` calls configuration-link checks but does not propagate their return value before pixel-rate setup. Stream enable starts sources sequentially; if a later source or link check fails, already-started sources are not explicitly unwound in that error path. Pixel-rate aggregation requires all sources to expose identical `V4L2_CID_PIXEL_RATE`. The mux-open state bypasses per-channel selection while streaming, which is required for sync but changes I2C isolation semantics. Empirical link/framesync delays may be board-sensitive.

## Test Signals
Tests should cover DT parse errors, invalid bus width/I2C speeds/lane counts, sparse mux channels, missing remote endpoints, PoC regulator/GPIO paths, mux select/open/close behavior, async bind/unbind masks and media links, missing/mismatched source pixel rates, stream enable failure unwinding, video/config link timeout, fsync auto/manual period programming, supported mbus formats, and remove cleanup of mux adapters, notifiers, PoC, GPIO, and fwnodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max9286.c -->
