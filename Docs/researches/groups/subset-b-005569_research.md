# subset-b-005569 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.c

## Purpose
`hdmi4_core.c` is the OMAP4/TI81xx HDMI core programming library used by the fbdev OMAP DSS HDMI path. It owns the HDMI4 core register block below the wrapper: DDC/EDID reads, video core reset and mode setup, AVI/audio packet programming, audio clock regeneration, I2S/channel-status programming, and debug register dumps.

## Important APIs, types, and functions
External entry points are `hdmi4_read_edid`, `hdmi4_configure`, `hdmi4_core_dump`, `hdmi4_core_init`, `hdmi4_audio_config`, `hdmi4_audio_start`, and `hdmi4_audio_stop`. Internal helpers include `hdmi_core_ddc_init`, `hdmi_core_ddc_edid`, `hdmi_core_init`, reset/powerdown helpers, `hdmi_core_video_config`, `hdmi_core_write_avi_infoframe`, `hdmi_core_av_packet_config`, `hdmi_core_audio_config`, and `hdmi_core_audio_infoframe_cfg`. It uses `struct hdmi_core_data`, `struct hdmi_wp_data`, `struct hdmi_config`, `struct omap_dss_audio`, and HDMI4-specific register symbols from `hdmi4_core.h`.

## Control Flow
EDID reads initialize DDC clocks, abort any in-progress transaction, clear the FIFO, read the base block, validate its checksum, and optionally read one extension block. Video configuration initializes wrapper timing and format first, asserts HDMI core software reset, disables powerdown, programs input bus width/dither/packet mode/DVI-HDMI mode/TMDS clock, releases reset, then writes and repeats AVI/audio packets when HDMI mode is selected. Audio configuration validates IEC/CEA metadata, derives N/CTS with `hdmi_compute_acr`, selects software or hardware CTS mode by SoC feature, configures wrapper DMA/FIFO, programs ACR/I2S/channel status registers, writes the CEA audio infoframe, and start/stop toggles audio mode plus wrapper core request.

## State and Persistence
Software state is limited to `core->base` plus feature decisions from `dss_has_feature`; the larger state is register-resident in DDC, SYS, AV packet, ACR, I2S, and infoframe registers. Audio setup mutates `audio->cea->db1_ct_cc` and `db4_ca` for multi-channel layouts, so caller-owned configuration can be changed.

## Dependencies and Integration Points
The file depends on `hdmi4_core.h`, common HDMI wrapper helpers from `hdmi.h`/`hdmi_wp.c`, ALSA IEC958 and CEA audio structs, Linux HDMI infoframe packing, and DSS feature flags. It is called by the OMAP4 HDMI display driver and shares PLL/PHY/wrapper state with the rest of the HDMI stack.

## Risks
DDC polling and FIFO reads are timeout-driven and can fail on stuck sinks, bus-low, no-ack, or bad checksums. Only one EDID extension is read. Video programming assumes 24-bit RGB/YUV444-style packing and fixed core defaults. Audio behavior depends on SoC feature flags, fixed channel remapping, and in-place CEA infoframe edits.

## Test Signals
Useful signals include base and extension EDID reads, DDC bus-low/no-ack fault tests, HDMI and DVI video modes, AVI infoframe inspection, 2-channel and multi-channel LPCM playback, 16/24-bit IEC word-length cases, ACR N/CTS checks across 32-192 kHz sample rates, audio start/stop around display disable, and debugfs core register dumps while runtime PM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.h

## Purpose
`hdmi4_core.h` defines the OMAP4 HDMI core register map, field value enums, private video/audio configuration structs, and exported HDMI4 core function prototypes used by `hdmi4_core.c` and its display driver.

## Important APIs, types, and functions
The header declares SYS, DDC, and AV register offsets such as `HDMI_CORE_SYS_SYS_CTRL1`, `HDMI_CORE_DDC_STATUS`, `HDMI_CORE_AV_ACR_CTRL`, and infoframe byte macros. It defines enums for input bus width, dither/truncation, deep-color packet enable, packet modes, TMDS clock multiplier, packet enable/repeat flags, and I2S bit layout. Key structs are `struct hdmi_core_video_config` and `struct hdmi_core_packet_enable_repeat`. Public prototypes cover EDID, video configure, debug dump, core init, and audio config/start/stop.

## Control Flow
The header has no runtime flow, but it encodes the register contract used by OMAP4 HDMI operations. `hdmi4_configure` consumes the video config enums to program SYS and AV registers, while `hdmi4_audio_config` uses the I2S enum bits and AV audio offsets to program ACR and channel-status registers.

## State and Persistence
There is no software state in the header. Its constants describe hardware state that persists in the HDMI core until reset, power loss, or a later configuration call. The packet byte macros define register layout for repeated AVI, SPD, audio, MPEG, and generic packets.

## Dependencies and Integration Points
It includes `hdmi.h` for common OMAP HDMI data structures, common register access macros, and shared audio/video enums. It is tightly coupled to `hdmi4_core.c`; mismatches in bit values or offsets directly affect register programming.

## Risks
Risks are stale or incorrect register offsets, typo-prone enum values, and the legacy typo `HDMI_DEEPCOLORPACKECT...` being part of the local API. The header exposes only the supported subset of the core, so future deep-color or packet features would require carefully extending these constants.

## Test Signals
Build coverage of `hdmi4_core.c`, register dump comparisons against the TRM, EDID/DDC behavior, AVI/audio packet bytes on a sink or analyzer, and audio/video bring-up on OMAP4 variants are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5.c

## Purpose
`hdmi5.c` is the fbdev OMAP DSS platform/component driver for OMAP5/DRA7 HDMI. It binds wrapper, PLL, PHY, and HDMI5 core helpers into an `omap_dss_device` output, handles runtime PM and regulators, services link connect/disconnect IRQs, exposes EDID/timing/infoframe operations, and registers the `omap-hdmi-audio` child platform device.

## Important APIs, types, and functions
The file uses the global `static struct omap_hdmi hdmi`. Key functions are `hdmi_power_on_core`, `hdmi_power_on_full`, `hdmi_power_off_full`, timing operations, `read_edid`, display enable/disable, core enable/disable, connect/disconnect, HDMI ops, audio callbacks, `hdmi5_bind`, `hdmi5_unbind`, runtime PM callbacks, and platform driver init/uninit. It integrates `hdmi_wp_init`, `hdmi_pll_init`, `hdmi_phy_init`, `hdmi5_core_init`, `dss_pll_*`, and `dss_mgr_*`.

## Control Flow
Component bind initializes locks, parses DT lane mapping, maps wrapper/PLL/PHY/core resources, requests the IRQ, enables runtime PM, registers the output, registers HDMI audio, and creates debugfs. Display enable locks the HDMI singleton, powers the core and regulator, computes and enables the PLL, configures PHY and link power, calls `hdmi5_configure`, programs DISPC manager timings, starts wrapper video, enables the manager, and unmasks link IRQs. Disable reverses manager, video, PHY, PLL, runtime PM, and regulator state. EDID can temporarily core-enable the hardware. Audio startup/config/start/stop are allowed only in HDMI mode with display enabled.

## State and Persistence
Runtime state is in the global `hdmi`: current `hdmi_config`, output object, `core_enabled`, `display_enabled`, audio configuration/playback flags, saved wrapper idle mode, regulator pointer, component resources, and mapped register blocks. Hardware state persists in wrapper, PLL, PHY, core, and DISPC registers while powered.

## Dependencies and Integration Points
Dependencies include component framework, runtime PM, regulator and clock APIs, OF graph lane parsing, DSS manager/output APIs, DISPC runtime, debugfs, HDMI wrapper/PLL/PHY/core libraries, and the OMAP HDMI audio platform interface.

## Risks
The global singleton model assumes one HDMI5 instance. Error unwinding partly shares a generic `err` path and must keep PLL registration, output registration, runtime PM, and audio child lifetime consistent. The IRQ handler manipulates PHY power and pad force bits from interrupt context. Audio callbacks depend on spinlock/mutex ordering and display state.

## Test Signals
Test with OMAP5 and DRA7 DT compatibles, lane remapping, EDID reads before and after enable, HDMI/DVI mode toggles, hotplug connect/disconnect and simultaneous IRQ cases, display enable error injection at PLL/PHY/video/manager stages, suspend/resume, audio startup/config/play/stop across display off/on, and debugfs HDMI dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.c

## Purpose
`hdmi5_core.c` programs the OMAP5/DRA7 HDMI core IP beneath the wrapper. It implements DesignWare-style I2C-master EDID reads, frame composer timing, packetizer/sampler setup, CSC/range conversion, AVI infoframe fields, core interrupt masks, GPA audio setup, ACR N/CTS programming, audio infoframe registers, debug dumps, and core resource mapping.

## Important APIs, types, and functions
External functions are `hdmi5_read_edid`, `hdmi5_core_dump`, `hdmi5_configure`, `hdmi5_audio_config`, and `hdmi5_core_init`. Internal helpers include `hdmi_core_ddc_init`, `hdmi_core_ddc_uninit`, `hdmi_core_ddc_edid`, `hdmi_core_init`, `hdmi_core_video_config`, packetizer/CSC/sampler helpers, `hdmi_core_write_avi_infoframe`, `hdmi_core_csc_config`, interrupt mask/unmask helpers, `hdmi5_core_audio_config`, and `hdmi5_core_audio_infoframe_cfg`.

## Control Flow
EDID read initializes the I2C master timing counters, reads the base block one byte at a time, clamps extension count to the caller buffer, then reads extensions and masks I2C interrupts. Video configure masks core interrupts, derives wrapper and frame-composer timing from `struct hdmi_config`, writes wrapper timing/format/interface registers, programs limited-range CSC, sets the infoframe quantization range, configures frame composer, packetizer, CSC, sampler, optionally writes AVI infoframe, enables the video path, and unmutes core interrupts. Audio config validates pointers and 16-bit LPCM word length, maps IEC sample frequency, computes ACR, chooses 2/6/8-channel layout from CEA channel count, configures wrapper DMA/FIFO, then programs core audio and infoframe registers.

## State and Persistence
Software state is only `core->base`; all operational state is in core and wrapper registers. `hdmi5_configure` mutates `cfg->infoframe.quantization_range` to limited. Audio configuration is not cached here; `hdmi5.c` caches it for restore after display enable.

## Dependencies and Integration Points
The file depends on `hdmi5_core.h`, shared `hdmi.h` helpers/macros, `hdmi_wp.c`, Linux HDMI AVI packing, DRM EDID length constants, ALSA IEC958/CEA audio definitions, and shared `hdmi_compute_acr`.

## Risks
DDC polling can spend significant time per byte on bad sinks and has no interrupt-driven recovery. Only 16-bit LPCM samples are accepted. CSC/range handling is fixed to 24-bit limited-range behavior. Frame timing subtracts one from horizontal sync and has limited interlace handling, while `hdmi5.c` rejects interlace.

## Test Signals
Validate EDID base and multiple extension blocks, DDC timeout/error paths, frame composer values for representative CEA/VESA modes, HDMI versus DVI infoframe behavior, quantization range on sinks, audio configs for 2/6/8 channels at 32-192 kHz, rejection of unsupported word lengths, and debugfs register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.h

## Purpose
`hdmi5_core.h` is the HDMI5 core contract for OMAP5/DRA7. It enumerates the register map for identification, interrupt handling, video sampler, video packetizer, frame composer, audio, main controller, CSC, HDCP/CEC masks, and I2C-master DDC, plus the small structs and function prototypes used by `hdmi5_core.c`.

## Important APIs, types, and functions
Important definitions include `HDMI_CORE_IH_*`, `HDMI_CORE_TX_*`, `HDMI_CORE_VP_*`, `HDMI_CORE_FC_*`, `HDMI_CORE_AUD_*`, `HDMI_CORE_MC_*`, `HDMI_CORE_CSC_*`, and `HDMI_CORE_I2CM_*`. `enum hdmi_core_packet_mode` defines pixel packet modes. `struct hdmi_core_vid_config` carries derived frame-composer state, and `struct csc_table` carries twelve coefficients. Prototypes expose EDID, dump, video configure, init, and audio configure routines.

## Control Flow
The header has no executable flow. Its register and type definitions support the control flow in `hdmi5_core.c`: DDC uses the I2CM offsets, video setup uses FC/VP/TX/CSC/MC offsets, audio uses AUD and FC audio offsets, and interrupt masking uses IH and mask registers.

## State and Persistence
No state is stored in the header. It describes register-resident state retained by the HDMI core until reset or reprogramming. The macros for indexed payload/channel registers define how variable register arrays are addressed.

## Dependencies and Integration Points
It includes the shared `hdmi.h` API, making common wrapper structures available to HDMI5 core code. It is consumed by `hdmi5_core.c` and indirectly by `hdmi5.c` through the exported prototypes.

## Risks
Because this is a dense hardware register header, risks are incorrect offsets, bit-width assumptions, and mismatch with the HDMI IP revision. The `HDMI_CORE_I2CM_DATAI` define uses uppercase `0X`, which compiles but is visually inconsistent. Feature expansion for HDCP/CEC or deep color would need coordinated additions here and in the core implementation.

## Test Signals
Compile coverage, register dump sanity against TRM values, EDID/DDC operation, HDMI5 video bring-up, audio register programming, and analyzer-observed infoframe/audio packets are the practical validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_common.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_common.c

## Purpose
`hdmi_common.c` provides shared helpers used by OMAP4 and OMAP5 HDMI drivers: DT lane parsing and HDMI audio clock regeneration N/CTS calculation.

## Important APIs, types, and functions
The exported helpers are `hdmi_parse_lanes_of` and `hdmi_compute_acr`. `hdmi_parse_lanes_of` reads an endpoint `lanes` property of eight `u32` values or falls back to identity lane order, then delegates validation and mapping to `hdmi_phy_parse_lanes`. `hdmi_compute_acr` maps sample frequencies to HDMI N values and derives CTS from pixel clock, N, and deep-color percentage.

## Control Flow
Lane parsing checks property length, reads the array, and reports DT parse errors through the platform device. With no property, it uses lanes `{0..7}` and treats validation failure as unexpected. ACR computation validates output pointers, sets deep color to the currently hard-coded 100 percent path, chooses standard N values for 32, 44.1, 48, 88.2, 96, 176.4, and 192 kHz, and computes CTS with integer arithmetic.

## State and Persistence
No global state is held. Lane parsing writes into the caller-owned `struct hdmi_phy_data`. ACR values are returned through caller-provided `u32` pointers and later persisted in HDMI core registers by HDMI4/5 audio code.

## Dependencies and Integration Points
The file depends on OF property APIs, `hdmi.h`, `omapfb_dss.h`, and the HDMI PHY parser. `hdmi4_core.c` and `hdmi5_core.c` both use `hdmi_compute_acr`; `hdmi5.c` uses the lane parser during DT probe.

## Risks
The lane property must contain exactly eight cells. Deep-color handling is stubbed to 100 percent, so future 30/36-bit modes need this calculation revisited. CTS calculation uses integer division and assumes `pclk` in Hz and supported sample frequencies only.

## Test Signals
DT tests with missing, valid, and malformed lane arrays; PHY lane/polarity outcomes; ACR N/CTS comparisons against HDMI spec tables; invalid sample frequency handling; and audio playback at all supported rates are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_phy.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_phy.c

## Purpose
`hdmi_phy.c` initializes, maps, configures, and dumps the HDMI TX PHY for OMAP4/OMAP5/DRA7 fbdev DSS HDMI paths. It handles feature differences, lane remapping/polarity, frequency-output selection, line enable, and optional LDO/BIST controls.

## Important APIs, types, and functions
Key public functions are `hdmi_phy_parse_lanes`, `hdmi_phy_configure`, `hdmi_phy_dump`, and `hdmi_phy_init`. The private `struct hdmi_phy_features` records whether BIST control and LDO voltage fields exist plus the maximum PHY threshold. Internal helpers include `hdmi_phy_configure_lanes` and `hdmi_phy_get_features`.

## Control Flow
Init selects feature data from `omapdss_get_version` and maps the `"phy"` resource. Lane parsing consumes four differential pairs, verifies each pair is adjacent and ordered as normal or inverted polarity, and fills `phy->lane_function`/`lane_polarity`. Configure performs a dummy read after reset, enables HFBITCLK divide-by-two for PHYs with BIST control, selects `freqout` based on high/low bit clocks and feature limits, enables TXVALID/TMDSCLKEN, optionally sets max LDO voltage, and writes lane/polarity fields.

## State and Persistence
The file has one global `phy_feat` pointer shared by the driver instance. Per-device state lives in `struct hdmi_phy_data` lane arrays and `base`. Hardware state remains in PHY TX, digital, power, pad config, and optional BIST registers while powered.

## Dependencies and Integration Points
It depends on platform resource mapping, `omapdss_get_version`, HDMI register access macros, and `hdmi_common.c`/DT lane parsing. HDMI display drivers call it before raising wrapper PHY power to LDO/TX modes.

## Risks
The global `phy_feat` assumes a single active feature set. Lane validation rejects non-adjacent or duplicate-looking pair layouts but does not explicitly detect duplicate lanes beyond invalid final mapping. Frequency threshold selection is coarse and depends on correct PLL clock values.

## Test Signals
Test default and DT-remapped lanes, polarity inversion, unsupported SoC version handling, OMAP4 versus OMAP5/DRA7 feature behavior, PHY bring-up at low/high TMDS clocks, hotplug power transitions, and PHY debug dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_pll.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_pll.c

## Purpose
`hdmi_pll.c` implements HDMI-specific PLL setup on top of the generic DSS PLL helpers. It computes HDMI TMDS-derived PLL parameters, maps the PLLCTRL register block, registers the PLL with the DSS PLL registry, and controls HDMI wrapper PLL power.

## Important APIs, types, and functions
Public APIs are `hdmi_pll_dump`, `hdmi_pll_compute`, `hdmi_pll_init`, and `hdmi_pll_uninit`. The PLL ops are `hdmi_pll_enable`, `hdmi_pll_disable`, and `dss_pll_write_config_type_b` through `dsi_pll_ops`. Hardware descriptions are `dss_omap4_hdmi_pll_hw` and `dss_omap5_hdmi_pll_hw`.

## Control Flow
`hdmi_pll_compute` reads `sys_clk`, computes target bit clock as TMDS times ten, selects `n` to keep Fint below hardware max, chooses `m2` to keep DCO above the minimum, computes integer and fractional M, derives `clkout`, and stores sigma-delta and clock info. Init maps `"pll"`, gets `"sys_clk"`, chooses OMAP4 or OMAP5/DRA7 hardware limits, and registers the PLL. Enable turns on DSS HDMI PLL control and wrapper PLL power; disable powers it off and clears DSS control.

## State and Persistence
Per-instance state is `struct hdmi_pll_data`, containing mapped base, wrapper pointer, and embedded `struct dss_pll`. Generic PLL state caches the last `dss_pll_clock_info`. Hardware state persists in PLLCTRL registers and wrapper power control while enabled.

## Dependencies and Integration Points
The file depends on clock APIs, DSS feature/version detection, wrapper power helpers from `hdmi_wp.c`, generic PLL code in `pll.c`, and HDMI display power-on flows in `hdmi5.c` or the OMAP4 counterpart.

## Risks
Clock math assumes the requested TMDS target is reachable and does not search alternatives; bad parent clock rates or extreme pixel clocks can produce out-of-range PLL parameters. Enable/disable errors from wrapper power transitions are timeout-based. The ops variable name `dsi_pll_ops` is misleading but functional.

## Test Signals
Validate computed N/M/MF/M2/SD for common HDMI pixel clocks, PLL lock across OMAP4 and OMAP5/DRA7, failure paths for missing resources/clocks, power on/off sequencing, register dumps, and video output stability across mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_wp.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_wp.c

## Purpose
`hdmi_wp.c` is the common HDMI wrapper programming layer. It maps wrapper registers, manages IRQ status/enables, controls PHY/PLL power commands, starts/stops wrapper video, writes wrapper timing/format/interface fields, configures audio DMA/FIFO format, exposes the audio DMA address, and dumps wrapper registers.

## Important APIs, types, and functions
Key functions are `hdmi_wp_init`, `hdmi_wp_dump`, IRQ helpers, `hdmi_wp_set_phy_pwr`, `hdmi_wp_set_pll_pwr`, `hdmi_wp_video_start`, `hdmi_wp_video_stop`, `hdmi_wp_init_vid_fmt_timings`, `hdmi_wp_video_config_*`, `hdmi_wp_audio_config_format`, `hdmi_wp_audio_config_dma`, `hdmi_wp_audio_enable`, `hdmi_wp_audio_core_req_enable`, and `hdmi_wp_get_audio_dma_addr`.

## Control Flow
Init obtains the named `"wp"` memory resource, saves its physical base, and maps it. Power helpers write command fields and poll status fields using `hdmi_wait_for_bit_change`. Video setup initializes wrapper-local timing from `struct hdmi_config`, writes size and sync porch registers, writes packing/polarity/master mode, and start sets the enable bit. Stop clears the enable bit and waits up to roughly one second for frame-done. Audio config writes format fields, SoC-specific channel fields, DMA block/transfer sizes, DMA mode, and FIFO threshold; audio enable toggles wrapper control bits.

## State and Persistence
Software state is `wp->base` and `wp->phys_base`. Register state persists in wrapper video, timing, power, IRQ, audio, and sysconfig registers until reset or reconfiguration. Callers cache idle mode separately before audio streaming changes it.

## Dependencies and Integration Points
The wrapper layer is used by HDMI4/5 core, PLL, display, and audio code. It depends on platform resources, `hdmi.h` register definitions/macros, DSS version detection, and seq_file debug output.

## Risks
PHY/PLL status polling can timeout if hardware is wedged. `hdmi_wp_video_stop` logs but does not return failure when frame-done is missing. Audio channel format fields are conditional on older OMAP4 versions, so SoC detection must be correct. Register writes assume runtime PM has already made the wrapper accessible.

## Test Signals
Test wrapper mapping, PHY/PLL power transitions, video start/stop with frame-done, timing register values for progressive/interlaced modes, audio DMA address correctness, audio FIFO threshold programming, and IRQ status clear/enable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_wp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager-sysfs.c

## Purpose
`manager-sysfs.c` exposes OMAP DSS overlay manager attributes under sysfs. It lets users inspect manager names and attached displays and mutate manager-level display attachment, default color, transparency keying, alpha blending, and color phase rotation coefficients.

## Important APIs, types, and functions
The public lifecycle functions are `dss_manager_kobj_init` and `dss_manager_kobj_uninit`. Attribute handlers include `manager_display_store`, default color, transparency type/value/enabled, alpha blending, CPR enable, and CPR coefficient show/store functions. `struct manager_attribute`, `MANAGER_ATTR`, `manager_sysfs_ops`, and `manager_ktype` implement the kobject dispatch.

## Control Flow
Kobject init creates `manager%d` under the DSS platform device. Show/store dispatch converts from kobject to `struct omap_overlay_manager`. Most stores fetch current manager info, parse sysfs input with `kstrto*`, `sysfs_match_string`, or `sscanf`, update one field, call `mgr->set_manager_info`, then `mgr->apply`. Display store finds the named display, verifies new and old displays are disabled, disconnects the old display, connects the new one, verifies it landed on this manager, and applies the config.

## State and Persistence
State is stored in manager objects and lower DISPC shadow/hardware state through `set_manager_info` and `apply`. Sysfs kobject lifetime is tied to overlay manager lifetime. No settings persist across driver unload or reboot except through whatever userspace reapplies.

## Dependencies and Integration Points
The file depends on `omapfb_dss.h` manager/display APIs, DSS feature flags for alpha/CPR support, sysfs/kobject APIs, and display driver connect/disconnect callbacks.

## Risks
Most stores are not protected by a file-local lock, relying on lower layers. `manager_display_store` may leave the old display disconnected if new connect or apply fails. CPR parsing uses `sscanf` and enforces coefficient range after parsing. Feature-gated attributes still exist but return `-ENODEV` on unsupported hardware.

## Test Signals
Exercise all sysfs attributes, invalid strings/ranges, unsupported feature returns, display reassignment while enabled versus disabled, failure injection around connect/apply, CPR coefficient boundary values, and concurrent sysfs/ioctl display configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager.c

## Purpose
`manager.c` allocates and exposes OMAP DSS overlay manager objects and provides validation helpers for manager and overlay configurations before applying them to DISPC.

## Important APIs, types, and functions
Public functions include `dss_init_overlay_managers`, `dss_init_overlay_managers_sysfs`, uninit counterparts, `omap_dss_get_num_overlay_managers`, `omap_dss_get_overlay_manager`, `dss_mgr_simple_check`, `dss_mgr_check_timings`, and `dss_mgr_check`. Internal helpers include `dss_mgr_check_zorder` and `dss_mgr_check_lcd_config`.

## Control Flow
Initialization queries DSS feature data for manager count, allocates the manager array, assigns stable names/ids (`lcd`, `tv`, `lcd2`, `lcd3`), fills supported display/output masks, and initializes overlay lists. Sysfs init creates a kobject for each manager. Validation checks feature-specific alpha/keying constraints, unique zorder when free zorder is supported, manager timing validity via DISPC, LCD clock divisor and data-line constraints, and then calls `dss_ovl_check` for each active overlay on the manager.

## State and Persistence
Global runtime state is `num_managers` and the allocated `managers` array. Each manager stores name, id, capability masks, overlay list, kobject, and function pointers filled by other DSS code. No state persists across driver teardown.

## Dependencies and Integration Points
It depends on DSS feature tables, DISPC timing validation, overlay validation from `overlay.c`, manager sysfs from `manager-sysfs.c`, and exported fbdev/DSS APIs used by output drivers and omapfb.

## Risks
Allocation failure uses `BUG_ON`, which is harsh for memory pressure. `omap_dss_get_overlay_manager` checks only upper bound and not negative indices. Validation depends on callers passing complete `overlay_infos` arrays. LCD config checks are generic and defer some interface-specific validation.

## Test Signals
Test manager count/name/id per SoC, sysfs kobject creation/removal, invalid duplicate zorders, alpha/keying constraints on OMAP3, invalid timing and LCD divisors, unsupported video port widths, overlay bounds failures, and manager lookup edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/omapdss-boot-init.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/omapdss-boot-init.c

## Purpose
`omapdss-boot-init.c` is an early boot compatibility shim for legacy OMAP DSS panel/encoder drivers. It walks the display graph and rewrites non-root connected display node `compatible` strings by prepending `omapdss,`, allowing generic-looking DT data to bind to OMAPDSS-specific drivers.

## Important APIs, types, and functions
The file is driven by `subsys_initcall(omapdss_boot_init)`. Important helpers are `omapdss_count_strings`, `omapdss_update_prop`, `omapdss_prefix_strcpy`, `omapdss_omapify_node`, `omapdss_add_to_list`, `omapdss_list_contains`, and `omapdss_walk_device`. `struct dss_conv_node` tracks walked device nodes and whether they are graph roots.

## Control Flow
Boot init finds an available DSS root compatible with OMAP2/3/4/5 or DRA7. It walks the DSS node and available DSS children through OF graph endpoints, collecting each reachable node once. During cleanup of the list, it skips root nodes and rewrites non-root nodes with valid, unprefixed `compatible` properties. The rewrite allocates a new property and calls `of_update_property`.

## State and Persistence
State is early-init-only: `dss_conv_list` and allocated `dss_conv_node` entries are freed before returning. Rewritten OF properties persist in the live device tree for the rest of the boot, but not across reboot.

## Dependencies and Integration Points
It depends on OF graph APIs, device tree node availability, and OMAP DSS compatible strings. Its output affects later platform driver matching for panels and encoders.

## Risks
The code intentionally mutates the live device tree, which can surprise generic panel drivers. Allocation failures silently skip property/list updates. The walker relies on graph topology and may miss devices not reachable through endpoints. `omapdss_count_strings` assumes a valid string-list property after a first string-length check.

## Test Signals
Boot DTs with legacy and already-prefixed compatible strings, disconnected or unavailable graph nodes, multiple compatible strings, missing `port`/`ports`, graph cycles, allocation failure simulation, and driver binding order before panel probes are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/omapdss-boot-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/output.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/output.c

## Purpose
`output.c` manages registered OMAP DSS output devices and provides the indirection layer from output drivers to installed manager operations. It connects outputs to display devices, finds outputs by id/name/OF port/display chain, and exports manager operation wrappers.

## Important APIs, types, and functions
Output APIs include `omapdss_output_set_device`, `omapdss_output_unset_device`, `omapdss_register_output`, `omapdss_unregister_output`, `omap_dss_get_output`, `omap_dss_find_output`, `omap_dss_find_output_by_port_node`, `omapdss_find_output_from_display`, and `omapdss_find_mgr_from_display`. Manager ops APIs include `dss_install_mgr_ops`, `dss_uninstall_mgr_ops`, `dss_mgr_connect`, `dss_mgr_disconnect`, timing/config setters, enable/disable/update, and framedone handler registration wrappers.

## Control Flow
Outputs register onto `output_list`. Set/unset device runs under `output_lock`, verifies single attachment, matching output/display type, and disabled state on unset, then links or clears `out->dst` and `dssdev->src`. Find helpers walk the list or climb `src` pointers. Manager wrappers dispatch through the globally installed `dss_mgr_ops`.

## State and Persistence
Runtime state is the global output list, `output_lock`, and global `dss_mgr_ops` pointer. Link state is stored in `struct omap_dss_device` `src`/`dst` fields. No state persists across driver lifetime.

## Dependencies and Integration Points
The file depends on OMAP DSS device structs, OF graph helper `dss_of_port_get_parent_device`, module exports, and a manager backend that installs `struct dss_mgr_ops`. HDMI, SDI, and VENC output drivers register outputs here.

## Risks
Register/unregister and lookup list walks are mostly unlocked except set/unset, so concurrent registration/removal would be unsafe if it happened after init. Manager wrappers assume `dss_mgr_ops` is installed and valid. `omapdss_find_output_from_display` relies on `id != 0` as an output test.

## Test Signals
Test output registration/removal, type mismatch rejection, duplicate connection rejection, unset while enabled, OF port lookup, display-chain manager lookup, manager ops install `-EBUSY`, and calls before/after manager ops installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay-sysfs.c

## Purpose
`overlay-sysfs.c` exposes OMAP DSS overlay controls in sysfs. It allows users to inspect and mutate overlay manager assignment, position, output size, enable state, global alpha, pre-multiplied alpha, and z-order.

## Important APIs, types, and functions
The public lifecycle APIs are `dss_overlay_kobj_init` and `dss_overlay_kobj_uninit`. Attribute handlers cover `name`, `manager`, `input_size`, `screen_width`, `position`, `output_size`, `enabled`, `global_alpha`, `pre_mult_alpha`, and `zorder`. `struct overlay_attribute`, `OVERLAY_ATTR`, `overlay_sysfs_ops`, and `overlay_ktype` provide sysfs dispatch.

## Control Flow
Kobject init creates `overlay%d`. Show/store dispatch maps the kobject back to `struct omap_overlay`. Manager store resolves a manager name, gets DISPC runtime PM, unsets the old manager and applies it, sets the new manager and applies it, then releases runtime PM. Geometry/alpha/zorder stores parse input, update the overlay info through `ovl->set_overlay_info`, and apply the attached manager if present. Enable store calls `ovl->enable` or `ovl->disable`.

## State and Persistence
State changes live in overlay info, manager attachment, hardware shadow registers, and DISPC state through `apply`. The sysfs object lifetime follows the overlay object. There is no persistence beyond runtime.

## Dependencies and Integration Points
It depends on OMAP overlay callbacks, manager apply paths, DISPC runtime PM, DSS feature/capability flags, kobject/sysfs APIs, and `dss_features.h`.

## Risks
Position and output-size parsing uses `simple_strtoul` and minimal separator validation. Manager reassignment error handling can leave an overlay detached or partially applied after old manager removal. Stores are mostly not serialized by a local lock. Unsupported capability attributes remain visible but return `-ENODEV`.

## Test Signals
Exercise all attributes, invalid geometry strings, capability-gated alpha/zorder on different overlays, manager attach/detach success and failure, enabled toggles, runtime PM failure paths, concurrent sysfs changes, and apply failures after geometry mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay.c

## Purpose
`overlay.c` allocates OMAP DSS overlay objects, initializes overlay sysfs nodes, exposes overlay lookup APIs, and provides common validation helpers for overlay capabilities, color modes, scaling, z-order, rotation type, display bounds, and replication needs.

## Important APIs, types, and functions
Public APIs include `omap_dss_get_num_overlays`, `omap_dss_get_overlay`, `dss_init_overlays`, `dss_uninit_overlays`, `dss_ovl_simple_check`, `dss_ovl_check`, and `dss_ovl_use_replication`. It initializes overlays named `gfx`, `vid1`, `vid2`, and `vid3` based on feature-reported overlay count.

## Control Flow
Initialization allocates the overlay array, assigns names/ids, fills capabilities and supported color modes from DSS feature tables, and creates a sysfs kobject per overlay. Uninit removes kobjects and frees the array. Simple checks reject scaling on non-scaling overlays, unsupported color modes, too-high zorder, and unsupported rotation type. Full checks compute effective output size and ensure the overlay rectangle is inside manager timings. Replication is selected only for RGB12U/RGB16 over wider LCD ports.

## State and Persistence
Global runtime state is `num_overlays` and the allocated `overlays` array. Each overlay stores callback pointers and runtime info managed by other DSS code. No state persists after driver uninit.

## Dependencies and Integration Points
The file depends on DSS feature tables, manager timings, overlay sysfs, exported OMAP DSS APIs, and caller-supplied overlay callback implementations.

## Risks
Allocation failure uses `BUG_ON`. `omap_dss_get_overlay` checks upper bound but not negative input. Bounds checks use `pos + size` and should be watched for integer wrap if inputs are not sanitized elsewhere. Validation only covers common constraints; DISPC-specific limits are in lower layers.

## Test Signals
Test overlay count/name/capability per SoC, sysfs lifecycle, unsupported color/scaling/rotation, zorder bounds, placement outside display, zero output-size fallback, replication decisions, and lookup edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/pll.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/pll.c

## Purpose
`pll.c` is the generic DSS PLL framework for fbdev OMAP DSS. It registers PLL objects, controls enable/disable and cached configuration, searches clock/divider combinations, waits for hardware state changes, and writes two supported PLL register programming formats.

## Important APIs, types, and functions
Public APIs are `dss_pll_register`, `dss_pll_unregister`, `dss_pll_find`, `dss_pll_enable`, `dss_pll_disable`, `dss_pll_set_config`, `dss_pll_hsdiv_calc`, `dss_pll_calc`, `dss_pll_wait_reset_done`, `dss_pll_write_config_type_a`, and `dss_pll_write_config_type_b`. State is held in `static struct dss_pll *dss_plls[4]`.

## Control Flow
Registration stores PLLs in the first free slot. Enable prepares the input clock, enables an optional regulator, then calls the PLL-specific enable op; errors unwind regulator and clock. Disable calls the PLL-specific disable op, disables regulator and clock, and clears cached clock info. Calculation helpers iterate legal `n`, `m`, and HSDIV ranges and stop when a callback accepts a candidate. Type A/B writers program PLL configuration registers, trigger GO, wait for GO clear and lock, and for type A enable HSDIV outputs and wait for acknowledgements.

## State and Persistence
Runtime state is the PLL registry and each PLL's cached `cinfo`. Hardware state persists in PLL control/configuration/status registers while powered. No persistent storage exists.

## Dependencies and Integration Points
It depends on common DSS structs in `dss.h`, clocks, optional regulators, jiffies/hrtimeout polling, and low-level MMIO. HDMI and DRA7 video PLL drivers build `struct dss_pll` instances and use these helpers.

## Risks
The registry has no locking and fixed capacity. Waits are polling/time-based. Type-specific register writers rely on correct `dss_pll_hw` bit metadata. Search helpers can be expensive across ranges but stop early by callback. Error returns differ (`-EIO` versus `-ETIMEDOUT`) across lock failures.

## Test Signals
Test registration capacity and unregister, enable failure unwinding, regulator/clock behavior, PLL search callbacks for edge frequencies, type A and B register programming against known configurations, timeout paths for GO/LOCK/HSDIV ack, and cached `cinfo` clearing on disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/sdi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/sdi.c

## Purpose
`sdi.c` implements the OMAP DSS Serial Display Interface output driver. It registers an SDI output, calculates clocks, configures the LCD manager for SDI, controls the SDI regulator and DISPC runtime state, handles DT datapair parsing, and exposes SDI ops to display devices.

## Important APIs, types, and functions
The file centers on the global `sdi` state. Important functions are `sdi_calc_clock_div`, `sdi_config_lcd_manager`, `sdi_display_enable`, `sdi_display_disable`, timing get/set/check, `sdi_set_datapairs`, `sdi_connect`, `sdi_disconnect`, output init/uninit, component bind/unbind, platform driver init/uninit, `sdi_init_port`, and `sdi_uninit_port`.

## Control Flow
Enable validates a connected manager, enables the SDI regulator and DISPC runtime, forces SDI signal edges, searches DSS/DISPC divisors with gradually widened pixel-clock tolerance, updates the requested pixel clock if only an approximate value is found, sets manager timings and DSS fclk, writes LCD manager config and divisors early for pck-free, initializes/enables the SDI block, delays 2 ms, then enables the manager. Disable reverses manager, SDI block, DISPC runtime, and regulator. Connect obtains regulator and binds manager/output to the destination display.

## State and Persistence
Runtime state includes platform device, regulator pointer, LCD manager config, timings, datapairs, output object, and `port_initialized`. Hardware state is in DSS SDI, DISPC manager, clock, and regulator state. Nothing persists across driver unload.

## Dependencies and Integration Points
It depends on component framework, OF graph endpoints, regulator APIs, DSS clock/divider helpers, DISPC runtime and manager APIs, and output registration.

## Risks
Global singleton state assumes one SDI output. Clock calculation may alter `timings->pixelclock`, which callers must tolerate. Error paths must balance regulator and DISPC runtime. `sdi_uninit_port` does not clear `port_initialized`. DT endpoint parsing requires `datapairs`.

## Test Signals
Test OMAP3 SDI output registration, DT datapairs parsing, exact and approximate pixel clocks, regulator/runtime failure unwinds, pck-free divider programming, enable/disable cycles, invalid timings, connect/disconnect while display enabled, and datapair changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/sdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/venc.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/venc.c

## Purpose
`venc.c` implements the OMAP analog TV encoder output driver for PAL/NTSC composite and S-Video. It provides VENC register tables, exported PAL/NTSC timings, output registration, power/runtime/regulator handling, WSS support, DT channel parsing, debug dumps, and platform/component driver integration.

## Important APIs, types, and functions
Important data includes `struct venc_config`, `venc_config_pal_trm`, `venc_config_ntsc_trm`, exported `omap_dss_pal_timings`, `omap_dss_ntsc_timings`, and global `venc` state. Key functions are `venc_write_config`, `venc_reset`, runtime get/put, `venc_timings_to_config`, `venc_power_on/off`, display enable/disable, timing check/set/get, WSS get/set, type/polarity setters, `venc_connect`, `venc_disconnect`, `venc_probe_of`, `venc_bind/unbind`, runtime PM callbacks, and platform driver init/uninit.

## Control Flow
Bind maps VENC memory, gets optional TV DAC clock, enables runtime PM, reads revision, parses DT channel/polarity, creates debugfs, and registers output. Display enable locks `venc_lock`, runtime-resumes hardware, resets VENC, writes PAL/NTSC table plus WSS data, selects output type, enables DAC bias, writes output control, sets manager timings, enables regulator, and enables the manager. Disable clears output control and DAC bias, disables manager, regulator, and runtime PM. WSS writes update cached data and the BSTAMP/WSS register under runtime PM.

## State and Persistence
Global runtime state includes mapped base, mutex, WSS data, regulator, optional TV DAC clock, timings, output type, polarity, platform device, and output object. Hardware state lives in VENC registers, DAC control, manager timings, and regulator/clock state.

## Dependencies and Integration Points
The file depends on DSS feature flags, DISPC runtime through VENC runtime PM, regulator and clock APIs, OF graph parsing, component framework, output/manager APIs, and debugfs.

## Risks
`venc_timings_to_config` calls `BUG()` for unsupported timings, so callers must use `venc_check_timings`. `venc_probe_of` returns 0 even on invalid DT parse in its error path, potentially masking bad channel data. Runtime suspend disables `tv_dac_clk` even if NULL, relying on clock helpers. PAL/NTSC comparisons require exact struct matches.

## Test Signals
Test PAL and NTSC enable, rejection of non-TV timings, composite versus S-Video DT channels, polarity inversion, WSS set/get across standard changes, runtime PM suspend/resume, missing regulator/clock resources, reset timeout behavior, debugfs dumps, and manager/regulator failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/video-pll.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/video-pll.c

## Purpose
`video-pll.c` implements DRA7 video PLL instances on top of the generic DSS PLL framework. It maps PLL and clock-control resources, obtains input clocks, controls SCP and PLL power bits, registers PLLs named `video0`/`video1`, and unregisters them.

## Important APIs, types, and functions
The public APIs are `dss_video_pll_init` and `dss_video_pll_uninit`. The private `struct dss_video_pll` wraps `struct dss_pll`, device pointer, and `clkctrl_base`. Important helpers are `dss_dpll_enable_scp_clk`, `dss_dpll_disable_scp_clk`, `dss_dpll_power_enable`, `dss_dpll_power_disable`, `dss_video_pll_enable`, and `dss_video_pll_disable`. Hardware limits live in `dss_dra7_video_pll_hw`.

## Control Flow
Init maps `"pll1"`/`"pll2"` and matching clock-control resources, gets `"video1_clk"`/`"video2_clk"`, allocates state, fills `struct dss_pll` fields, and registers it. Enable runtime-resumes DSS, enables DSS PLL routing, enables SCP clock, waits for reset done, powers the PLL on with a fixed delay, and returns. Disable powers off, disables SCP clock, clears DSS routing, and runtime-suspends DSS.

## State and Persistence
Runtime state is devm-managed `struct dss_video_pll` plus the generic PLL registry entry. Hardware state persists in PLL control and clock-control registers while active. Cached clock configuration is managed by `pll.c`.

## Dependencies and Integration Points
It depends on DRA7 DSS resources, clocks, optional regulator passed by caller, generic PLL type-A programming, DSS runtime PM, and DSS PLL control routing.

## Risks
Only two IDs are supported by fixed arrays and no explicit bounds check protects bad `id`. DRA7 PLL power status is not trusted, so enable uses a fixed sleep. Error after SCP enable must unwind runtime and DSS control correctly. Resource names must match DT/platform data exactly.

## Test Signals
Test both video PLL IDs, missing resource/clock paths, invalid id handling, reset timeout, enable/disable balance, type-A config programming through `dss_pll_set_config`, regulator involvement, and DSS runtime PM reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/video-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-ioctl.c

## Purpose
`omapfb-ioctl.c` implements legacy OMAP framebuffer ioctls for plane setup/query, framebuffer memory resizing/query, manual update windows, update mode control, color keying, vsync/go waits, panel tests, memory readback, VRAM compatibility reporting, tear-sync toggling, and display information queries.

## Important APIs, types, and functions
The main dispatcher is `omapfb_ioctl`. Supporting functions include `get_mem_idx`, `get_mem_region`, `omapfb_setup_plane`, `omapfb_query_plane`, `omapfb_setup_mem`, `omapfb_query_mem`, `omapfb_update_window`, exported `omapfb_set_update_mode`/`omapfb_get_update_mode`, color-key helpers, `omapfb_memory_read`, `omapfb_get_ovl_colormode`, and `omapfb_wait_for_go`.

## Control Flow
The dispatcher copies user data into a union, routes by ioctl command, calls display/overlay/memory helpers, and copies results back. Plane setup locks old/new memory regions in id order, optionally switches framebuffer memory region, disables or configures the first overlay, applies the manager, enables the overlay, and rolls back on failure. Memory setup syncs the display, locks the current region, rejects mapped or enabled users, and reallocates framebuffer memory. Update mode toggles auto-update for manual-update displays under the fbdev lock. Color keying finds the first overlay with a manager and updates manager transparency state.

## State and Persistence
State changes affect `struct omapfb_info` region pointers, framebuffer fixed info, memory region size/type, display update mode, overlay info/enabled state, manager color-key state, and static `omapfb_color_keys[2]`. These are runtime-only and tied to fbdev/DSS lifetimes.

## Dependencies and Integration Points
The file depends on fbdev core structs, user-copy helpers, OMAPFB UAPI structs, omapfb internal memory/overlay helpers, VRFB headers, OMAP DSS display/overlay/manager callbacks, vmalloc, and update worker helpers in `omapfb-main.c`.

## Risks
This is a broad user-facing ioctl surface. Plane setup only uses the first overlay and rollback may not undo every hardware side effect after manager apply or enable failure. `omapfb_memory_read` validates width/height and buffer size but `w * h * 3` can overflow before comparison. Static color-key cache is sized for two managers, while newer SoCs can have more. Some compatibility responses such as VRAM info are fabricated.

## Test Signals
Exercise every ioctl with valid and invalid user pointers, plane enable/disable and memory-region switching, memory resize while mapped/enabled, update windows at boundaries, manual/auto update transitions, color key set/get on each manager, wait-for-vsync/go, memory readback size and overflow cases, overlay color mode enumeration, tear-sync support checks, and concurrent ioctl/sysfs reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-ioctl.c -->
