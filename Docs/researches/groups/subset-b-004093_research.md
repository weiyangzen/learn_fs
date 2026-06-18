# Research: subset-b-004093

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max96714.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/max96714.c

## Purpose
`max96714.c` is a V4L2 media-controller I2C driver for the Maxim MAX96714/MAX96714F GMSL2 deserializer. It exposes the deserializer as a two-pad video bridge with one sink pad for the GMSL input side and one source pad for CSI-2 output. It can either forward a remote serializer/camera stream or generate an internal test pattern.

## Important APIs, Types, and Functions
- `struct max96714_priv` is the driver state: I2C client, CCI regmap, optional powerdown GPIO, optional power-over-coax regulator, I2C mux, V4L2 subdev, media pads, MIPI CSI-2 bus config, async notifier, link frequency, current test pattern, and `enabled_source_streams`.
- `struct max96714_rxport` stores the bound remote subdev, remote pad, endpoint fwnode, and optional POC regulator.
- `max96714_enable_tx_port()`, `max96714_disable_tx_port()`, and `max96714_tx_port_enabled()` control/report the CSI transmitter standby bits.
- `max96714_apply_patgen_timing()` and `max96714_apply_patgen()` program the internal pattern generator using the current source-pad format.
- `max96714_s_ctrl()` handles `V4L2_CID_TEST_PATTERN`; it refuses changes while streams are active, toggles forced CSI output, and disables tunnel mode for pattern generation.
- `max96714_enable_streams()` and `max96714_disable_streams()` implement stream forwarding through V4L2 stream routing, translating source-pad stream masks to sink-pad stream masks before delegating to the upstream subdev when no pattern is active.
- `_max96714_set_routing()`, `max96714_set_routing()`, `max96714_set_fmt()`, and `max96714_init_state()` maintain a one-to-one route and mirrored sink/source formats.
- `max96714_notify_bound()` and `max96714_v4l2_notifier_register()` bind the remote endpoint and create an immutable media link.
- `max96714_init_tx_port()` programs CSI lane count, lane map, lane polarity, and DPLL frequency from firmware endpoint data.
- `max96714_parse_dt_txport()` and `max96714_parse_dt_rxport()` parse the CSI output endpoint, optional RX remote endpoint, and optional `port0-poc` regulator.
- `max96714_enable_core_hw()` exits reset, verifies device ID/revision, and requires tunnel mode to be enabled at probe time.

## Control Flow
Probe allocates `max96714_priv`, initializes the CCI regmap and optional powerdown GPIO, powers/resets the chip, validates the device ID and tunnel mode, parses firmware endpoints, initializes the CSI transmitter, enables optional POC power, adds a gated I2C mux adapter, creates the V4L2 subdev, registers the async notifier, and registers the subdev. Remove tears this down in reverse: unregister/cleanup subdev and notifier, delete mux adapters, disable POC, release the remote endpoint fwnode, and assert powerdown.

Normal media graph operation starts from the default route created by `max96714_init_state()`: sink stream 0 maps to source stream 0 with a default 1280x1080 Y8 format. A sink-format update is mirrored to the source side because the chip does not transcode in tunnel-forwarding mode. Starting a stream enables the CSI transmitter if this is the first active stream, applies pattern generator registers if requested, and either skips upstream streaming for patterns or enables the corresponding upstream sink streams. Stopping a stream disables upstream streams first for forwarded video and powers down the CSI transmitter when no source streams remain.

## State and Persistence Behavior
State is in memory only. `enabled_source_streams` tracks active streams and gates format/routing/control mutations. `pattern` persists the selected test-pattern mode until changed by a V4L2 control. `tx_link_freq` and `mipi_csi2` come from firmware and are applied to hardware during probe. `rxport.source.ep_fwnode` holds a reference that is released on error/remove. Hardware state is reset/configured at probe and not saved across driver unload.

## Dependencies and Integration Points
The driver depends on Linux I2C, CCI/regmap helpers, V4L2 controls, V4L2 subdev stream APIs, media controller pads/links, V4L2 fwnode endpoint parsing, optional regulators, optional GPIO descriptors, and I2C mux support. Device-tree integration requires a `maxim,max96714f` compatible node, a source CSI-2 endpoint with exactly one valid link frequency in 50 MHz steps from 50 MHz to 1250 MHz, 1-4 CSI data lanes, and optionally a sink endpoint plus `port0-poc` supply. Runtime media integration is through immutable links to the upstream source subdev and a source pad consumed by a CSI-2 receiver.

## Risks and Edge Cases
- Pattern generation depends on fixed porch/sync timing and a 75 MHz pixel clock assumption. Formats outside expected dimensions may produce timings the receiver cannot use.
- `max96714_s_ctrl()` returns the second `cci_update_bits()` result with the first result threaded through `ret`; test coverage should confirm errors from either write are observable.
- `max96714_enable_streams()` calls `max96714_enable_tx_port()` without checking its return before proceeding.
- The notifier registration error path contains a duplicated `return PTR_ERR(asd);`; harmless to behavior after the first return but a source-quality smell.
- When no RX endpoint exists, test pattern mode is allowed, but forwarded streaming returns `-ENODEV`. Tests should cover both standalone pattern and missing-upstream forwarding.
- The driver assumes tunnel mode is already enabled by hardware/boot state and refuses unsupported state at probe.

## Test Signals
- Build with `CONFIG_VIDEO_MAX96714` and media-controller/V4L2 subdev stream support enabled.
- Probe with valid and invalid device IDs, tunnel mode disabled, missing TX endpoint, invalid link frequencies, and invalid lane counts.
- Exercise async binding and verify the immutable remote-source-to-deserializer-sink media link.
- Use `media-ctl`/V4L2 subdev ioctls to set routing and sink format before streaming, then verify source format mirrors the sink format.
- Start/stop forwarded streams and ensure upstream `enable_streams`/`disable_streams` calls receive translated masks and CSI output standby toggles only on first/last stream.
- Enable checkerboard/gradient with no remote endpoint and verify CSI output plus log-status link/pipe/CSI reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max96714.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max96717.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/max96717.c

## Purpose
`max96717.c` is a V4L2 I2C driver for the Maxim MAX96717/MAX96717F GMSL2 serializer. It models the serializer as a two-pad media bridge from a local CSI-2 sink to a remote GMSL source, supports internal video pattern generation, exposes the serializer GPIOs as a `gpio_chip`, and registers a programmable clock output provider for sensor/reference clocks.

## Important APIs, Types, and Functions
- `struct max96717_priv` contains the I2C client, CCI regmap, I2C mux, CSI-2 endpoint config, V4L2 subdev/pads/control handler/notifier, upstream source subdev and pad, stream mask, clock-output state, GPIO chip, and active pattern mode.
- `max96717_start_csi()` starts or stops the CSI input port by toggling `MAX96717_START_PORT_B`.
- `max96717_apply_patgen_timing()` and `max96717_apply_patgen()` program internal VTX pattern generator timing and colors.
- `max96717_s_ctrl()` handles `V4L2_CID_TEST_PATTERN`, disallowing changes during streaming, toggling automatic BPP use, and disabling tunnel mode for pattern generation.
- GPIO callbacks `max96717_gpiochip_get()`, `max96717_gpiochip_set()`, `max96717_gpio_get_direction()`, `max96717_gpio_direction_out()`, and `max96717_gpio_direction_in()` map gpiolib operations to the MAX96717 per-GPIO register block.
- `_max96717_set_routing()`, `max96717_set_routing()`, and `max96717_set_fmt()` enforce one-to-one stream routing and mirrored sink/source formats.
- `max96717_enable_streams()` and `max96717_disable_streams()` start/stop local CSI capture, optionally delegate stream control to the bound source subdev, and maintain `enabled_source_streams`.
- `max96717_notify_bound()` and `max96717_v4l2_notifier_register()` find the upstream media pad from fwnode data and create an immutable media link.
- Clock-output functions `max96717_clk_recalc_rate()`, `max96717_clk_determine_rate()`, `max96717_clk_set_rate()`, `max96717_clk_prepare()`, and `max96717_clk_unprepare()` expose a discrete-rate reference clock.
- `max96717_init_csi_lanes()` programs CSI lane count, mapping, and polarity; `max96717_hw_init()` validates chip ID/revision and tunnel mode.

## Control Flow
Probe allocates state, initializes the CCI regmap, parses the CSI-2 sink endpoint, validates and initializes hardware, disables GPIO forwarding before registering the local gpiochip, registers the clock output provider, initializes/registers the V4L2 subdev and async notifier, and finally adds a gated I2C mux adapter. Remove unregisters the subdev/notifier through `max96717_subdev_uninit()` and deletes mux adapters.

At media setup time the default state routes sink stream 0 to source stream 0 with a 1280x1080 Y8 default format. Setting an active format or routing is blocked while any source stream is enabled. Streaming starts local CSI before applying pattern generation and before delegating upstream stream enable, and streaming stops local CSI before disabling the upstream source, matching the code comment that stopping the serializer-side CSI first avoids a device lockup with the I2C bus held low.

## State and Persistence Behavior
All state is volatile driver state. `enabled_source_streams` gates runtime reconfiguration. `pattern` records the requested pattern generator mode. `pll_predef_index` records the selected reference-clock rate from a small static table. `source_sd`/`source_sd_pad` are populated by async binding. GPIO direction/output and CSI lane configuration are held in hardware registers and reinitialized only at probe.

## Dependencies and Integration Points
The driver depends on I2C, CCI/regmap, V4L2 subdev stream/routing APIs, V4L2 controls, V4L2 fwnode endpoint parsing, media-controller links, gpiolib, common clock framework, OF clock providers, and I2C mux support. Device-tree integration uses `maxim,max96717f`, a CSI-2 sink endpoint with 1-4 data lanes, an upstream remote endpoint, optional GPIO consumers under the exposed gpiochip, and clock consumers connected through the OF clock provider.

## Risks and Edge Cases
- The provided source contains a duplicated `static int max96717_gpiochip_set(struct gpio_chip *gpiochip,` line before the full function definition. As written, this is a build blocker.
- `max96717_gpiochip_set()` ignores its `value` argument and always writes `MAX96717_GPIO_OUT`, so setting a GPIO low will not work unless corrected.
- `max96717_subdev_uninit()` calls `v4l2_async_unregister_subdev(&priv->sd)` twice, which can cause double-unregister behavior depending on core handling.
- `max96717_set_fmt()` returns the value from `v4l2_subdev_state_xlate_streams()` after format propagation. That helper is used elsewhere as a translated stream mask, so returning it as an errno-style status can report success as a positive nonzero result.
- Pattern mode disables tunnel mode and automatic BPP; paired deserializer setup must match this or pattern output can fail.
- Stream enable assumes async binding populated `source_sd` when not in pattern mode; missing or late binding would lead to a null dereference unless the caller only streams after graph completion.

## Test Signals
- Compile the driver with warnings treated seriously; the duplicate function line should be caught immediately.
- Probe against valid/invalid IDs and with tunnel mode disabled.
- Validate CSI endpoint parsing for lane count, lane order, and polarity, including unused-lane mapping.
- Run gpiolib direction/get/set tests, especially setting an output low.
- Request each supported clock rate and nearby unsupported rates; verify rounding warnings and register programming.
- Exercise pattern and forwarded streaming, checking local CSI start/stop order, upstream stream delegation, and tunnel-mode toggling.
- Verify async media link creation from the remote endpoint and remove/unbind cleanup without double-unregister warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/max96717.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ml86v7667.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ml86v7667.c

## Purpose
`ml86v7667.c` is a V4L2 subdevice driver for the OKI Semiconductor ML86V7667 analog video decoder. It configures the chip for BT.656 output, exposes analog-video controls, reports PAL/NTSC status, and provides fixed media-bus format information for capture bridges.

## Important APIs, Types, and Functions
- `struct ml86v7667_priv` stores the V4L2 subdev, control handler, and current selected video standard.
- `ml86v7667_mask_set()` is the core register-update helper, reading one SMBus byte, applying a mask, and writing the result back.
- `ml86v7667_s_ctrl()` maps V4L2 controls to register fields: brightness, contrast, chroma gain, hue, red/blue balance, sharpness, and color killer.
- `ml86v7667_querystd()` reads `STATUS_REG` and intersects the caller-provided standard mask with detected 625/50 or 525/60 when horizontal lock is present.
- `ml86v7667_g_input_status()` reports `V4L2_IN_ST_NO_SIGNAL` when horizontal lock is missing.
- `ml86v7667_fill_fmt()` returns the fixed YUYV 8-bit 2x8 format, SMPTE170M colorspace, interlaced top-field-first field order, 720 width, and height based on `priv->std`.
- `ml86v7667_get_mbus_config()` advertises BT.656 master output with rising pixel clock and active-high data.
- `ml86v7667_s_std()` writes PAL/NTSC input mode and stores the selected standard.
- Optional ADV_DEBUG handlers expose raw register read/write.
- `ml86v7667_init()` sets BT.656/register mode, fixed PLL clock, ADC clamp, luminance/contrast behavior, derives initial standard from status, disables autodetect, and programs manual input mode.

## Control Flow
Probe first checks for SMBus byte-data support, allocates state, initializes the V4L2 I2C subdev, creates eight standard V4L2 controls, runs control setup, initializes chip registers, and logs detection. Remove frees the control handler and unregisters the subdev. There is no separate runtime stream operation; the decoder is configured at probe and then responds to V4L2 standard, status, format, and control callbacks.

## State and Persistence Behavior
The only persistent software state is `priv->std`, which determines reported frame height and is updated by `s_std()` or initial status sampling. Control values live in the V4L2 control framework and are pushed to registers when changed or during handler setup. Hardware register state is not cached beyond `priv->std`; raw SMBus reads are used for status and read-modify-write control updates.

## Dependencies and Integration Points
The driver depends on I2C SMBus byte-data operations, V4L2 subdev core/video/pad/control APIs, and legacy I2C device ID matching through `ml86v7667`. It integrates with a parallel/BT.656 capture receiver through `.get_mbus_config()`, `.get_fmt()`, `.set_fmt()`, `.g_std()`, `.s_std()`, `.querystd()`, and `.g_input_status()`.

## Risks and Edge Cases
- There is no explicit chip-ID register check, so probe success depends on the I2C address responding and the initialization writes succeeding.
- `s_std()` treats any non-525/60 standard as PAL-like. Callers passing broad masks or invalid standards may get PAL mode.
- `querystd()` intersects the caller mask in place; callers must initialize `*std` to a meaningful candidate mask.
- Controls use signed ranges but write masked byte fields. This matches many legacy V4L2 analog controls, but tests should confirm intended two's-complement field mapping for negative values.
- There is no media-entity pad initialization, runtime PM, or stream gating; integration relies on older subdev usage patterns.

## Test Signals
- Probe on adapters with and without `I2C_FUNC_SMBUS_BYTE_DATA`.
- Verify initialization writes to MRA, PLLR1, ADC2, SSEPL, CLC, MRC, and MRA input-mode fields.
- Toggle each V4L2 control and confirm masked register bits preserve unrelated bits.
- Simulate STATUS horizontal-lock/no-lock and PAL/NTSC bits for `querystd()` and `g_input_status()`.
- Check reported format is 720x480 for 525/60 and 720x576 for 625/50, with BT.656 bus flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ml86v7667.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-driver.c

## Purpose
`msp3400-driver.c` is the main V4L2 I2C driver for the MSP34xx family of TV sound processors. It provides low-level I2C read/write/reset helpers, V4L2 controls for audio processing, routing and tuner callbacks, power-management hooks, chip revision/feature detection, and lifecycle management for the MSP carrier-detection/autoselect kernel threads implemented in `msp3400-kthreads.c`.

## Important APIs, Types, and Functions
- Module parameters (`opmode`, `once`, `debug`, `stereo_threshold`, `standard`, `amsound`, `dolby`) control autodetection behavior, debug logging, stereo threshold, and audio processing choices.
- `msp_reset()` toggles the control subaddress reset state and reads a DSP revision register to verify bus communication.
- `msp_read()`/`msp_write()` implement three-attempt I2C transfers for demodulator and DSP subdevices, resetting the chip on repeated failure. Public wrappers include `msp_read_dem()`, `msp_read_dsp()`, `msp_write_dem()`, and `msp_write_dsp()`.
- `msp_set_scart()` updates the ACB SCART switch matrix and optional I2S mode.
- `msp_wake_thread()` sets `restart`, clears `watch_stereo`, and wakes the control thread.
- `msp_sleep()` waits interruptibly/freezably until timeout, stop, or restart.
- `msp_s_ctrl()` maps V4L2 audio controls to DSP registers: volume/mute cluster, bass, treble, loudness, and balance.
- `msp_update_volume()` forces the volume/mute cluster to be written, including scan-in-progress muting.
- V4L2 callbacks cover radio selection, frequency changes, queried/detected standard, standard selection, audio routing, tuner get/set, I2S clock frequency, and status logging.
- `msp_probe()` reads chip revision/product fields, derives feature flags, selects opmode, creates controls, initializes media pads when enabled, starts the proper kthread, and wakes it.
- `msp_remove()` unregisters the subdev, stops the kthread, resets hardware, and frees controls.

## Control Flow
Probe resets the device before allocation to reject non-MSP chips, initializes the subdev, optional media pads, default standards/routes/audio mode, and wait queue, then reads revision registers. It derives `ident` and feature booleans from family/product/revision fields, chooses manual/autodetect/autoselect opmode, initializes applicable controls, and starts one of `msp3400c_thread`, `msp3410d_thread`, or `msp34xxg_thread`.

Runtime control flow is split between ioctl callbacks and the background thread. Frequency, standard, routing, and radio changes update local state and call `msp_wake_thread()`. The thread then scans or programs the chip based on opmode. During scans, `scan_in_progress` causes volume writes to mute output. When the scan completes, the thread configures audio source/matrix and unmutes by calling `msp_update_volume()`.

## State and Persistence Behavior
`struct msp_state` is the central persistent software state: chip revisions and feature flags, opmode, current/detected standards, radio flag, current demod mode, carrier frequencies, route state, ACB switch state, I2S mode, audmode/rxsubchans, V4L2 controls, scan flags, kthread pointer, wait queue, and restart/watch bits. Hardware state is maintained through direct DSP/DEM writes and is reset on suspend and remove; resume wakes the thread to reprogram detection state.

## Dependencies and Integration Points
The file depends on Linux I2C, kthreads/freezer support, V4L2 device/subdev/control/tuner/audio APIs, media-controller audio pads under `CONFIG_MEDIA_CONTROLLER`, and the shared MSP definitions in `msp3400-driver.h` and `<media/drv-intf/msp3400.h>`. It integrates with board routing through `MSP_INPUT_DEFAULT`, `MSP_OUTPUT_DEFAULT`, and packed route bitfields interpreted by `msp_s_routing()`.

## Risks and Edge Cases
- The provided source contains an extra closing brace immediately after `msp_s_std()`. As written, that is a build blocker.
- `msp_set_scart()` indexes `scart_names[in]` even after invalid `in` values fall into the mute/default path; invalid routes can produce out-of-bounds debug-string access.
- `restart`, `watch_stereo`, `scan_in_progress`, route fields, and audio state are shared between ioctl paths and kthreads without a dedicated mutex. Legacy usage may tolerate this, but races can cause stale programming or missed state changes.
- I2C read/write helpers reset the chip on repeated failure but do not automatically restore all state; the control thread or caller must reprogram later.
- `msp_s_i2s_clock_freq()` only stores `i2s_mode`; hardware is updated by SCART setup/thread paths, so immediate clock changes may not take effect until later programming.
- Feature detection is revision-code based; unsupported or unusual clones can be misclassified.

## Test Signals
- Compile the file with `msp3400-kthreads.c` and header after checking the stray brace.
- Probe failure tests: reset transfer failure, unreadable revision registers, zero revisions, and control allocation errors.
- Feature-detection tests for representative C/D/G family revision/product values.
- V4L2 audio control tests verifying DSP register writes for mute, scan mute, volume, bass, treble, loudness, balance, headphone, and SCART2 volume variants.
- Route tests for default, external-only, tuner, invalid SCART selections, and I2S-capable chips.
- Suspend/resume tests should show reset on suspend and thread wake/reprogramming on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-driver.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-driver.h

## Purpose
`msp3400-driver.h` is the shared internal header for the MSP34xx TV sound processor driver. It defines mode/routing constants, module-parameter externs, the driver-private `struct msp_state`, helper accessors, and cross-file function prototypes used by `msp3400-driver.c` and `msp3400-kthreads.c`.

## Important APIs, Types, and Functions
- `MSP_CARRIER(freq)` converts an audio carrier frequency into the fixed-point carrier value expected by MSP demodulator registers.
- `MSP_MODE_*` constants enumerate demodulator/DSP modes: AM detect, FM radio, terrestrial FM, satellite FM, NICAM variants, BTSC, and external input.
- `SCART_*` constants encode SCART inputs and outputs used by the ACB switch matrix.
- `OPMODE_*` constants select manual, autodetect, or autoselect operation.
- `enum msp3400_pads` defines optional media-controller audio sink/source pads.
- `struct msp_state` stores all persistent driver state: subdev/control handler, revision IDs, feature flags, runtime audio/radio/standard/mode/carrier/routing state, V4L2 audio controls, scan flags, kthread/wait-queue control, and optional media pads.
- `to_state()` and `ctrl_to_state()` recover `struct msp_state` from a subdev or control.
- Prototypes expose low-level DSP/DEM access, reset, SCART switching, volume update, sleep/wake-thread helpers, standard naming/detection helpers, kthread entry points, and manual-mode programming helpers.

## Control Flow
The header does not execute control flow directly, but it defines the data and call surface that binds the main driver and the kthread implementation. The main driver owns allocation, probe/remove, V4L2 callbacks, and control setup. The kthread file owns carrier-detection/autoselect loops and calls the public low-level helpers declared here.

## State and Persistence Behavior
`struct msp_state` is the persistent state object attached to the V4L2 subdev/I2C client. It is shared by synchronous ioctl/control callbacks and asynchronous kthreads. Route, mode, standard, and audio fields mirror both requested software state and programmed hardware state. The restart/watch bits and wait queue are the thread-control mechanism.

## Dependencies and Integration Points
The header depends on V4L2 device/control/media-controller headers and `<media/drv-intf/msp3400.h>` for external routing constants. It is included by both MSP source files, so any change to `struct msp_state` or prototypes affects the whole MSP driver.

## Risks and Edge Cases
- `MSP_CARRIER()` uses floating-point syntax in a macro intended for constants only, relying on compile-time folding. Using it with non-constant values would violate kernel floating-point rules.
- `struct msp_state` exposes many mutable fields without lock annotations, making it easy to add racy call paths.
- The header prototypes create tight coupling between main driver and kthread internals; changing opmode behavior needs coordinated updates in both files.
- Feature flags are compact `u8` booleans; new features should keep semantics clear to avoid confusing capability-derived code paths.

## Test Signals
- Compile with media-controller enabled and disabled to validate the conditional pad member.
- Validate all prototypes match definitions in `msp3400-driver.c` and `msp3400-kthreads.c`.
- Static analysis should check shared state use across kthread and V4L2 callbacks.
- Unit-style checks for `MSP_CARRIER()` should use only literal constants and verify known carrier register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-kthreads.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-kthreads.c

## Purpose
`msp3400-kthreads.c` implements the asynchronous audio-standard detection, carrier scanning, stereo/NICAM/SAP monitoring, and audio-source selection logic for the MSP34xx TV sound processor driver. It contains separate thread flows for older manual carrier-detect devices, newer autodetect devices, and G-family autoselect devices.

## Important APIs, Types, and Functions
- `msp_stdlist[]` maps MSP standard return values to main/secondary carrier values, human-readable names, and V4L2 standard masks.
- `msp3400c_init_data[]` holds demodulator FIR, carrier, mode, source, and matrix programming for manual modes.
- Carrier-detect tables enumerate candidate main and secondary carriers for 4.5, 5.5, 6.0, and 6.5 MHz families.
- `msp_standard_std_name()` and `msp_standard_std()` translate MSP standard codes to names and V4L2 standard masks.
- `msp_set_source()` writes DSP source registers, optionally selecting I2S inputs when Dolby processing is requested.
- `msp3400c_set_carrier()` writes carrier frequency registers and triggers load.
- `msp3400c_set_mode()` programs demodulator filters, mode registers, carriers, DSP source/matrix, and prescales.
- `msp3400c_set_audmode()` chooses mono/stereo/language/NICAM/SCART source routing for manual/autodetect modes.
- `msp3400c_detect_stereo()` reads FM/NICAM detection registers and updates `rxsubchans`/`nicam_on`.
- `watch_stereo()` refreshes stereo state and reapplies audio mode; `msp_once` disables repeated monitoring.
- `msp3400c_thread()`, `msp3410d_thread()`, and `msp34xxg_thread()` are the three background control loops.
- `msp34xxg_modus()`, `msp34xxg_set_sources()`, `msp34xxg_reset()`, `msp34xxg_detect_stereo()`, and `msp34xxg_set_audmode()` implement G-family autoselect support.
- Public dispatchers `msp_set_audmode()` and `msp_detect_stereo()` call the correct implementation based on `state->opmode`.

## Control Flow
All thread functions are freezable loops sleeping on `msp_sleep()` until `restart` or stop. The manual `msp3400c_thread()` mutes output, programs AM detect, waits for tuner settle, scans main carriers, optionally scans secondary carriers, selects the best mode/carriers, unmutes, and then monitors stereo/NICAM changes. The `msp3410d_thread()` uses hardware standard autodetect where possible, falls back for radio/NTSC/AM-sound cases, programs prescales, sets audio mode, unmutes, and monitors stereo. The `msp34xxg_thread()` resets and initializes G-family devices, writes the requested/autodetect standard, waits briefly for hardware detection, unmutes, restores ACB, and monitors BTSC/SAP when relevant.

## State and Persistence Behavior
The threads mutate shared `msp_state` fields: `std`, `detected_std`, `main`, `second`, `mode`, `rxsubchans`, `nicam_on`, `scan_in_progress`, `watch_stereo`, and `restart`. The state persists in memory while the driver is bound and is re-derived from hardware scans after channel changes, routing changes, suspend/resume wakeups, and radio/standard changes. Hardware programming is direct and cumulative; reset paths must reapply mode/source/prescale state.

## Dependencies and Integration Points
The file depends on low-level helpers and state definitions from `msp3400-driver.h`, Linux kthreads/freezer/suspend support, V4L2 standard/tuner constants, and I2C client data. It is tightly integrated with the main driver's V4L2 callbacks: those callbacks set state and wake these threads, while these threads update detected standard and audio status consumed by tuner/status callbacks.

## Risks and Edge Cases
- The provided source contains a duplicated `} else {` in `msp3400c_detect_stereo()` and a duplicated `if (count)` in `msp3410d_thread()`. As written, these are likely build blockers or at least source corruption that must be fixed before compile testing.
- Shared state is not protected by a mutex; thread and ioctl paths can race on route, standard, audmode, and scan flags.
- Carrier scan decisions are threshold/best-value based and can misdetect noisy signals; module parameters (`amsound`, `stereo_threshold`, `standard`, `once`) are important test axes.
- `msp3410d_thread()` indexes `msp_stdlist[i]` after searching for a detected value. The sentinel prevents an immediate out-of-bounds read, but unknown values produce zero carriers and "unknown" behavior unless handled.
- Threads rely on `msp_sleep()` returning restart state; missed wakeups or state changes without `msp_wake_thread()` can leave hardware programmed for the previous channel.
- Hardware resets from low-level I2C errors can invalidate the assumptions of the currently running thread iteration.

## Test Signals
- Compile both MSP source files together to catch the duplicated/stray source lines.
- Simulate manual carrier scans for each main/secondary carrier table, including AM-sound SECAM override.
- Exercise `msp3410d_thread()` autodetect values for NICAM, BTSC, radio, and failed/unknown detection.
- Exercise G-family autoselect for radio, NTSC-J, NTSC-KR, SECAM-L, M/BTSC, and generic autodetect.
- Verify `rxsubchans`, `nicam_on`, `detected_std`, and DSP source registers after stereo/NICAM/SAP changes.
- Test restart behavior during each sleep point to ensure scans abort and restart cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/msp3400-kthreads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m001.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m001.c

## Purpose
`mt9m001.c` is a V4L2 subdevice driver for the Micron MT9M001 CMOS image sensor. It exposes a single-source-pad camera sensor with crop/format controls, runtime power management, basic image controls, and chip detection for color and monochrome sensor variants.

## Important APIs, Types, and Functions
- `struct mt9m001` stores the V4L2 subdev/control handler, exposure cluster, mutex, active crop rectangle, clock, optional standby/reset GPIOs, active and supported media-bus formats, frame-height accounting, top-line skip, and media pad.
- Register helpers `reg_read()`, `reg_write()`, `reg_set()`, `reg_clear()`, and `multi_reg_write()` use SMBus word-swapped operations.
- `mt9m001_init()` soft-resets the sensor and disables output.
- `mt9m001_apply_selection()` programs blanking, row/column start, and window dimensions from the active crop rectangle.
- `mt9m001_s_stream()` powers the device through runtime PM, applies crop, sets up controls, and writes output control to start/stop readout.
- `mt9m001_set_selection()` and `mt9m001_get_selection()` implement active crop bounds and alignment requirements.
- `mt9m001_get_fmt()`, `mt9m001_s_fmt()`, `mt9m001_set_fmt()`, and `mt9m001_enum_mbus_code()` report and select Bayer or monochrome bus formats.
- `mt9m001_power_on()` and `mt9m001_power_off()` manage the sensor clock and optional GPIOs.
- `mt9m001_s_ctrl()` handles vertical flip, gain conversion to sensor register encoding, and simulated auto/manual exposure.
- `mt9m001_video_probe()` enables the chip, reads the chip-version register, selects color or monochrome format tables, resets the sensor, and applies controls.
- Probe configures resources, controls, runtime PM, media entity pad, and async subdev registration.

## Control Flow
Probe checks SMBus word-data support, allocates state, obtains the sensor clock and optional GPIOs, initializes the subdev and controls, initializes default crop to the full active array, powers the sensor, enables runtime PM, detects the chip, initializes registers, creates the media source pad, registers the async subdev, and idles runtime PM. Streaming later resumes the device, applies the current crop/window, reapplies controls, and enables output. Stopping streaming disables output and drops the runtime PM reference.

## State and Persistence Behavior
The active crop rectangle, format pointer, total frame height, exposure/gain/flip controls, and top-skip value are stored in `struct mt9m001`. Runtime PM owns whether hardware is powered. Control writes are skipped when the device is not in use via `pm_runtime_get_if_in_use()`, so control state can be changed while suspended and then pushed by handler setup at stream start/probe. Hardware register state is reset during probe initialization and rewritten on stream start.

## Dependencies and Integration Points
The driver depends on I2C SMBus word-data support, V4L2 controls/events/subdev APIs, media-controller entity pads, runtime PM, sensor clock helpers, GPIO descriptors, and OF/I2C matching (`onnn,mt9m001` and `mt9m001`). It integrates with a parallel camera receiver through a single source pad, fixed bus flags, crop/format pad ops, and `.g_skip_top_lines()`.

## Risks and Edge Cases
- The provided source contains a duplicated local declaration line in `mt9m001_get_fmt()` and a duplicated `.s_ctrl = mt9m001_s_ctrl` initializer in `mt9m001_ctrl_ops`; the duplicated declaration is a build blocker, while the initializer duplication is also invalid C in standard struct initialization.
- `mt9m001_set_selection()` only accepts active selections and ignores TRY selection state, so users cannot test crop changes through TRY state.
- `mt9m001_s_ctrl()` silently returns success when the device is not runtime-active; correctness relies on later handler setup pushing cached values.
- Exposure conversion depends on `total_h`, which changes with crop and `y_skip_top`; tests should verify volatile auto-exposure values after crop changes.
- Format/crop operations are protected by the same mutex only when controls use `hdl.lock`; not all pad operations explicitly lock, so caller/core locking assumptions matter.
- Chip detection writes `MT9M001_CHIP_ENABLE` before reading version; failure from that write is logged but not checked before the read.

## Test Signals
- Compile with runtime PM, V4L2 controls, and media-controller support to catch duplicated source issues.
- Probe color IDs `0x8411`/`0x8421`, monochrome ID `0x8431`, and invalid IDs.
- Test stream start error paths after runtime resume, crop write failure, control setup failure, and output-control write failure.
- Exercise crop alignment/clamping at minimum, maximum, odd width/left, and color Bayer height alignment.
- Verify gain register programming across default, low, mid, and high gain ranges.
- Verify control changes while suspended are applied on next stream start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m111.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m111.c

## Purpose
`mt9m111.c` is a V4L2 subdevice driver for the Micron/Aptina MT9M111, MT9M112, and MT9M131 CMOS image sensors. It supports a parallel camera sensor interface with crop, scaling through sensor contexts, multiple YUV/RGB/Bayer media-bus formats, frame interval selection, power sequencing, and image controls.

## Important APIs, Types, and Functions
- `struct mt9m111_context` describes the context-specific registers for read mode, blanking, reducer/scaler sizes, output format control, and context-control bits. `context_a` and `context_b` represent the sensor's alternate timing/processing contexts.
- `struct mt9m111_mode_info` describes supported frame-rate modes, maximum image size, and read-mode bit programming.
- `struct mt9m111` stores subdev/control state, active context, crop rectangle, clock, output size, frame interval, selected mode, power lock/count, active format, page-map cache, regulator, stream flag, pixel-clock sample polarity, and media pad.
- `reg_page_map_set()` caches page-map changes for 16-bit register addresses across sensor core/colorpipe pages.
- `mt9m111_reg_read()`, `mt9m111_reg_write()`, `mt9m111_reg_set()`, `mt9m111_reg_clear()`, and `mt9m111_reg_mask()` are the SMBus word-swapped register access layer.
- `mt9m111_setup_geometry()` programs crop/window registers and context reducer/scaler registers when the image-flow processor is active.
- `mt9m111_set_selection()` and `mt9m111_get_selection()` implement crop selection.
- `mt9m111_set_pixfmt()` maps V4L2 media-bus codes to output-format bits in both contexts.
- `mt9m111_set_fmt()` chooses a supported format, enforces Bayer/no-upscale rules, programs geometry and pixel format, and blocks active changes while streaming.
- `mt9m111_find_mode()` selects the closest supported frame-rate mode subject to crop and size constraints.
- Control helpers implement flip, gain, auto exposure, auto white balance, test pattern, and color effects.
- `mt9m111_suspend()`, `mt9m111_restore_state()`, `mt9m111_resume()`, `mt9m111_power_on()`, `mt9m111_power_off()`, and `mt9m111_s_power()` manage hardware state and power-counted power transitions.
- `mt9m111_video_probe()` powers the device, validates chip ID, initializes hardware, applies controls, and powers back down.
- `mt9m111_probe_fw()` parses parallel-bus pixel-clock sampling from firmware.

## Control Flow
Probe checks SMBus word-data support, allocates state, parses optional firmware endpoint flags, obtains the `mclk` and `vdd` regulator, initializes defaults and V4L2 controls, creates the media source pad, initializes frame interval and full-frame geometry, probes the powered sensor ID, initializes registers, registers the async subdev, and returns. Power is reference-counted through `.s_power()`: transitioning from zero to one enables clock/regulator and restores sensor state; transitioning back to zero suspends sensor registers, disables regulator, and disables the clock.

Format and crop control are active-state oriented. Crop updates program sensor geometry immediately. Format updates are refused while streaming, clamp output size to crop constraints, handle IFP bypass for 10-bit Bayer, program both context output format registers, and update cached width/height/format. Frame interval selection is also refused while streaming and chooses a mode only when full sensor crop makes the row/column skipping assumptions valid.

## State and Persistence Behavior
The driver caches the active register page (`lastpage`), active context (`ctx`), crop and output geometry, current mode, frame interval, selected pixel format, gain control, power count, and streaming flag. Suspend saves current global gain back into the V4L2 control and powers down sensor blocks. Resume re-enables, resets, restores context, pixel format, geometry, control handler state, and read-mode bits for the selected frame-rate mode. This makes software state the authority after power cycling.

## Dependencies and Integration Points
The driver depends on I2C SMBus word-data operations, V4L2 async/subdev/control/event/fwnode APIs, media-controller pads, regulator and clock frameworks, firmware graph parsing, and OF/I2C matching (`micron,mt9m111` and `mt9m111`). It integrates with parallel capture hosts through a single source pad, `.get_mbus_config()` flags including pixel-clock sampling, pad crop/format/frame-interval ops, and legacy `.s_power()`.

## Risks and Edge Cases
- The provided source includes stray closing braces after `mt9m111_reg_clear()` and after `mt9m111_enum_mbus_code()`, plus a duplicated `return -EIO;` in ADV_DEBUG code. The stray braces are build blockers.
- `mt9m111_s_stream()` only toggles `is_streaming`; it does not start/stop sensor output. Streaming behavior depends on power state and prior register programming rather than stream-time writes.
- `mt9m111_set_selection()` programs hardware directly and has no explicit streaming guard, so crop changes during active capture may disturb frames.
- Page-map caching assumes all register access goes through this helper; debug or external writes to page-map could desynchronize `lastpage`.
- `mt9m111_reg_mask()` writes `(ret & ~mask) | data` instead of masking `data`; callers appear to pass pre-masked values, but new callers must preserve that convention.
- Frame-rate selection returns success without changing mode when crop is not full-frame, which can surprise callers expecting the requested interval to be applied.
- Power-counted `.s_power()` can underflow if callers unbalance power calls; it warns but still depends on correct subdev users.

## Test Signals
- Compile the file to catch stray braces and duplicate code before runtime tests.
- Probe valid IDs `0x143a` and `0x148c`, invalid IDs, missing clock, missing regulator, and firmware endpoint parse errors.
- Exercise power-count transitions, including repeated power-on/off and error unwinds from regulator or resume failure.
- Test all media-bus formats for correct output-format bits, pclk inversion behavior, and no-upscale/IFP-bypass constraints.
- Test crop bounds/alignment and verify geometry/reducer registers for context A and B.
- Test frame interval requests for 8, 15, and 30 fps, cropped-frame refusal, and >640x512 skip of 30 fps.
- Verify restore after suspend/resume reapplies controls, geometry, context, pixel format, and mode read bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/mt9m111.c -->
