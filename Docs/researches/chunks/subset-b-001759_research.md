# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 19869-22375

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register bitfield header segment. It contains preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro for the bit offset and a `_MASK` macro for the bit mask. The assigned range spans 2,507 source lines, with 2,117 `#define` entries, 1,061 shift definitions, and 1,066 mask definitions.

The chunk starts inside the `CM2_CM_SHAPER_RAMB_*` definitions and ends inside `DC_PERFMON14_PERFCOUNTER_STATE`. The merge lane must stitch adjacent chunks before treating the opening CM2 shaper group or closing perfmon14 group as complete.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.2 display pipe programming in the AMDGPU display driver. Driver code includes this file, along with companion address and base-index headers, so register read-modify-write helpers can program MMIO fields without duplicating raw numeric constants.

The covered register surfaces are concentrated around DPP pipe 3 and the tail of DPP pipe 2:

- tail of `CM2` color-management shaper and 3D LUT state for DPP2.
- `DC_PERFMON13` performance counter controls for DPP2.
- `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3` display pipe 3 blocks.
- beginning of `DC_PERFMON14` performance counter controls for DPP3.

This is data-like source rather than executable logic. Its behavior is indirect: correctness depends on exact alignment with AMD's hardware register specification and with the corresponding `dcn_3_0_2` register-address header.

## Address Blocks And Register Surface

Visible address blocks:

- `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON13` performance counter control, counter state, perfmon control, interrupt/status, and low/high value fields for the DPP2 monitor.
- `dce_dc_dpp3_dispdec_dpp_top_dispdec`: `DPP_TOP3` clock, gate, soft-reset, CRC value/control, and host-read rate fields.
- `dce_dc_dpp3_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG3` pixel-format conversion, format expansion, alpha, color keyer, pre-dealpha, pre-CSC matrix, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp3_dispdec_cnvc_cur_dispdec`: `CNVC_CUR3` cursor enable, mode, color, floating-point scale, and bias fields.
- `dce_dc_dpp3_dispdec_dscl_dispdec`: `DSCL3` scaler coefficient RAM, scaling mode/taps/ratios/inits, overscan, recout/MPC size, line-buffer format/memory, scaler and output-buffer memory power, and update/status fields.
- `dce_dc_dpp3_dispdec_cm_dispdec`: `CM3` color-management controls, post-CSC, gamut remap, gamma correction, blend gamma, HDR multiplier, dealpha, shaper LUT, 3D LUT, memory power, and debug fields.
- `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: starts `DC_PERFMON14` counter control and state fields for DPP3; the range ends before the `PERFCOUNTER_STATE` register is fully listed.

## Important Macros And Register Families

`CM2_CM_SHAPER_RAMB_*` continues the DPP2 color-management shaper RAM-B region table. The visible fields define per-channel end controls for B/G/R and paired region descriptors from `REGION_0_1` through `REGION_32_33`. Each region descriptor packs two piecewise-linear region LUT offsets and segment counts into one register, using 9-bit offset masks and 3-bit segment-count masks. `CM2_CM_MEM_PWR_CTRL2`, `CM2_CM_MEM_PWR_STATUS2`, `CM2_CM_3DLUT_*`, and `CM2_CM_TEST_DEBUG_*` expose shaper/HDR 3D LUT memory power, 3D LUT mode/size/current state, index/data access, 30-bit data access, RAM selection/write/read controls, output normalization and RGB offset/scale, and test-debug index/data fields.

`DC_PERFMON13_*` defines the DPP2 performance-monitor programming interface. `PERFCOUNTER_CNTL` selects events, counted value, increment mode, hardware control, run-enable mode, restart, interrupt enable, off-mask behavior, active state, and counter selector. `PERFCOUNTER_CNTL2` selects counted value type, hardware stop inputs, counter-off source, and counter-control selector. `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` define state selection, report count, counter-off interrupt status/acknowledge, clock enable, run-enable start/stop sources, per-counter interrupt bits, and counter value readback.

`DPP_TOP3_*` defines top-level DPP3 control bits. These include DPP clock enable, static/dynamic clock-gate disables, DSCL gate disable, DISPCLK/DPPCLK gate controls, test clock selection, CNVC/DSCL/CM/OBUF soft resets, CRC result registers, CRC enable/one-shot/status/source/pixel-format/cursor-format/mask fields, and host-read rate control.

`CNVC_CFG3_*` defines the converter configuration path before scaling/color management. It covers surface pixel format and alpha-plane enable, format expansion and 16-bit conversion, CNVC bypass/MSB alignment, positive clamps, update-pending status, RGB crossbar selection, floating-point bias/scale for R/G/B, color-keyer enable/alpha and low/high thresholds for RGB, four-entry 2-bit alpha LUT, pre-dealpha and pre-realpha enable/ABLND enable, pre-CSC mode/current mode, primary and alternate 3x4 pre-CSC matrices, coefficient format, and pre-degamma mode/select.

`CNVC_CUR3_*` defines a narrow cursor surface for pipe 3: cursor0 enable, expansion mode, pixel inversion, ROM enable, mode, pixel-alpha modulation, update-pending status, two 24-bit cursor colors, and floating-point scale/bias.

`DSCL3_*` defines DPP3 scaler and line-buffer fields. The coefficient RAM fields select tap pair, phase, filter type, and even/odd tap coefficients with enable bits. Scale mode fields select scaler mode, coefficient RAM bank and current/readback bank, chroma/alpha coefficient modes, luma/chroma tap counts, boundary mode, two-tap hard-coded/sharp mode and sharp factors, manual replicate factors, horizontal and vertical scale ratios and init phases for luma/chroma/top/bottom paths, black color, update-pending, autocal mode/pipe selection, external overscan, OTG blanking, recout start/size, MPC size, line-buffer interleave/alpha, memory partitioning, vertical counters, DSCL/LB memory power control/status, OBUF bypass/full-buffer/hold behavior, and OBUF memory power state.

`CM3_*` is the largest family in this range. It defines the DPP3 color-management pipeline: global bypass/update pending, post-CSC mode and A/B 3x4 matrices, gamut-remap mode and A/B 3x4 matrices, bias registers, gamma-correction controls and LUT access, gamma RAM A/B PWL region programming, blend-gamma controls and RAM A/B PWL region programming, HDR multiplier, CM memory power control/status, dealpha enable, coefficient formats, shaper control/offset/scale/LUT access, shaper RAM A/B region programming, shaper and HDR3DLUT memory power control/status, 3D LUT mode/index/data/read-write controls, output normalization and RGB offset/scale, and CM test-debug index/data.

`DC_PERFMON14_*` begins the DPP3 performance-monitor interface and mirrors the `DC_PERFMON13` structure for pipe 3. This chunk includes full `PERFCOUNTER_CNTL` and `PERFCOUNTER_CNTL2` definitions plus the start of `PERFCOUNTER_STATE`; masks for counter states 5 through 7 and following perfmon registers are outside the assigned range.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime control flow is represented by hardware programming sequences that consume these masks through AMDGPU register helpers.

The likely hardware flows represented here are:

- DPP3 pipe bring-up and reset sequencing: `DPP_TOP3_DPP_CONTROL` enables the pipe clock and controls clock gating, while `DPP_TOP3_DPP_SOFT_RESET` resets CNVC, DSCL, CM, and OBUF subblocks.
- Pixel conversion before scaling: `CNVC_CFG3_*` fields configure the source pixel format, alpha handling, color keying, crossbar, pre-CSC matrices, pre-degamma, and update-pending handshakes.
- Cursor composition preparation: `CNVC_CUR3_*` fields select cursor mode, color registers, ROM/pixel-inversion behavior, alpha modulation, and update-pending status.
- Scaling and viewport sizing: `DSCL3_*` fields program coefficient RAM, scaler mode, taps, ratios, init phases, overscan, recout/MPC size, line-buffer partitions, and OBUF behavior.
- Color-management programming: `CM3_*` fields program post-CSC, gamut remap, gamma correction, blend gamma, shaper curves, 3D LUT RAM selection/data, output normalization, and bypass/update state.
- Performance monitoring: `DC_PERFMON13_*` and `DC_PERFMON14_*` select events, value types, counter sources, run/stop conditions, interrupt behavior, and value readback for display performance counters.
- Memory-power management: `CM2_CM_MEM_PWR_*`, `DSCL3_DSCL_MEM_PWR_*`, `DSCL3_OBUF_MEM_PWR_*`, and `CM3_CM_MEM_PWR_*` expose force/disable/state bits for LUTs, line-buffer banks, OBUF, gamma/blend/shaper memories, and HDR 3D LUT memory.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe fields in persistent MMIO registers. Writes through these fields can change display hardware state until another write, block reset, GPU reset, suspend/resume restore, or mode-set reprogramming occurs.

Important state classes represented by this chunk:

- Double-buffer and update state: `*_UPDATE_PENDING`, `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `SCL_COEF_RAM_SELECT_CURRENT`, and `SCL_COEF_RAM_SELECT_RD` fields expose hardware-applied vs requested state. Consumers must sequence writes around vupdate or other hardware latch points.
- Indexed RAM state: `CM*_3DLUT_INDEX`, `CM*_3DLUT_DATA`, `CM*_SHAPER_LUT_INDEX`, `CM*_SHAPER_LUT_DATA`, `CM*_GAMCOR_LUT_*`, `CM*_BLNDGAM_LUT_*`, and `DSCL3_SCL_COEF_RAM_*` represent address/data style access to internal RAMs. The selected index, RAM bank, color mask, read selector, and write-enable fields are stateful programming context.
- Piecewise-linear curve state: gamma, blend-gamma, and shaper RAM A/B region definitions persist as hardware curve descriptors. Region offset/segment fields must match the LUT data layout programmed through the corresponding indexed data registers.
- Power state: memory force, disable, mode, and state fields expose low-power state machines. Incorrect writes can leave LUT or line-buffer memories forced on, disabled during active scanout, or inconsistent with status bits.
- Interrupt and acknowledgement state: perfmon counter-off and per-counter interrupt status/ack fields are latched hardware events; header masks do not encode write-one-to-clear or acknowledgement ordering semantics.
- Debug/readback state: CRC, performance counters, vertical counters, and CM test-debug registers expose diagnostic state rather than pure configuration.

## Dependencies And Integration Points

This chunk depends on companion generated DCN 3.0.2 headers for register addresses, base indices, and field aggregation. The naming convention is the AMDGPU DC convention where a register symbol, a field symbol, a `__SHIFT`, and a `_MASK` are combined by generated or hand-written register access macros.

Likely integration points include:

- DPP3 resource construction and pipe programming code in AMDGPU DC, especially CNVC, DSCL, CM, cursor, and DPP top helper code.
- Color-management code that loads transfer functions, shaper curves, blend/gamma curves, post-CSC/gamut matrices, and 3D LUT data.
- Scaler code that programs DSCL ratios, taps, coefficient RAM, recout/MPC dimensions, line-buffer partitioning, and overscan.
- Display diagnostics that use DPP CRC registers, DSCL counters, perfmon counters, and CM debug registers.
- Power-management and suspend/resume paths that restore DPP subblock memory power and indexed LUT state.
- Generated register tables that map generic block instances to instance-specific names such as `CM2`, `CM3`, `DSCL3`, `CNVC_CFG3`, `DPP_TOP3`, `DC_PERFMON13`, and `DC_PERFMON14`.

Because this is a public include within the AMDGPU source tree, compile-time consumers are sensitive to exact macro spelling. A rename, missing field, or bit-position drift can break builds or silently program the wrong hardware field.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift can corrupt neighboring fields in the same 32-bit MMIO register, causing display blanking, color errors, bad scaling, cursor artifacts, incorrect performance data, or power-management regressions.
- The assigned range starts and ends mid-block. `CM2_CM_SHAPER_RAMB_END_CNTL_B` starts before line 19869, and `DC_PERFMON14_PERFCOUNTER_STATE` continues after line 22375. File-level conclusions must merge adjacent chunks.
- Repeated RAM region tables are easy to misgenerate. Gamma, blend-gamma, and shaper RAM A/B each use many near-identical `REGION_N_N+1` macros, with offsets at bits 0 and 16 and segment counts at bits 12 and 28. Off-by-two or RAM A/B swaps would route PWL descriptors to the wrong curve bank.
- Several logical field names include the word `MASK`, producing generated names such as `CM3_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK` and perfmon off-mask fields. Parsers that naively split on `_MASK` can misclassify these.
- Status, ack, and current-state bits have hardware-specific semantics that are not represented in the header. Consumers must not infer safe write values solely from the mask constants.
- Indexed RAM programming is order-sensitive. Losing the selected index, RAM bank, 30-bit mode, color write mask, or host/config mode can corrupt LUT contents even when the individual masks are correct.
- Memory-power fields can interact with active scanout. Forcing or disabling DSCL, OBUF, gamma/blend, shaper, or HDR3DLUT memories at the wrong time can produce visible underflow, stale color data, or hangs.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display regression signals:

- AMDGPU DCN 3.0.2 compile coverage catches missing or renamed macros used by register tables and helper code.
- Generated-header checks should verify every `__SHIFT` has a corresponding `_MASK`, masks fit within 32 bits, repeated DPP2/DPP3 and RAM A/B families retain expected parity, and partial chunk boundaries are reconciled by adjacent chunks.
- Display mode-set tests should exercise DPP3 enable/reset, CNVC pixel formats, alpha, color-keying, cursor modes, DSCL scaling ratios/taps/coefficients, recout/MPC sizing, and line-buffer partitioning.
- Color-management tests should cover post-CSC, gamut remap, gamma correction, blend gamma, shaper LUTs, HDR 3D LUT mode/data paths, output normalization, and bypass/current-mode readbacks.
- Power tests should cover suspend/resume and runtime power transitions for DSCL LUT/LB banks, OBUF, CM gamma/blend/shaper memories, and HDR3DLUT memory.
- Diagnostic tests should compare DPP CRC results, perfmon13/perfmon14 counter programming/readback, interrupt ack behavior, DSCL vertical counters, and CM debug-index/data readback against expected hardware behavior.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of `CM2_CM_SHAPER_RAMB_END_CNTL_B` and any preceding CM2 shaper setup needed to describe the complete RAM-B programming surface.
- Confirm the next chunk completes `DC_PERFMON14_PERFCOUNTER_STATE` and includes the remaining perfmon14 control/value registers.
- Identify the concrete AMDGPU DCN 3.0.2 register tables and helper functions that consume the DPP3 `CNVC`, `DSCL`, `CM`, `DPP_TOP`, and `DC_PERFMON` macros before the final per-file report names call sites.
