# Research group subset-b-003640

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_gamma.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_gamma.c

### Purpose

`mtk_disp_gamma.c` implements the MediaTek DISP_GAMMA DDP component. It owns gamma LUT programming, optional dithering setup, enable/disable sequencing, clock control, platform capability data, and component registration for gamma blocks on MT8173, MT8183, and MT8195-class display pipelines.

### Important APIs, types, and functions

The main state is `struct mtk_disp_gamma`, which stores the MMIO base, component clock, CMDQ client register, and `struct mtk_disp_gamma_data`. Platform data describes whether dithering exists, whether odd LUT entries are differential, LUT bank size, total LUT size, and LUT bit depth.

External DDP-facing functions are `mtk_gamma_clk_enable()`, `mtk_gamma_clk_disable()`, `mtk_gamma_get_lut_size()`, `mtk_gamma_set()`, `mtk_gamma_config()`, `mtk_gamma_start()`, and `mtk_gamma_stop()`. Probe/remove are `mtk_disp_gamma_probe()` and `mtk_disp_gamma_remove()`, exported through `mtk_disp_gamma_driver`.

### Control flow

Probe allocates private state, obtains the unnamed gamma clock, maps register resource 0, optionally obtains the CMDQ client register, attaches match data, stores drvdata, and registers as a component. Bind and unbind are empty because the operational hooks are called through the DDP component abstraction.

Mode setup calls `mtk_gamma_config()`, which programs `DISP_GAMMA_SIZE` through `mtk_ddp_write()` and, on dither-capable platforms, delegates common dither fields to `mtk_dither_set_common()`. `mtk_gamma_set()` is called with the CRTC state gamma blob: it selects LUT data mode and bank, converts DRM 16-bit LUT entries down to 10 or 12 hardware bits, optionally encodes differential odd entries, writes LUT RAM, sets rising/descending LUT type on non-dither hardware, enables the LUT, and disables relay mode. Start/stop write `DISP_GAMMA_EN`.

### State and persistence behavior

Software state is devm-managed and persists for the platform device lifetime. Hardware state persists in MMIO registers: size, dither configuration, relay mode, LUT enable/type, bank selector, and LUT RAM contents. LUT writes are direct `writel()` operations, not CMDQ queued, so gamma table updates are immediate relative to CPU execution. Size and dither changes may be synchronized by CMDQ when a packet is supplied.

### Dependencies

The file depends on Linux clock, component, platform, OF, bitfield, and CMDQ APIs, DRM color LUT helpers, and MediaTek local headers `mtk_crtc.h`, `mtk_ddp_comp.h`, `mtk_disp_drv.h`, and `mtk_drm_drv.h`. Dithering is provided by shared MediaTek display helpers, and register writes use both raw MMIO and `mtk_ddp_write()`.

### Integration points

The gamma component appears in SoC display paths in `mtk_drm_drv.c` and is initialized through `mtk_ddp_comp_init()`. CRTC gamma property sizing is driven by `mtk_gamma_get_lut_size()`. Atomic modeset and plane/color-management code call the config, start, stop, clock, and LUT hooks through DDP component function tables.

### Risks

The 12-bit layout writes red/green to `DISP_GAMMA_LUT` and blue to `DISP_GAMMA_LUT1`; using the wrong layout or bank size corrupts colors. Differential LUT mode subtracts previous entries without monotonic validation, so unexpected descending or non-monotonic LUTs can underflow before extraction. `mtk_gamma_lut_is_descending()` is called with `lut_size - 1`, which intentionally ignores the last entry in the current code path and should be treated carefully if LUT sizing changes. Direct LUT writes bypass CMDQ ordering, so callers must ensure the block is clocked and safe to update.

### Test signals

Useful signals include successful probe for each compatible, gamma LUT size exposure, KMS color-management tests with linear and non-linear LUTs, suspend/resume retaining or restoring expected color output, visual checks for 10-bit and 12-bit LUT platforms, dither enable behavior on MT8173, and register traces confirming banked MT8195 LUT programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_gamma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_merge.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_merge.c

### Purpose

`mtk_disp_merge.c` implements the DISP_MERGE component used to buffer or merge display streams, including left/right merge programming for wide layers and FIFO mode for OVL adaptor pipelines. It also provides mode validation based on merge clock and prefetch bandwidth constraints.

### Important APIs, types, and functions

`struct mtk_disp_merge` stores MMIO, main and optional async clocks, CMDQ register metadata, FIFO/mute feature flags, and an optional reset control. Public hooks include `mtk_merge_start()`, `mtk_merge_stop()`, `mtk_merge_start_cmdq()`, `mtk_merge_stop_cmdq()`, `mtk_merge_config()`, `mtk_merge_advance_config()`, `mtk_merge_clk_enable()`, `mtk_merge_clk_disable()`, and `mtk_merge_mode_valid()`.

Key register groups are `DISP_REG_MERGE_CTRL`, size registers `CFG_0/1/4/24/25/26/27`, merge mode register `CFG_12`, swap register `CFG_10`, FIFO threshold registers `CFG_36/37/40/41`, and `DISP_REG_MERGE_MUTE_0`.

### Control flow

Probe maps registers, obtains clocks, optionally obtains the async clock and reset control, obtains CMDQ metadata, reads `mediatek,merge-fifo-en` and `mediatek,merge-mute`, stores drvdata, and registers the component. Start clears mute if supported and enables the merge block. Stop optionally mutes, disables the block, and performs a reset when invoked synchronously without CMDQ and an async clock is present.

`mtk_merge_config()` is a simple one-input wrapper. `mtk_merge_advance_config()` validates nonzero height and left width, optionally sets FIFO thresholds, selects buffer mode, two-input FIFO mode, or left/right merge mode depending on `fifo_en` and `r_w`, programs input/output/SRAM dimensions, clears swap mode, and writes the merge mode.

### State and persistence behavior

Private state is platform-device lifetime state. Hardware state persists across the block until rewritten or reset: merge mode, input and output dimensions, SRAM dimensions, FIFO thresholding, mute, swap, and enable. Clock enable state is reference-managed externally by DDP component sequencing, while stop may reset async-clock variants only for direct CPU stop calls.

### Dependencies

The driver uses clock, reset, component, OF, platform, CMDQ, and DRM mode APIs. It depends on `mtk_ddp_write()` and `mtk_ddp_write_mask()` for optional CMDQ-backed register programming and is consumed by `mtk_disp_ovl_adaptor.c` and CRTC path management.

### Integration points

In normal DDP paths, merge is a component in SoC path arrays. In the OVL adaptor path, per-layer MDP RDMA outputs feed MERGE blocks before ETHDR, with `mtk_merge_advance_config()` receiving left/right widths. `mtk_merge_mode_valid()` is called through component function tables to reject modes that exceed merge clock or prefetch bandwidth assumptions.

### Risks

The async-clock error unwind in `mtk_merge_clk_enable()` correctly disables the main clock, but the rollback loop in OVL adaptor clock enable calls must pass the matching component pointer or clocks can be unbalanced there. Width and height validation only rejects zero left width and height; extreme dimensions rely on register mask limits and upstream mode checks. The mode-valid prefetch formula uses a fixed threshold derived from 4K60 assumptions, so new SoCs or clocks may need updated limits. Reset is skipped for CMDQ stops, which may matter if a CMDQ stop is expected to fully clear state.

### Test signals

Test with single-input buffer mode, dual-input left/right merge mode, FIFO-enabled OVL adaptor layers, mute-capable compatibles, async reset paths, mode validation for high-pixel-clock and low-VBP modes, and CMDQ versus direct start/stop paths. Display bringup on MT8195 merge paths is the primary integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl.c

### Purpose

`mtk_disp_ovl.c` implements the classic MediaTek DISP_OVL overlay engine. It exposes plane-layer count, supported formats, blending capabilities, AFBC support, vblank IRQ handling, clock control, ROI setup, layer enable/disable, format conversion, rotation/reflection handling, and platform-specific OVL data.

### Important APIs, types, and functions

`struct mtk_disp_ovl_data` describes register address layout, GMC bit width, layer count, RGB565/RGB888 encoding variant, SMI ID behavior, AFBC support, DRM blend modes, formats, and extended color-format support. `struct mtk_disp_ovl` stores CRTC/vblank callback state, clock, MMIO, CMDQ register, and data.

Important exported hooks include `mtk_ovl_register_vblank_cb()`, `mtk_ovl_enable_vblank()`, `mtk_ovl_get_blend_modes()`, `mtk_ovl_get_formats()`, `mtk_ovl_is_afbc_supported()`, `mtk_ovl_clk_enable()`, `mtk_ovl_start()`, `mtk_ovl_config()`, `mtk_ovl_layer_nr()`, `mtk_ovl_layer_check()`, `mtk_ovl_layer_config()`, and `mtk_ovl_bgclr_in_on/off()`.

### Control flow

Probe obtains IRQ, clock, MMIO, optional CMDQ register, platform data, registers the IRQ handler, enables runtime PM, and adds the component. The IRQ handler clears frame-completion status and calls the registered vblank callback.

CRTC configuration writes ROI size, opaque black background color, and pulses reset. Start enables SMI ID if required and sets `DISP_REG_OVL_EN`; stop clears enable and SMI ID. Plane validation rejects unsupported rotations and rotated/reflected YUV layers. `mtk_ovl_layer_config()` exits through `mtk_ovl_layer_off()` when disabled; otherwise it converts DRM format and blend mode to OVL control bits, applies constant alpha, handles pixel-alpha ignore rules, turns 180-degree rotation into X/Y reflection, adjusts base addresses for reflection, toggles AFBC, writes control/pitch/size/offset/address/header registers, updates extended bit depth, and enables layer RDMA plus source bit.

### State and persistence behavior

Software state includes vblank callback pointers and immutable platform data. Hardware state persists in OVL registers: enabled state, ROI, background color, source layer enables, per-layer format/control/address/pitch/size/offset, AFBC header address/pitch, RDMA GMC thresholds, extended color depth, and datapath options. Layer programming is CMDQ-capable, so atomic updates can be synchronized with display events.

### Dependencies

The driver uses DRM format/blend/framebuffer metadata, Linux clock/component/PM/IRQ/platform/CMDQ APIs, and local MediaTek DDP, CRTC, display, and DRM headers. It depends on `mtk_plane_state` pending fields prepared by the DRM plane path and on `mtk_ddp_write*()` helpers.

### Integration points

OVL is a primary CRTC input component in many path arrays in `mtk_drm_drv.c`. Its DMA device can be used for GEM allocation through CRTC helpers. Plane initialization queries its format and blend support. Vblank is reported through the callback registered by the CRTC. AFBC and 10-bit support affect modifier and format exposure on MT8195.

### Risks

Format conversion has SoC-specific RGB565/RGB888 encodings and blend-mode-dependent premultiplied formats; adding formats without matching hardware encodings can silently corrupt pixels. Reflection adjusts addresses using pitch and height but assumes pending state has already been clipped and validated. AFBC enables are keyed only on non-linear modifier and require correct header address and pitch. The IRQ handler returns `IRQ_NONE` when no callback is registered after clearing status, which is acceptable but can look like a spurious interrupt. GMC threshold programming depends on `gmc_bits` and differs for 8-bit versus 10-bit hardware.

### Test signals

Signals include KMS plane tests across all advertised formats, alpha and premultiplied blend modes, X/Y reflection and 180-degree rotation, YUV non-rotated layers, AFBC and linear modifiers, 10-bit RGB on MT8195, vblank events, suspend/resume, and register traces for source enables and RDMA GMC setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl_adaptor.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl_adaptor.c

### Purpose

`mtk_disp_ovl_adaptor.c` implements a pseudo overlay component for newer MediaTek display systems where overlay behavior is assembled from ETHDR, multiple MDP RDMA blocks, MERGE blocks, and padding blocks. It lets the rest of the DRM pipeline treat that collection as one DDP component.

### Important APIs, types, and functions

The key types are `enum mtk_ovl_adaptor_comp_type`, `enum mtk_ovl_adaptor_comp_id`, `struct ovl_adaptor_comp_match`, and `struct mtk_disp_ovl_adaptor`. `comp_matches[]` maps adaptor-local component slots to DDP component IDs, alias IDs, and function tables. Public hooks include layer/config/start/stop, power and clock control, mode validation, format/blend queries, DMA device lookup, vblank forwarding, mutex add/remove, connect/disconnect, and presence detection.

Important functions are `mtk_ovl_adaptor_layer_config()`, `mtk_ovl_adaptor_power_on/off()`, `mtk_ovl_adaptor_clk_enable/disable()`, `mtk_ovl_adaptor_add_comp/remove_comp()`, `mtk_ovl_adaptor_connect/disconnect()`, `mtk_ovl_adaptor_is_comp_present()`, `ovl_adaptor_comp_init()`, and the component/master bind callbacks.

### Control flow

Probe allocates adaptor state, scans the parent display node for compatible ETHDR, MDP RDMA, MERGE, and padding child devices, maps them into adaptor slots by alias ID, adds component matches, stores the MMSYS device passed as platform data, registers a component master, enables runtime PM, and registers the pseudo component. Master bind calls `component_bind_all()` on children and then marks `children_bound`; the component bind defers until that is true.

Layer configuration maps each logical layer to two MDP RDMA engines and one MERGE. Disabled or zero-sized layers stop both RDMAs and merge then update ETHDR layer state. Enabled layers align width down to two pixels for the 1T2P ETHDR domain, split over two pipes if the aligned width exceeds 1920, programs MERGE dimensions and MMSYS async merge, configures left and optional right MDP RDMA, starts/stops the relevant engines, and finally programs ETHDR layer blending.

### State and persistence behavior

The adaptor itself stores only child device pointers, MMSYS device, and bind state. Persistent hardware state lives in child components: MDP RDMA memory fetch configuration, MERGE sizes and enable bits, ETHDR layer state, padding state, MMSYS routing, and mutex membership. Power and clock helpers explicitly walk children because the pseudo device has no independent hardware power domain.

### Dependencies

It depends on DRM format and OF component matching, MediaTek MMSYS and mutex APIs, CMDQ, MDP RDMA, MERGE, ETHDR, padding, and DDP component function tables. It is tightly coupled to device-tree aliases such as `vdo1-rdma`, `merge`, `ethdr`, and `padding`.

### Integration points

`mtk_drm_drv.c` detects adaptor-exclusive child nodes and inserts `DDP_COMPONENT_DRM_OVL_ADAPTOR` into graph-built paths. The CRTC/plane path calls the adaptor just like OVL for layer count, format list, blend modes, vblank, and DMA device. MMSYS route connection wires MDP RDMA to MERGE and MERGE to ETHDR, then ETHDR to the next display component.

### Risks

The error unwind in `mtk_ovl_adaptor_clk_enable()` uses the current `comp` variable while walking prior indices, which is a bug risk because it may call `clk_disable()` with the wrong device pointer. `mtk_ovl_adaptor_clk_disable()` additionally calls `pm_runtime_put()` for indices before MERGE even though power-on is handled separately, so ordering must match child PM expectations. Width is aligned down, so odd-width layer handling relies on the pipeline accepting the dropped pixel or upstream alignment. Device-tree alias mismatches cause components to be skipped. Connect/disconnect currently wires only a fixed subset of MDP RDMA paths.

### Test signals

Use MT8195/MT8188 graph-built pipelines with OVL adaptor, multi-layer composition, layers wider than 1920 that require dual pipe, odd widths, disable/enable layer transitions, vblank through ETHDR, mutex route programming, suspend/resume power sequencing, clock error injection, and mode validation through the MERGE child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_ovl_adaptor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_rdma.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_rdma.c

### Purpose

`mtk_disp_rdma.c` implements the classic DISP_RDMA read-DMA component. It fetches a single framebuffer layer from memory into the display pipeline, handles vblank/frame-end interrupts, programs FIFO thresholds, exposes supported formats, and provides clock/start/stop/config hooks.

### Important APIs, types, and functions

`struct mtk_disp_rdma_data` stores FIFO size and supported DRM formats. `struct mtk_disp_rdma` stores clock, MMIO, CMDQ register metadata, platform data, vblank callback, and optional DT FIFO override.

External hooks include `mtk_rdma_register_vblank_cb()`, `mtk_rdma_enable_vblank()`, `mtk_rdma_get_formats()`, `mtk_rdma_clk_enable()`, `mtk_rdma_start()`, `mtk_rdma_config()`, `mtk_rdma_layer_nr()`, and `mtk_rdma_layer_config()`. Internal helpers include `rdma_update_bits()` and `rdma_fmt_convert()`.

### Control flow

Probe allocates private state, obtains IRQ, clock, MMIO, optional CMDQ register, optional `mediatek,rdma-fifo-size`, clears interrupts, registers IRQ, sets platform data, enables runtime PM, and adds the component. The IRQ handler clears frame-completion status and dispatches the registered vblank callback.

`mtk_rdma_config()` programs output width and height, selects the DT FIFO override or platform FIFO size, and configures underflow enable, pseudo FIFO size, and output-valid threshold at 70 percent of FIFO capacity. `mtk_rdma_layer_config()` converts DRM format to memory mode, enables BT.601 YUV-to-RGB matrix for UYVY/YUYV, writes memory start address and pitch, programs GMC, and enables memory mode.

### State and persistence behavior

Software state is limited to callback pointers and FIFO override. Hardware state persists in RDMA registers: interrupt enables/status, global engine/memory mode, output dimensions, matrix selection, memory format, source address/pitch, GMC settings, and FIFO thresholds. Register updates during atomic paths can use CMDQ.

### Dependencies

The file depends on DRM fourcc metadata, Linux clock/component/IRQ/PM/platform/CMDQ APIs, and MediaTek DDP/CRTC/display/DRM headers. It consumes `mtk_plane_state` pending address, pitch, format, and dimensions prepared by the plane layer.

### Integration points

RDMA is used both as a standalone path component in many SoC arrays and as a one-layer memory source. CRTC code uses vblank callbacks, clock/start/stop/config hooks, and DMA-device lookup. For newer pseudo-OVL paths, separate MDP RDMA code is used instead of this DISP_RDMA.

### Risks

Only one layer is supported, and the code does not inspect `pending->enable` in `mtk_rdma_layer_config()`, so callers must avoid configuring disabled layers incorrectly. Pitch is masked to 16 bits, limiting wide or high-bpp buffers unless hardware supports more elsewhere. YUV matrix selection is hard-coded to BT.601. FIFO sizing mistakes can trigger underflow on DSI/DPI outputs that cannot backpressure the pipeline.

### Test signals

Test signals include frame-end vblank interrupts, memory-mode scanout in all advertised RGB and packed YUV formats, YUV matrix behavior, FIFO underflow interrupt absence under stress, DT FIFO override, mode changes across platform FIFO sizes, and suspend/resume with runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp.c

### Purpose

`mtk_dp.c` is the MediaTek DisplayPort/eDP bridge driver for MT8188 and MT8195 families. It owns DP register access, AUX transfers, HPD handling, link capability parsing, PHY calibration and configuration, link training, video timing setup, bridge atomic format negotiation, audio packet programming, HDMI-codec registration, eDP panel linking, and suspend/resume power sequencing.

### Important APIs, types, and functions

Core state is `struct mtk_dp`, containing enable/HPD state, RX DPCD caps, calibration data, bridge/connector/AUX objects, train info, video/audio info, PHY/regmap devices, debounce timer, HDMI-codec callback state, and platform data. `struct mtk_dp_data` selects connector type, secure monitor command, efuse layout, audio support, audio packet placement, and audio divider bits.

Major function groups are register helpers (`mtk_dp_read/write/update_bits()`), video setup (`mtk_dp_set_msa()`, `mtk_dp_set_color_format()`, `mtk_dp_setup_encoder()`, `mtk_dp_video_config()`), AUX (`mtk_dp_aux_do_transfer()`, `mtk_dp_aux_transfer()`), IRQ/HPD (`mtk_dp_hpd_event()`, `mtk_dp_hpd_event_thread()`), calibration/PHY (`mtk_dp_get_calibration_data()`, `mtk_dp_phy_configure()`), link training (`mtk_dp_training()`, `mtk_dp_train_cr()`, `mtk_dp_train_eq()`), bridge ops, and HDMI-codec ops.

### Control flow

Probe allocates a DRM bridge, parses MMIO/data-lanes/max-linkrate, requests threaded HPD IRQ for external DP, initializes `drm_dp_aux`, optionally registers HDMI-codec audio, registers a child DP PHY platform device, configures bridge type, and either populates the eDP AUX bus and panel bridge or registers a hotpluggable DP bridge. Runtime PM is enabled and held active.

Bridge attach registers AUX, powers on DP, attaches a downstream bridge, and enables IRQs for external DP. Atomic check records input bus format as RGB or YUV422 and converts adjusted mode to `videomode`. Atomic enable powers eDP AUX/panel if needed, performs eDP training, programs MSA/color, unmutes video, configures audio if EDID SADs/audio are present, updates plugged status, and marks eDP enabled. Atomic disable marks eDP disabled, powers eDP panel off, updates audio plug status, mutes video/audio, resets SDP path, and waits for sink mute.

External DP HPD IRQs are split into a hard IRQ that clears hardware/software IRQ state and records cable/event bits under a spinlock, and a threaded handler that debounces, emits DRM HPD events, powers AUX, parses capabilities, runs link training on connect, or disables audio/AUX and starts debounce on disconnect.

### State and persistence behavior

Persistent software state includes `enabled`, `need_debounce`, `train_info`, RX caps, calibration data, current video format/timing, current audio capabilities, and HDMI-codec callback pointers. Hardware state persists across register blocks: PHY power, AUX engine, HPD thresholds, MSA, pattern generator, video/audio mute, SDP packets, lane count, swing/pre-emphasis, FEC/scrambler, and PLL/lane PHY configuration. Suspend powers down DP and disables IRQs; resume reinitializes port settings and power.

### Dependencies

The driver depends on DRM bridge, atomic, DP helper, AUX bus, EDID, panel, and probe helper APIs; Linux regmap, PHY, NVMEM, OF graph, IRQ, PM, timer, and ARM SMCCC APIs; HDMI codec audio; and `mtk_dp_reg.h`. It relies on secure monitor calls for video mute/unmute and on the `mediatek-dp-phy` child driver for PHY programming.

### Integration points

It registers as a DRM bridge with detect/EDID/HPD ops for external DP and as an eDP bridge only after a panel is found. AUX is used for EDID, DPCD, link training, and eDP panel power. The MediaTek DPI/DP-INTF path negotiates input bus formats with this bridge, allowing YUV422 when RGB888 bandwidth is too high but YUV422 fits. HDMI-codec callbacks expose DP audio to ALSA.

### Risks

AUX transactions are timing-sensitive and return NACK on unsupported requests, timeouts, or PHY hang; failures can break EDID and training. Link training downshifts link rate and lane count, but repeated failures end in `-ETIMEDOUT` or `-EIO`. eDP capability caching assumes fixed panel capabilities during a boot. Video mute uses secure monitor commands, so firmware behavior is part of display correctness. Audio capability parsing only tracks SAD count and monitor-audio detection, with FIXME comments around newer EDID handling. Probe holds runtime PM active, so power-management changes need care.

### Test signals

Validate external DP hotplug/unplug, HPD IRQ events, EDID reads through AUX, DPCD capability parsing, link training at 1/2/4 lanes and multiple link rates, fallback after CR/EQ failure, eDP AUX-bus panel discovery, suspend/resume, YUV422 bus-format fallback for bandwidth-limited modes, audio ELD and HDMI-codec playback, secure mute/unmute, and nvmem calibration fallback/default paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp_reg.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp_reg.h

### Purpose

`mtk_dp_reg.h` defines the MMIO register offsets and bit fields consumed by the MediaTek DP/eDP bridge driver. It covers PHY analog controls, top-level power/IRQ/memory controls, encoder timing and audio registers, transmitter pattern/HPD/FEC/scrambler registers, and AUX engine registers.

### Important APIs, types, and functions

The header has no functions or types beyond preprocessor definitions. Important groups include PHY calibration fields (`DP_PHY_GLB_*`, `DP_PHY_LANE_TX_*`), top registers (`MTK_DP_TOP_PWR_STATE`, `MTK_DP_TOP_SWING_EMP`, `MTK_DP_TOP_IRQ_MASK`), encoder registers (`MTK_DP_ENC0_*`, `MTK_DP_ENC1_*`), transmitter registers (`MTK_DP_TRANS_*`), and AUX registers (`MTK_DP_AUX_*`). It also defines HPD event bits and SoC-specific audio M-code divider encodings.

### Control flow

There is no runtime control flow. `mtk_dp.c` uses these constants in regmap read/write/update operations to initialize the block, perform AUX transfers, program video timing, set color depth/format, train links, program audio SDP packets, and handle HPD IRQs.

### State and persistence behavior

The header owns no state. It describes persistent hardware state in DP/eDP registers, including power state, lane swing/pre-emphasis, HPD debounce thresholds and status, MSA timing, video/audio mute, FIFO thresholds, FEC/scrambler, SDP payload/header data, AUX FIFO/request/status, and PHY calibration.

### Dependencies

It depends on common Linux bit macros being available through including code. Its semantic dependency is `mtk_dp.c`; field names are matched directly to MediaTek register programming sequences.

### Integration points

The definitions are the low-level contract between `mtk_dp.c`, the DP PHY child device, and the hardware register map. Any bridge, AUX, audio, or training behavior change in `mtk_dp.c` uses this header for masks and offsets.

### Risks

Wrong masks or shifts can corrupt unrelated fields because most writes are read-modify-write through regmap. Audio divider encodings differ between MT8188 and MT8195. AUX and HPD status/clear bits are sequence-sensitive; incorrect definitions can cause stuck IRQs, AUX timeouts, or false cable state. The regmap maximum in `mtk_dp.c` must continue covering all offsets defined here.

### Test signals

Build coverage is the first signal. Runtime validation includes register readback during DP initialization, HPD IRQ clear behavior, successful AUX EDID/DPCD transfers, link training lane/swing changes, video timing output, audio packet generation, and suspend/resume power-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi.c

### Purpose

`mtk_dpi.c` implements the MediaTek DPI and DP-INTF bridge/encoder component. It programs parallel display output timing, pixel clocks, bus formats, RGB/YUV conversion, polarity, DDR/dual-edge output, pinctrl states, debug test patterns, and bridge connector integration.

### Important APIs, types, and functions

`struct mtk_dpi` holds encoder/bridge/connector objects, MMIO, clocks, mmsys device, mode, SoC config, selected bus format/color settings, pinctrl states, and a power refcount. `struct mtk_dpi_conf` describes PLL factors, register masks, max clock, supported output formats, polarity and input-swap support, direct pin behavior, DP-INTF variants, pixels per iteration, MMSYS edge config, HDMI-clocked variants, and output 1-pixel mode.

Major helpers include timing programming (`mtk_dpi_config_hsync()`, `mtk_dpi_config_vsync_*()`), format programming (`mtk_dpi_config_bit_num()`, `mtk_dpi_config_color_format()`, `mtk_dpi_dual_edge()`), power/clock (`mtk_dpi_power_on/off()`), clock calculation (`mtk_dpi_set_pixel_clk()`), mode setup (`mtk_dpi_set_display_mode()`), bridge ops, debugfs test-pattern ops, and component bind/unbind.

### Control flow

Probe allocates a DRM bridge, loads compatible-specific config, initializes default output format, optionally selects sleep pinctrl, maps registers, gets engine/pixel/pll clocks, gets IRQ, locates downstream bridge through OF graph, registers the DRM bridge, and adds the component. Component bind creates a TMDS encoder, computes possible CRTCs, attaches the DPI bridge chain with no connector, creates a bridge connector, and attaches it to the encoder.

Atomic bridge check chooses output format, bit depth, channel swap, YC map, and RGB/YUV color format. Mode set stores adjusted mode. Enable selects active pins, powers clocks, programs display mode, and enables the block. Disable powers off and returns pins to sleep. Public `mtk_dpi_start/stop()` only power non-HDMI-clocked variants.

### State and persistence behavior

Software state persists selected output format and mode between atomic check/mode_set/enable. `refcount` prevents double clock disable when DPI is used through both DDP start/stop and bridge enable/disable. Hardware state persists in timing generator, size, output setting, color conversion, channel limits, DDR, frequency-control, pattern, and enable registers. Pinctrl state persists at the SoC pinmux level.

### Dependencies

The driver depends on DRM bridge, bridge-connector, atomic helper, EDID, OF graph, MediaTek MMSYS, clocks, pinctrl, debugfs, and `mtk_dpi_regs.h`. It integrates with `mtk_drm_drv.c` as a DDP component and downstream panels/bridges through standard DRM bridge APIs.

### Integration points

DPI/DP-INTF sits near the end of a MediaTek CRTC path and feeds an external bridge, panel, HDMI path, or DP transmitter. Its output bus format negotiation feeds downstream bridge requirements and upstream color conversion. `mtk_dpi_encoder_index()` exposes encoder index to other MediaTek code. Debugfs exposes `dpi_test_pattern` for hardware pattern generation.

### Risks

Clock programming mutates a local `videomode` pixelclock after PLL rounding and divides by `pixels_per_iter`, so porch/timing assumptions must stay consistent with DP-INTF variants. The debugfs write checks unsigned values for `< 0`, which is ineffective but harmless. Power refcounting must stay balanced across DDP and bridge callers. Some configurations are `clocked_by_hdmi`, so register access and clock ownership differ from normal DPI. YUV422 matrix selection uses `mode.hdisplay <= 720` rather than detailed colorimetry.

### Test signals

Validate bridge attach and connector creation, mode-valid clock rejection, output bus-format negotiation for RGB/YUV and 8/10/12-bit formats, DPI and DP-INTF modes at different pixel clocks, pinctrl active/sleep transitions, suspend/resume, debugfs pattern enable/disable, dual-edge RGB888 modes, and interlaced/3D timing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi_regs.h

### Purpose

`mtk_dpi_regs.h` defines the DPI/DP-INTF register offsets and bit fields used by `mtk_dpi.c`. It names enable/reset/interrupt bits, output settings, timing generator registers, color limit and conversion fields, embedded sync fields, matrix selection, and test pattern controls.

### Important APIs, types, and functions

The header is macro-only. Major groups are `DPI_EN`, `DPI_RET`, `DPI_INTEN/INTSTA`, `DPI_CON`, `DPI_OUTPUT_SETTING`, `DPI_SIZE`, `DPI_DDR_SETTING`, horizontal/vertical timing registers, background/status/checksum registers, interlace/3D timing extensions, Y/C limit registers, YUV422 and embedded sync fields, matrix selection, frequency/edge bits, and `DPI_PATTERN0`.

### Control flow

There is no runtime control flow. `mtk_dpi.c` combines these masks with SoC-specific `mtk_dpi_conf` masks and shifts to program timing, polarity, bit depth, channel order, color conversion, DDR/edge behavior, input/output pixel packing, and test patterns.

### State and persistence behavior

The header owns no state. It describes persistent DPI hardware registers whose values remain until rewritten or reset: enable, reset, timing, output packing, color conversion, limits, DDR mode, interrupts, checksum, embedded sync, and pattern generator.

### Dependencies

The macros assume standard `BIT()`, `GENMASK()`, and related bit helpers are available through including files. Semantically it depends on `mtk_dpi.c` and MediaTek display hardware manuals.

### Integration points

All DPI bridge and component programming is expressed through this header. SoC variants in `mtk_dpi.c` choose different masks for the same conceptual fields, especially DP-INTF wide masks and channel-swap/input-2P bits.

### Risks

Many masks are unshifted legacy constants, while the driver also shifts config masks in several places; changing masks without checking call sites can double-shift or under-mask writes. DPI and DP-INTF reuse some registers with different bit positions. Incorrect DDR or channel swap definitions can produce wrong colors or broken output timing without compile-time failures.

### Test signals

Build coverage plus hardware readback while setting modes, RGB/YUV bus-format tests, interrupt/status behavior if enabled by future code, test-pattern debugfs output, and DP-INTF modes using 16-bit masks are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dpi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.c

### Purpose

`mtk_drm_drv.c` is the main MediaTek DRM/KMS driver. It defines SoC display paths, registers all MediaTek display sub-drivers, builds component matches from hardcoded data or OF graphs, coordinates one or more MMSYS/VDOSYS instances into a DRM device, initializes mode config, creates CRTCs, sets DMA allocation device, registers DRM, and handles system suspend/resume and shutdown.

### Important APIs, types, and functions

Important data includes path arrays for MT2701, MT7623, MT2712, MT8167, MT8173, MT8183, MT8186, MT8188, MT8192, and MT8195, plus `struct mtk_mmsys_driver_data` instances that define path lengths, connector routes, mmsys IDs, multi-MMSYS counts, shadow-register support, and width/height limits.

Core functions are `mtk_drm_kms_init()`, `mtk_drm_kms_deinit()`, `mtk_drm_bind()`, `mtk_drm_unbind()`, `mtk_drm_of_get_ddp_ep_cid()`, `mtk_drm_of_ddp_path_build_one()`, `mtk_drm_of_ddp_path_build()`, `mtk_drm_probe()`, `mtk_drm_remove()`, `mtk_drm_shutdown()`, and PM callbacks. The DRM driver uses GEM DMA helpers and a custom `fb_create` that rejects multi-plane framebuffers.

### Control flow

Module init registers all component platform drivers and the main DRM platform driver. Probe identifies the parent MMSYS compatible, copies path data when OF graph paths are present, optionally builds paths by walking graph endpoints, allocates the cross-MMSYS private pointer array, creates an OVL adaptor pseudo-device if the path needs one, scans sibling display nodes for known DDP components, stores component nodes, initializes DDP component descriptors, finds the matching mutex node, enables PM, and registers a component master.

Master bind finds the mutex platform device, marks this DRM node bound, waits until all required MMSYS instances are bound, allocates the DRM device once on the master, points all MMSYS private structures to it, initializes KMS, removes conflicting firmware apertures, registers DRM, and starts DRM clients. KMS init initializes mode config, binds all components for every MMSYS instance, creates CRTCs in main/ext/third order, sets cursor size, chooses the first CRTC OVL DMA device for GEM allocation, sets max segment size, initializes vblank and polling, and resets mode config.

### State and persistence behavior

`struct mtk_drm_private` persists per mediatek-drm platform device and stores the DRM device pointer, bound/master flags, mutex/mmsys devices, component nodes, component descriptors, SoC data, suspend atomic state pointer, mailbox index, and all-MMSYS private array. DRM device state persists registered CRTCs, connectors, planes, vblank, GEM DMA settings, and mode config. System suspend uses `drm_mode_config_helper_suspend()` only from the DRM master, and complete resumes through DRM helpers.

### Dependencies

The driver depends on Linux component, OF graph, platform, PM runtime, DMA mapping, aperture removal, and DRM core/atomic/GEM/DMA/fbdev/vblank helpers. It depends on all MediaTek component drivers declared in `mtk_drm_drv.h`, on `mtk_crtc_create()`, `mtk_crtc_dma_dev_get()`, `mtk_ddp_comp_init()`, and OVL adaptor graph detection.

### Integration points

This file is the central integration point for the entire MediaTek DRM stack. It registers sub-drivers, maps DT compatibles to DDP component types, builds display pipelines, creates pseudo OVL adaptor devices, coordinates multiple VDOSYS devices for MT8188/MT8195, binds encoders/connectors through component drivers, and exposes the final DRM device to userspace.

### Risks

Multi-MMSYS bind ordering is subtle: non-master binds can return success without registering DRM until all instances are present. `mtk_drm_get_all_drm_priv()` indexes `all_drm_priv` by path type and assumes all expected instances can be found. Graph path building treats the final output component specially and suppresses duplicate OVL adaptor entries; malformed graphs can fail late. `mtk_drm_kms_deinit()` unbinds only `drm->dev`, whereas init bound all MMSYS devices, so multi-device cleanup depends on surrounding paths and should be reviewed if changed. Only single-plane framebuffer creation is allowed.

### Test signals

Signals include boot and DRM registration on each compatible, graph-built and hardcoded path systems, multi-MMSYS MT8188/MT8195 bringup, CRTC creation order, connector route selection, OVL adaptor pseudo-device creation, fbdev/client setup, PRIME import with contiguous IOVA, vblank init, suspend/resume, shutdown, and failure injection around missing mutex/component nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.h

### Purpose

`mtk_drm_drv.h` declares the shared driver-private data structures and platform driver externs used by the MediaTek DRM master and component drivers. It is the cross-file contract for CRTC paths, MMSYS SoC data, private DRM state, and sub-driver registration.

### Important APIs, types, and functions

Important constants are `MAX_CONNECTOR`, `DDP_COMPONENT_DRM_OVL_ADAPTOR`, and `DDP_COMPONENT_DRM_ID_MAX`. `enum mtk_crtc_path` defines `CRTC_MAIN`, `CRTC_EXT`, and `CRTC_THIRD`. `struct mtk_drm_route` describes connector route options. `struct mtk_mmsys_driver_data` describes per-SoC paths, route tables, shadow-register flag, MMSYS identity/count, and size limits. `struct mtk_drm_private` stores per-device DRM, component, mutex, MMSYS, suspend, mailbox, and multi-private coordination state.

### Control flow

The header has no runtime control flow. It enables `mtk_drm_drv.c` to register all component platform drivers and lets component code include common definitions without circular declarations.

### State and persistence behavior

The header owns no state, but defines the layout of persistent per-MMSYS state in `struct mtk_drm_private` and immutable/mostly immutable path data in `struct mtk_mmsys_driver_data`. These structures persist for the platform-device lifetime and are used throughout component binding and KMS operation.

### Dependencies

It includes `<linux/io.h>` and `mtk_ddp_comp.h`, forward-declares DRM/device/regmap types, and declares extern platform drivers for AAL, CCORR, COLOR, GAMMA, MERGE, OVL adaptor, OVL, RDMA, DPI, DSI, ETHDR, MDP RDMA, and padding.

### Integration points

`mtk_drm_drv.c` is the primary consumer. Component drivers rely on the extern declarations for the unified driver registration array. Path and private structs are used by DPI bind, CRTC creation, DDP component initialization, graph path building, and multi-MMSYS coordination.

### Risks

Changing `DDP_COMPONENT_DRM_OVL_ADAPTOR` or `DDP_COMPONENT_DRM_ID_MAX` affects array sizing and pseudo-component indexing across the driver. Adding fields to `mtk_mmsys_driver_data` or `mtk_drm_private` requires updating copy/allocation behavior in graph-built paths. Extern platform-driver declarations must match actual definitions or module link fails.

### Test signals

Build coverage across enabled MediaTek DRM components is the main signal. Runtime signals include successful component registration, OVL adaptor path construction using the pseudo ID, and multi-MMSYS state sharing through `all_drm_private`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.h -->
