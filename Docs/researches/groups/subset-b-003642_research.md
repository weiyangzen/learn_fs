# Research Report: subset-b-003642

Grouped source-tree-aligned research for Meson DRM HDMI, DSI, CVBS, overlay, plane, AFBCD, RDMA, register, and video-clock files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.c

Purpose: Implements the platform glue driver for Amlogic Meson Synopsys DesignWare HDMI TX. It owns HDMI TOP register access, DesignWare controller register access, PHY setup, HPD interrupt handling, component bind/unbind, runtime state for reset/clock resources, and suspend/resume restoration.

Important APIs, types, and functions: `struct meson_dw_hdmi_data` abstracts SoC-specific TOP/DWC register access and PHY init values. `struct meson_dw_hdmi` stores DRM-private state, MMIO base, reset controls, `dw_hdmi` handle, bridge pointer, and last IRQ status. Register access helpers include legacy indirect `dw_hdmi_top_read/write()` and `dw_hdmi_dwc_read/write()` plus direct G12A variants. DRM/bridge entry points are `meson_dw_hdmi_bind()`, `meson_dw_hdmi_unbind()`, and platform `probe/remove`. PHY callbacks are exported through `meson_dw_hdmi_phy_ops`.

Control flow: probe only registers the component. During bind the driver resolves match data, enables optional HDMI regulator, gets reset lines and clocks, maps HDMITX MMIO, creates a regmap for the DW core, requests the shared threaded IRQ, runs `meson_dw_hdmi_init()`, then calls `dw_hdmi_probe()`. PHY init selects 4:2:0 mode when required by sink or bus format, programs TOP TMDS clock patterns, configures HHI PHY registers from pixel clock thresholds, resets PHY three times, briefly disables ENCI/ENCP video, restores HDMI write clock bits, and routes ENCI or ENCP into HDMI-TX.

State and persistence: mutable state is hardware-centric: HHI register programming, TOP interrupt masks/status, reset lines, enabled clocks, `irq_stat`, bridge references, and `priv->venc.hdmi_use_enci`. Suspend asserts TOP reset; resume reruns initialization and calls `dw_hdmi_resume()`. Clock resources are devm-managed with action cleanup.

Dependencies and integration points: depends on Linux component framework, reset/clock/regulator APIs, `regmap`, DRM bridge helpers, `dw_hdmi`, EDID/SCDC helpers, Meson DRM private `hhi` and `io_base`, and register definitions from `meson_dw_hdmi.h` and `meson_registers.h`. It integrates with the HDMI encoder bridge, which supplies VENC/VCLK setup and bus format decisions.

Risks: register access is protected by one global spinlock, but G12A direct accesses bypass it. PHY constants are SoC-specific magic values with limited validation. HPD interrupt top-half returns `IRQ_NONE` when only core interrupt bit is set, relying on DW core behavior. `of_drm_find_and_get_bridge()` result is stored after `dw_hdmi_probe()` and must be released on unbind. PLL/PHY/4:2:0 interactions are timing-sensitive and hardware-revision dependent.

Test signals: boot/probe on GXBB/GXL/GXM/G12A DT compatibles, HDMI HPD connect/disconnect events, EDID reads, 480i/576i ENCI modes, progressive ENCP modes, 4:2:0-only sinks, suspend/resume with display attached, and DRM debug traces for selected TMDS division and VENC source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.h

Purpose: Defines HDMI TOP block register offsets and interrupt/status bit masks used by the Meson DW-HDMI glue driver.

Important APIs, types, and functions: This header exports no functions or structs. Its public surface is a compact set of `#define`s for `HDMITX_TOP_SW_RESET`, `HDMITX_TOP_CLK_CNTL`, HPD filter and interrupt registers, BIST/shift-pattern controls, TMDS clock pattern registers, revocation memory status, and `HDMITX_TOP_STAT0`. Named interrupt masks include `HDMITX_TOP_INTR_CORE`, `HDMITX_TOP_INTR_HPD_RISE`, `HDMITX_TOP_INTR_HPD_FALL`, and G12A RxSense bits.

Control flow: The header has no execution path. It drives control flow in `meson_dw_hdmi.c` by naming registers touched during initialization, PHY TMDS pattern setup, HPD setup, interrupt clearing/masking, HPD polling, and TOP reset.

State and persistence: Register constants describe persistent HDMI TOP hardware state. `HDMITX_TOP_INTR_STAT_CLR` is write-one-to-clear, while `HDMITX_TOP_INTR_MASKN` is active-high unmask. `HDMITX_TOP_STAT0` reports filtered HPD/RxSense. `HDMITX_TOP_SW_RESET` bit comments document which sub-block resets persist until cleared.

Dependencies and integration points: Requires bit macros from normal Linux kernel headers included by consumers. Used directly by `meson_dw_hdmi.c`; the values are passed through either indirect TOP register access or direct G12A TOP MMIO offseting.

Risks: The header encodes hardware semantics in comments and constants; wrong bit polarity causes hard-to-debug HPD or reset failures. Some fields are G12A-specific while sharing the same register names, so consumers must keep compatible-specific behavior outside the header.

Test signals: HDMI initialization should clear `HDMITX_TOP_SW_RESET`, enable TOP clocks, install HPD filters, and observe HPD changes via `HDMITX_TOP_STAT0`. Interrupt tests should verify rise/fall bits are cleared and unmasked correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.c

Purpose: Provides the Meson platform glue for Synopsys DW MIPI-DSI on G12A-class SoCs. It maps the DSI TOP registers, owns the D-PHY, clocks, TOP reset, and supplies host/PHY callbacks to the generic `dw_mipi_dsi` bridge core.

Important APIs, types, and functions: `struct meson_dw_mipi_dsi` stores MMIO base, `phy`, D-PHY options, `dw_mipi_dsi` handle, attached `mipi_dsi_device`, current mode, bit/pixel clocks, and TOP reset. Key callbacks are `dw_mipi_dsi_phy_init()`, `dw_mipi_dsi_phy_power_on/off()`, `dw_mipi_dsi_get_lane_mbps()`, `dw_mipi_dsi_phy_get_timing()`, `meson_dw_mipi_dsi_host_attach()`, and `host_detach()`.

Control flow: platform probe allocates state, maps registers, gets the D-PHY and enabled bit/px clocks, toggles the TOP reset, fills `dw_mipi_dsi_plat_data`, and calls `dw_mipi_dsi_probe()`. Attach validates RGB888/RGB666, initializes the PHY, and resets/enables TOP clock/memory. The DW core asks for lane Mbps, timing, and escape clock; PHY init then sets bit clock to computed HS rate, takes an exclusive rate lock, resets the pixel clock to mode clock, configures DPI/VENC color mode, and calls `phy_configure()`.

State and persistence: `mipi_dsi->mode` is captured during lane-rate calculation and later reused by timing and clock setup, so ordering with the DW core matters. `dsi_device` persists between host attach/detach. `clk_rate_exclusive_get()` is released only on PHY power-off. TOP reset, clock enable, memory power, and color mux registers persist until reprogrammed or reset.

Dependencies and integration points: Integrates with `dw_mipi_dsi`, MIPI DSI host attach semantics, Linux PHY and CCF clock APIs, `meson_dw_mipi_dsi.h` register definitions, and `meson_encoder_dsi.c`, which configures ENCL/VENC for the panel mode.

Risks: Failure after `clk_rate_exclusive_get()` but before power-off can leave exclusivity held. Pixel format support is intentionally narrow. Timing values are keyed to a few `hdisplay` widths, so new panels may need tuning. Probe defers early `-EIO` bit-clock failures.

Test signals: G12A DT probe, panel attach/detach, RGB888 and RGB666 panels, lane-rate and D-PHY timing validation, clock-rate changes visible through CCF, and successful display enable via the DSI encoder bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.h

Purpose: Defines Meson MIPI-DSI TOP register offsets, reset/clock bits, DPI/VENC color mode fields, component selectors, and status/interrupt registers for the DW MIPI-DSI glue driver.

Important APIs, types, and functions: No functions or structs are exported. Important constants include `MIPI_DSI_TOP_SW_RESET`, reset bits for DWC/intr/DPI/timing, `MIPI_DSI_TOP_CLK_CNTL`, `MIPI_DSI_TOP_CNTL`, `VENC_IN_COLOR_*`, `DPI_COLOR_*`, `MIPI_DSI_TOP_*` field masks, status/measurement registers, interrupt control/status, and `MIPI_DSI_TOP_MEM_PD`.

Control flow: The consumer toggles software reset bits, enables sysclk/pixclk, clears memory power-down, and writes `MIPI_DSI_TOP_CNTL` after selecting DSI pixel format in `dw_mipi_dsi_phy_init()`.

State and persistence: Constants define latched TOP-level DSI configuration: reset state, manual/automatic halt settings, DPI format, VENC data width, component ordering, sync polarity, and memory power. The header also documents interrupt status/clear layout, though the current driver does not request or service DSI TOP interrupts.

Dependencies and integration points: Used by `meson_dw_mipi_dsi.c` with Linux `FIELD_PREP()` and bit macros. It bridges generic MIPI pixel formats to Meson hardware color-mode values.

Risks: Field layout comments include active-reset semantics where names can be misleading, so the driver must write matching assert/deassert sequences. Unused interrupt and measurement constants may lag hardware behavior if future interrupt handling is added.

Test signals: TOP reset pulse should leave DWC/DPI/timing blocks released, `MIPI_DSI_TOP_CLK_SYSCLK_EN` and `PIXCLK_EN` should be set, and RGB888/RGB666 formats should map to expected `DPI_COLOR_*` and `VENC_IN_COLOR_*` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_mipi_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.c

Purpose: Implements the Meson DRM CVBS encoder bridge and simple DRM encoder for composite analog output. It exposes PAL and NTSC modes, validates them, configures ENCI timings and VCLK2, powers the VDAC, and attaches a downstream connector bridge.

Important APIs, types, and functions: `struct meson_encoder_cvbs` owns a `drm_encoder`, a Meson bridge, and `meson_drm *priv`. `meson_cvbs_modes[]` defines PAL `720x576i` and NTSC `720x480i` modes with ENCI mode descriptors. Bridge callbacks include `attach`, `get_modes`, `mode_valid`, `atomic_check`, `atomic_enable`, and `atomic_disable`. Public entry points are `meson_encoder_cvbs_probe()` and `meson_encoder_cvbs_remove()`.

Control flow: probe finds graph port 0 remote connector bridge, creates a DRM bridge of type Composite, initializes a TVDAC encoder, attaches bridge and bridge-connector, and stores the encoder in `priv->encoders[MESON_ENC_CVBS]`. Atomic enable finds the active connector/CRTC state, maps adjusted mode to one of the two CVBS definitions, programs ENCI via `meson_venci_cvbs_mode_set()`, sets VCLK2 to 27 MHz through `meson_vclk_setup()`, selects VDAC0 source, then writes SoC-specific VDAC HHI registers. Atomic disable powers down VDAC.

State and persistence: The file does not maintain mode state beyond DRM object lifetime. Hardware state persists in ENCI, VCLK2, VDAC selection, and HHI VDAC control registers until disabled or overwritten. The bridge is removed on `remove`; devm allocation handles memory lifetime.

Dependencies and integration points: Depends on DRM bridge/connector helpers, OF graph, `meson_venc` ENCI mode data, `meson_vclk`, and `meson_registers.h`. It shares the same CRTC/VIU pipeline as HDMI/DSI but targets analog ENCI/VDAC output.

Risks: Only two fixed modes are supported. Mode matching is strict on timings, clock, flags, and 3D flags, so userspace modelines must match exactly. VDAC register constants are SoC-specific and differ on G12A. Missing connector bridge returns success with no CVBS output, which is expected for disabled hardware but can hide DT issues.

Test signals: `modetest` should list only PAL/NTSC composite modes. Atomic commits for both modes should enable ENCI and VDAC. Disable should zero the G12A VDAC controls or set legacy `HHI_VDAC_CNTL1` to 8. Probe deferral should occur if the connector bridge is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.h

Purpose: Declares the CVBS mode descriptor, fixed supported-mode count, global mode table, and probe/remove hooks for the Meson composite encoder.

Important APIs, types, and functions: `struct meson_cvbs_mode` pairs an ENCI hardware mode descriptor with a DRM display mode. `MESON_CVBS_MODES_COUNT` is fixed at 2. The header exports `meson_cvbs_modes[]`, `meson_encoder_cvbs_probe()`, and `meson_encoder_cvbs_remove()`.

Control flow: No runtime control flow exists in the header. Consumers call probe/remove from the main Meson DRM driver and inspect `meson_cvbs_modes[]` for supported composite modes.

State and persistence: The table declared here is defined in `meson_encoder_cvbs.c` and represents static driver-supported state, not dynamically learned hardware state.

Dependencies and integration points: Includes `meson_drv.h` and `meson_venc.h` so the descriptor can reference `struct meson_drm`, `struct drm_display_mode`, and `struct meson_cvbs_enci_mode`.

Risks: The fixed count must stay synchronized with the array definition. The include guard name references VENC/CVBS rather than encoder/CVBS, so future renames should avoid duplicate guards.

Test signals: Build coverage should catch mismatched table count and missing `struct meson_cvbs_enci_mode`. Runtime output should expose exactly `MESON_CVBS_MODES_COUNT` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_cvbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.c

Purpose: Implements the Meson-side DSI encoder bridge. It connects the DRM encoder to the DW MIPI-DSI bridge/panel chain and programs the ENCL VENC path during atomic enable/disable.

Important APIs, types, and functions: `struct meson_encoder_dsi` wraps a `drm_encoder`, a Meson bridge, and `meson_drm *priv`. Bridge callbacks are `attach`, `atomic_enable`, and `atomic_disable`, with standard atomic state helpers. Public functions are `meson_encoder_dsi_probe()` and `meson_encoder_dsi_remove()`.

Control flow: probe allocates a bridge, finds graph port 2 remote DSI transceiver, resolves the downstream bridge, adds the Meson DSI bridge, initializes a simple DSI encoder, attaches the bridge chain, and stores it in `priv->encoders[MESON_ENC_DSI]`. Atomic enable obtains new connector and CRTC state, calls `meson_venc_mipi_dsi_mode_set()` for adjusted mode, loads ENCL gamma, disables ENCL video, enables ENCL FIFO mode, disables test output, disables OSD1 matrix wrapping, then enables ENCL video. Disable turns off ENCL and re-enables OSD1 matrix bit 0.

State and persistence: The driver persists only DRM object references; hardware state persists in ENCL registers and `VPP_WRAP_OSD1_MATRIX_EN_CTRL`. It relies on the clock framework and DSI bridge for DSI pixel/bit clock programming rather than direct VCLK setup.

Dependencies and integration points: Depends on DRM bridge/simple-KMS helpers, OF graph, `meson_venc`, `meson_vclk` includes, and register definitions. It is paired with `meson_dw_mipi_dsi.c`, which handles DW host/PHY details and panel attachment.

Risks: No explicit mode validation is implemented here; validation is delegated to bridge/panel and VENC helpers. Missing remote DSI bridge logs an error but returns 0, allowing systems without DSI. The matrix enable/disable side effect is specific and could interact with other output paths if multiple encoders were active.

Test signals: DT graph with DSI panel should produce bridge chain `encoder -> dsi encoder -> dw-mipi-dsi -> panel`. Atomic enable should program ENCL and show panel output. Disable should blank ENCL and restore matrix control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.h

Purpose: Declares the DSI encoder lifecycle hooks used by the main Meson DRM driver.

Important APIs, types, and functions: Exports `meson_encoder_dsi_probe(struct meson_drm *priv)` and `meson_encoder_dsi_remove(struct meson_drm *priv)`. It relies on `struct meson_drm` being visible before or through included driver context.

Control flow: No direct control flow exists. The main driver calls probe during DRM device setup and remove during teardown.

State and persistence: The header defines no state. State is held privately in `meson_encoder_dsi.c` and in `priv->encoders[MESON_ENC_DSI]`.

Dependencies and integration points: Minimal internal header for the Meson DRM encoder registry. It intentionally hides `struct meson_encoder_dsi` internals.

Risks: Because the header does not include `meson_drv.h` or forward declare `struct meson_drm`, callers must already have the type declared. That is acceptable in current local include order but can be fragile if reused standalone.

Test signals: Compile coverage from main driver inclusion is the main signal; runtime signals live in `meson_encoder_dsi.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.c

Purpose: Implements the Meson HDMI encoder bridge that sits before the DW-HDMI transceiver bridge. It validates HDMI modes against VENC and VCLK capabilities, selects output bus format, programs VENC/VCLK/format muxing on atomic enable, creates the HDMI bridge connector, and manages CEC notifier physical address updates.

Important APIs, types, and functions: `struct meson_encoder_hdmi` stores encoder, bridge, connector, `meson_drm *priv`, selected `output_bus_fmt`, and CEC notifier. Bridge callbacks include `attach`, `detach`, `mode_valid`, `hpd_notify`, `atomic_enable`, `atomic_disable`, `atomic_get_input_bus_fmts`, and `atomic_check`. Public hooks are `meson_encoder_hdmi_probe()` and `remove()`.

Control flow: probe finds graph port 1 remote DW-HDMI bridge, adds a Meson HDMI bridge, initializes a TMDS encoder, attaches the bridge without creating a connector, creates a bridge connector, resets connector state, attaches HDR metadata when supported, attaches max-bpc 8..8, enables 4:2:0, and registers a CEC notifier against the remote platform device. Atomic check records negotiated output bus format and marks mode changed on HDR metadata changes. Mode validation rejects unsupported TMDS/sink combinations, checks CEA VIC modes with `meson_venc_hdmi_supported_vic()` and `meson_vclk_vic_supported_freq()`, or DMT modes with `meson_venc_hdmi_supported_mode()` and `meson_vclk_dmt_supported_freq()`. Enable programs VENC HDMI mode, VCLK, VPU HDMI format control, and ENCI/ENCP enable.

State and persistence: `output_bus_fmt` persists between atomic check and enable. Connector state carries HDR metadata and 4:2:0 allowance. Hardware state persists in VENC, VCLK, `VPU_HDMI_FMT_CTRL`, `VPU_HDMI_SETTING`, and ENCI/ENCP enable bits. CEC notifier persists until detach.

Dependencies and integration points: Depends on DRM bridge connector, media bus formats, CEC notifier, OF graph/platform lookup, `meson_venc`, `meson_vclk`, and DW-HDMI bridge HPD/EDID callbacks.

Risks: 4:2:0 selection is split between display capability, negotiated bus format, and DW-HDMI PHY setup. CEC physical address is currently set by reading EDID in HPD notify, with an inline FIXME about better use of connector display info. Max bpc is constrained to 8. Probe error paths release the DT node but CEC `put_device()` is only called on notifier allocation failure.

Test signals: HDMI mode lists for CEA and DMT modes, 4:2:0-only sink validation, HDR metadata property causing mode_changed, HPD notifications updating CEC physical address, ENCI path for 480i/576i, ENCP path for progressive/HD interlace, and disable clearing HDMI routing plus ENCI/ENCP enables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.h

Purpose: Declares the HDMI encoder probe/remove functions used by the Meson DRM device setup and teardown paths.

Important APIs, types, and functions: Exports `meson_encoder_hdmi_probe(struct meson_drm *priv)` and `meson_encoder_hdmi_remove(struct meson_drm *priv)`.

Control flow: No local execution. It is a private module boundary between the main Meson DRM driver and the HDMI encoder implementation.

State and persistence: No state is declared here. The implementation stores the encoder object in `priv->encoders[MESON_ENC_HDMI]` and maintains connector/CEC state privately.

Dependencies and integration points: Like the DSI header, it assumes `struct meson_drm` is declared by including context. It keeps HDMI internals opaque to the rest of the driver.

Risks: Standalone inclusion without a prior `struct meson_drm` declaration would fail. Any future consumer outside the current Meson DRM include order should add a forward declaration or include `meson_drv.h`.

Test signals: Build coverage and successful main-driver invocation of probe/remove are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_encoder_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.c

Purpose: Implements AFBC decoder operation tables for Meson OSD primary-plane compressed framebuffers. It supports the Amlogic GXM AFBC 1.0 decoder and the ARM Mali AFBC decoder on G12A, translating DRM modifiers/formats and staged plane state into decoder register programming.

Important APIs, types, and functions: Exports `meson_afbcd_gxm_ops` and `meson_afbcd_g12a_ops` as `struct meson_afbcd_ops`. GXM helpers include pixel-format validation, reset, enable/disable, and setup for OSD1_AFBCD registers. G12A helpers include pixel-format, bits-per-pixel, block-mode mapping, RDMA-backed reset/init/enable/setup, and format support checks.

Control flow: Plane update sets `priv->afbcd.modifier`, `format`, OSD size/address, and then the broader VIU commit path can call these ops. GXM setup writes mode flags, input size, header/frame/chroma pointers, line-buffer length, and pixel scopes directly. G12A init allocates/sets up RDMA and asserts manual reset. G12A setup queues format specifier, buffer dimensions, bounding box, output internal address, and output stride through `meson_rdma_writel_sync()`. G12A enable masks AFBC IRQs, enables surface 0, issues direct swap, and flushes RDMA so writes replay on VSYNC.

State and persistence: Uses `priv->afbcd` for modifier/format and `priv->viu` for width, height, and framebuffer DMA address. G12A owns `priv->rdma` coherent descriptor state while active. Hardware state persists in AFBCD/MAFBC registers and, on G12A, in the RDMA channel trigger list.

Dependencies and integration points: Depends on DRM fourcc AFBC modifier definitions, `meson_plane.c` modifier checks, `meson_rdma`, and register constants from `meson_registers.h`. G12A decoded output goes to fixed internal address `MESON_G12A_AFBCD_OUT_ADDR` from the header and is consumed by OSD unpacking.

Risks: GXM supports only XBGR/ABGR RGB32 with YTR and no 32x8 blocks. G12A rejects YTR on non-XBGR formats and leaves YUV support as TODO. Several magic register values are undocumented. G12A RDMA buffer overflow is only warned once by RDMA helper. Fixed internal output address must match hardware expectations and not normal memory.

Test signals: AFBC primary-plane scanout on GXM and G12A, modifier rejection for unsupported YTR/block combinations, visual validation of RGB565/RGB888/XRGB/ARGB/XBGR/ABGR on G12A, VSYNC-synchronized AFBC updates, and decoder reset/disable on plane disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.h

Purpose: Defines the internal AFBCD operation interface and G12A decoded-output address used by Meson OSD AFBC support.

Important APIs, types, and functions: `MESON_G12A_AFBCD_OUT_ADDR` is the hardware-internal buffer address used to transfer decoded pixels from the ARM AFBC decoder to VIU/OSD. `struct meson_afbcd_ops` contains callbacks for `init`, `exit`, `reset`, `enable`, `disable`, `setup`, optional `fmt_to_blk_mode`, and `supported_fmt`. It exports `meson_afbcd_gxm_ops` and `meson_afbcd_g12a_ops`.

Control flow: The main driver selects one ops table by SoC family, planes call support functions during format/modifier validation, and commit/disable paths call setup/enable/reset/disable through this vtable.

State and persistence: The header defines interface shape only. Callback implementations use `struct meson_drm` to read staged plane state and write persistent decoder hardware registers.

Dependencies and integration points: Includes `meson_drv.h` for `struct meson_drm`. Integrated by `meson_plane.c`, `meson_osd_afbcd.c`, and likely the main VIU commit code.

Risks: The fixed G12A output address is not memory allocated by this driver; misuse outside the intended hardware path would be dangerous. `fmt_to_blk_mode` is optional and must be NULL-checked or used only with ops that provide it.

Test signals: Compile-time conformance of both ops tables and runtime primary-plane AFBC enable/disable on GXM/G12A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_osd_afbcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.c

Purpose: Implements the Meson video overlay plane backed by the VD1 video path. It supports multiple YUV packed/planar formats plus Amlogic FBC-only YUV420 modifiers, computes crop/scale windows, stages canvas/DMA/AFBC state, and creates the immutable zpos overlay plane.

Important APIs, types, and functions: `struct meson_overlay` wraps `drm_plane` and `meson_drm *priv`. Core callbacks are `meson_overlay_atomic_check()`, `atomic_update()`, `atomic_disable()`, and `format_mod_supported()`. Helpers include `fixed16_to_int()`, `meson_overlay_get_vertical_phase()`, and `meson_overlay_setup_scaler_params()`.

Control flow: atomic check delegates to `drm_atomic_helper_check_plane_state()` with 1/5 to 5x scaling, clipping, and visibility enabled. Atomic update locks `event_lock`, classifies the framebuffer as Amlogic FBC or linear, stages AFBC decode mode/default color/chroma formatting or VD1 IF0 settings, computes scaler and crop scopes, programs format-specific canvas/color-map/chroma subsampling fields, records DMA addresses/strides/heights for up to three planes, computes AFBC header/body addresses, and marks `vd1_enabled`. Disable clears VD1 blend/source registers on G12A or VPP pre/postblend bits on older SoCs.

State and persistence: The plane writes mostly into `priv->viu`, not directly to all hardware registers. This makes atomic update a staging step consumed by the VIU commit path. Direct writes are used for disable. AFBC body/header state is derived from GEM DMA address, pitch, height, modifier layout, and memory-saving/scatter mode.

Dependencies and integration points: Depends on DRM atomic/fb DMA/GEM helpers, Meson VIU/VPP register constants, canvas IDs in `meson_drm`, and the main VIU update path. It is separate from ARM AFBCD primary-plane support; this overlay supports Amlogic FBC modifiers for YUV420-specific video decode paths.

Risks: Crop-axis additions appear easy to confuse because vertical start/end later add `crop_left` and horizontal adds `crop_top`; this deserves regression attention. Interlaced input is explicitly TODO and treated like progressive input. AFBC size math assumes known Amlogic layouts and block sizes. Register staging under `event_lock` requires the consumer path to follow the same locking expectations.

Test signals: atomic scaling/clipping tests, YUYV/NV12/NV21/YUV444/422/420/411/410 scanout, Amlogic FBC basic/scatter with and without memory saving, multi-plane DMA address correctness, interlaced CRTC mode behavior, and disable clearing VD1 on both G12A and legacy VPP paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.h

Purpose: Declares overlay plane creation for the Meson DRM driver.

Important APIs, types, and functions: Exports `meson_overlay_create(struct meson_drm *priv)`.

Control flow: The main driver calls create during DRM device initialization. The implementation allocates and registers a DRM universal overlay plane, assigns helper callbacks, sets immutable zpos, and stores it in `priv->overlay_plane`.

State and persistence: No state is declared in the header. Plane state lives in `meson_overlay.c`, DRM plane state, and staged `priv->viu` fields.

Dependencies and integration points: Includes `meson_drv.h` for private driver structures. The function integrates the VD1 overlay into the KMS plane list.

Risks: Minimal header risk. Any future multiple-overlay support would require changing the single create API and `priv->overlay_plane` assumption.

Test signals: Successful DRM plane enumeration with `"meson_overlay_plane"` after `meson_overlay_create()` returns 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_overlay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.c

Purpose: Implements the primary OSD1 DRM plane for Meson. It validates primary-plane scaling, supports RGB formats with linear and SoC-specific ARM AFBC modifiers, stages OSD/scaler/blend/canvas state, and coordinates with AFBCD ops when compressed scanout is used.

Important APIs, types, and functions: `struct meson_plane` wraps `drm_plane`, private pointer, and enabled flag. Main callbacks are `meson_plane_atomic_check()`, `atomic_update()`, `atomic_disable()`, and `format_mod_supported()`. Helpers include `meson_g12a_afbcd_line_stride()` and `fixed16_to_int()`. Public constructor is `meson_plane_create()`.

Control flow: atomic check allows upscaling up to 5x and no downscaling (`DRM_PLANE_NO_SCALING`) while requiring final coordinates. Update locks `event_lock`, decides whether ARM AFBC is required on GXM/G12A, configures OSD control/global alpha/canvas/endian/path bits, selects block mode and color matrix from DRM format, configures alpha replacement, computes OSD scaler registers for interlaced/progressive output, fills source/destination windows, sets G12A blend scopes, records DMA address/stride/height/width, updates AFBCD modifier/format/stride when needed, resets OSD1 before first enable on GXM/GXL, and marks `osd1_enabled`. Disable resets/disables AFBCD if present and clears OSD1 blend source.

State and persistence: Most hardware programming is staged in `priv->viu` and later committed by the VIU path. Plane-local `enabled` gates first-enable reset. AFBC details persist in `priv->afbcd`. Direct disable writes alter live VPP/OSD blend registers.

Dependencies and integration points: Uses DRM atomic/GEM DMA/fourcc helpers, `meson_osd_afbcd` ops, `meson_viu` reset helper, and register definitions. Modifier support depends on selected SoC compatibility and selected `priv->afbcd.ops`.

Risks: `drm_universal_plane_init()` return is checked but helper/property calls after success are not. AFBC modifier validation relies on bitmask comparison and the plane modifier list. G12A AFBC output stride math supports only currently accepted RGB formats. Interlace scaler handling is complex and should be visually tested.

Test signals: primary plane enumeration, RGB565/RGB888/XRGB/ARGB/XBGR/ABGR linear scanout, AFBC modifier acceptance/rejection on GXBB/GXL/GXM/G12A, alpha replacement behavior, interlaced output field positioning, first-enable reset on GXM/GXL, and disable resetting AFBCD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.h

Purpose: Declares primary plane creation for the Meson DRM driver.

Important APIs, types, and functions: Exports `meson_plane_create(struct meson_drm *priv)`.

Control flow: The main DRM initialization path calls create to allocate and register the OSD1 primary plane, choose modifier list by SoC family, install plane helpers, and store the result in `priv->primary_plane`.

State and persistence: No header state. The implementation stores runtime plane state in DRM plane state, a private `enabled` flag, and staged `priv->viu`/`priv->afbcd` fields.

Dependencies and integration points: Includes `meson_drv.h`. Provides a small internal API between the main driver and the OSD primary-plane implementation.

Risks: The API assumes one primary plane. Future multi-OSD primary/overlay support would require expanding the function signature or creating additional constructors.

Test signals: Compile and runtime KMS plane enumeration with `"meson_primary_plane"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.c

Purpose: Provides a small Register DMA helper for Meson VPU register writes. It builds a coherent descriptor buffer of register/value pairs and configures RDMA channel 1 to replay them on VSYNC, used primarily by G12A AFBCD updates.

Important APIs, types, and functions: Public functions are `meson_rdma_init()`, `meson_rdma_free()`, `meson_rdma_setup()`, `meson_rdma_stop()`, `meson_rdma_reset()`, `meson_rdma_writel_sync()`, and `meson_rdma_flush()`. Internal `meson_rdma_writel()` appends register/value pairs. Descriptors are two `u32`s, with a single 4 KiB buffer.

Control flow: init allocates a coherent page if absent, resets offset, resets/configures RDMA control. setup marks channel 1 as write, no address increment. `writel_sync()` appends the pair and writes immediately to hardware, so current state changes now and is also replayable later. flush stops channel 1, writes DMA start/end addresses for the filled buffer, sets channel 1 trigger to VSYNC, and clears the offset for the next batch. free stops and releases coherent memory.

State and persistence: State is `priv->rdma.addr`, DMA address, and offset. Hardware state includes RDMA control, access-auto trigger mode, IRQ clear bits, and channel start/end addresses. After flush, the hardware can replay the just-built sequence on every VSYNC until stopped or reconfigured.

Dependencies and integration points: Uses Linux DMA coherent allocation, `meson_registers.h` RDMA constants, and `priv->io_base`. G12A AFBCD calls init/setup/writel_sync/flush/reset/free.

Risks: Buffer overflow is handled by a `dev_warn_once()` and dropped writes, which can leave an incomplete replay sequence. No locking is present; callers must serialize access. `meson_rdma_flush()` assumes offset is non-zero when computing end address. The implementation uses only channel 1 and does not service RDMA IRQs.

Test signals: G12A AFBCD setup should allocate one page, write immediate MAFBC registers, and replay them on VSYNC. Stress tests should verify no overflow for the current register sequence and that reset/free stop channel 1 cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.h

Purpose: Declares the Meson VPU Register DMA helper API.

Important APIs, types, and functions: Exports lifecycle functions `meson_rdma_init()`, `meson_rdma_free()`, setup/control functions `meson_rdma_setup()`, `meson_rdma_reset()`, `meson_rdma_stop()`, and write/commit functions `meson_rdma_writel_sync()` and `meson_rdma_flush()`.

Control flow: Callers initialize, set up access mode, queue synchronous register writes, flush to start VSYNC replay, and stop/reset/free during teardown or disable.

State and persistence: No state is declared in the header; all state lives in `priv->rdma` and RDMA hardware registers.

Dependencies and integration points: Includes `meson_drv.h` for `struct meson_drm`. Used by G12A AFBCD and can be reused by other Meson display blocks that need synchronized register programming.

Risks: The API does not expose locking or capacity, so callers must know that the implementation has one small channel-1 buffer. Misuse from multiple subsystems would interleave descriptors.

Test signals: Compile coverage plus runtime G12A AFBCD operation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_registers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_registers.h

Purpose: Central Meson DRM VPU register map and bitfield header. It names register offsets for VPP, VIU, OSD, VD input, VENC, HDMI routing, RDMA, gamma/TCON/LCD, AFBC decoders, blend units, and memory arbitration, and provides `_REG()` and `writel_bits_relaxed()` helpers.

Important APIs, types, and functions: `_REG(reg)` converts Meson register numbers to byte offsets by shifting left by two. `writel_bits_relaxed(mask, val, addr)` performs a read-modify-write. The remainder is macro definitions: VPP/VPP2 scaling/blend/color registers, VIU OSD/VD registers, matrix/HDR registers, AFBC and MAFBC registers, ENCI/ENCP/ENCL/ENCT encoder timing registers, VPU mux/HDMI setting bits, RDMA registers/control bits, LCD/gamma/TCON registers, and G12A blend-source controls.

Control flow: No runtime flow in the header, but it controls almost every MMIO access in this subset. Encoder files use ENCI/ENCP/ENCL/VPU HDMI constants, plane/overlay files use OSD/VD/VPP/blend constants, AFBCD uses OSD1_AFBCD and VPU_MAFBC constants, and RDMA uses channel register constants.

State and persistence: All macros represent persistent hardware state. Many registers are write-once-until-mode-change, while interrupt/status/reset registers have side effects. `writel_bits_relaxed()` is non-atomic with respect to concurrent MMIO users unless callers serialize externally.

Dependencies and integration points: Includes `<linux/io.h>` and assumes Linux bit macros are available through consumers. It is the source of truth for register numbers shared across Meson DRM modules.

Risks: A wrong offset or bit definition affects hardware globally. Duplicate numeric aliases exist for hardware overlays, such as `VPU_HDMI_FMT_CTRL` and `VPU_VDIN_ASYNC_HOLD_CTRL`, requiring context-aware use. The read-modify-write helper can race if used on registers touched by interrupt handlers or other display paths. The file is large and includes blocks not used by this subset, so changes should be scoped carefully.

Test signals: Broad hardware smoke tests are needed: primary/overlay scanout, HDMI/CVBS/DSI output, scaling, AFBC decode, RDMA replay, suspend/resume, and SoC-specific register paths. Compile-time references catch only spelling, not semantic bit errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.c

Purpose: Implements Meson video clock programming for CVBS, HDMI CEA/VIC modes, and HDMI DMT modes. It configures HDMI PLL parameters, VID PLL fractional divider, VCLK/VCLK2 dividers and gates, ENCI/ENCP/VDAC/HDMI clock selection, and mode-frequency validation.

Important APIs, types, and functions: Exported APIs are `meson_vclk_dmt_supported_freq()`, `meson_vclk_vic_supported_freq()`, and `meson_vclk_setup()`. Important helpers include `meson_vid_pll_set()`, `meson_venci_cvbs_clock_config()`, `meson_hdmi_pll_set_params()`, `meson_hdmi_pll_find_params()`, `meson_hdmi_pll_generic_set()`, `meson_vclk_freqs_are_matching_param()`, and `meson_vclk_set()`. `params[]` is the table of supported HDMI clock topologies.

Control flow: CVBS setup programs a fixed 1.485 GHz HDMI PLL, VID PLL `/1`, VCLK2 divider for 27 MHz, VCLK2 gates, ENCI and VDAC clock selects. DMT validation/generation computes generic PLL parameters for pixel clock times ten. VIC validation compares requested PHY/VCLK frequencies against the supported table, including 1000/1001 variants and SoC package limits. HDMI setup selects a matching table row, derives HDMI-TX and VENC divisors, accounts for ENCI/DDR/YUV420 alternatives, sets HDMI system clock, HDMI PLL, VID PLL divider, VCLK divider, HDMI-TX pixel clock source, VENC source, and enables the relevant gates.

State and persistence: Programming persists in HHI PLL, divider, mux, reset, and gate registers. The function does not keep software state except through debug output and `priv->limits` checks. PLL lock polling waits until hardware reports lock, including an unbounded G12A retry loop.

Dependencies and integration points: Depends on `regmap`, `meson_vpu_is_compatible()`, SoC compatibility flags, DRM mode status values, and consumers in HDMI/CVBS encoders. HDMI encoder calculates `phy_freq`, `vclk_freq`, `venc_freq`, and HDMI pixel/dac frequencies, then calls this module.

Risks: Clock tables are finite and reject unsupported but potentially valid modes. PLL magic constants are SoC-specific and empirically bounded. G12A PLL lock loop can spin indefinitely if hardware never locks. DMT generic path logs fatal errors but cannot recover beyond returning from setup. 10-bit 2K/4K support is explicitly missing.

Test signals: `mode_valid` outcomes for CEA modes, DMT modelines, 1000/1001 refresh variants, SoC max PHY limits, CVBS 27 MHz output, HDMI 27/74.25/148.5/297/594 MHz paths, YUV420 4K modes, and PLL lock behavior on GXBB/GXL/GXM/G12A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.h

Purpose: Declares the Meson video-clock programming and validation API used by encoder code.

Important APIs, types, and functions: Defines target IDs `MESON_VCLK_TARGET_CVBS`, `MESON_VCLK_TARGET_HDMI`, and `MESON_VCLK_TARGET_DMT`, plus `MESON_VCLK_CVBS` as 27 MHz. Exports `meson_vclk_dmt_supported_freq()`, `meson_vclk_vic_supported_freq()`, and `meson_vclk_setup()`.

Control flow: HDMI mode validation calls the supported-frequency helpers before accepting modes. CVBS and HDMI atomic-enable paths call `meson_vclk_setup()` with a target and computed clock frequencies. The implementation chooses fixed CVBS, table-driven HDMI VIC, or generic DMT programming.

State and persistence: The header has no state. The implementation writes persistent HHI PLL/divider/gate state.

Dependencies and integration points: Includes `<drm/drm_modes.h>` for `enum drm_mode_status` and forward declares `struct meson_drm`. It is consumed by HDMI and CVBS encoders and potentially any future Meson encoder needing VCLK programming.

Risks: Callers must pass frequencies in Hz and a coherent set of PHY/VCLK/VENC/DAC values; wrong units or mismatched divisors can produce invalid clock programming. The `target` is an untyped unsigned int, so invalid values are only handled by falling into HDMI logic.

Test signals: Compile coverage for encoder callers and runtime validation that CVBS/HDMI modes call the expected target with accepted frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vclk.h -->
