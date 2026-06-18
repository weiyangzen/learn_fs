# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_sh_mask.h lines 7462-9948

## Scope And Purpose

This chunk is the tail section of the generated AMD DCE 6.0 register shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable control flow. Each exported symbol describes either the bit mask or shift for one hardware register field, normally consumed through AMDGPU/DC helper macros such as `REG_SET_FIELD()` or direct mask writes.

The source tree is a Ceph-client repository that vendors Linux GPU driver code; this file belongs to the AMD display engine support code, not to Ceph filesystem behavior. The purpose of this header section is to give DCE 6.0 display, memory-interface, encoder, PLL, VGA, and XDMA programming code stable symbolic names for MMIO bit positions.

The chunk begins in the middle of the `HDMI_INFOFRAME_CONTROL0` macro family: the `HDMI_AUDIO_INFO_SEND_MASK` definition is in the previous chunk, while this chunk starts with its `__SHIFT`. It then covers HDMI packet/status fields, CSC/gamma/keyer and line-buffer controls, LVDS/LVTMA panel power sequencing, MCIF and DMIF-related status, MVP multi-view/AFR controls, overlay surface/scaler/update fields, pipe arbitration and power-gating fields for pipes 0 through 5, PLL/display-clock programming, prescale/regamma/scaler fields, VGA sequencer and legacy VGA aperture controls, TMDS/UNIPHY encoder/link controls, XDMA master/slave fields, and a final commented block for selected data format, line-buffer, priority, interrupt, vline/vblank, and scaler-init fields before the include guard closes.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this range. The interface is the macro namespace. Most names follow `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, with register fields encoded as hexadecimal masks and shift values.

Major display-output and packet families include `HDMI_INFOFRAME_CONTROL0/1`, `HDMI_STATUS`, and `HDMI_VBI_PACKET_CONTROL`. These describe AVI/audio/MPEG infoframe send/continuous modes, line placement, AVMUTE and packet error state, and VBI packets such as GC, ISRC, ACP, and NULL packets.

Color pipeline and blending families include `INPUT_CSC_*`, `INPUT_CSC_CONTROL`, `INPUT_GAMMA_CONTROL`, `KEY_CONTROL`, `KEY_RANGE_*`, `OUTPUT_CSC_*`, `OUTPUT_CSC_CONTROL`, `PRESCALE_*`, `REGAMMA_*`, `REGAMMA_LUT_*`, and `OUT_ROUND_CONTROL`. These provide packed coefficient fields, LUT mode selection, color-key limits, prescale bias/scale fields, regamma piecewise-region controls for CNTLA/CNTLB, and truncation/rounding controls.

Line-buffer, timing, and interrupt families include `LB_*`, `DATA_FORMAT`, `DC_LB_MEMORY_SPLIT`, `DC_LB_MEM_SIZE`, `INT_MASK`, `PRIORITY_A_CNT`, `PRIORITY_B_CNT`, `VLINE_STATUS`, `VBLANK_STATUS`, `VIEWPORT_SIZE`, and `VIEWPORT_START`. These fields control interlace/data fetch formatting, line-buffer allocation and memory split, urgent watermark priority, vblank/vline masking and acknowledgement, and viewport geometry.

Panel, encoder, and link families include `LVDS_DATA_CNTL`, `LVTMA_PWRSEQ_*`, `PHY_AUX_CNTL`, `TMDS_*`, `SYMCLK[A-F]_CLOCK_ENABLE`, and `UNIPHY_*`. These cover LVDS 24-bit and dual-link timing pins, embedded-panel power-up/down sequencing and status, AUX pad behavior, TMDS control-character generation and DC balancing, symbol clock gating/forcing, UNIPHY test-pattern generation, lane crossbar/inversion, data synchronization, impedance calibration, PLL configuration, power control, soft reset, and transmitter voltage/pre-emphasis settings.

Display memory, power, and diagnostics families include `MC_DC_INTERFACE_NACK_STATUS`, `MCIF_CONTROL`, `MCIF_MEM_CONTROL`, `MCIF_VMID`, `MCIF_WRITE_COMBINE_CONTROL`, `PIPE[0-5]_*`, `LIGHT_SLEEP_CNTL`, `LOW_POWER_TILING_CONTROL`, `SCLK_CGTT_BLK_CTRL_REG`, `MILLISECOND_TIME_BASE_DIV`, and `MICROSECOND_TIME_BASE_DIV`. These describe memory-client NACK status/clear bits, address translation and privileged access, MCIF cache and VMID fields, write-combine timeout, per-pipe DMIF buffer allocation, maximum requests, power-gating force/gate/status fields, memory light-sleep/shutdown disables, low-power tiling geometry, clock-gating delays, and display timebase dividers.

MVP and overlay families include `MVP_*`, `OVL_*`, and `OVLSCL_EDGE_PIXEL_CNTL`. The MVP block contains AFR flip FIFO control, mixer/channel/flow-control state, CRC masks/results, debug taps, FIFO underflow/overflow acknowledgement/status, flip-line insertion, in-band control, slave receive counters, and test debug index/data. Overlay fields describe surface format/depth/tiling, address translation, privileged access, primary/secondary surface addresses and high bits, in-use addresses, DFQ controls/status, start/end/offset geometry, stereo sync flip state, channel crossbars, endian swap, update lock/pending/taken, and overlay scaler edge color.

PLL and clock families include `PIXCLK[0-2]_RESYNC_CNTL`, `PLL_ANALOG`, `PLL_CNTL`, `PLL_DEBUG_CNTL`, `PLL_DISPCLK_*`, `PLL_DS_CNTL`, `PLL_FB_DIV`, `PLL_IDCLK_CNTL`, `PLL_POST_DIV`, `PLL_REF_DIV`, `PLL_SS_*`, `PLL_UNLOCK_DETECT_CNTL`, `PLL_UPDATE_*`, `PLL_VREG_CNTL`, and the legacy `VGA25/28/41_PPLL_*` blocks. These fields are used for display PLL reset, power, ref/post/fb dividers, spread-spectrum controls, DTO updates, lock detection, VCO/analog tuning, and VGA pixel-clock PLLs.

Scaler and LUT families include `SCL_*` and `SCL_TAP_CONTROL`. They define scaler enable/bypass, coefficient RAM select/tap data, coefficient conflict interrupt/status/ack, sharpness controls, horizontal and vertical ratios, filter initial phases, mode-change detection and masking, update lock/pending/taken, tap counts, and test/debug registers.

Legacy VGA families include `SEQ*`, `VGA_*`, and `VGADCC_DBG_DCCIF_C`. They describe VGA sequencer reset, font/map/chain controls, debug readback, VGA display buffers and memory base, HDP/reset/page select, interrupt mask/status/clear bits, main/render/mode/cache controls, source selection, pitch/height selection, and test controls.

XDMA families include `XDMA_CLOCK_GATING_CNTL`, `XDMA_IF_BIF_STATUS`, `XDMA_INTERRUPT`, `XDMA_LOCAL_SURFACE_TILING*`, `XDMA_MC_PCIE_CLIENT_CONFIG`, `XDMA_MEM_POWER_CNTL`, `XDMA_MSTR_*`, `XDMA_SLV_*`, and `XDMA_TEST_DEBUG_*`. They describe cross-GPU/display DMA clock gating, BIF errors, urgent/underflow interrupts, local surface tiling, VMID/swap/privilege, memory power, master and slave enable/reset/ready bits, addresses, pitches, request size/prefetch, NACK status/tag/clear fields, urgent thresholds, latency counters, writeback rate, and debug indexes.

## Control Flow And Data Flow

The chunk has no internal runtime control flow. Data flow is compile-time substitution: source files include `dce_6_0_sh_mask.h`, combine these field descriptors with companion register offsets from DCE 6.0 address headers, and read or write MMIO registers through AMDGPU register helpers.

The classic AMDGPU DCE 6.0 path shows representative use. In `amdgpu/dce_v6_0.c`, HDMI audio enable logic reads `mmHDMI_INFOFRAME_CONTROL0`, updates `HDMI_AVI_INFO_SEND`, `HDMI_AVI_INFO_CONT`, `HDMI_AUDIO_INFO_SEND`, and `HDMI_AUDIO_INFO_CONT` through `REG_SET_FIELD()`, then writes the register back. The same file writes `DATA_FORMAT__INTERLEAVE_EN_MASK` directly when programming interlaced scanout, and uses `INPUT_CSC_CONTROL__INPUT_CSC_GRPH_MODE__SHIFT`, `INPUT_CSC_CONTROL__INPUT_CSC_OVL_MODE__SHIFT`, `PRESCALE_*_BYPASS_MASK`, and `INPUT_GAMMA_CONTROL` shifts while loading a CRTC LUT.

Interrupt handling is another direct integration path. `amdgpu/dce_v6_0.c` acknowledges vblank and vline interrupts by writing `VBLANK_STATUS__VBLANK_ACK_MASK` or `VLINE_STATUS__VLINE_ACK_MASK`. The DC IRQ service for DCE 6.0 builds `irq_source_info` entries with `INT_MASK__VBLANK_INT_MASK` as the enable/mask field and `VBLANK_STATUS__VBLANK_ACK_MASK` as the acknowledgement value.

Because this header is generated, the field names also act as a contract for generic field manipulation helpers. A wrong `_MASK` or `__SHIFT` value still compiles but causes callers to set, clear, or test the wrong hardware bits.

## State And Persistence Behavior

This file stores no process state and performs no I/O. The mutable state represented by the constants lives in DCE 6.0 display hardware registers. Writes made with these masks persist in the device until the driver reprograms the register, a modeset or page flip updates latched state, an interrupt acknowledgement clears sticky status, a power-management transition resets a block, or a GPU reset/suspend-resume sequence restores display state.

Important persistent or latched state categories represented by this chunk include HDMI infoframe and packet generation state, CSC/gamma/regamma/LUT programming, overlay surface address and tiling state, scaler ratios and coefficient RAM state, line-buffer memory split and priority watermarks, vblank/vline interrupt masks and sticky acknowledgements, LVDS/eDP-style power-sequencing state, TMDS/UNIPHY link and transmitter electrical state, PLL clock state, VGA compatibility state, MCIF/DMIF and pipe power-gating status, MVP FIFO/CRC/debug state, and XDMA transfer/configuration/status state.

Several fields are sequencing-sensitive. `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `MASTER_UPDATE_*`, `PLL_UPDATE_*`, `OVL_UPDATE`, `SCL_UPDATE`, power-gate status, LVTMA power-sequence target/done state, FIFO reset/ack bits, and interrupt clear/ack bits require caller-side ordering. The macros do not encode whether a bit is write-one-to-clear, read-only status, latch control, or ordinary configuration; the call site must know the hardware contract.

## Dependencies And Integration Points

This chunk depends on the rest of `dce_6_0_sh_mask.h` for include guard context and for fields that start before line 7462. It also depends on companion DCE 6.0 offset/register definition headers, especially the `mm...` register address symbols used by AMDGPU/DC code.

Direct include users in this tree include `amd/amdgpu/dce_v6_0.c`, `amd/amdgpu/gfx_v6_0.c`, `amd/amdgpu/gmc_v6_0.c`, `amd/amdgpu/si.c`, `amd/pm/legacy-dpm/si_dpm.c`, and DCE 6.0 DC files such as `display/dc/dce60/dce60_timing_generator.c`, `display/dc/hwss/dce60/dce60_hwseq.c`, `display/dc/resource/dce60/dce60_resource.c`, and `display/dc/irq/dce60/irq_service_dce60.c`.

The primary integration surfaces are DRM/KMS modesetting, CRTC timing and vblank handling, HDMI/DP audio and infoframe setup, panel and encoder link bring-up, color management and gamma LUT programming, overlay plane scanout, scaler setup, display memory fetch and arbitration, pipe power gating, legacy VGA handling, display PLL programming, suspend/resume restoration, debug/CRC paths, and XDMA-based display data movement.

The names are ASIC-generation specific. Many register fields have close analogs in DCE 8/10/11/12 and DCN headers, but those versions may have different offsets, replicated instance names, or additional/missing fields. Mixing DCE generation headers with the wrong offset table is a high-risk integration error.

## Risks And Edge Cases

The highest risk is silent numeric drift from the authoritative AMD register database. The compiler validates macro syntax, not hardware correctness. An incorrect mask or shift can modify adjacent fields, leave a status bit uncleared, disable a clock or lane, corrupt a surface address, or destabilize display timing while still building cleanly.

This is a partial file chunk. It starts after the first `HDMI_INFOFRAME_CONTROL0` mask in the previous chunk and ends at the `#endif` for the header. The final merged per-file report should not treat the beginning as a complete HDMI family, but it can treat the end as the end of the source file.

Packed fields are common. CSC coefficients, prescale bias/scale, regamma regions, viewport/geometry fields, PLL dividers, link electrical settings, VGA page addresses, and XDMA addresses/pitches often share 32-bit registers. Off-by-one shifts, signedness assumptions, or stale field widths can cause adjacent channel, clock, address, or status corruption.

Interrupt and status fields are easy to misuse because many names have parallel mask, status, occurred, ack, clear, and interrupt bits. Examples include HDMI error bits, MVP FIFO status, SCL coefficient conflict, VGA interrupt status/clear, XDMA interrupt/NACK fields, MC interface NACK fields, and vblank/vline status. Writing a status mask where an ack mask is required can lose events or leave interrupts asserted.

Clock, link, and panel power fields have visible failure modes. Wrong PLL, UNIPHY, TMDS, SYMCLK, LVDS, or LVTMA power-sequence fields can produce blank displays, unstable link training, incorrect color depth, stuck backlight/panel power, or failure to resume after suspend.

Memory-fetch and DMA fields can cause underflow or memory faults. Overlay tiling/address fields, MCIF/VMID/privilege fields, pipe buffer allocation, priority marks, low-power tiling, and XDMA master/slave configuration must agree with framebuffer layout, memory controller setup, and display timing.

## Test Signals

There are no meaningful unit tests for this header chunk alone. Useful validation starts with build coverage for DCE 6.0 AMDGPU/DC configurations that include `dce_6_0_sh_mask.h`, ensuring all macro names used by call sites resolve.

Generated-header integrity should be checked against the authoritative DCE 6.0 register database or a known-good upstream header. Focus areas for this chunk are the partial `HDMI_INFOFRAME_CONTROL0` boundary, packed CSC/regamma/prescale fields, interrupt ack/mask/status bits, pipe 0-5 repeated fields, PLL/UNIPHY electrical fields, VGA compatibility fields, XDMA address/NACK/urgent fields, and the final commented block before `#endif`.

Runtime validation signals include successful modeset on DCE 6.0 hardware, stable vblank/vline interrupt delivery and acknowledgement, correct HDMI/DP audio/infoframe behavior, correct LUT/gamma/color conversion output, no display underflow or FIFO error interrupts, working overlay/scaler configurations, correct panel backlight/power sequencing, stable suspend/resume, and no link-training or PLL lock failures.

Targeted diagnostic tests should exercise interlaced and progressive scanout (`DATA_FORMAT`), vblank/vline interrupt enable and ack paths, color LUT reload, overlay primary/secondary address flips, scaler coefficient updates, HDMI AVMUTE and infoframes, VGA legacy register access if enabled, pipe power-gate status transitions, and XDMA master/slave NACK/underflow/urgent reporting.
