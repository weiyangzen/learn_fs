# subset-b-003553 Research

Work item: subset-b-003553

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi.c

Purpose: implements the generic Synopsys DesignWare HDMI transmitter DRM bridge. It owns HDMI/DVI mode setup, EDID/DDC access, HPD/RXSENSE handling, SCDC and HDMI 2.0 scrambling setup, Synopsys PHY control, video packetizer/CSC/sample configuration, infoframe programming, audio child-device integration, CEC child-device integration, and the exported probe/bind/remove API used by SoC glue drivers.

Important APIs and types: `struct dw_hdmi` is the central runtime object and embeds `drm_bridge`, optional legacy `drm_connector`, DDC/I2C state, PHY callbacks/data, audio/CEC child devices, current connector/mode state, HPD force/disabled/rxsense state, audio parameters, regmap access, and CEC notifier state. `struct hdmi_data_info` tracks negotiated input/output media bus formats, encodings, pixel repetition, HDCP keepout, video timing, and RGB limited range. `struct dw_hdmi_i2c` implements the internal DDC adapter. Exported entry points include `dw_hdmi_probe()`, `dw_hdmi_remove()`, `dw_hdmi_bind()`, `dw_hdmi_unbind()`, `dw_hdmi_resume()`, `dw_hdmi_to_plat_data()`, audio setters/enablers, PHY helpers such as `dw_hdmi_phy_i2c_write()`, and `dw_hdmi_bus_fmt_is_420()`.

Control flow: probe allocates the bridge object, parses downstream graph bridge information, chooses an external DDC adapter or registers the internal HDMI I2C master, configures an 8-bit or 32-bit regmap, enables clocks, validates product IDs, detects the PHY, initializes interrupt masks/DDC/HPD, requests the IRQ, initializes audio CTS/N, optionally registers audio and CEC platform children, then adds the DRM bridge. DRM atomic flow stores the adjusted mode in `mode_set`, records the current connector in `atomic_enable`, powers up according to force/rxsense/disabled state, and powers down in `atomic_disable`. `dw_hdmi_setup()` is the main mode-programming sequence: choose CEA/VIC colorimetry, normalize fixed bus formats, derive RGB quantization, program the frame composer, initialize PHY, enable video path, update audio clocks, emit AVI/Vendor/DRM infoframes, configure packetizer/CSC/sample mappings, configure HDCP keepout, and clear frame-composer overflow.

State and persistence: driver state persists in `struct dw_hdmi` for the bridge lifetime. `previous_mode` is retained so HPD/RXSENSE power events can reprogram the transmitter. `curr_conn`, `disabled`, `bridge_is_on`, `force`, `rxsense`, and `phy_mask` are mutex-protected power/detect state. Audio parameters are protected by `audio_mutex` and `audio_lock`; `audio_n`/`audio_cts` are recomputed from pixel/TMDS clock and sample rate. Hardware state persists in DesignWare registers until power/reset or reprogramming. `cec_notifier` is registered per connector and invalidated on disconnect.

Dependencies and integration: integrates with DRM bridge/connector/atomic helpers, DRM EDID and HDMI infoframe helpers, DRM SCDC helpers, media bus formats, V4L2 YCbCr encoding constants, Linux regmap/clk/pinctrl/I2C/IRQ/platform-device APIs, CEC notifier, and child drivers `dw-hdmi-ahb-audio`, `dw-hdmi-i2s-audio`, `dw-hdmi-gp-audio`, and `dw-hdmi-cec`. Platform glue supplies `struct dw_hdmi_plat_data`, PHY tables/callbacks, mode validation, optional external regmap, output graph port, and audio/PHY hooks.

Risks: register programming is order-sensitive, especially SCDC scrambling, high-TMDS clock ratio, PHY power-on, and frame-composer reset/overflow workaround. The internal DDC controller has unsupported DDC/CI transfers and an optional pinctrl unwedge hack that depends on board pinmux states. Power state is split between DRM callbacks and HPD/RXSENSE IRQs, so lock ordering and `curr_conn` validity matter. Audio enable runs under spinlock while platform hooks can touch hardware. Bus-format negotiation influences TMDS rate, CSC, GCP deep-color packets, and 4:2:0 timing halving; mistakes can produce blank displays. Probe cleanup must keep `i2c_put_adapter()` and internal adapter deletion balanced.

Test signals: compile with representative DW HDMI glue drivers, boot with external and internal DDC, hotplug and unplug with HPD/RXSENSE IRQs, forced connector modes, EDID read and CEC physical address updates, HDMI and DVI sinks, RGB/YUV444/YUV422/YUV420 and deep-color modes, SCDC scrambling above 340 MHz and low-rate scrambling, audio playback through I2S/AHB/GP variants, suspend/resume calling `dw_hdmi_resume()`, and error injection for PHY lock timeout, DDC timeout/unwedge, and child-device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi.h

Purpose: private register and bitfield definition header for the DesignWare HDMI bridge implementation. It maps the controller register space, interrupt status/mute registers, frame composer, video packetizer, PHY, audio, DMA, main controller, CSC, HDCP, DDC I2C, and HDMI 3D TX PHY fields used by `dw-hdmi.c` and sibling audio/CEC support.

Important APIs and types: this file defines register offsets such as `HDMI_FC_INVIDCONF`, `HDMI_VP_CONF`, `HDMI_PHY_CONF0`, `HDMI_AUD_N1`, `HDMI_MC_CLKDIS`, `HDMI_CSC_CFG`, and `HDMI_I2CM_OPERATION`, plus an anonymous enum of masks, shifts, and field values. It also defines the HDMI 3D TX PHY register addresses and field bits used for PHY I2C programming. There are no functions or storage; the header is a hardware contract for register access helpers in the C files.

Control flow: no executable control flow exists here. Runtime code reads these constants to build ordered programming sequences: IRQ initialization masks and clears `HDMI_IH_*`; DDC uses `HDMI_I2CM_*`; video setup uses frame-composer and packetizer fields; PHY bring-up uses `HDMI_PHY_*` and `HDMI_3D_TX_PHY_*`; audio setup uses `HDMI_AUD_*`, `HDMI_FC_AUD*`, and AHB DMA bits; SCDC/scrambling setup uses `HDMI_FC_SCRAMBLER_CTRL` and `HDMI_MC_SWRSTZ`.

State and persistence: the header itself holds no state. The constants describe hardware state persisted in MMIO registers, accessed through regmap with possible register shifting in `dw-hdmi.c`.

Dependencies and integration: included by the Synopsys DW HDMI implementation and related bridge components. The naming and masks must stay consistent with the DesignWare HDMI IP manual and the register access style in `hdmi_writeb()`, `hdmi_readb()`, and `hdmi_modb()`.

Risks: incorrect masks or offsets can silently program unrelated hardware fields. Some fields have inverted or historical names, such as `HDMI_A_HDCPCFG1_ENCRYPTIONDISABLE_DISABLE`, and some comments note IP-specific behavior such as the CTS manual bit. Register offsets are byte offsets and are shifted by `reg_shift` for 32-bit register windows, so duplicate shifting in callers would break access. The header is broad and private, so unused-looking definitions may still support optional audio/CEC or platform PHY paths.

Test signals: full build of DW HDMI, DW HDMI audio, and CEC objects; runtime smoke tests covering HDMI mode set, DDC, audio, CEC, SCDC, and PHY configuration; static review when changing register definitions to compare every mask/shift against the IP documentation and current call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi.c

Purpose: generic Synopsys DesignWare MIPI DSI host controller bridge driver for the older DSI IP. It provides a `mipi_dsi_host` for panel command transfers, a DRM bridge for encoder/panel chaining, mode programming for DPI video output, D-PHY timing and power sequencing through platform callbacks, optional dual-DSI mirroring, and debugfs controls for the controller video pattern generator.

Important APIs and types: `struct dw_mipi_dsi` embeds `drm_bridge`, `mipi_dsi_host`, MMIO base, pixel clock, panel bridge, DSI lane/channel/format/mode flags, current mode, platform data, optional master/slave pointers, and debugfs state. Important functions are `dw_mipi_dsi_host_attach()`, `dw_mipi_dsi_host_transfer()`, `dw_mipi_dsi_mode_set()`, `dw_mipi_dsi_bridge_atomic_pre_enable()`, `dw_mipi_dsi_bridge_atomic_enable()`, `dw_mipi_dsi_bridge_post_atomic_disable()`, `dw_mipi_dsi_set_slave()`, `dw_mipi_dsi_get_bridge()`, `dw_mipi_dsi_probe()`, `dw_mipi_dsi_remove()`, and `dw_mipi_dsi_bind()`.

Control flow: host attach validates lane count, records the attached peripheral parameters, finds the downstream panel bridge from port 1, adds the DSI bridge, and calls optional platform host attach. Transfers create a MIPI DSI packet, configure low-power/ack command bits, write payload words then a header, mirror writes to a slave controller when present, and read response payloads from the generic read FIFO. Atomic pre-enable enables clocks/runtime PM, asks PHY ops for lane Mbps and timings, resets/programs the controller, configures DPI color/polarity, packet handling, video mode, packet size, command timeouts, line/vertical timing, D-PHY timers/interface, clears errors, initializes/enables PHY, waits two frames, then switches to command mode so the panel can prepare. Atomic enable switches to video mode; post-disable switches back to command mode, powers off PHY, disables slave then master clocks/runtime PM, and resets controller/PHY.

State and persistence: lane/channel/format/mode flags are latched at host attach; the adjusted DRM mode is stored in `dsi->mode` for later pre-enable. `lane_mbps` is computed per enable. Dual DSI persists via symmetric master/slave pointers and replicated display parameters. Hardware state is volatile MMIO state; runtime PM and `pclk` lifetime are tied to bridge enable/disable. Debugfs booleans persist in driver memory and immediately update `DSI_VID_MODE_CFG` when written.

Dependencies and integration: depends on DRM bridge/atomic helpers, DRM OF panel bridge lookup, MIPI DSI packet helpers, `struct dw_mipi_dsi_plat_data` and PHY callbacks from `<drm/bridge/dw_mipi_dsi.h>`, Linux clk/reset/pm_runtime/iopoll/debugfs APIs, and platform glue drivers such as STM/Rockchip implementations that provide lane-rate and timing calculations.

Risks: many timing calculations are marked TODO and approximate, especially non-burst packet sizing, timeout counters, and stop-wait times. `pm_runtime_get_sync()` and `clk_prepare_enable()` return values are not fully checked in the mode path. Dual-DSI mirrors command writes but reads only from the master. Host attach adds the bridge only after a DSI peripheral appears, so bridge-chain timing depends on panel attachment. Debugfs writes access registers directly and assume the block is powered. Error paths in PHY timing/init log failures but continue.

Test signals: attach/detach with lane counts at and above `max_data_lanes`, panel prepare commands in LP and HS modes, DCS/generic reads and writes with FIFO timeouts, video modes for burst/sync-pulse/sync-event, RGB565/666/888 formats, suspend/resume or disable/enable cycles, dual-DSI split modes, debugfs VPG toggles while enabled, and platform PHY callback failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi2.c

Purpose: generic Synopsys DesignWare MIPI DSI2 host controller bridge driver for newer DSI2 IP. It exposes a MIPI DSI host and DRM bridge, programs the newer CRI/IPI/manual-mode register model through regmap, configures D-PHY ratios and timings using platform PHY callbacks, and supports video or data-stream output modes.

Important APIs and types: `struct dw_mipi_dsi2` embeds `drm_bridge`, `mipi_dsi_host`, downstream panel bridge, regmap, `pclk`, `sys_clk`, lane Mbps, lane/channel/format/mode flags, current DRM mode, and platform data. Key functions are `dw_mipi_dsi2_host_attach()`, `dw_mipi_dsi2_host_transfer()`, `dw_mipi_dsi2_mode_set()`, `dw_mipi_dsi2_bridge_atomic_pre_enable()`, `dw_mipi_dsi2_bridge_atomic_enable()`, `dw_mipi_dsi2_bridge_post_atomic_disable()`, `dw_mipi_dsi2_probe()`, `dw_mipi_dsi2_remove()`, and `dw_mipi_dsi2_bind()`. Register programming helpers cover command FIFO availability, command/video/data-stream mode changes, soft reset, PHY clock/ratio/timing setup, IPI color/timing setup, and TX options.

Control flow: probe allocates the bridge, validates required PHY ops, creates or adopts a regmap, gets `pclk` and `sys` clocks, optionally toggles APB reset, enables runtime PM, registers the MIPI DSI host, and initializes bridge metadata. Host attach records device parameters, finds the downstream bridge, adds this bridge, and calls optional host attach. Command transfer toggles LP display-command enable, creates a packet, waits for CRI FIFOs idle, writes payload and header with the requested command TX mode, and reads short or long responses from CRI RX registers. Pre-enable enables clocks/runtime PM, soft-resets, powers down, selects manual mode, configures PHY mode/clock ratios/LP-HS timings, powers on PHY, programs TX options, updates continuous/non-continuous clock selection, powers up, enters command mode, and programs IPI packet/color/timing. Atomic enable enters video mode for video peripherals or data-stream mode otherwise; post-disable clears pixel packet size, enters command mode, powers down, powers off PHY, disables clocks, and drops runtime PM.

State and persistence: attached DSI device parameters persist in `lanes`, `channel`, `format`, and `mode_flags`; adjusted mode persists in `mode`; lane Mbps is recomputed at enable. Hardware state is held in regmap-backed DSI2 registers and is reset/reprogrammed on each enable. Runtime PM and clock state are expected to balance across pre-enable/post-disable.

Dependencies and integration: depends on DRM bridge and MIPI DSI helpers, regmap, clk/reset/pm_runtime/iopoll, `struct dw_mipi_dsi2_plat_data` and PHY ops from `<drm/bridge/dw_mipi_dsi2.h>`, and platform glue such as Rockchip DSI2. PHY callbacks provide lane rate, timing, and interface width. Downstream panels are discovered via DRM OF graph port 1.

Risks: `CMD_TX_MODE` is defined twice, which is harmless with identical replacement but fragile for future edits. `clk_prepare_enable()` and `pm_runtime_get_sync()` results are not checked in the enable path. The PHY interface callback result is not validated at use time, and unsupported PPI widths rely on probe/platform validation. Timing math uses fixed assumptions for DPHY high-speed clock and IPI clock division. There is no dual-DSI support in this generic DSI2 file. Several mode-change polling failures only log errors and continue.

Test signals: host attach/detach, MIPI DCS/generic short and long reads/writes, LP and HS command modes, video and non-video data-stream modes, RGB565/RGB666/RGB888, continuous and non-continuous clock, APB reset present/absent, clock/runtime PM balance over repeated enable/disable, PHY callback failures, and mode-valid/mode-fixup platform callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/tc358762.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/tc358762.c

Purpose: DRM bridge and MIPI DSI driver for the Toshiba TC358762 DSI-to-DPI bridge. It configures a one-lane RGB888 DSI receiver, powers and resets the bridge, writes the small register initialization sequence over MIPI DSI generic packets, and attaches the downstream DPI panel bridge.

Important APIs and types: `struct tc358762` stores device, embedded `drm_bridge`, single `vddc` regulator, downstream panel bridge, optional reset GPIO, last mode, `pre_enabled` regulator-balance flag, and sticky transfer error. Important functions are `tc358762_probe()`, `tc358762_remove()`, `tc358762_parse_dt()`, `tc358762_pre_enable()`, `tc358762_enable()`, `tc358762_post_disable()`, `tc358762_init()`, `tc358762_write()`, and `tc358762_attach()`.

Control flow: probe allocates the bridge, stores driver data, hard-codes the DSI peripheral to one lane, RGB888, video sync-pulse, LPM, and HSE flags, resolves the downstream bridge from graph port 1, gets optional reset GPIO and `vddc`, sets bridge type to DPI, adds the bridge, and attaches to the DSI host. Atomic pre-enable enables the regulator and deasserts reset with a short delay, then marks `pre_enabled`. Atomic enable writes DSI/PPI lane setup, SIPO counters, LPX timing, SPI command mode, LCD control based on stored mode polarity, system control, PPI start, and DSI start. Atomic post-disable guards against duplicate calls with `pre_enabled`, asserts reset low if present, then disables the regulator.

State and persistence: `mode` is copied in `mode_set` and used during initialization for HSYNC/VSYNC polarity. `ctx->error` accumulates the first failed generic write until `tc358762_clear_error()`. `pre_enabled` prevents regulator imbalance when post-disable is repeated. Hardware configuration persists until reset or power removal.

Dependencies and integration: depends on DRM bridge atomic helpers, DRM OF panel bridge lookup, MIPI DSI generic write, regulator and optional GPIO consumers, and the `toshiba,tc358762` OF compatible. It is a DSI peripheral driver registered with `module_mipi_dsi_driver()`.

Risks: dual-lane support is explicitly TODO and the driver forces one lane. Most register values are fixed or described as guesswork based on TC358764, so unsupported panels or timings may fail. `regulator_enable()` failures are logged but pre-enable continues. Only write errors are tracked; there is no readback validation. Optional reset polarity and timing must match board wiring.

Test signals: probe with and without reset GPIO, DSI attach failure cleanup, regulator enable/disable balance over repeated modesets, panel enable producing visible DPI output, HSYNC/VSYNC polarity changes, generic write error injection, and one-lane DSI timing on target boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/tc358762.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/tc358764.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/tc358764.c

Purpose: DRM bridge and MIPI DSI driver for the Toshiba TC358764 DSI-to-LVDS bridge. It powers three regulators, toggles reset, configures a four-lane RGB888 burst-mode DSI receiver, initializes PPI/DSI/video/LVDS register blocks over MIPI DSI generic transfers, and attaches a downstream LVDS bridge or panel.

Important APIs and types: `struct tc358764` stores device, embedded `drm_bridge`, downstream `next_bridge`, regulator bulk array for `vddc`, `vddio`, and `vddlvds`, required reset GPIO, and sticky transfer error. Important functions are `tc358764_probe()`, `tc358764_remove()`, `tc358764_parse_dt()`, `tc358764_configure_regulators()`, `tc358764_pre_enable()`, `tc358764_post_disable()`, `tc358764_init()`, `tc358764_read()`, `tc358764_write()`, and `tc358764_attach()`.

Control flow: probe allocates the bridge, forces DSI settings to four lanes, RGB888, video burst, auto vertical, and LPM, gets the required reset GPIO, resolves graph port 1 to the downstream bridge, obtains the regulator bulk supplies, adds the bridge, then attaches to the DSI host. Pre-enable powers regulators, waits, resets the chip, and calls `tc358764_init()`. Initialization reads and logs `SYS_ID`, configures PPI timing and lane enables, starts PPI/DSI, sets the video path, resets/programs the LVDS PHY, resets the LCD block, writes LVDS bit mux mappings, and enables LVDS output. Post-disable resets the chip, waits, and disables regulators.

State and persistence: transfer failures persist in `ctx->error` until `tc358764_clear_error()`, causing later reads/writes in the same init sequence to be skipped. There is no stored display mode; timing programming is fixed. Hardware state persists until reset/power removal. Regulator and reset state are managed by bridge pre-enable/post-disable.

Dependencies and integration: depends on DRM bridge, DRM OF bridge lookup, MIPI DSI generic read/write, regulator bulk APIs, reset GPIO, and the `toshiba,tc358764` OF compatible. It is a MIPI DSI peripheral driver with a downstream bridge in the DRM bridge chain.

Risks: bridge ops use legacy `.pre_enable`/`.post_disable` signatures rather than atomic hooks, unlike newer bridge drivers. Reset GPIO is mandatory and uses non-cansleep `gpiod_set_value()`, so GPIO provider constraints matter. Initialization uses fixed LVDS mux, video-path, polarity, and PHY values with no mode-based timing programming. `tc358764_read()` logs the endian-converted address after `cpu_to_le16s()`, which can confuse debug output. Regulator enable errors are logged but initialization still proceeds.

Test signals: probe with all three supplies and reset GPIO, DSI attach failure cleanup, SYS_ID read success, visible LVDS output on a known panel, repeated enable/disable cycles checking regulator balance, generic transfer failure paths, reset timing validation, and bridge-chain attach to the downstream panel/bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/tc358764.c -->
