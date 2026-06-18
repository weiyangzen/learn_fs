# subset-b-004104 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tc358743.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tc358743.c

### Purpose
`tc358743.c` is the V4L2 subdevice driver for the Toshiba TC358743 HDMI-to-MIPI CSI-2 bridge. It receives HDMI or DVI-D, exposes detected digital video timings, programs HDMI receiver, audio, EDID/HPD, optional CEC, and CSI-2 transmitter blocks, and presents one source media pad to downstream capture hardware.

### Important APIs, Types, And Functions
The central state is `struct tc358743_state`, which combines platform data, parsed CSI-2 bus configuration, subdev/media pad/control handler, EDID count, configured DV timings, current mbus format, active CSI lane count, optional reset GPIO, polling/IRQ work, debugfs infoframe objects, and optional `cec_adapter`. Register access is through local `i2c_rd*()` and `i2c_wr*()` helpers that handle 16-bit register addresses and little-endian 8/16/32-bit values. Key setup functions are `tc358743_initial_setup()`, `tc358743_set_ref_clk()`, `tc358743_set_pll()`, `tc358743_set_csi()`, `tc358743_set_csi_color_space()`, `tc358743_set_hdmi_phy()`, `tc358743_set_hdmi_audio()`, and `tc358743_set_hdmi_info_frame_mode()`. V4L2 entry points include DV timing query/set/get, mbus code enum/get/set, EDID get/set, `s_stream`, `g_input_status`, event subscription, and log status. Optional CEC hooks implement adapter enable, logical address, monitor-all, transmit, and RX/TX interrupt handling.

### Control Flow
Probe allocates state, accepts platform data or parses device-tree endpoint/refclk/link-frequency/reset GPIO data, initializes the V4L2 subdev, validates the chip ID, creates read-only power/audio controls, initializes media entity state, optional CEC, hardware defaults, default 640x480 timings, CSI color space, interrupts, IRQ or polling timer, CEC registration, async subdev registration, packet monitoring, and debugfs infoframe files. Runtime format control is driven by HDMI interrupt sources and by userspace pad operations. `tc358743_get_detected_timings()` reads receiver measurement registers only when HPD is high, TMDS exists, and sync is stable. `tc358743_s_dv_timings()` validates timings, stores them in state, disables streaming, then reprograms PLL and CSI. `tc358743_set_fmt()` selects RGB888 or UYVY, disables streaming, reprograms PLL/CSI/color space, and keeps width/height tied to configured timings. `tc358743_s_stream()` toggles video/audio buffers and CSI lane state; disabling also reinitializes CSI to return lanes to LP-11.

### State, Persistence, And Dependencies
Persistent driver state is in memory: EDID block count, current `v4l2_dv_timings`, selected mbus code, CSI lanes in use, CEC physical address via the CEC core, and cached platform timing parameters. Hardware state is persisted in device registers until reset or power loss, including EDID RAM, HPD output, PLL, CSI, PHY, audio, and interrupt masks. `confctl_mutex` protects shared `CONFCTL` bit updates between streaming/configuration paths and HDMI system interrupt handling. Dependencies include Linux I2C, V4L2 subdev/control/event/debugfs/DV timings/media frameworks, OF graph and `v4l2_fwnode`, GPIO, delayed work/timers, HDMI infoframe parsing, optional CEC, and `media/i2c/tc358743.h` platform data.

### Integration Points
The driver registers as an I2C driver with `toshiba,tc358743` OF match and `tc358743` I2C ID. It integrates with a downstream CSI-2 receiver through one source pad and `get_mbus_config()`, with userspace through V4L2 subdev devnode/events/controls/EDID/DV timing ioctls, with system firmware through refclk and endpoint link frequencies, with debugfs for infoframe reads, and optionally with the CEC framework. Interrupt service can use a threaded GPIO/IRQ line or an internal polling timer, with faster polling when CEC is active.

### Risks
CSI lane selection is derived from configured timings and PLL lane bitrate; bad timings, unsupported link frequency, or low-lane configurations can underprovision throughput. `i2c_wr()` truncates writes beyond the EDID block transfer limit after warning, so future callers must respect `I2C_MAX_XFER_SIZE`. HPD/EDID sequencing is delayed and tied to +5V detection, making source-change races possible if work cancellation or interrupt masking is wrong. HDCP programming is deliberately restricted in debug register writes, but HDCP enablement still changes authentication registers and BKSV clearing behavior. Probe OF code enables the refclk and only disables it on error, so board power management expectations depend on the clock framework lifetime. Interrupt handlers often log unhandled bits but continue, so hardware revisions with new bits need validation.

### Test Signals
Useful signals include successful probe with platform data and OF endpoints, chip-ID rejection, EDID set/get for zero, one, and eight blocks, HPD assertion only after EDID and +5V, source connect/disconnect events, stable/unstable timing queries, RGB and UYVY format changes, stream enable/disable lane LP-11 behavior, CSI error interrupt logging/clear, audio-present and sampling-rate control updates, CEC RX/TX if configured, debugfs infoframe reads, and suspend-like reset/power-cycle retesting on boards with reset GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tc358743.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tc358743_regs.h -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tc358743_regs.h

### Purpose
`tc358743_regs.h` defines the TC358743 register addresses, masks, and value-construction macros used by the HDMI receiver, CSI-2 transmitter, EDID RAM, HDCP, audio, infoframe, interrupt, and optional CEC paths in `tc358743.c`.

### Important APIs, Types, And Functions
The header is macro-only. It defines global registers such as `CHIPID`, `SYSCTL`, `CONFCTL`, `INTSTATUS`, `PLLCTL0/1`; CSI/PHY registers such as lane control, timing counters, `CSI_CONFW`, `CSI_START`, error masks; CEC registers and CEC RX/TX status/buffer masks; HDMI interrupt/status/mask registers under the `0x8500` range; video output/color registers; EDID mode/length/RAM registers; audio control registers; infoframe packet ranges and lengths; HDCP key/status registers; and helper macros like `SET_PLL_PRD()`, `SET_PLL_FBD()`, `SET_PHY_AUTO_RST1_US()`, `SET_BUFINIT_START_MS()`, and `SET_NO_AVI_LIMIT_MS()`.

### Control Flow
There is no executable flow. The macros encode the register programming contract that the C file follows: probe validates `CHIPID`, setup drives `SYSCTL`, PLL, PHY, HDMI, audio, infoframe, and CSI registers, interrupt handlers read and clear `*_INT` and `INTSTATUS` bits, EDID operations use `EDID_LEN*` and `EDID_RAM`, and CEC operations use `CEC*` addresses and status masks.

### State, Persistence, And Dependencies
This file contains no state. Its constants describe persistent hardware state stored in the TC358743 registers. It depends only on kernel bit operations being available through including C files and on the driver using correct access widths for each register range.

### Integration Points
The header is included by `tc358743.c`. It is the integration boundary between driver logic and the vendor register map, including named ranges for V4L2 ADV_DEBUG register dumping, debugfs infoframe extraction, audio and HDMI status logging, and optional CEC adapter handling.

### Risks
Incorrect masks or helper macros can silently misprogram hardware because most writes are raw register writes. Register width varies by address range; callers must use the right 8/16/32-bit helper. Some symbols are marked as not present in the referenced functional spec, so they are likely based on empirical or later-source information and should be validated on hardware revisions. Macro names reuse generic terms like `CHIPID` and many `MASK_*` names, so this header should stay private to the driver translation unit.

### Test Signals
Compile coverage catches missing or renamed macros. Runtime evidence includes correct chip ID/revision reporting, PLL lock, CSI lane activation, infoframe reads with expected packet lengths, EDID RAM readback, audio sampling-rate updates, interrupt clear behavior, and CEC TX/RX status if CEC is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tc358743_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tc358746.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tc358746.c

### Purpose
`tc358746.c` implements a V4L2 media-controller subdevice for the Toshiba TC358746 parallel-to-CSI-2 bridge. The driver currently supports only parallel input to CSI-2 output, including format propagation, PLL/MIPI D-PHY timing programming, FIFO sizing, runtime PM, regulators, reset GPIO, and optional MCLK clock-provider support.

### Important APIs, Types, And Functions
`struct tc358746` holds the subdev, two media pads, async notifier, parsed CSI endpoint, control handler, regmap, refclk, reset GPIO, regulators, MCLK `clk_hw`, PLL settings, and `phy_configure_opts_mipi_dphy`. `struct tc358746_format` maps V4L2 mbus codes to peripheral data format, parallel data format mode, bus width, and bits per pixel. Important helpers include `tc358746_write/read/update_bits()`, `tc358746_sw_reset()`, `tc358746_find_pll_settings()`, `tc358746_apply_pll_config()`, `tc358746_apply_dphy_config()`, `tc358746_apply_misc_config()`, `tc358746_calc_vb_size()`, `tc358746_enable_csi_lanes()`, `tc358746_enable_csi_module()`, `tc358746_enable_parallel_port()`, `tc358746_s_stream()`, MCLK clock ops, output endpoint parsing, async notifier registration, and runtime PM suspend/resume.

### Control Flow
Probe creates regmap, obtains and samples `refclk`, validates refclk range, gets regulators and reset GPIO, initializes the subdev/entity/state, parses the CSI-2 output endpoint, calculates PLL rate from the first link frequency, derives default D-PHY timing config, creates a read-only link-frequency control, enables runtime PM, initializes hardware and chip ID, registers optional MCLK, then registers the async notifier and subdev. Streaming enable resumes the device, applies D-PHY counters, programs data format/FIFO/word count based on the active sink format and remote source link frequency, enables CSI lanes and module, enables the parallel port, then starts the upstream subdev. Streaming disable disables lanes first, resets the CSI module to force LP-11, disables the parallel port, autosuspends, and then stops the upstream subdev.

### State, Persistence, And Dependencies
Active V4L2 formats live in subdev active state; PLL/MCLK derived values live in `struct tc358746`; endpoint link frequencies are retained in `csi_vep`; runtime power state is handled by PM core. Hardware registers persist until reset or power removal; software reset does not clear all register values, which the driver relies on when disabling CSI. Dependencies include regmap over I2C with 16-bit register/value formatting, regulator bulk APIs, clk and clk-provider APIs, runtime PM, GPIO descriptors, `phy-mipi-dphy` timing helpers, V4L2 subdev/media/fwnode/async frameworks, and a remote parallel-input source subdev.

### Integration Points
The driver binds via `toshiba,tc358746`. It exposes a sink pad for the upstream parallel source and a source pad for the downstream CSI-2 receiver. Firmware graph endpoints provide sink and source bus information; source endpoint link frequency drives PLL and D-PHY setup. `V4L2_CID_LINK_FREQ` reports the single supported CSI link frequency. Optional `#clock-cells` lets the bridge export an MCLK to a sensor or upstream device.

### Risks
Only the first link frequency is supported despite endpoint arrays allowing more. PLL and MCLK search choose nearest feasible rates and warn on mismatch, so marginal timing can occur if board firmware asks for unsupported clocks. FIFO sizing depends on the upstream source link frequency and active width; underflow/overflow prevention returns `-EINVAL` but only at stream-on. `regmap_bulk_write/read()` uses a count of 2 for 32-bit registers while `val_bits` is 16, so endian assumptions and register autoincrement must remain correct. Runtime PM resume is shared between streaming and MCLK clock ops, making ordering and autosuspend timing important. The code supports many raw Bayer codes but the source pad exposes only CSI-compatible transformed codes where marked.

### Test Signals
High-value tests include DT endpoint validation failures, unsupported refclk/link-rate/lane-count cases, chip ID validation, stream-on/off with upstream subdev call ordering, LP-11 observation after disable, active format propagation from sink to source, FIFO sizing for equal and faster CSI bitrates, single link-frequency control reporting, MCLK rate determination/set/enable/disable, runtime PM autosuspend/resume cycles, and regulator/reset GPIO sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tc358746.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda1997x.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tda1997x.c

### Purpose
`tda1997x.c` is a V4L2 subdevice driver for NXP TDA19971/TDA19973 HDMI receivers. It manages HDMI input detection, EDID/HPD, video timing detection, color-space conversion, parallel or BT.656 video output formatting, audio output and ASoC capture registration, interrupt handling, regulators, and platform/OF configuration.

### Important APIs, Types, And Functions
`struct tda1997x_state` contains chip metadata, platform data, primary and CEC I2C clients, subdev, regulators, media pad, page and state locks, chip configuration flags, input/activity status, HDMI AVI/colorimetry/timings/current mbus code/video format, controls, audio state, and cached EDID. Register access is page-based through `tda1997x_setpage()`, `io_read/write()`, `io_read16/24()`, `io_write16/24()`, and `io_readn()`, protected by `page_lock`. Major logic includes `tda1997x_manual_hpd()`, EDID enable/disable/set/get, `tda1997x_setup_format()`, `tda1997x_configure_csc()`, `tda1997x_configure_vhref()`, `tda1997x_configure_vidout()`, `tda1997x_configure_audout()`, `tda1997x_detect_std()`, infoframe parsing, per-source IRQ handlers, V4L2 timing/format ops, control ops, `tda1997x_core_init()`, DT parsing, module identification, ASoC DAI startup, probe, and remove.

### Control Flow
Probe validates SMBus support, allocates state, parses OF or platform data, obtains regulators, powers the chip, initializes locks and delayed HPD work, identifies chip type/revision, initializes the V4L2 subdev and allowed mbus codes based on chip variant, output bus type, and bus width, sets default 1080p60 timings and SRGB full-range colorimetry, disables/resets HDCP for correct I2C access, creates a dummy CEC-address I2C client, runs core hardware initialization, creates controls, initializes the media entity, registers the subdev, optionally registers an ASoC codec/DAI, and requests a threaded IRQ. Interrupt handling loops over top-level flags under `state->lock`, dispatching SUS, DDC, RATE, INFO, AUDIO, and HDCP handlers. Timing detection reads measured format registers and normalizes through `v4l2_find_dv_timings_cap()`. Format and timing set operations update state, then reconfigure VHREF, CSC, and video output.

### State, Persistence, And Dependencies
Software state persists in `tda1997x_state`: cached page number, input-detect flags, activity state, selected mbus code, timing, colorimetry, audio parameters, EDID bytes, and control values. EDID is also written into hardware RAM and exposed through HPD after delayed work. Hardware state includes paged register banks for SUS/DDC/RATE/INFO/AUDIO/HDCP interrupts, video data path, output pin mapping, audio formatter, and power control. Dependencies include V4L2 subdev/control/event/DV timing/media APIs, HDMI infoframe helpers, OF graph/fwnode parsing, regulators, I2C dummy device support for CEC register address space, interrupt framework, and ASoC PCM/DAI/component APIs.

### Integration Points
The driver binds to `nxp,tda19971` and `nxp,tda19973` or matching I2C IDs. Device-tree endpoint flags and `nxp,vidout-portcfg` define output bus geometry and pin mapping; optional `nxp,audout-*` properties enable I2S or SPDIF audio output. It exposes one source pad as a digital video decoder, V4L2 events for source changes, controls for +5V, RGB range, and IT content type, EDID ioctls, timing query/set/get, and optional ASoC capture constrained to the detected HDMI sample rate.

### Risks
The paged I2C model relies on `page_lock` and a cached page byte; any direct access outside helpers would corrupt addressing. EDID storage is fixed at 256 bytes and `set_edid()` writes both base and extension loops even when one block is requested, so callers must provide a valid buffer for the requested operation. `set_rgb_quantization_range()` appears to invert the manual limited/full assignments relative to the control names, which deserves hardware/user-visible validation. Interrupt dispatch uses an `else if` chain for several top-level flags, so simultaneous sources are processed over repeated loop iterations and rely on flags remaining latched. Remove destroys `audio_lock` only when audio is enabled, but that mutex is not initialized in probe in the visible code. The ASoC startup constrains the PCM rate to current detected audio rate; if no rate has been detected yet, startup can constrain to zero.

### Test Signals
Tests should cover probe for both chip variants and bus widths, missing/invalid `nxp,vidout-portcfg`, regulator power failure cleanup, chip mismatch, EDID one/two block set/get and HPD delay, +5V control update on DDC interrupt, RATE activity lost/detected events, format-change events from SUS/FMT, timing query for no-link/no-sync/valid HDMI, RGB/YUV output format changes and CSC matrix selection, audio infoframe parsing and DAI rate constraints, IRQ storm handling with multiple top-level flags, and remove cleanup with audio enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda1997x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda1997x_regs.h -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tda1997x_regs.h

### Purpose
`tda1997x_regs.h` defines the paged register address space and bit fields for the NXP TDA1997x HDMI receiver family. It supports `tda1997x.c` hardware programming for general control, video timing measurement, HPD/EDID, HDMI/HDCP/audio/infoframe blocks, video formatter output, interrupt sources, and CEC-side power/clock control.

### Important APIs, Types, And Functions
The file is macro-only. It defines page 0 general registers (`REG_VERSION`, interrupt mask/clear/status, timing measurement registers, output controls), page 1 HDMI packet flags, page 0x12/0x13 extra HDMI controls, page 0x14 audio controls, pages 0x20/0x21 EDID and HPD storage, page 0x30 nonvolatile/config mirror registers, and page 0x80 CEC-side control registers. It also defines masks for detected 5V/HPD, input selection, service mode, VHREF, PCLK, audio formatter, video formatter, HDMI resets, HDCP flags, interrupt category bits, audio/infoframe flags, rate/SUS status, and fixed tuning values such as `CLK_MIN_RATE`, `CLK_MAX_RATE`, `WDL_CFG_VAL`, and `DC_FILTER_VAL`.

### Control Flow
There is no executable code. The address high byte is the page selected through `REG_CURPAGE_00H`; low bytes are then used for SMBus byte accesses. Driver control flow maps directly to these groups: core init programs HPD, interrupts, rate windows, HDCP, output, and audio registers; timing detection reads `REG_FMT_*` and period registers; IRQ handlers read/clear `REG_INT_FLG_CLR_*`; EDID APIs write `REG_EDID_IN_BYTE*`; and infoframe handlers read `*_IF` packet areas.

### State, Persistence, And Dependencies
The header has no mutable state. It describes hardware state across multiple register pages. It depends on kernel `BIT()` definitions and on callers using page-aware access helpers. Several masks encode hardware status conventions, such as `LAST_STATE_REACHED` for SUS lock and `MASK_CLK_STABLE/MASK_CLK_ACTIVE` for activity detection.

### Integration Points
This header is private to the TDA1997x driver. It is the shared vocabulary for V4L2 timing reporting, HPD/EDID behavior, IRQ masking and clearing, ASoC audio output configuration, and board-specific output pin mapping written from device-tree data.

### Risks
Register-page addressing makes high-byte mistakes severe; a correct macro can still be misused if a caller bypasses `io_read/write()`. Some masks and comments contain legacy spelling or naming inconsistencies, and constants like clock ranges and DC filter values are board/hardware-tuning sensitive. The file does not encode access size or signedness for matrix coefficients, so C code must choose byte/16/24-bit helpers correctly.

### Test Signals
Compile coverage verifies symbol availability. Runtime signals include correct page switching, chip version/config reads, stable interrupt clear behavior, timing register decoding, EDID HPD operation, audio output enable bits matching channel allocation, video output pin map programming, and expected activity detection from RATE/SUS status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda1997x_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda7432.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tda7432.c

### Purpose
`tda7432.c` is a simple V4L2 I2C subdevice driver for the ST/STS-Thomson TDA7432 audio processor. It controls audio volume, mute, balance, bass, treble, and loudness for older video-capture boards.

### Important APIs, Types, And Functions
`struct tda7432` wraps a V4L2 subdev and control handler, with clustered bass/treble and mute/balance controls. Module parameters are `debug`, `loudness`, and `maxvol`. Register constants cover input selection, volume, tone, four channel attenuators, and loudness. `tda7432_write()` sends two-byte subaddress/value writes, `tda7432_set()` initializes the chip, `tda7432_s_ctrl()` maps V4L2 audio controls to chip attenuation/tone/volume registers, `tda7432_log_status()` logs control state, and probe/remove manage controls and subdev registration.

### Control Flow
Probe allocates state, initializes the I2C subdev, creates volume/mute/balance/bass/treble controls, clusters bass with treble and mute with balance, sets up controls, clamps the `loudness` module parameter to 0..15, and writes initial chip registers. Control writes update only the affected hardware registers: mute/balance writes all four attenuators, volume writes the global volume register with optional loudness bit, and bass/treble writes the tone register. Remove writes the default initialization sequence again, unregisters the subdev, and frees controls.

### State, Persistence, And Dependencies
Software state is limited to V4L2 control values and module parameters. Hardware state persists in the TDA7432 registers until rewritten. The driver depends on Linux I2C, V4L2 subdev/control frameworks, and the board creating an I2C client at the expected address; it does not identify the chip.

### Integration Points
The driver binds to the `tda7432` I2C ID and exposes standard audio controls through a V4L2 subdev. It is intended to be composed into larger analog capture-card drivers that route audio through this processor.

### Risks
The driver explicitly does not verify the chip, so any device at the same I2C address can be programmed. `tda7432_write()` returns `-1` instead of a conventional errno and most callers ignore write failures. The `maxvol` parameter naming/description is confusing relative to the control range setup. Balance attenuation and tone conversion encode chip-specific inverse scales that need hardware confirmation. No locking is used beyond V4L2 control serialization.

### Test Signals
Useful tests include probe/control creation, loudness parameter clamping, volume min/max mapping with and without `maxvol`, mute plus left/right balance attenuation writes, bass/treble center and extremes, I2C write-failure logging, and remove restoring the initialization sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda7432.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda9840.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tda9840.c

### Purpose
`tda9840.c` implements a V4L2 I2C subdevice driver for the SGS/Thomson TDA9840 stereo/dual-sound processor. It detects mono/stereo/bilingual audio status and selects the requested tuner audio mode.

### Important APIs, Types, And Functions
The file defines register addresses for switch, level adjust, stereo adjust, and test registers, plus encoded switch values for mute, mono, stereo, language 1, language 2, both channels, reversed both, and external input. `tda9840_write()` performs SMBus byte-data writes. `tda9840_status()` reads one status byte with `i2c_master_recv()` and extracts detection bits. `tda9840_s_tuner()` maps `v4l2_tuner.audmode` and detected status to a switch register value. `tda9840_g_tuner()` maps detection bits to `rxsubchans`. Probe verifies adapter functionality, initializes a V4L2 I2C subdev, and writes default level/stereo/switch settings.

### Control Flow
When setting tuner mode, the driver rejects nonzero tuner indexes, reads chip status, treats read failure as mono for selection, and chooses mono/stereo/lang1/lang2/both based on status and requested mode. When getting tuner state, it reads status and returns mono, bilingual, or stereo/mono subchannel flags. Probe sets initial adjustment registers to zero and switch mode to stereo.

### State, Persistence, And Dependencies
There is no private state beyond the `v4l2_subdev`; hardware register values hold the current mode. The driver depends on SMBus byte-data support, raw `i2c_master_recv()` for status, and V4L2 tuner subdev operations. It does not perform chip ID validation.

### Integration Points
The driver binds to `tda9840` I2C clients and provides `.s_tuner` and `.g_tuner` operations for parent analog TV/capture drivers that expose tuner audio mode controls.

### Risks
The adapter functionality check requires SMBus read/write byte-data even though status uses `i2c_master_recv()`, so adapter capability assumptions are conservative but not exact. `s_tuner()` masks status read errors by selecting mono, which may hide I2C failures. Invalid detect values fall back inconsistently: `g_tuner()` writes a tuner mode constant into `rxsubchans` for the default branch. There is no locking or chip detection.

### Test Signals
Tests should exercise probe capability rejection, initial register writes, status read failure paths, mono/stereo/bilingual status mapping, each supported `audmode`, invalid tuner index rejection, and I2C write-error debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tda9840.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6415c.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tea6415c.c

### Purpose
`tea6415c.c` implements a V4L2 I2C subdevice driver for the SGS/Thomson TEA6415C video matrix switch. It programs connections between one of eight physical input pins and one of six physical output pins.

### Important APIs, Types, And Functions
The driver has no private state beyond `struct v4l2_subdev`. `tea6415c_s_routing()` is the core operation: it validates input and output pin numbers, translates the selected output to upper control bits and input to lower control bits, and sends the resulting byte with `i2c_smbus_write_byte()`. Probe verifies SMBus write-byte support, allocates a subdev, and initializes `.video.s_routing`. Remove unregisters the subdev.

### Control Flow
Parent drivers call `.s_routing(i, o, config)` with physical or header-defined pin numbers. Invalid pins return `-EINVAL`. Valid pins are encoded according to the chip datasheet mapping, written as a single byte, and write failures return `-EIO`. Probe only registers the subdevice; it does not set a default route.

### State, Persistence, And Dependencies
There is no software routing cache. The selected switch paths live in the external chip until changed or reset. Dependencies include Linux I2C SMBus write-byte support, V4L2 subdev video operations, and the companion `tea6415c.h` pin macros for callers.

### Integration Points
The driver binds to `tea6415c` I2C clients. Larger analog video capture drivers use `s_routing` to connect board inputs to decoder or output paths. The `config` argument is unused.

### Risks
The validation expression is dense and easy to break when adding aliases. The driver does not verify chip identity and does not track routes for diagnostics. Pin names are physical package pin numbers, so callers should use the header macros to avoid swapped input/output confusion. No default routing means board drivers must explicitly configure startup paths.

### Test Signals
Useful tests include all valid input/output combinations, each invalid input and output returning `-EINVAL`, exact byte encodings for known routes from the datasheet, I2C write failure returning `-EIO`, and parent-driver route changes after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6415c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6415c.h -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/tea6415c.h

### Purpose
`tea6415c.h` provides symbolic pin definitions for the TEA6415C video matrix switch so board drivers can request routes without hard-coding package pin numbers.

### Important APIs, Types, And Functions
The header defines an include guard and twelve macros: `TEA6415C_OUTPUT1` through `TEA6415C_OUTPUT6` map to physical output pins 18, 14, 16, 17, 13, and 15, and `TEA6415C_INPUT1` through `TEA6415C_INPUT8` map to physical input pins 5, 8, 3, 20, 6, 10, 1, and 11. It contains no functions or types.

### Control Flow
There is no control flow. Callers pass these macro values to the `tea6415c.c` `.s_routing` operation, which validates the same physical pin numbers and encodes them into the chip control byte.

### State, Persistence, And Dependencies
The header has no state and no external dependencies. Its definitions must remain synchronized with the validation and encoding tables in `tea6415c.c`.

### Integration Points
Analog video board drivers include this header to express matrix routes using stable logical names. It is a small source-level ABI between board-specific routing code and the TEA6415C subdevice driver.

### Risks
The comment labels are potentially confusing because it says "input pins" before output macros and "output pins" before input macros. The logical numbering is arbitrary and not discoverable from hardware, so changing macro values would break board routing. There are no aliases for signal names or board connectors.

### Test Signals
Compile-time users should build without pin-number literals. Runtime route tests in `tea6415c.c` should verify every macro value is accepted and maps to the expected byte encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/tea6415c.h -->
