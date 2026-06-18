# subset-b-003694 Research

Grouped research for OMAP DRM HDMI/DSS output, PLL, CRTC, DMM/TILER, framebuffer, fbdev, encoder, and driver files. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.h

Purpose: Declares the OMAP4 HDMI core register map, audio/video packet constants, core video configuration types, and public HDMI4 core entry points used by the OMAP HDMI4 implementation.

Important APIs/types: The file defines system, DDC, audio-video, packet, and infoframe register offsets such as `HDMI_CORE_SYS_*`, `HDMI_CORE_DDC_*`, and `HDMI_CORE_AV_*`. It declares enums for input bus width, output truncation/dither, deep-color packet enable, packet mode, clock multiplier, packet enable/repeat, and I2S audio setup. `struct hdmi_core_video_config` captures bus width, dither/truncation, deep color, packet mode, DVI/HDMI selection, and clock multiplier. `struct hdmi_core_packet_enable_repeat` controls audio, AVI, generic, and control packet repetition. Public functions cover DDC init/read, core configure/dump/init, core enable/disable/powerdown, and HDMI4 audio start/stop/config.

Control flow: This header is consumed by HDMI4 core and top-level HDMI4 code. Runtime flow is implemented elsewhere: probe maps the core, enable powers it, configure programs video, DDC read fetches EDID, and audio_config/start/stop program and gate audio packets.

State and persistence: No storage is allocated here. The declared APIs operate on `struct hdmi_core_data`, `struct hdmi_wp_data`, `struct hdmi_config`, and `struct omap_dss_audio`, which are volatile driver state.

Dependencies/integration: Includes `hdmi.h` for common HDMI structs, register helpers, and shared enums. Integrates with HDMI wrapper programming, DRM EDID callbacks, DSS output bridge enable paths, and OMAP HDMI audio.

Risks and test signals: Header-level risk is register offset or bitfield mismatch with OMAP4 TRM. Audio and DDC APIs depend on callers keeping runtime PM and regulators active. Validate with OMAP4 HDMI probe, EDID read, DVI/HDMI mode programming, infoframe emission, audio startup, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5.c

Purpose: Implements the OMAP5/DRA7 HDMI platform driver, DRM bridge, component binding, power sequencing, hotplug IRQ handling, EDID access, and HDMI audio platform integration.

Important APIs/functions: `hdmi5_probe()` allocates `struct omap_hdmi`, parses lane DT data, initializes wrapper/PHY/core blocks, requests the IRQ, gets the `vdda` regulator, enables runtime PM, registers an OMAP DSS output, and adds a component. `hdmi5_bind()` attaches the DSS master, initializes the HDMI PLL, registers `omap-hdmi-audio`, and creates debugfs. Bridge callbacks attach to the next bridge, set mode timings, enable/disable the full HDMI pipeline, and read EDID through `drm_edid_read_custom()`. Audio callbacks track startup/shutdown/config/start/stop and restore audio when display output is enabled.

Control flow: Probe initializes hardware sub-block handles but does not fully power video. Bridge `mode_set` stores the adjusted videomode and programs TV pixel clock. Bridge `atomic_enable` derives HDMI/DVI mode and AVI infoframe from connector state, powers core/regulator/runtime PM, computes and configures the PLL, configures PHY, sets PHY LDOON, configures HDMI5 core and wrapper, enables the DISPC manager, starts wrapper video, enables connect/disconnect IRQs, and optionally restores audio. Disable reverses IRQ, video, manager, PHY, PLL, and core power. EDID reads temporarily power the core if needed and force wrapper no-idle around DDC.

State and persistence: Driver state lives in `struct omap_hdmi`: locks, DSS pointer, output/bridge, wrapper, PHY, core, PLL, runtime/core/display flags, cached HDMI config, audio config, audio platform device, and audio playing/configured flags protected by mutex plus `audio_playing_lock`. No disk persistence exists.

Dependencies/integration: Depends on DRM bridge/atomic/EDID helpers, OMAP DSS manager callbacks, DISPC clock programming, HDMI common wrapper/PHY/PLL/core helpers, runtime PM, regulators, OF graph lane parsing, Linux component framework, and `omap-hdmi-audio`.

Risks and test signals: Failure unwinding in full power-on must leave regulators/runtime PM/PLL/PHY balanced. The IRQ handler handles simultaneous connect/disconnect by forcing RXDET low around PHY LDOON, which needs hardware regression coverage. Audio start can occur before video and is replayed later. Test OMAP5/DRA7 HDMI hotplug, EDID reads when disabled, HDMI versus DVI sinks, interlaced/double-clock modes, audio reconfiguration across modesets, runtime suspend, and error paths for PLL/PHY timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.c

Purpose: Provides the OMAP5 HDMI core programming library for DDC, video frame composer, packetizer/sampler, CSC range conversion, AVI infoframe emission, interrupt masking, and audio core/audio infoframe configuration.

Important APIs/functions: `hdmi5_core_ddc_init()`, `hdmi5_core_ddc_read()`, and `hdmi5_core_ddc_uninit()` configure the DesignWare HDMI I2C master and poll EDID bytes. `hdmi5_configure()` is the main video setup entry: masks interrupts, chooses quantization range, initializes core timing state, configures wrapper timing/format/interface, programs CSC, frame composer, packetizer, sampler, optional AVI infoframe, and unmasks interrupts. `hdmi5_audio_config()` validates IEC/CEA audio metadata, computes ACR N/CTS via `hdmi_compute_acr()`, configures wrapper DMA/FIFO format, core audio registers, and CEA audio infoframe. `hdmi5_core_init()` maps the `core` resource.

Control flow: Video configuration starts from `struct hdmi_config`, adjusts timing for interlace and double-clock, programs wrapper-facing timing first, then programs core frame composer registers and CSC. HDMI mode emits AVI infoframes; DVI mode leaves infoframes disabled. DDC read clears DONE/ERROR bits, issues a segment-aware read operation per byte, polls status with retries, and returns `-EIO` on error/timeout.

State and persistence: The code stores no persistent data beyond register state and the mapped `core->base`. Temporary config structs are stack-local. Audio configuration copies no state; callers cache audio settings in `hdmi5.c`.

Dependencies/integration: Uses `hdmi5_core.h` register definitions, `hdmi.h` common structures, HDMI wrapper configuration helpers, DRM HDMI AVI helpers, ALSA IEC958/CEA definitions, and shared ACR calculation.

Risks and test signals: DDC polling is synchronous and may block roughly one byte times retry sleep on bad sinks. Only 16-bit LPCM word length is accepted. Quantization range policy treats VIC 1 as full and other CEA VICs as limited. CSC is always enabled for range mapping. Validate EDID segment reads, HDMI/DVI range behavior, double-clock/interlaced timing fields, 2/6/8 channel LPCM, invalid sample widths/rates, and debugfs register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.h

Purpose: Declares the OMAP5 HDMI core register map, video configuration structs, CSC coefficient table, packet mode enum, and public OMAP5 core/audio/DDC APIs.

Important APIs/types: Register definitions cover identification, interrupt handler status/mute, video sampler, packetizer, frame composer, audio core, generic parallel audio, main controller, CSC, HDCP/CEC masks, and I2C master registers. `enum hdmi_core_packet_mode` declares pixel-packing packet modes. `struct hdmi_core_vid_config` combines a wrapper/frame-composer `hdmi_config`, packet mode, data enable polarity, vertical blank oscillator flag, and blanking lengths. `struct csc_table` stores 3x4 fixed-point CSC coefficients. Public prototypes include DDC init/read/uninit, core dump/init/configure, and `hdmi5_audio_config()`.

Control flow: This header supports `hdmi5_core.c` register programming and is included by the HDMI5 top-level driver. Callers are expected to initialize `struct hdmi_core_data` with `hdmi5_core_init()` before video, audio, DDC, or dump operations.

State and persistence: No runtime state is allocated by the header. It defines register constants and stack/config data shapes used to program volatile HDMI hardware.

Dependencies/integration: Includes common `hdmi.h` definitions for shared OMAP HDMI structs and enums. Integrates with DRM bridge enable, EDID read, OMAP HDMI audio, and debugfs register dumping.

Risks and test signals: Register map correctness is critical because helper macros do raw MMIO field writes. The header includes a broad register surface, but implementation uses a subset; unused offsets still need compile-time consistency with the core IP. Test by building HDMI5/DRA7 configs and exercising video, DDC, audio, interrupt masking, and debugfs paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_common.c

Purpose: Implements shared HDMI helper functions for PHY lane parsing from device tree and HDMI Audio Clock Regeneration N/CTS calculation.

Important APIs/functions: `hdmi_parse_lanes_of()` reads an optional 8-entry `lanes` property from an OF graph endpoint, validates its length, and delegates to `hdmi_phy_parse_lanes()`. If absent, it applies the default ordered lane map `{0,1,2,3,4,5,6,7}`. `hdmi_compute_acr()` accepts pixel clock and audio sample frequency, selects HDMI-spec N values, applies limited deep-color corrections when applicable, and computes CTS.

Control flow: HDMI4/HDMI5 probe code calls lane parsing after locating the output endpoint. Audio configuration calls ACR calculation after deriving the sample rate from IEC958 channel status. Unsupported sample rates or null output pointers return `-EINVAL`.

State and persistence: No state persists here. Lane results are stored in caller-owned `struct hdmi_phy_data`; ACR results are written through caller pointers.

Dependencies/integration: Uses OF property helpers, OMAP HDMI common headers, HDMI PHY parsing, and kernel division helpers. It supports both HDMI4 and HDMI5 top-level drivers.

Risks and test signals: `hdmi_compute_acr()` currently hardcodes deep color to 100 percent, so deep-color modes are not truly represented. Lane parsing requires exactly four differential pairs encoded as eight cells. Validate DT lane remap/polarity variants, missing lane defaults, invalid lane arrays, and all supported audio sample rates from 32 kHz to 192 kHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_phy.c

Purpose: Implements shared OMAP HDMI PHY support: register dump, DT lane remap/polarity interpretation, PHY lane configuration, clock/frequency setup, feature selection for OMAP4 versus OMAP5, and resource mapping.

Important APIs/functions: `hdmi_phy_parse_lanes()` validates four differential pairs and fills `lane_function[]` and `lane_polarity[]`. `hdmi_phy_configure()` performs a dummy TX control read after reset, enables HFBITCLK divide-by-2 on OMAP5-class PHYs, chooses `freqout` from high/low bit clocks and hardware limit, enables TXVALID/TMDSCLKEN, optionally sets LDO voltage, and writes lane mux/polarity. `hdmi_phy_init()` selects feature flags and maps the `phy` resource. `hdmi_phy_dump()` prints key TX PHY registers.

Control flow: Top-level HDMI probe parses lanes and maps the PHY; full bridge enable computes PLL outputs, calls `hdmi_phy_configure()`, then wrapper power commands move the PHY through OFF/LDOON/TXON.

State and persistence: `struct hdmi_phy_data` holds mapped base, feature table pointer, lane functions, and lane polarities for device lifetime. Hardware register state is volatile and reprogrammed on enable.

Dependencies/integration: Uses `hdmi.h` register helpers, DSS logging, OF lane parsing through `hdmi_common.c`, and wrapper power state functions.

Risks and test signals: Lane table lookup supports only known permutations; invalid DT pairs reject probe. `freqout` selection depends on `hfbitclk / 10` versus SoC max PHY threshold. Validate default and swapped lane DTs, polarity inversion, OMAP4/OMAP5 feature differences, hotplug reconfiguration, and high pixel clock modes around the PHY max threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_pll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_pll.c

Purpose: Adapts the HDMI PLL hardware to the generic DSS PLL framework for OMAP4 and OMAP5/DRA7 HDMI outputs.

Important APIs/functions: `hdmi_pll_init()` maps the `pll` resource, stores the platform device and wrapper pointer, obtains `sys_clk`, fills `struct dss_pll`, selects OMAP4 or OMAP5 type-B PLL limits, and registers it with DSS. `hdmi_pll_enable()` runtime-resumes the HDMI device, enables DSS PLL routing, and commands wrapper PLL power `BOTHON_ALLCLKS`. `hdmi_pll_disable()` powers the PLL off, disables routing, and releases runtime PM. `hdmi_pll_uninit()` unregisters the PLL. `hdmi_pll_dump()` prints PLL control/status/config registers.

Control flow: HDMI bridge enable computes `dss_pll_clock_info`, calls `dss_pll_enable()`, then `dss_pll_set_config()`, whose ops route to `dss_pll_write_config_type_b()`. Disable calls `dss_pll_disable()`.

State and persistence: Device-lifetime state in `struct hdmi_pll_data` includes base, platform device, wrapper pointer, and embedded `struct dss_pll`. Active clock config is cached in `pll->cinfo` by the generic PLL layer and cleared on disable.

Dependencies/integration: Depends on runtime PM, `sys_clk`, HDMI wrapper PLL power commands, DSS PLL registration/calculation/programming, and debugfs dumping from HDMI top-level code.

Risks and test signals: `hdmi_pll_enable()` warns on negative runtime PM but does not unwind runtime PM if wrapper power command fails. PLL hardware constraints differ between OMAP4 and OMAP5. Test PLL lock at common CEA clocks, error unwinding for wrapper timeout, runtime PM balance, and debugfs reads while powered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_wp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_wp.c

Purpose: Implements the HDMI wrapper register helper layer for IRQs, PHY/PLL power commands, video start/stop, timing/interface programming, audio DMA/FIFO programming, and DMA address discovery.

Important APIs/functions: IRQ helpers get/ack/enable/disable wrapper IRQ status. `hdmi_wp_set_phy_pwr()` and `hdmi_wp_set_pll_pwr()` issue power commands and poll status fields with timeout. `hdmi_wp_video_config_format()`, `hdmi_wp_video_config_interface()`, `hdmi_wp_video_config_timing()`, and `hdmi_wp_init_vid_fmt_timings()` translate `videomode`/`hdmi_config` into wrapper registers, including interlace and double-clock adjustments. `hdmi_wp_video_start()` enables video, while `hdmi_wp_video_stop()` waits for frame done. Audio helpers configure format, DMA block/transfer size, threshold, DMA mode, and audio/core request enable bits. `hdmi_wp_init()` maps the `wp` resource and stores physical base/version.

Control flow: HDMI full enable clears IRQs, powers PLL/PHY, configures core and wrapper, then starts video. Full disable clears IRQs, stops wrapper video, disables manager and PHY/PLL. Audio config/start paths program wrapper DMA and toggle audio enable bits.

State and persistence: `struct hdmi_wp_data` stores mapped base, physical base, and version. Register state persists only while the hardware is powered. Top-level drivers cache idlemode and audio state.

Dependencies/integration: Shared by HDMI4 and HDMI5. Uses common HDMI register helpers, DSS logging, wrapper register definitions from `hdmi.h`, and top-level IRQ/audio/video paths.

Risks and test signals: Power command polling failures return `-ETIMEDOUT`; video stop logs if FRAMEDONE never arrives after up to about one second. OMAP4 and OMAP5 differ in HSW programming. Test enable/disable cycles, frame-done on stop, PLL/PHY timeout injection, interlaced/double-clock timing, IRQ ack flushing, and audio DMA address correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_wp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/omapdss.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/omapdss.h

Purpose: Public internal DSS interface header shared between OMAP DRM and DSS output drivers. It defines display types, channels, plane/output IDs, overlay/manager/writeback data contracts, DSS device descriptors, IRQ bits, and manager/output API prototypes.

Important APIs/types: `enum omap_display_type`, `omap_plane_id`, `omap_channel`, `omap_dss_output_id`, and related enums describe hardware display routing and features. `struct omap_overlay_info`, `omap_overlay_manager_info`, and `omap_dss_writeback_info` carry plane, manager, and writeback programming data. `struct omap_dss_device` is the central output/sink object with device, bridge, panel, list node, type/name, DSI ops, bus flags, DISPC channel, output ID, and OF port. Prototypes cover device registration/connect/disconnect, output initialization/cleanup, DISPC ISR registration, CRTC manager operations, manager timing/config/enable/update/framedone APIs, component readiness, DSS init/exit, and DISPC lookup.

Control flow: Output drivers create and register `omap_dss_device` objects. The DRM driver connects them into pipelines and manager helpers call back into `omap_crtc_dss_*()` to program DISPC/CRTC state. DSI manual update and framedone paths use the function pointer contracts here.

State and persistence: The header defines in-memory device and programming state only. Lifetime is controlled by platform probes, component bind/unbind, and DRM modeset objects.

Dependencies/integration: Includes DRM color/mode types, Linux device/list/IRQ types, OMAP platform data, and videomode. It is the integration point between DSS hardware drivers and DRM KMS.

Risks and test signals: Because many modules share these structs, enum/channel/output ID mismatches can break pipeline routing. Fixed array users assume channel and output IDs fit local limits. Validate multi-output probe, bridge/panel graph handling, DSI manual update, writeback users, and IRQ mapping for each SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/omapdss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/output.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/output.c

Purpose: Provides common OMAP DSS output setup and manager wrapper functions used by DSS output drivers to connect local bridges/panels to DRM and to call back into OMAP DRM CRTC manager operations.

Important APIs/functions: `omapdss_device_init_output()` finds the remote OF graph sink, resolves a DRM bridge or panel, wraps panels with `drm_panel_bridge_add()`, chains an optional local bridge ahead of the next bridge, and defers probe when no sink bridge is ready. `omapdss_device_cleanup_output()` removes any panel bridge. `dss_mgr_set_timings()`, `dss_mgr_set_lcd_config()`, `dss_mgr_enable()`, `dss_mgr_disable()`, `dss_mgr_start_update()`, and framedone register/unregister wrappers dispatch through `dss->mgr_ops_priv` into `omap_crtc_dss_*()`.

Control flow: Output probe initializes an `omap_dss_device` and calls `omapdss_device_init_output()` before registering it. DRM modeset later attaches bridges, creates connectors, and uses the manager wrappers during bridge enable/disable or mode setting.

State and persistence: Updates fields in caller-owned `struct omap_dss_device`: `bridge`, `next_bridge`, and `panel`. No persistent storage exists.

Dependencies/integration: Depends on OF graph, DRM bridge/panel helpers, `dss.h`, `omapdss.h`, and the OMAP DRM CRTC manager API.

Risks and test signals: Missing remote nodes are tolerated as no sink, while missing resolved bridges with local bridges defer probe. Cleanup only removes panel bridges when both bridge and panel are present. Test panel and bridge sinks, chained local bridge outputs like HDMI/SDI/VENC, deferred probe ordering, and manager callback availability before bridge enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/pll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/pll.c

Purpose: Implements the generic DSS PLL registry, enable/disable/configuration facade, clock divider calculation helpers, and low-level type-A/type-B PLL programming routines.

Important APIs/functions: `dss_pll_register()`, `dss_pll_unregister()`, `dss_pll_find()`, and `dss_pll_find_by_src()` manage PLLs in `dss->plls`. `dss_pll_enable()`, `dss_pll_disable()`, and `dss_pll_set_config()` wrap input clocks, regulators, hardware ops, and cached clock info. `dss_pll_calc_a()` and `dss_pll_hsdiv_calc_a()` search integer PLL/HSDIV parameters for type-A hardware. `dss_pll_calc_b()` calculates type-B fractional PLL settings for a target clkout. `dss_pll_write_config_type_a()` and `_type_b()` program registers, wait for GO/lock, handle errata i886/i932, and enable HSDIV outputs.

Control flow: HDMI and video PLL frontends register `struct dss_pll` instances with hardware limits and ops. Output enable computes clock info, enables the PLL, writes config, and later disables/clears cached info.

State and persistence: `struct dss_pll` stores hardware descriptors, base, clkin/regulator, ops, cached `cinfo`, and DSS owner. All state is runtime memory and hardware registers.

Dependencies/integration: Uses kernel clk/regulator APIs, DSS logging/control routing, SoC-specific PLL descriptors, and callers in HDMI/video/DPI/SDI paths.

Risks and test signals: Search loops must obey hardware min/max and errata direction constraints. Type-B calculation uses WARN_ON for unexpected fractional delta but still proceeds. Lock/GO timeouts fail modeset. Test PLL calculations near min/max clocks, OMAP3/4/5/DRA7 variants, regulator failure unwind, HSDIV ack bits, and errata retry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/sdi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/sdi.c

Purpose: Implements the OMAP SDI output as a DRM bridge and OMAP DSS output, including clock divisor search, LCD manager configuration, regulator/runtime sequencing, and DT parsing.

Important APIs/functions: `sdi_init_port()` allocates `struct sdi_device`, reads endpoint `datapairs`, gets `vdds_sdi`, initializes the local bridge/output, and stores the object in `port->data`. `sdi_calc_clock_div()` repeatedly widens the accepted pixel-clock range and uses `dss_div_calc()` plus `dispc_div_calc()` callbacks to find a DSS fclk and DISPC divisors. Bridge callbacks validate/fixup/set modes, attach to the next bridge, enable/disable SDI, and store adjusted pixel clock.

Control flow: Mode validation and fixup search for achievable clocks; fixup adjusts `adjusted_mode->clock` to the exact computed pclk. Enable turns on the regulator, runtime-resumes DISPC, recomputes clocks, sets DSS fclk, configures LCD manager, writes DISPC clock divisors early for pck-free use, initializes/enables SDI in DSS, delays, and enables the manager. Disable reverses manager, SDI, runtime PM, and regulator.

State and persistence: `struct sdi_device` stores DSS pointer, pixelclock, datapairs, regulator, manager config, output, and bridge. No disk persistence exists.

Dependencies/integration: Depends on DRM bridge callbacks, OF graph endpoint data, DSS SDI control functions, DISPC clock/divider APIs, OMAP DSS output/manager helpers, and regulator framework.

Risks and test signals: Clock search may accept up to about +/-1 MHz drift after retries; no exact clock guarantee. Enable failures must unwind regulator and DISPC runtime PM. Early direct divider programming bypasses normal shadow timing semantics by necessity. Test supported panels, adjusted clock reporting, regulator failure, SDI enable timeout, suspend/resume, and invalid/missing `datapairs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/sdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/venc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/venc.c

Purpose: Implements the OMAP VENC analog TV encoder platform driver and DRM bridge for PAL/NTSC composite or S-Video output.

Important APIs/functions: Static `venc_config_pal_trm` and `venc_config_ntsc_trm` hold TRM-derived register tables. `venc_probe()` maps registers, gets VDDA DAC regulator, optionally gets `tv_dac_clk` for matching OMAP3/AM35 SoCs, parses endpoint channel/polarity, enables runtime PM, registers output, and adds a component. `venc_bind()` reads revision and creates debugfs. Bridge callbacks expose PAL/NTSC modes, validate/fixup to canonical interlaced modes, set the active config and TV pixel clock, and power on/off. Runtime PM callbacks control optional TV DAC clock.

Control flow: Bridge mode_set chooses PAL or NTSC table and sets DISPC TV pclk to 13.5 MHz. Enable runtime-resumes VENC, resets it, writes the selected table, selects VENC output and DAC power in DSS, programs output control for composite/S-Video and polarity, enables VDDA DAC, and enables the DSS manager. Disable clears output control/DAC power, disables manager, regulator, and runtime PM.

State and persistence: `struct venc_device` stores base, regulator, optional clock, DSS pointer, selected config, type, polarity, output, bridge, and debugfs handle. Register state is reprogrammed on enable.

Dependencies/integration: Uses component framework, runtime PM, regulators/clocks, SoC matching, OF graph properties `ti,channels` and `ti,invert-polarity`, DRM bridge modes, and DSS manager/output helpers.

Risks and test signals: Only PAL and NTSC exact mode families are accepted. Probe requires valid `ti,channels` when endpoint exists. Power-off disables manager after clearing output/DAC, which may have analog artifact implications. Test PAL/NTSC mode enumeration, composite and S-Video DTs, OMAP3 TV DAC clock PM, regulator failures, debugfs register dump, and repeated enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/video-pll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/video-pll.c

Purpose: Implements DRA7 video PLL frontends for the generic DSS PLL framework, including clock-control power sequencing and errata-aware type-A PLL registration.

Important APIs/functions: `dss_video_pll_init()` maps per-ID PLL and clock-control resources (`pll1`/`pll2`, `pll1_clkctrl`/`pll2_clkctrl`), gets `video1_clk` or `video2_clk`, allocates `struct dss_video_pll`, fills the embedded `struct dss_pll`, assigns DRA7 type-A hardware limits, stores optional regulator, and registers with DSS. `dss_video_pll_enable()` runtime-resumes DSS, enables DSS PLL routing, enables SCP clock, waits reset done, and powers the PLL. `dss_video_pll_disable()` powers down, disables SCP clock/routing, and runtime-suspends DSS. `dss_video_pll_uninit()` unregisters.

Control flow: Output clock users find the PLL by source/name, calculate type-A settings through `pll.c`, enable it, program config through `dss_pll_write_config_type_a()`, then disable on output teardown.

State and persistence: `struct dss_video_pll` wraps `struct dss_pll` plus device and clkctrl base. Active config is held by the generic `dss_pll` cache and hardware registers only.

Dependencies/integration: Depends on platform resource names, kernel clk/regulator APIs, DSS runtime/control helpers, generic PLL math/programming, and DRA7 errata flags i886/i932.

Risks and test signals: DRA7 PLL power status is not reliable, so enable uses a fixed 1 ms delay. Resource array indexing assumes valid caller IDs. Test both video PLLs, missing resources, regulator use, reset timeout, suspend/resume, and clock rates requiring errata retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/video-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.c

Purpose: Implements OMAP DRM CRTC objects, DISPC manager callbacks, atomic CRTC state, pending flip completion, vblank/framedone IRQ handling, manual DSI updates, color management, and CRTC creation.

Important APIs/functions: `omap_crtc_init()` allocates a CRTC for a pipeline/channel, initializes pending wait and manual update work, enables color management when DISPC supports gamma, and installs primary plane properties. DSS manager entry points set timings/config, enable/disable manager, start updates, and register framedone callbacks. IRQ entry points handle error, vblank, and framedone events. Atomic helpers validate mode/bandwidth, mirror legacy rotation/zpos to primary plane state, program gamma/CTM manager properties, trigger DISPC GO or manual update, and arm events.

Control flow: Encoder/output mode paths set `omap_crtc->vm`. Bridge enable calls manager enable, which writes timings and calls `omap_crtc_set_enabled()`. Atomic flush writes gamma/manager properties and, if enabled, marks a pending update, takes a vblank reference, and either triggers DISPC GO or schedules manual DSI update. Vblank/framedone IRQs send pending events, clear pending, drop vblank refs, and wake commit waiters.

State and persistence: `struct omap_crtc` tracks channel, pipeline, videomode, enabled/pending/event state, delayed work, and framedone callback. `struct omap_crtc_state` extends DRM state with legacy rotation/zpos shadows and `manually_updated`. No persistent storage exists.

Dependencies/integration: Depends on DRM atomic/vblank/color helpers, DISPC manager/IRQ APIs, OMAP plane properties, OMAP DSS outputs/DSI ops, and driver private bandwidth limits.

Risks and test signals: Pending state is protected by `event_lock` and commit waits timeout after 250 ms. HDMI bypasses normal enable wait because HDMI wrapper manages completion. Manual DSI updates do not trigger vsync and depend on framedone callback. Test atomic page flips, manual command-mode DSI dirty updates, HDMI enable, sync-lost handling on digit output, color CTM/gamma programming, suspend/resume, and bandwidth rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.h

Purpose: Declares the OMAP DRM CRTC public interface used by the driver core, encoders, planes, IRQ code, and DSS manager wrappers.

Important APIs/functions: The header exposes `omap_crtc_timings()`, `omap_crtc_channel()`, `omap_crtc_init()`, `omap_crtc_wait_pending()`, IRQ handlers for error/vblank/framedone, and `omap_crtc_flush()`. Forward declarations keep dependencies light while allowing callers to pass DRM and DSS objects.

Control flow: Driver modeset setup calls `omap_crtc_init()`. Encoder/output code obtains timing/channel data or invokes manager wrappers that eventually reach CRTC functions. IRQ dispatch calls error/vblank/framedone functions. Framebuffer dirty and manual-update paths call `omap_crtc_flush()`.

State and persistence: No state is stored here; it declares access to state owned by `omap_crtc.c`.

Dependencies/integration: Depends only on basic Linux types and forward declarations for DRM, videomode, DSS channel, and OMAP pipeline structs. Integrated by `omap_drv.h`, IRQ code, plane/framebuffer code, and DSS output wrappers.

Risks and test signals: Header changes affect many modules. ABI is internal but must remain consistent with CRTC implementation. Compile coverage across fbdev, IRQ, plane, and DSS output configurations is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_debugfs.c

Purpose: Registers OMAP DRM debugfs files for GEM object inspection, DRM MM address-space inspection, framebuffer inspection, and optional DMM/TILER map visualization.

Important APIs/functions: `gem_show()` locks `priv->list_lock` and calls `omap_gem_describe_objects()`. `mm_show()` prints the DRM VMA offset manager address-space `drm_mm`. `fb_show()` lists fbcon and userspace framebuffers when fbdev emulation is enabled. `omap_debugfs_init()` creates common files and conditionally adds `tiler_map` when `dmm_is_available()` reports a DMM/TILER device.

Control flow: The DRM driver installs `omap_debugfs_init` in `drm_driver.debugfs_init`. DRM core invokes it for a minor, and show callbacks read current driver state on demand.

State and persistence: No persistent state is stored; debugfs output reflects live kernel objects and TILER allocations.

Dependencies/integration: Depends on DRM debugfs, fb helper, framebuffer list locking, GEM describe helpers, and DMM/TILER debug map helper.

Risks and test signals: Debugfs callbacks must tolerate missing fbdev helper depending on config and device state. `fb_show()` assumes `dev->fb_helper` is valid when fbdev emulation exists. Test debugfs reads during normal operation, with and without DMM, with multiple framebuffers, and during driver teardown races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_priv.h

Purpose: Defines private DMM/TILER register offsets, IRQ/status bits, PAT descriptor formats, refill engine structures, platform data, and the central `struct dmm` used by `omap_dmm_tiler.c`.

Important APIs/types: Register macros cover DMM revision/sysconfig, LISA map, TILER orientation, PAT geometry/view/IRQ/status/descriptor registers, and PEG priority registers. IRQ/status masks identify transaction completion and error conditions. `struct pat_area`, `struct pat_ctrl`, and `struct pat` describe PAT refill descriptors. `struct dmm_txn` tracks descriptor allocation within a refill buffer. `struct refill_engine` tracks one PAT engine, refill memory, completion, async state, and idle list node. `struct dmm` stores MMIO, IRQ, dummy page, refill memory, engine pool, TCM containers, allocation list, platform data, and DRA7 i878 DMA workaround state.

Control flow: The implementation allocates and initializes these objects at DMM probe, uses transactions to append PAT descriptors for TILER region fills, and releases engines via IRQ or synchronous completion.

State and persistence: All state is runtime-only. DMM LUT contents are hardware state and are reinitialized on probe/resume.

Dependencies/integration: Depends on `struct pat_area` from the public TILER header, TCM allocator objects, DMA engine concepts, and OMAP GEM/fbdev users through TILER APIs.

Risks and test signals: Bitfield layouts in `struct pat_ctrl` must match hardware descriptor encoding and endianness expectations. Refill buffer sizing assumes worst-case descriptor counts. Test compile/layout on supported architectures, DMM probe, resume LUT refill, DRA7 workaround path, and error IRQ reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.c

Purpose: Implements OMAP DMM/TILER support: TILER block reservation, page pin/unpin programming through PAT refill engines, rotated/tiled address calculation, DMM probe/remove/resume, DRA7 register-access workaround, and debugfs map rendering.

Important APIs/functions: Public APIs include `tiler_reserve_2d()`, `tiler_reserve_1d()`, `tiler_release()`, `tiler_pin()`, `tiler_unpin()`, `tiler_ssptr()`, `tiler_tsptr()`, `tiler_stride()`, `tiler_size()`, `tiler_vsize()`, `tiler_align()`, `tiler_get_cpu_cache_flags()`, `dmm_is_available()`, and `tiler_map_show()`. Internal transaction functions allocate 16-byte-aligned descriptors, append PAT areas with page or dummy-page entries, commit through PAT_DESCR, and wait for IRQ completion/status.

Control flow: Probe maps DMM, optionally enables the DRA7 i878 DMA workaround, reads PAT geometry, allocates dummy/refill memory and engines, creates SITA TCM containers, maps formats to containers, requests IRQ, enables PAT interrupts, and fills all LUTs with dummy pages. Reserving a TILER block allocates TCM space and tracks it globally. Pinning builds PAT descriptors for each TCM slice, programming page physical addresses with optional roll; unpin fills with dummy pages. IRQ ack completes engines and releases async ones, though current fill forces synchronous operation.

State and persistence: Global `omap_dmm` owns hardware state, containers, engine pool, allocation list, dummy/refill DMA memory, and platform data. TILER blocks persist until release. Hardware LUTs are reinitialized on resume and probe; no disk persistence exists.

Dependencies/integration: Depends on TCM/SITA allocator, DMA mapping/engine, IRQ/completion APIs, OMAP GEM for tiled scanout and fbdev ywrap, DRM debugfs, OF match data, and DRA7 machine compatibility.

Risks and test signals: Asynchronous fill is force-disabled because error paths can leak engines. Physical addresses are stored in 32-bit PAT data, so 32-bit DMA constraints matter. Error handling in probe funnels through remove. Test DMM availability, 1D/2D allocations, tiled rotation scanout, fbdev ywrap roll, resume LUT refill, DRA7 i878 fallback, IRQ timeout/error paths, and debugfs map output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.h

Purpose: Declares the public OMAP DMM/TILER API, tiler formats, block/area structures, orientation/address constants, sizing helpers, and platform driver symbol.

Important APIs/types: `enum tiler_fmt` defines 8-bit, 16-bit, 32-bit, and page modes. `struct pat_area` encodes hardware PAT rectangle coordinates. `struct tiler_block` stores allocation list node, TCM area, and format. Constants define slot/container geometry, TILER view base addresses, orientation bits, access-mode shift, and `TIL_ADDR()`. APIs reserve/release blocks, pin/unpin pages, produce system-space and transformed-space pointers, calculate stride/size/virtual size, align dimensions, return CPU cache flags, and report DMM availability. `gem2fmt()` maps OMAP GEM tiling flags to TILER formats.

Control flow: GEM and framebuffer code reserve blocks for tiled buffers, pin pages before scanout, compute rotated addresses for DISPC, and release blocks when BOs go away. fbdev uses page-mode rolling through GEM/TILER integration.

State and persistence: Public `tiler_block` objects represent live TILER allocations until release. Header itself stores no state.

Dependencies/integration: Includes `omap_drv.h` for OMAP BO flags and `tcm.h` for container allocator types. Integrates with GEM, framebuffer scanout, fbdev, debugfs, and the DMM platform driver.

Risks and test signals: Geometry constants and orientation bit definitions must match hardware TRM. `validfmt()` and `gem2fmt()` are relied on before BUG_ON paths. Test all tiler formats, rotations/reflections, NV12/YUYV address calculations, page-mode ywrap, and builds with/without debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.c

Purpose: Implements the main OMAP DRM platform driver, DRM device setup/teardown, modeset pipeline construction, global atomic private state, atomic commit tail, custom zpos normalization, GEM ioctls, PM hooks, and module registration.

Important APIs/functions: `omapdrm_init()` allocates/registers a DRM device, initializes private state, GEM, mode config, global private object, overlays, modeset, vblank, poll helpers, fbdev, and DRM registration. `omap_modeset_init()` connects DSS outputs, creates planes, encoders, bridge connectors, CRTCs, pipeline/channel lookup tables, mode limits, and IRQ install. `omap_atomic_commit_tail()` sequences modeset disables/enables, plane commits, waits for completion, and cleanup, with an OMAP3-specific ordering exception. `omap_atomic_update_normalize_zpos()` adjusts normalized zpos for dual-overlay planes. Ioctls expose chipset ID and GEM create/info.

Control flow: Module init initializes DSS and registers DMM plus DRM platform drivers. Probe sets a 32-bit DMA mask, allocates `omap_drm_private`, and calls init. Modeset setup builds one connector/encoder/CRTC chain per connected DSS output. Atomic commit runtime-resumes DISPC around the hardware update and waits for CRTC pending completion before old buffers are released.

State and persistence: `struct omap_drm_private` owns DSS/DISPC pointers, pipelines, channels, planes, overlays, global private object, GEM object list, workqueue, IRQ waits, fbdev, and bandwidth limit. No disk persistence exists.

Dependencies/integration: Depends on DRM core/atomic/bridge connector/GEM/PRIME/fbdev helpers, OMAP DSS stack readiness, DISPC, overlays/planes/CRTC/encoder/fb/IRQ/GEM modules, DMM driver, SoC matching, and PM helpers.

Risks and test signals: Pipeline assumptions require one output per DISPC channel and no more outputs than managers/primary planes. Atomic ordering differs for OMAP3 versus later SoCs. Cleanup must disconnect pipelines after failure. Test multi-display DT aliases, deferred bridge probes, zpos with dual-overlay planes, GEM ioctls, suspend/resume, vblank init, max bandwidth filtering, and driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.h

Purpose: Central private OMAP DRM header defining shared driver structures, logging macros, global atomic resource state, and cross-module prototypes.

Important APIs/types: `struct omap_drm_pipeline` groups a CRTC, encoder, connector, output, and display alias. `struct omap_global_state` embeds DRM private state and maps up to eight hardware overlays to DRM planes. `struct omap_drm_private` stores the DRM device, SoC revision, DSS/DISPC, pipeline/channel arrays, planes/overlays, global private object, workqueue, GEM list and lock, DMM/GART flags, zorder property, IRQ wait state, bandwidth limit, and fbdev pointer. Prototypes expose global atomic state accessors and debugfs init.

Control flow: `omap_drv.c` initializes this shared state; plane/overlay code uses global private state for resource assignment; CRTC/IRQ/GEM/fbdev/debugfs modules consume the private object and common includes.

State and persistence: Defines runtime state only. Lifetimes are tied to DRM device probe/remove and atomic transaction state.

Dependencies/integration: Includes DSS headers, DRM atomic/GEM/omap UAPI, and all major OMAP DRM private module headers. It is the include hub for the driver.

Risks and test signals: Fixed-size arrays of eight pipelines/channels/planes/overlays must cover supported hardware. Header inclusion can create broad rebuild impacts. Compile all OMAP DRM configurations and exercise multiple outputs/overlays to validate array indexing and global state duplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.c

Purpose: Implements the OMAP DRM encoder object that bridges DRM mode setting to OMAP DSS output timing configuration.

Important APIs/functions: `omap_encoder_init()` allocates `struct omap_encoder`, initializes a DRM encoder of type TMDS, stores the target `omap_dss_device`, and installs helper callbacks. `omap_encoder_mode_set()` converts the adjusted DRM mode to `videomode`, restores missing sync/data-enable/pixel-edge flags from bridge timings and connector display info bus flags, and calls `dss_mgr_set_timings()`. `omap_encoder_destroy()` cleans up and frees the encoder.

Control flow: Modeset setup creates an encoder for each connected output and attaches the output bridge chain. During modeset, DRM helper calls `mode_set`, which writes upstream manager timings through DSS manager wrappers before bridge/output enable.

State and persistence: `struct omap_encoder` only stores the DRM encoder and output pointer. No persistent storage exists.

Dependencies/integration: Depends on DRM encoder/bridge/connector helpers, videomode conversion, OMAP DSS manager timing API, and bridge timing/display info bus flags.

Risks and test signals: The mode flag restoration is a documented hack because DRM display modes lose some videomode flags. The connector search assumes the matching connector is present in the mode config list. Test panels/bridges with DE and pixel/sync edge flags, chained bridges, and modeset ordering with each DSS output type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.h

Purpose: Declares the OMAP DRM encoder creation API.

Important APIs/functions: `omap_encoder_init(struct drm_device *dev, struct omap_dss_device *output)` creates a DRM encoder bound to one DSS output. The header forward-declares DRM and DSS structures to keep dependencies minimal.

Control flow: `omap_drv.c` calls this during modeset pipeline construction before bridge attachment and connector/CRTC creation.

State and persistence: No state is stored in the header; encoder state is implemented in `omap_encoder.c`.

Dependencies/integration: Used by the main driver through `omap_drv.h`; integrates with DRM mode setting and DSS output objects.

Risks and test signals: Interface is small but central to pipeline construction. Build and modeset probe failures are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.c

Purpose: Implements OMAP DRM framebuffer creation, validation, pin/unpin for scanout, dirty handling, format support, and scanout address generation for linear and TILER-rotated buffers.

Important APIs/functions: `omap_framebuffer_create()` resolves GEM handles and calls `omap_framebuffer_init()`. `omap_framebuffer_init()` validates supported formats, plane pitch consistency, pitch alignment, and BO sizes before initializing a DRM framebuffer. `omap_framebuffer_pin()` and `_unpin()` pin all GEM planes and cache DMA addresses with a pin count. `omap_framebuffer_update_scanout()` fills `omap_overlay_info` for DISPC, computing source/destination dimensions, tiled orientation, rotation, stride, NV12 UV address, and optional right-half info for dual-overlay scanout. `omap_framebuffer_dirty()` flushes all CRTCs for manual displays.

Control flow: Userspace/fbdev creates framebuffers from GEM BOs. Plane atomic update pins framebuffers and asks update_scanout for DISPC programming. Dirty callbacks trigger CRTC manual update work.

State and persistence: `struct omap_framebuffer` embeds DRM framebuffer, pin count, format pointer, per-plane DMA addresses, and a mutex. State lives until framebuffer destroy; pin state is transient.

Dependencies/integration: Depends on DRM framebuffer/GEM helpers, OMAP GEM pin/sync/tiled address APIs, TILER orientation constants, OMAP CRTC flush, and DISPC overlay info contracts.

Risks and test signals: Non-tiled rotations are ignored with warning. Dual-overlay split uses linear address helpers and has special YUV even-width adjustment. Debug describe appears to print `fb->offsets[n]` instead of `offsets[i]`, which is a likely diagnostic bug. Test supported RGB/YUV formats, NV12 multi-plane, tiled rotations/reflections, dual-overlay wide modes, dirty updates, BO size rejection, and pin count balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.h

Purpose: Declares the OMAP DRM framebuffer API used by mode config, planes, fbdev, and debugfs.

Important APIs/functions: Creation/init APIs build framebuffers from userspace file handles or existing GEM objects. Pin/unpin APIs prepare buffers for scanout. `omap_framebuffer_update_scanout()` converts framebuffer and plane state into one or two `omap_overlay_info` structures. `omap_framebuffer_supports_rotation()` reports TILER-backed rotation support. `omap_framebuffer_describe()` emits debugfs information.

Control flow: Main mode config uses `omap_framebuffer_create()` as `fb_create`; fbdev uses `omap_framebuffer_init()` around its BO; plane code pins and updates scanout; debugfs calls describe.

State and persistence: No state is stored in the header; framebuffer state is private to `omap_fb.c`.

Dependencies/integration: Forward-declares DRM, GEM, plane state, overlay info, and seq_file types. Included by `omap_drv.h` for broad driver use.

Risks and test signals: API callers must pin before using scanout DMA addresses and unpin when done. Build coverage plus plane/fbdev scanout tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.c

Purpose: Provides legacy fbdev emulation for OMAP DRM, including fb helper probe, deferred I/O, write-combine mmap, damage forwarding, and optional DMM y-wrap scrolling.

Important APIs/functions: `omap_fbdev_driver_fbdev_probe()` creates a 32bpp XRGB fbdev surface, allocates an OMAP GEM scanout/WC BO, initializes an OMAP framebuffer, pins it for `fix.smem_start`, fills `fb_info`, sets up deferred I/O, and enables y-wrap when DMM is present and module parameter `ywrap` is true. `omap_fbdev_pan_display()` uses DMM roll through `pan_worker()` for y-wrap or falls back to DRM helper pan. `omap_fbdev_dirty()` forwards fbdev damage to framebuffer dirty. `omap_fbdev_setup()` allocates managed fbdev state and calls `drm_client_setup()`.

Control flow: Main DRM registration calls `omap_fbdev_setup()`. DRM client/fb helper invokes fbdev probe, which allocates the backing BO and framebuffer. Deferred writes trigger damage, and panning either rolls TILER page mappings immediately or queues work if atomic context.

State and persistence: `struct omap_fbdev` stores DRM device, ywrap flag, and work item. The fbdev BO remains pinned for the fb_info lifetime and is cleaned in `omap_fbdev_fb_destroy()`.

Dependencies/integration: Depends on DRM fb helper/client setup, OMAP GEM allocation/pin/vaddr/roll, OMAP framebuffer init/dirty, DMM availability, and the driver ordered workqueue.

Risks and test signals: Permanent pinning is intentional for fb_mmap but increases memory pressure. y-wrap requires DMM and page-aligned pitch. Destroy must unpin and remove framebuffer exactly once. Test fbcon boot, mmap writes, deferred damage, pan/ywrap on DMM and non-DMM systems, module parameter disabling, and cleanup on fbdev removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.h

Purpose: Declares and conditionally compiles the OMAP DRM fbdev emulation entry points.

Important APIs/functions: When `CONFIG_DRM_FBDEV_EMULATION` is enabled, it declares `omap_fbdev_driver_fbdev_probe()` and `omap_fbdev_setup()` and defines `OMAP_FBDEV_DRIVER_OPS` to populate `.fbdev_probe`. When disabled, the macro sets `.fbdev_probe = NULL` and `omap_fbdev_setup()` is an inline no-op.

Control flow: `omap_drv.c` includes this header to wire driver ops and to call fbdev setup after DRM registration.

State and persistence: No state is stored here; it gates fbdev state allocation in `omap_fbdev.c`.

Dependencies/integration: Forward-declares DRM device/fb helper/surface size types and integrates with DRM driver ops.

Risks and test signals: Conditional compilation must keep the main driver valid with fbdev enabled or disabled. Build both configurations and verify DRM registration succeeds without fbdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.h -->
