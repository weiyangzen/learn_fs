# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 7764-11652

## Scope And Purpose

This chunk is a generated-style AMD DCE 10.0 register shift/mask header section. It contains only C preprocessor constants for bitfield masks and shifts; there are no functions, structs, enums, or executable branches. The mapped range starts mid-register at `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2` and ends at `PLL_CNTL__PLL_VCOREF__SHIFT`, so the first and last register groups are partial chunk boundaries.

The purpose is to give AMDGPU and display code symbolic access to DCE 10.0 hardware fields for Display Microcontroller Unit interrupt routing, DisplayPort link/AUX handling, DVO output, framebuffer compression, formatter/dithering, line buffer and multi-view pipe state, scaler/filter setup, color management, unpinned graphics plane programming, legacy VGA compatibility, DAC calibration, and display PLL programming.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. Each register field is expressed as a paired `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` definition. Consumers typically use helpers such as `REG_SET_FIELD()` or direct `(value & MASK) >> SHIFT` / `(field << SHIFT) & MASK` expressions together with the sibling DCE 10.0 address header.

Important macro families in this chunk include:

- DMCU performance-monitor interrupt routing: `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2` through `MASK5`, `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` through `SEL5`, and `DMCU_PERFMON_INTERRUPT_TO_HOST_EN_MASK1` through `MASK5` route DCI, DCO, DCCG, DCFE0-5, WB, DCRX, and DCFEV performance counter interrupts to the microcontroller, XIRQ/IRQ selection, or host.
- DMCU DPRX interrupt reporting and routing: `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` cover stream events, vertical interrupts, SDP/MSA reception, VBID toggles, DisplayPort PHY error thresholds, loss of alignment/deskw, excessive error events, AUX/I2C/CPU interrupts, and AUX message timeouts.
- DisplayPort main-link and secondary-data controls: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_MSA_MISC`, timing, `DP_DPHY_*`, CRC, fast-training, MSA overrides, secondary packet/audio/timestamp controls, and MST/MSE rate-allocation registers define link framing, lane count, pixel encoding, TU, training, PRBS, scrambling, CRC, audio packetization, and multi-stream bandwidth state.
- AUX and GTC synchronization: `AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, `AUX_LS_DATA`, `AUX_DPHY_*`, `AUX_GTC_SYNC_*`, and `DP_AUX_DEBUG_*` describe AUX transaction command/status, HPD/AUX arbitration, I2C-over-AUX, low-speed data, PHY controls, global-time-code sync, phase offset, and debug readback.
- DVO and FBC: `DVO_ENABLE`, `DVO_SOURCE_SELECT`, `DVO_OUTPUT`, `DVO_CONTROL`, DVO CRC/FIFO/debug fields, plus `FBC_CNTL`, `FBC_IDLE_*`, `FBC_COMP_*`, `FBC_IND_LUT*`, CSM/client-region fields, debug CSR fields, `FBC_MISC`, and `FBC_STATUS` describe digital video output and framebuffer compression control/status.
- Formatter, line buffer, and multi-view pipe: `FMT_*` fields cover clamping, dynamic expansion, forced output, bit-depth conversion, truncation, dithering, CRC, and debug. `LB_*` and `LBV_*` cover line-buffer format, memory sizing, vline/vblank interrupts, urgency/status, keying, counters, and debug for primary/video paths. `MVP_*` covers AFR flip behavior, FIFO status, in-band controls, CRC, receive counters, and debug.
- Scaler and viewport programming: `SCL_*` and `SCLV_*` fields define coefficient RAM access, mode, tap selection, filter scale ratios/init phases, manual/automatic replication, bypass/update controls, viewport and overscan rectangles, mode-change detection, chroma-plane video-scaler parameters, and test/debug access.
- Color management and gamma: `COL_MAN_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `PRESCALE_*`, `DENORM_CLAMP_*`, `GAMMA_CORR_*`, and debug fields describe CSC matrix coefficients, prescale values, denormal clamp ranges, gamma LUT index/data/write enable, and piecewise gamma-region controls for A/B segments.
- Unpinned graphics plane: `UNP_GRPH_*` fields cover enablement, format/tiling/bank/pipe controls, stereo, swap controls, primary/secondary luma/chroma surface addresses, high address words, pitch, offsets, start/end coordinates, update pending/lock behavior, in-use addresses, data-fabric queue status, flip interrupts, CRC, rotation, and debug.
- VGA compatibility and legacy indexed registers: `GENMO_*`, `SEQ*`, `CRT*`, `GRA*`, `ATTR*`, `VGA_RENDER_CONTROL`, `VGA_SOURCE_SELECT`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_MEMORY_BASE_ADDRESS*`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA interrupt/status/clear/debug/page fields, and `VGADCC_DBG_DCCIF_C` describe legacy VGA register access and routing onto modern display pipes.
- Analog DAC and PLL controls: `BPHYC_DAC_MACRO_CNTL`, `BPHYC_DAC_AUTO_CALIB_CONTROL`, `PLL_REF_DIV`, `PLL_FB_DIV`, `PLL_POST_DIV`, `PLL_SS_*`, `PLL_DS_CNTL`, `PLL_IDCLK_CNTL`, and the initial `PLL_CNTL` fields define DAC white level/bandgap/monitoring/calibration and display PLL dividers, spread spectrum, delta-sigma modulation, IDCLK outputs, differential post-divider behavior, current/drive strength, reset, power-down, bypass, post-divider source, and VCO reference bits.

## Control Flow And Data Flow

This header chunk has no runtime control flow. Its data flow is compile-time substitution into register access sequences in DCE 10.0 display, AMDGPU, and power-management code.

The implied hardware flows are still important:

- Interrupt routing fields select whether DMCU-visible performance and DPRX events are delivered to firmware, a selected XIRQ/IRQ line, or the host.
- DisplayPort programming combines link-control, pixel-format, timing, DPHY, CRC, secondary-data, and MST/MSE fields with per-encoder register offsets to bring up or validate a link.
- AUX programming writes command/address/data fields, arbitrates SW versus HPD/AUX access, then polls status, reply, timeout, defer, or error fields.
- Formatter, line-buffer, scaler, color-management, and unpinned-graphics fields are programmed in display pipe update sequences, often using locked/update-pending bits so plane, scaler, color, and timing state changes become visible at a safe point.
- FBC fields describe enable/compression/mode/LUT/state registers that compression management code can program and then inspect through status/debug fields.
- VGA fields bridge indexed legacy VGA state to DCE display pipes, including source selection, surface addresses, sequencer reset behavior, memory access status, interrupt masking, and page-address windows.
- PLL and DAC fields are low-level hardware sequencing inputs; callers must reset/power/calibrate/program dividers in the order required by the ASIC and board tables.

## State And Persistence Behavior

The header stores no state. Persistent and mutable state lives in DCE 10.0 MMIO registers, indexed VGA registers, display firmware/DMCU-visible interrupt state, display pipe shadow registers, framebuffer-compression state machines, AUX transaction state, DP link-training status, DAC calibration logic, and PLL hardware.

State classes represented by this chunk include:

- Latched or sticky event state: DMCU DPRX interrupt status, AUX interrupt/status bits, DP CRC results, DVO FIFO errors, FBC status, LB/LBV vline and vblank status, MVP FIFO/status counters, VGA access/interrupt status, and DAC calibration completion.
- Mutable configuration state: DP link enable/lane/pixel/timing/training, AUX command/arbitration/PHY settings, DVO output source, FBC enable/mode/LUTs, formatter dithering/truncation/CRC, line-buffer formats and urgency thresholds, scaler taps/ratios/viewports, CSC/gamma tables, UNP surface addresses and format, VGA mode/source/page controls, DAC calibration controls, and PLL divider/spread-spectrum controls.
- Shadowed update state: plane addresses, viewport/overscan, scaler coefficients, color-management tables, and unpinned graphics update locks/pending flags are designed to synchronize hardware-visible display changes.
- Hardware-derived diagnostic state: DP/AUX debug readbacks, FBC debug CSR data, MVP and VGA debug data, DPHY error/CRC counters, line-buffer status, and PLL/DAC monitor fields.

Incorrect constants can persist until the relevant block is reprogrammed or reset. For example, a wrong surface-address, scaler, gamma, or PLL mask can affect active scanout; a wrong interrupt mask can hide hotplug/AUX/DPRX errors; a wrong FBC field can leave compression in an invalid state; and a wrong VGA memory-control bit can expose or block legacy apertures.

## Dependencies And Integration Points

This header is included by DCE 10.0 display and VI-era AMDGPU code, including `amdgpu/dce_v10_0.c`, `amdgpu/vi.c`, `amdgpu/mxgpu_vi.c`, `amdgpu/gmc_v8_0.c`, `amdgpu/gfx_v8_0.c`, DC DCE100 resource/hwseq code, and legacy PowerPlay/SMU managers such as Tonga, Fiji, Iceland, and Polaris paths. It is normally paired with DCE 10.0 register address definitions and AMDGPU register helpers (`RREG32`, `WREG32`, `REG_SET_FIELD`, and offset-based CRTC/encoder access).

Concrete repository usage in this namespace includes `dce_v10_0.c` programming `FMT_BIT_DEPTH_CONTROL` through `REG_SET_FIELD()` for display dithering/truncation based on framebuffer depth. Similar DCE generations use the same mask/shift style directly, so these macros are part of a shared AMD display-driver idiom even when some fields in this chunk are consumed only on specific ASICs, boards, firmware paths, or diagnostic flows.

Major integration surfaces are:

- DRM/KMS mode setting, CRTC, encoder, connector, and plane code for display format, timing, scaler, viewport, color, and scanout-address programming.
- DisplayPort link training, MST allocation, secondary-data/audio packet generation, and AUX/I2C transaction handling.
- DMCU and host interrupt plumbing for performance counters, DPRX events, AUX events, vline/vblank-like line-buffer events, VGA events, and error/status clear flows.
- Power-management and BACO/SMU paths that include the header for display PLL, clock, DAC, compression, or DCE power/display state programming.
- Legacy VGA emulation and early boot/display handoff code that must map indexed VGA registers and VGA apertures onto DCE display pipes.
- Hardware diagnostics, debugfs-style readback, bring-up scripts, and ASIC validation paths that rely on debug indices/data, CRC results, PRBS/training, FBC status, and FIFO/error counters.

## Risks And Edge Cases

The primary risk is drift between generated constants and the DCE 10.0 register specification. Since many consumers write hardware with generic field helpers, the compiler cannot detect an incorrect mask value or shift position.

Specific high-risk areas in this chunk are:

- Chunk boundaries: line 7764 starts after the first field of `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2`, and line 11652 stops before the rest of `PLL_CNTL`; full-register conclusions require adjacent chunk research.
- Repeated bit layouts across pipes and paths: DCFE0-5, D1-D6 VGA controls, LB/LBV, SCL/SCLV, and luma/chroma UNP address fields are easy to copy incorrectly because names differ only by pipe, plane, or component suffix.
- Interrupt mask/status naming: fields with `MASK_MASK`, `INT_MASK`, `STATUS`, `CLEAR`, `TO_UC_EN`, `TO_HOST_EN`, and `XIRQ_IRQ_SEL` have similar names but different semantics; confusing enable, mask, route, clear, and status bits can drop or storm interrupts.
- DisplayPort/AUX training sensitivity: incorrect DPHY, AUX timing, CRC, PRBS, or fast-training fields can cause link-training failures, AUX timeouts, or false error reporting.
- Atomic display updates: surface address, scaler, viewport, color, and update-lock bits must line up with hardware shadow/update behavior; wrong masks can produce tearing, bad scanout, or stale register programming.
- FBC and line-buffer state: compression and buffer-urgency fields affect memory bandwidth and scanout correctness; wrong values can cause corruption or underflow.
- VGA compatibility: legacy indexed registers, aperture paging, sequencer reset, and memory-disable bits can affect boot consoles, handoff, and host-visible VGA behavior.
- Analog and PLL programming: DAC calibration and PLL divider/spread-spectrum fields are board/ASIC-sensitive; bad masks can produce unstable clocks, no display output, or analog signal-quality failures.

## Test Signals

There are no unit tests for this header alone. Useful validation is mostly build, generated-header comparison, and hardware integration testing:

- Build AMDGPU and DC configurations that include `dce_10_0_sh_mask.h`; this catches missing or renamed macros but not wrong numeric values.
- Compare the chunk against the authoritative AMD DCE 10.0 register database or an upstream generated copy, paying special attention to the partial `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK2` and `PLL_CNTL` boundaries.
- Exercise DCE 10.0 display mode setting across multiple CRTCs and formats; verify `FMT_BIT_DEPTH_CONTROL`, scaler, viewport, color, line-buffer, and UNP surface programming by visual output and register readback.
- Run DisplayPort link-training, MST, audio/secondary-data, AUX/I2C, hotplug, and error-path tests that validate DP, AUX, DPRX, and DMCU interrupt fields.
- Validate vblank/vline, AUX, VGA, and DPRX interrupt mask/status/clear behavior with interrupt counters and timeout/error injection where possible.
- Test FBC enable/disable, idle behavior, compression status, and debug readback under scanout workloads.
- Exercise legacy VGA handoff or VGA-compatible modes to verify source selection, sequencer reset, aperture paging, VGA memory/reg access status, and D1-D6 pipe routing.
- Validate suspend/resume, power-management, DAC calibration, and PLL programming paths through display bring-up, clock readback, and signal/link stability tests.
