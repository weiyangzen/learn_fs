# subset-b-004191 research

Grouped research for Vivid video capture/output helpers and selected media tuner drivers. Each section is keyed by the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-cap.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-cap.c

Purpose: implements Vivid video capture queue operations, capture format negotiation, input/audio/tuner ioctls, TV standard/DV timing/EDID handling, and webcam frame interval enumeration. Important APIs include `vivid_vid_cap_qops`, `vivid_update_quality`, `vivid_update_format_cap`, `vivid_g/try/s_fmt_vid_cap`, selection ioctls, `vidioc_s_input`, `vivid_video_*`, `vivid_vid_cap_s_std`, `vivid_vid_cap_s_dv_timings`, `vidioc_s_edid`, and stream parameters.

Control flow centers on vb2 callbacks: queue setup validates plane count and size, prepare sets payload/data offsets, start calls `vivid_start_generating_vid_cap`, and stop tears down generation. Format set calls try-format first, rejects busy queues, updates crop/compose/scaler rectangles, field mode, bytesperline, test-pattern-generator color state, and per-webcam size/interval caches. Input and timing changes reject active capture/VBI/meta queues before mutating device state.

State is held in `struct vivid_dev`: current input, format, standard, DV timings, EDID blocks, source rectangles, per-input signal controls, TV frequency/audio mode, and TPG state. Dependencies include vb2, V4L2 controls/events/timings/rect helpers, CEC EDID physical address helpers, and vivid core/kthread code. Risks: rectangle scaling paths are branch-heavy, field-alternate has file-io restrictions, EDID/CEC propagation must stay synchronized, and `dv_timings_cap[dev->input]` is referenced before `dev->input` is changed in `vidioc_s_input`. Test signals: v4l2-compliance for capture formats/selection/EDID/source-change, streaming while changing inputs/timings, webcam interval limits, and injected queue/prepare/start failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-cap.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-cap.h

Purpose: public capture-side declaration header for Vivid video support. It exposes capture queue ops, format helpers, selection/pixel-aspect operations, input/audio/tuner controls, TV standard and DV timing ioctls, EDID programming, frame size/interval enumeration, and stream parameter handlers.

Important symbols include `vivid_update_quality`, `vivid_update_format_cap`, `vivid_update_outputs`, `vivid_update_connected_outputs`, `vivid_get_video_aspect`, `vivid_standard`, `vivid_ctrl_standard_strings`, `vivid_vid_cap_qops`, and the `vidioc_*`/`vivid_vid_cap_*` entry points wired into the V4L2 ioctl table elsewhere. It has no persistent state of its own; all state is in `struct vivid_dev` and related V4L2/vb2 objects used by implementation files.

Dependencies are implicit forward declarations from included vivid core headers in includers plus V4L2 types such as `struct file`, `struct v4l2_format`, `v4l2_std_id`, and `struct vb2_ops`. Risks are declaration/implementation drift and keeping `vivid_standard` in sync with its strings. Test signal is compile coverage plus V4L2 ioctl registration paths that depend on exact prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-cap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-common.c

Purpose: shared Vivid video support for capture and output. It defines `vivid_dv_timings_cap`, the full `vivid_formats[]` catalog, format lookup, input/output loopback connection helpers, source-change event dispatch, single-planar to multiplanar conversion, common selection sanitization, format enumeration, standard/timing getters, EDID getter, and event subscription.

Control flow is mostly utility-driven. `vivid_get_format` filters multiplanar formats unless the instance supports them. `vivid_input_is_connected_to` and `vivid_output_is_connected_to` map menu selections to other Vivid instances and validate that current input/output indexes still match. `vivid_vid_can_loop` permits loopback only when output streaming, dimensions, format, field, and SDTV family match. `fmt_sp2mp_func` adapts single-planar ioctl handlers onto mplane implementations. `vidioc_g_edid` can rewrite TX EDID physical address/checksum based on the CEC adapter.

State is global format/timing constants plus reads from `struct vivid_dev`; no independent persistence. Dependencies include V4L2 timing/event helpers, CEC EDID helpers, vivid control arrays, and TPG format metadata. Risks: the static `VIVID_MPLANAR_FORMATS` count must match the tail of `vivid_formats`, loopback assumes connected-instance arrays are valid, and EDID checksum rewrite is offset-sensitive. Test signals: enumerate all formats in single/mplane modes, loopback source-change events, EDID get on RX/TX, and selection flag boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-common.h

Purpose: shared declaration header for Vivid video helpers used by both capture and output. It declares the single-planar conversion callback type `fmtfunc`, `fmt_sp2mp`, `fmt_sp2mp_func`, the DV timing capability object, format lookup, loopback connection helpers, source-change helpers, selection adjustment, format enumeration, common standard/timing/EDID getters, and event subscription.

No control flow or persistent state lives here, but the header defines the API boundary between Vivid ioctl tables and common implementation. It depends on V4L2/vb2/media types supplied through includers and on `struct vivid_dev`/`struct vivid_fmt` definitions from vivid core. Integration points are capture/output format handlers, CEC/EDID paths, and V4L2 event subscription.

Risks are mainly prototype drift, especially `fmtfunc` signatures and helpers shared by single-planar and multiplanar paths. Test signals are build coverage and v4l2-compliance paths that exercise both RX and TX standard/timing/EDID common handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-out.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-out.c

Purpose: implements Vivid video output queue operations, output format negotiation, output selection, framebuffer/overlay controls, output/audio routing, TV standard/DV timing changes, stream parameters, and event subscription. Important APIs include `vivid_vid_out_qops`, `vivid_update_format_out`, `vivid_g/try/s_fmt_vid_out`, mplane/single-plane wrappers, selection handlers, overlay/fbuf handlers, output/audio ioctls, and `vivid_vid_out_s_std`/`s_dv_timings`.

Control flow mirrors capture with vb2 callbacks validating plane sizes, payloads, field alternation, start/stop generation, and request completion. Format setting tries first, rejects busy queues when dimensions/format/field would change, but permits colorspace-only updates during streaming for HDMI-style testing. It updates crop/compose/scaler rectangles, bytesperline arrays, field/std caches, and notifies connected inputs via source-change events.

State lives in `struct vivid_dev`: selected output, `fmt_out`, `bytesperline_out`, sink/crop/compose rectangles, output standard/timing, colorspace/xfer/encoding/quantization, framebuffer flags, overlay position/key/alpha, and audio output. Dependencies include vb2, V4L2 timing/rect/event helpers, vivid OSD, common format conversion, and output kthread generation. Risks: first-plane `sizeimage` accumulation for packed multi-plane formats, colorspace changes while streaming, output-to-input notification correctness, and selection rectangle factoring for interlaced fields. Test signals: v4l2-compliance output format/selection/overlay/fbuf tests, write streaming with field alternate, changing colorspace while queued, and S-Video vs HDMI timing transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-out.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-out.h

Purpose: declaration header for Vivid video output support. It exposes output queue ops, output format reset, mplane and single-plane output format handlers, selection/pixel-aspect operations, overlay and framebuffer controls, output/audio routing, TV standard/DV timing setters, and output stream parameter getter.

It owns no persistent state. Its functions operate on `struct vivid_dev` through V4L2 `file`/`priv` plumbing and use V4L2 buffer, format, selection, framebuffer, audioout, timing, and stream parameter types. Integration points are the Vivid video output ioctl table, vb2 queue setup, and output kthread paths.

Risks are declaration drift and forgetting to expose new output ioctls here when adding implementation in `vivid-vid-out.c`. Test signals are compile coverage and V4L2 output ioctl registration paths, particularly single-planar wrappers that call common SP-to-MP conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/Kconfig

Purpose: Kconfig menu for common media tuner drivers. It defines the umbrella `MEDIA_TUNER` tristate, autoselect behavior for ancillary subdrivers, the visible "Customize TV tuners" menu, and per-driver symbols including the files in this work item: `MEDIA_TUNER_E4000`, `FC0011`, `FC0012`, `FC0013`, `FC2580`, `IT913X`, `M88RS6000T`, `MAX2165`, and `MC44S803`.

Control flow is Kconfig dependency resolution: symbols depend mainly on `MEDIA_SUPPORT` and `I2C`; E4000/FC2580 additionally depend on `VIDEO_DEV` and select `REGMAP_I2C`, while IT913X/M88RS6000T select `REGMAP_I2C`. Defaults are modules when ancillary autoselect is disabled. The top-level `MEDIA_TUNER` selects older analog helpers when `MEDIA_SUBDRV_AUTOSELECT` is set.

State is build configuration only. Dependencies integrate with Makefile `obj-$(CONFIG_...)` lines and header `IS_REACHABLE()` attach stubs. Risks: missing dependency selects cause link failures, hiding ancillary subdrivers can make expected options invisible, and autoselect may include drivers unexpectedly. Test signals: `allyesconfig`, `allmodconfig`, minimal I2C-disabled configs, and build tests for each symbol as built-in/module/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/Makefile

Purpose: builds media tuner objects according to Kconfig symbols. It adds the DVB frontend include directory, defines composite objects for `tda18271`, and maps `CONFIG_MEDIA_TUNER_*` symbols to `.o` files.

Important integration points for this subset are `e4000.o`, `fc0011.o`, `fc0012.o`, `fc0013.o`, `fc2580.o`, `it913x.o`, `m88rs6000t.o`, `max2165.o`, and `mc44s803.o`. The file notes that entries should remain alphabetically sorted by Kconfig name, which helps reduce merge conflicts and makes symbol/object mismatches easier to audit.

There is no runtime state. Dependencies are the Kbuild system and Kconfig symbols. Risks: adding a tuner symbol without a matching object prevents code from building, and reordering against the documented sort convention increases maintenance friction. Test signals are kernel build coverage for each tuner as module/built-in and `scripts/checkkconfigsymbols.py`-style consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/e4000.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/e4000.c

Purpose: Elonics E4000 tuner driver with both DVB tuner ops and optional V4L2 subdev tuner controls. It probes an I2C device via regmap, validates chip id `0x40`, programs sleep/init state, exposes frequency/bandwidth/gain controls, and attaches tuner ops to a supplied DVB frontend.

Control flow: `e4000_probe` allocates `e4000_dev`, initializes regmap, registers V4L2 controls when `VIDEO_DEV` is enabled, installs `fe->ops.tuner_ops`, and stores client data. `e4000_init` writes reset/gain/DC-offset defaults and marks `active`. `e4000_set_params` returns early while sleeping; otherwise it computes fractional-N PLL values from frequency/clock, chooses RF/IF filters and band registers from LUTs, calibrates DC offset, and restores automatic gain. V4L2 controls call gain or bandwidth programming; DVB `set_params` copies frontend frequency/bandwidth cache then tunes.

State includes `active`, `f_frequency`, `f_bandwidth`, clock, regmap, frontend pointer, subdev, and control pointers. Dependencies include I2C/regmap, V4L2 controls/subdev, DVB frontend, and LUTs in `e4000_priv.h`. Risks: control callbacks are no-ops while inactive, bandwidth auto TODO means master must choose bandwidth, gain-control clusters interact through current vs new values, and register write failures can leave partially tuned hardware. Test signals: I2C probe id failure, init/sleep/tune cycles, V4L2 gain/bandwidth control changes, PLL lock volatile control, and DVB get-if-frequency zero-IF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/e4000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/e4000.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/e4000.h

Purpose: public platform-data header for the E4000 tuner I2C driver. It defines `struct e4000_config` with the target `dvb_frontend *fe` and tuner reference `clock`, plus notes the valid I2C address range `0x64`-`0x67`.

There is no control flow or persistent state in the header. State is supplied by board/parent code through `client->dev.platform_data` and consumed by `e4000_probe`, which copies the clock and frontend pointer into `struct e4000_dev` and installs tuner ops.

Dependencies are `media/dvb_frontend.h` and the parent driver that instantiates the I2C client with valid platform data. Risks: no attach stub is provided here, so users must instantiate the I2C driver path correctly; missing `fe` or invalid clock will fail or misprogram PLL math. Test signals: probe with valid platform data, null/invalid platform data review, and board integration compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/e4000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/e4000_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/e4000_priv.h

Purpose: private state and lookup tables for the E4000 driver. It defines `struct e4000_dev`, PLL divider LUT, LNA filter LUT, band register LUT, IF filter LUT, and IF gain register LUT.

Important fields in `e4000_dev` are `client`, `regmap`, `clk`, `fe`, `sd`, `active`, cached frequency/bandwidth, and V4L2 control handler/control pointers. The LUTs drive `e4000_set_params`: frequency chooses PLL output divider, RF/LNA filter, and band registers; bandwidth chooses IF filter; IF gain control indexes `e4000_if_gain_lut`.

State is runtime-private and freed on remove. Dependencies include `e4000.h`, `linux/math64.h`, V4L2 controls/subdev, and regmap. Risks: LUT sentinel values must cover the full accepted frequency/bandwidth/control range, IF gain control max must match the LUT length, and register values are hardware-specific with little self-description. Test signals: boundary frequencies at every LUT transition, bandwidth min/max, manual IF gain index 0 and max 54, and KASAN/UBSAN for out-of-range control indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/e4000_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0011.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0011.c

Purpose: attach-style Fitipower FC0011 DVB tuner driver. It provides raw I2C register read/write helpers, power/reset initialization via frontend callbacks, PLL/VCO programming in `fc0011_set_params`, frequency/bandwidth getters, zero-IF reporting, and `fc0011_attach`.

Control flow: attach allocates `fc0011_priv`, stores I2C/address, and copies tuner ops into the frontend. `fc0011_init` requires `fe->callback` and issues power then reset commands. `set_params` initializes fixed registers, calculates VCO multiplier, fractional XIN, FA/FP divider values, bandwidth bits, and VCO select bits from frontend frequency/bandwidth. It writes cached registers, triggers and reads VCO calibration, retries reset/reprogram up to three times if calibration fails, adjusts VCO selection based on calibration value, forces RC calibration, and caches requested frequency/bandwidth.

State is only `i2c`, `addr`, `frequency`, and `bandwidth` in `fc0011_priv`. Dependencies are DVB frontend callbacks, I2C transfer, delays, and FC0011 register definitions local to the file. Risks: callback absence makes init fail, unsupported bandwidth silently falls back to 6 MHz, repeated `err |= writereg` collapses exact failing register, and calibration retry paths must preserve register cache. Test signals: init without callback, 6/7/8 MHz bandwidths, low-frequency fix below 45 MHz, VCO calibration failure/retry, and attach/release lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0011.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0011.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0011.h

Purpose: public header for FC0011 attach-style tuner integration. It defines `struct fc0011_config` with I2C address, `enum fc0011_fe_callback_commands` for power and reset callbacks, and the reachable/disabled variants of `fc0011_attach`.

There is no runtime logic beyond the disabled inline stub, which logs that the driver is disabled and returns `NULL`. State is supplied by parent demod/board code through the config and frontend callback implementation, then stored in `fc0011_priv` by `fc0011_attach`.

Dependencies are `media/dvb_frontend.h` and `CONFIG_MEDIA_TUNER_FC0011`. Integration point is parent frontend code calling attach and implementing `fe->callback` for tuner power/reset. Risks: missing callback support causes runtime init failure even though attach succeeds; mismatched callback command values break board power control. Test signals: compile with driver disabled/enabled, attach failure handling in parents, and callback command invocation during `init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0011.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012-priv.h

Purpose: private state header for FC0012. It defines `struct fc0012_priv` containing the I2C adapter, immutable public config pointer, and cached frequency/bandwidth values.

There is no control flow. The implementation allocates this object in `fc0012_attach`, uses `cfg->i2c_address`, `xtal_freq`, `dual_master`, `loop_through`, and `clock_out` for initialization/tuning, and returns cached fields through DVB getter ops.

Dependencies are the public `fc0012_config` definition included before this header. Risks: the private struct stores a borrowed config pointer, so the parent-owned config must outlive the tuner; stale cached frequency/bandwidth can result if tuning fails before cache update. Test signals: attach with stack/static config lifetime review, release cleanup, and getter behavior before first successful tune.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012.c

Purpose: Fitipower FC0012 DVB-T tuner driver using attach-style integration. It implements I2C register helpers, init register programming, PLL/VCO tuning, RF strength estimation, frequency/bandwidth/IF getters, chip-id probe during attach, and release.

Control flow: attach opens the demod I2C gate, allocates private state, reads chip id `0xa1`, applies optional loop-through/clock-output writes, installs tuner ops, and closes the gate on all exits. `fc0012_init` writes a register default table adjusted for crystal frequency, dual-master, and loop-through. `set_params` optionally invokes VHF callback, computes VCO multiplier, divider values, fractional XIN, bandwidth bits for `SYS_DVBT` only, writes registers 1-6, runs VCO calibration/recalibration, conditionally toggles VCO select, then caches frequency/bandwidth. RF strength reads AGC/LNA registers and maps estimated power to 16-bit strength.

State is cached in `fc0012_priv`; hardware state is register-programmed, not persisted elsewhere. Dependencies include I2C gate control, DVB frontend property cache, FC001x common crystal/callback enums, and parent callback for VHF enable. Risks: only DVB-T is accepted, config lifetime is borrowed, I2C gate balance is critical, and strength tables are empirical. Test signals: 27/28.8/36 MHz crystals, 6/7/8 MHz bandwidths, non-DVBT rejection, VHF callback, chip-id failure, and strength reads with invalid LNA index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012.h

Purpose: public FC0012 integration header. It defines `struct fc0012_config` with I2C address, crystal frequency, dual-master flag, RF loop-through flag, and clock-output flag, plus enabled/disabled variants of `fc0012_attach`.

No persistent state is owned here. Parent code supplies config to `fc0012_attach`; the implementation stores the pointer in private state and uses the fields during init and tuning. Dependencies are DVB frontend types and `fc001x-common.h` for crystal frequency enum.

Risks: config lifetime must exceed tuner lifetime, disabled Kconfig stub returns `NULL` after a warning, and parent code must handle attach failure cleanly. Test signals: build with `CONFIG_MEDIA_TUNER_FC0012` disabled/enabled, board configs for each crystal/loop/clock combination, and parent cleanup when attach fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0012.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013-priv.h

Purpose: private header for FC0013 logging macros and private state. It defines `err`, `info`, and `warn` printk wrappers with `fc0013` prefix and `struct fc0013_priv` containing I2C adapter, address, dual-master flag, crystal frequency, and cached frequency/bandwidth.

No control flow is present beyond macro expansion. The implementation uses this state for raw I2C transfers, PLL math, VHF/UHF/GPS path selection, and DVB getter ops.

Dependencies are kernel printk levels and public FC0013/FC001x types included by the C file. Risks: macros redefine common names (`err`, `info`, `warn`) after `#undef`, so include ordering matters; `xtal_freq` is stored as `u8` rather than enum; cached frequency/bandwidth are only updated on successful tuning. Test signals: compile with warning macro users, attach/release memory checks, and getter-before-tune behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013.c

Purpose: Fitipower FC0013 DVB tuner driver. It provides raw I2C helpers, init/default register programming, sleep stub, VHF tracking filter selection, PLL/VCO tuning for DVB-T, RF strength estimation, cached getters, and attach/release.

Control flow: attach allocates `fc0013_priv`, stores I2C address, dual-master, and crystal frequency, then installs tuner ops without probing chip id. Init writes a default register table adjusted for crystal and dual-master. `fc0013_set_params` optionally calls frontend VHF enable, opens the I2C gate, sets VHF track, selects VHF/UHF/GPS front-end bits based on frequency, computes VCO multiplier/divider/XIN and bandwidth bits for `SYS_DVBT`, writes registers, adjusts a special register for multiplier 64, runs VCO calibration and optional reselection, caches frequency/bandwidth, and closes the gate. Strength estimation mirrors FC0012 using AGC/LNA tables.

State is private cached config and last successful tune. Dependencies include I2C, DVB frontend cache, optional gate control/callback, and common FC001x enums. Risks: no chip-id validation at attach, only DVB-T supported, GPS/high-frequency branch extends range beyond ordinary DVB-T, and gate closure must happen on all error paths. Test signals: low/VHF/UHF/high-frequency tuning, 6/7/8 MHz bandwidth, non-DVBT rejection, RF strength edge indexes, and attach followed by failed init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013.h

Purpose: public FC0013 attach header. It declares `fc0013_attach(fe, i2c, i2c_address, dual_master, xtal_freq)` when reachable and a disabled inline stub otherwise.

There is no runtime state in the header. Parent code passes address, dual-master flag, and `enum fc001x_xtal_freq` directly instead of through a config struct. The implementation copies those into `fc0013_priv`.

Dependencies are DVB frontend types and `fc001x-common.h`. Risks: direct argument API is less self-documenting than a config struct, disabled builds return `NULL`, and parent code must match the crystal enum values. Test signals: compile enabled/disabled, parent attach failure handling, and argument-order audits for call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc001x-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc001x-common.h

Purpose: common definitions shared by FC0012 and FC0013. It defines supported crystal frequencies (`FC_XTAL_27_MHZ`, `FC_XTAL_28_8_MHZ`, `FC_XTAL_36_MHZ`) and `FC_FE_CALLBACK_VHF_ENABLE` for parent frontend callbacks.

There is no state or control flow. The crystal enum drives PLL reference calculations in FC0012/FC0013, and the callback command lets parent demod/board code switch RF path or GPIO state for VHF.

Dependencies are only includers. Risks: enum value changes would silently alter persisted call-site ABI inside the kernel tree; callback semantics must remain aligned between tuner and parent frontend. Test signals: FC0012/FC0013 tuning across all crystal values and parent callback verification for frequencies below/above 300 MHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc001x-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580.c

Purpose: FCI FC2580 tuner I2C driver with DVB tuner ops and optional V4L2 subdev tuner controls. It probes chip ids `0x56`/`0x5a`, initializes regmap-backed state, tunes fractional-N PLL and IF filters, and exposes bandwidth/frequency control.

Control flow: probe allocates `fc2580_dev`, uses platform data for frontend and clock, initializes regmap, validates chip id, registers optional V4L2 bandwidth controls/subdev ops, installs DVB tuner ops, and exposes a `get_v4l2_subdev` callback through platform data. Init writes a register table and sets active; sleep clears active and writes power state. `fc2580_set_params` returns early while sleeping, computes VCO/dividers/reference divider/fractional word, writes PLL registers, applies many frequency-range register values from LUT using `0xff` as no-op, chooses IF filter values, and polls filter lock for up to 30 ms.

State includes active flag, frequency, bandwidth, clock, regmap, subdev/control handler, and frontend private pointer. Dependencies include regmap/I2C, V4L2 controls/subdev, DVB frontend, jiffies timing, and private LUTs. Risks: single-register regmap access only, TODO bandwidth auto limitation, filter lock timeout logs but does not fail, and platform data is mandatory. Test signals: probe chip-id variants, clock default vs provided, frequency/bandwidth boundary LUTs, V4L2 bandwidth control, and sleep/tune while inactive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580.h

Purpose: public platform-data header for FC2580. It defines `struct fc2580_platform_data` with optional clock, DVB frontend pointer, and a callback slot `get_v4l2_subdev` filled by the driver after probe.

There is no control flow in the header. Runtime state is passed via `client->dev.platform_data`; `fc2580_probe` reads `clk` and `dvb_frontend`, then writes back the subdev accessor for parent drivers that need V4L2 subdev access.

Dependencies are DVB frontend, V4L2 subdev, and I2C types. Risks: platform data must be valid and writable; missing frontend pointer breaks tuner op installation; `get_v4l2_subdev` is only useful after successful probe. Test signals: parent probe ordering, null/zero clock default behavior, and V4L2 subdev retrieval when `CONFIG_VIDEO_DEV` is enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580_priv.h

Purpose: private FC2580 state and hardware lookup tables. It defines initialization register pairs, PLL divider/band LUT, IF filter LUT, frequency-specific register table with `0xff` no-op sentinels, and `struct fc2580_dev`.

The LUTs are consumed by `fc2580_set_params`: PLL LUT selects output divider and band, frequency LUT programs RF/front-end registers, and IF filter LUT selects registers for bandwidth. `struct fc2580_dev` holds clock, client, regmap, V4L2 subdev/control handler, active flag, and cached frequency/bandwidth.

Dependencies include `fc2580.h`, V4L2 controls/subdev, regmap, and math64. Risks: `0xff` sentinel is valid only for the dedicated LUT write helper, frequency/bandwidth sentinels must cover all accepted values, and control ranges must stay consistent with LUT expectations. Test signals: boundary frequencies around 400/538/794/1000 MHz, 6/7/8 MHz bandwidths, active/sleep transitions, and table-sentinel no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/fc2580_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/it913x.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/it913x.c

Purpose: ITE IT913X platform tuner driver, integrated as a child using a demodulator-provided regmap instead of a standalone I2C client. It supports IT9133 AX/BX variants, single/dual roles, DVB tuner init/sleep/set_params, and platform probe/remove.

Control flow: probe allocates `it913x_dev`, copies platform data regmap/frontend/role and platform id chip version, installs tuner ops, and stores driver data. Init writes wake/calibration registers, detects clock mode, derives xtal/fdiv/IQ calibration, polls calibration values with timeouts, handles AX vs BX initialization delay differences, and marks active. Sleep clears active and writes several register ranges, with a shorter first range for dual master to avoid losing slave communication. `set_params` rejects inactive state, chooses LO divider from frequency and `fn_min`, computes IQ calibration and PLL words, selects L-band/LNA band, writes bandwidth and frequency registers.

State includes chip version, role, xtal/fdiv/clock mode, `fn_min`, active flag, frontend, platform device, and shared regmap. Dependencies include platform bus, regmap, DVB frontend property cache, jiffies/delays, and parent demod register map. Risks: tuning before init fails, dual-master sleep path is hardware-sensitive, timeouts may proceed with zero calibration-derived values, and register addresses are demod/tuner shared. Test signals: AX/BX probe ids, single/dual master/slave sleep, init clock identifiers 0/1/unknown, 5/6/7/8 MHz bandwidth selection, and frequency boundary bands including out-of-range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/it913x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/it913x.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/it913x.h

Purpose: public platform-data header for the IT913X tuner child driver. It defines `struct it913x_platform_data` with parent regmap, DVB frontend, and 2-bit role, plus role constants for single, dual master, and dual slave.

No runtime logic exists here. Parent demod code instantiates a platform device with this data; `it913x_probe` copies it into private state and installs tuner ops on the provided frontend.

Dependencies are DVB frontend type declarations and a regmap pointer supplied by the parent. Risks: role constants must match implementation sleep behavior, platform data must outlive probe use, and the regmap must address the combined demod/tuner register space expected by `it913x.c`. Test signals: parent platform-device creation for all roles and compile coverage with `CONFIG_MEDIA_TUNER_IT913X` modular/built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/it913x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/m88rs6000t.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/m88rs6000t.c

Purpose: Montage M88RS6000 internal satellite tuner I2C driver. It validates chip id `0x64`, programs tuner defaults, installs DVB tuner ops, tunes PLL/baseband, sets demodulator master/TS clocks, reports actual frequency/zero IF, and estimates RF strength.

Control flow: probe allocates `m88rs6000t_dev`, initializes regmap, wakes/resets hardware, checks chip id, writes PLL/init/default register sequences, then attaches ops. `set_params` computes an LPF offset for low symbol rates, tunes PLL via `m88rs6000t_set_pll_freq`, programs baseband low-pass bandwidth, pulses register 0, then calls `m88rs6000t_set_demod_mclk`. PLL tuning tries two LO divider candidates, calibrates and reads hardware selection, possibly changes reference divider, finalizes dividers, and caches actual tuned kHz. Demod clock setup derives TS MCLK dividers from delivery system and symbol rate. Strength reads multiple gain registers, accumulates empirical gain tables, and scales to 16-bit.

State is config copy, client, regmap, and `frequency_khz`. Dependencies include I2C/regmap, DVB frontend cache, delays, and satellite delivery fields. Risks: tuner programming also mutates demod clocks, so integration with the demod driver is tight; many register writes are sequential with partial-programming risk; strength math depends on empirical tables; and `get_frequency` returns actual kHz-like value while DVB expects Hz semantics in many tuners. Test signals: probe id failure, symbol-rate branches, DVB-S vs other TS clock, PLL frequency boundaries 520-1550 MHz, low symbol-rate LPF offset, and strength reads at gain extremes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/m88rs6000t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/m88rs6000t.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/m88rs6000t.h

Purpose: public platform-data header for the M88RS6000 internal tuner. It defines `struct m88rs6000t_config` with a DVB frontend pointer.

There is no control flow or persistent state here. The I2C probe obtains this config from `client->dev.platform_data`, copies it into private state, and uses `cfg.fe` to install tuner ops and clear them on remove.

Dependencies are DVB frontend types and parent code that instantiates the internal tuner I2C client. Risks: missing or invalid frontend pointer prevents safe ops installation/removal; the minimal config leaves all hardware assumptions inside the driver. Test signals: parent platform-data validity, probe/remove lifecycle, and disabled/built-in module build combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/m88rs6000t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/max2165.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/max2165.c

Purpose: Maxim MAX2165 attach-style DVB tuner driver. It implements raw I2C register access, ROM-table calibration reads, oscillator/bandwidth/RF programming, debug status dumping, DVB tuner ops, and `max2165_attach`.

Control flow: attach allocates private state, copies tuner ops, stores config/I2C, immediately calls init, and dumps status. Init opens I2C gate, writes initial register defaults, sets oscillator from `osc_clk`, reads ROM calibration values, selects 8 MHz bandwidth, and closes gate. `set_params` accepts only 7 or 8 MHz bandwidth, caches frequency, opens gate, writes bandwidth and fractional PLL/tracking-filter values, delays, dumps status, and closes gate. PLL math uses `fixpt_div32` to produce integer and 20-bit fractional dividers. Getters return cached frequency/bandwidth, while status currently returns zero after debug dump.

State is `max2165_priv`: borrowed config, I2C adapter, cached frequency/bandwidth, and ROM-derived filter coefficients. Dependencies include I2C, DVB frontend, tuner-i2c include, module parameter `debug`, and I2C gate control. Risks: `priv->bandwidth` is never updated in `set_params`, attach ignores init errors, ROM read helper ignores individual I2C errors, and `get_status` does not expose real lock bits. Test signals: 7/8 MHz acceptance, unsupported bandwidth rejection, oscillator values, attach with failed init/I2C, bandwidth getter after tune, and debug status reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/max2165.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/max2165.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/max2165.h

Purpose: public MAX2165 attach header. It forward-declares DVB/I2C types, defines `struct max2165_config` with I2C address and oscillator clock in MHz, and provides enabled/disabled variants of `max2165_attach`.

No runtime state is owned here. Parent code provides config to attach; implementation stores the pointer and uses `osc_clk` for PLL reference setup and `i2c_address` for transfers. The disabled stub prints a warning and returns `NULL`.

Dependencies are `CONFIG_MEDIA_TUNER_MAX2165`, parent frontend code, and valid oscillator values documented as 4, 16, 18, 20, 22, 24, 26, or 28 MHz. Risks: config lifetime is borrowed, invalid oscillator values are not validated in the header, and parents must handle disabled/failed attach. Test signals: enabled/disabled builds, oscillator value coverage, and parent cleanup after `NULL` attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/max2165.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/max2165_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/max2165_priv.h

Purpose: private register map and state for MAX2165. It defines register addresses for PLL divider, tracking filter, LNA, PLL config, shutdown/VCO/baseband/DC-offset, ROM table access, status, and autotune registers, plus `struct max2165_priv`.

The private state stores parent config/I2C, cached frequency/bandwidth, and calibration values read from the chip ROM: notch filter configs, balun references, and 7/8 MHz baseband filter configs. These fields are consumed by bandwidth and RF tuning paths.

Dependencies are the public config type included by the C file. Risks: register constants are untyped raw values, cached bandwidth must be kept in sync by implementation, and ROM-derived values need valid reads before tuning. Test signals: init path reading ROM table, set-bandwidth using both 7 and 8 MHz values, and failure injection for ROM/status register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/max2165_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803.c

Purpose: Freescale MC44S803 attach-style DVB tuner driver. It performs 24-bit register read/write over I2C, identifies the tuner by ID, initializes oscillator/power/mixer/circuit/AGC state, programs dual-LO tuning parameters, and exposes frequency/IF getters.

Control flow: attach allocates private state, opens I2C gate, reads `MC44S803_REG_ID` through the data-register indirection, validates ID `0x14`, installs tuner ops, stores private state, and closes the gate. Init opens the gate, resets the chip, powers oscillator, configures mixer/circuit adjust/digital tune/AGC registers, and closes the gate on success or error. `set_params` caches requested frequency, calculates reference dividers, first and second LO divider values using `MC44S803_IF1` and `MC44S803_IF2`, opens the gate, writes reference/LO/digital-tune registers, and closes the gate. `get_if_frequency` reports 36.125 MHz.

State is private config/I2C/frontend pointer plus cached frequency. Dependencies include I2C gate control, DVB frontend cache, and bitfield macros/register definitions in `mc44s803_priv.h`. Risks: register access uses packed 24-bit values and field macros, attach ID read is described as hasty, partial init/tune writes can leave hardware inconsistent, and no sleep op is provided. Test signals: ID mismatch, gate balance on each error, frequencies across 48-1000 MHz, IF reporting, and digital-output config variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803.h

Purpose: public MC44S803 attach header. It forward-declares DVB/I2C types, defines `struct mc44s803_config` with I2C address and digital-output flag, and provides enabled/disabled variants of `mc44s803_attach`.

No runtime state is owned here. Parent code passes config to attach; implementation stores the pointer and uses `dig_out` during circuit-adjust initialization. The disabled stub logs a warning and returns `NULL`.

Dependencies are `CONFIG_MEDIA_TUNER_MC44S803` and parent frontend code. Risks: config lifetime is borrowed by private state, disabled/failed attach must be handled by the parent, and invalid `dig_out` values are not constrained by type. Test signals: enabled/disabled builds, parent attach error handling, and init with both digital output settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803_priv.h

Purpose: private MC44S803 register/bitfield definitions and state. It documents the tuner register map, defines oscillator and IF constants, register numbers, bit masks/shifts, field pack/unpack macros `MC44S803_REG_SM` and `MC44S803_REG_MS`, and `struct mc44s803_priv`.

The constants drive all init and tuning writes in `mc44s803.c`: oscillator/power/reference/mixer/reset/LO/circuit/digital tune/AGC/data/id fields are packed into 24-bit register values. Private state stores public config, I2C adapter, frontend pointer, and cached frequency.

Dependencies are the public config type and kernel integer types through includers. Risks: field macro correctness is critical because every write packs raw bitfields; comments contain hardware datasheet assumptions; IF constants directly shape LO math; and cached state is minimal. Test signals: field macro pack/unpack sanity checks, ID extraction from read value, frequency calculations around range limits, and static review of mask/shift overlaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mc44s803_priv.h -->
