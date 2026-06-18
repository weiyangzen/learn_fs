# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 27782-30308

## Purpose

This chunk is a generated AMD DCN 4.2.0 shift/mask header slice for display pipeline registers. It contains no executable C logic; its public interface is a set of preprocessor constants that map register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for the DCN42 display pipeline.

The requested range contains 2,113 generated definitions and 400 commented register headings. It starts inside the `DSCL2` display scaler block, covers the rest of DSCL2 enhanced adaptive scaler and image-sharpening controls, covers the `CM2` color-management block, covers the `DC_PERFMON12` performance-monitor block, then starts DPP instance 3 with `DPP_TOP3`, `CNVC_CFG3`, `CM_CUR3`, `DSCL3`, and the beginning of `CM3` gamma-correction RAM metadata. The chunk boundary is artificial: DSCL2 started before line 27782, and the final `CM3_CM_GAMCOR_RAMB_REGION_*` series continues after line 30308.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO reads/writes in this range. The generated macro naming convention is the API:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the field mask within the same register.

The main register families in this chunk are:

- `DSCL2_DSCL_EASF_*`: enhanced adaptive scaler fields for horizontal and vertical ring-estimation force, blur-filter control, final max/min limits, BF1 piecewise-linear segments 0-7, and BF3 piecewise-linear segments 0-5. These define the tuning surface for adaptive sharpening/ringing behavior on DPP/scaler instance 2.
- `DSCL2_ISHARP_*`: image sharpening controls, delta LUT host/index/data fields, nonlinear delta soft clipping, noise-detection thresholds, noise-gain PWL fields, LBA PWL segments, and image-sharpening delta LUT memory-power control/status.
- `CM2_CM_*`: color-management fields for bypass/update state, post-CSC controls and matrix coefficients, bias, gamma-correction control, gamma LUT index/data/control, RAM A and RAM B gamma-correction region starts/slopes/bases/ends/offsets/region tables, HDR multiplier, memory-power control/status, dealpha, coefficient format, test-debug registers, and histogram controls/data/status/interrupt controls.
- `DC_PERFMON12_*`: display performance counter and perfmon control/state/value registers. This block names fields such as counter enable/reset/mode, event selection, perfmon state, manual trigger, and counter high/low/current-value fields.
- `DPP_TOP3_*`: DPP instance 3 top-level control, soft reset, CRC values/control, and host-read control.
- `CNVC_CFG3_*`: converter-format and pre-color-processing fields for DPP instance 3, including surface pixel format, format expansion/crossbar/clamping, fixed-point bias/scale, color/luma keyer limits, alpha 2-bit LUT values, pre-dealpha, pre-CSC mode/matrices, pre-degamma, and pre-realpha.
- `CM_CUR3_*`: cursor color-management fields for cursor mode/enable/expansion, color entries, floating-point scale/bias, and cursor matrix mode/coefficient sets.
- `DSCL3_*`: instance 3 scaler fields for coefficient RAM, scaler mode/taps, viewport/output sizes, line-buffer format/memory, update/autocal, overscan/blanking, scaler ratios/init values, memory power, output buffer, scaler color-conversion matrix, EASF, iSharp, and bottom-field vertical init values.
- `CM3_CM_*` beginning: DPP instance 3 color-management and gamma-correction RAM A/B field definitions. This chunk reaches only the early part of `CM3_CM_GAMCOR_RAMB_REGION_*`.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN42 display code includes `dcn_4_2_0_offset.h` and this matching `dcn_4_2_0_sh_mask.h`.
2. `dcn42_resource.c` builds per-instance DPP register tables with `DPP_REG_LIST_DCN42_COMMON_RI(id)` and initializes global `dcn42_dpp_shift` / `dcn42_dpp_mask` tables with `DPP_REG_LIST_SH_MASK_DCN42_COMMON(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN42_COMMON(_MASK)`.
3. `dcn42_dpp_create()` initializes `dpp_regs[0..3]` and passes the selected instance register table plus the shared shift/mask tables to `dpp42_construct()`.
4. Runtime DPP code uses generic register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_*`, `REG_GET`, and `REG_WAIT`. Those helpers consume the register offsets and these generated shift/mask values to program hardware fields.

The macros in this chunk do not describe programming order. Sequencing for scaler setup, sharpening, gamma LUT programming, CSC updates, cursor conversion, histogram reads, memory-power transitions, and perfmon sampling is implemented in DPP/resource/hardware-sequencer code and constrained by hardware behavior outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- DSCL2/DSCL3 scaler configuration: scaling modes, tap counts, coefficient RAM selectors/data, horizontal/vertical scale ratios, initial phases, recout/MPC dimensions, overscan, blanking windows, line-buffer memory layout, update-pending state, autocal parameters, scaler color-conversion matrix, EASF tuning, iSharp tuning, and scaler/LUT/output-buffer memory-power controls.
- CM2/CM3 color-management state: bypass/update-pending bits, pre/post CSC modes and matrices, bias and HDR multiplier, gamma-correction LUT RAM selection and current selection, LUT index/data access windows, RAM A/B PWL region descriptors, memory-power state, dealpha/coefficient format, histogram controls/data/status/lock, and test-debug muxes.
- CNVC_CFG3 and CM_CUR3 state: input format conversion, alpha handling, color keying, pre-degamma/pre-CSC/pre-dealpha/pre-realpha, cursor enable/mode/color, cursor FP scale/bias, and cursor matrix selection/current state.
- DPP_TOP3 state: DPP clock enable, soft reset, CRC capture/readback, and host-read control.
- DC_PERFMON12 state: performance-counter control, selected event source, counter state, high/low/current-value registers, and manual/auto perfmon controls.

Persistence and side effects are hardware-defined. Configuration fields typically remain until modeset, plane update, pipe disable, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status fields can be latched, read-only, write-one-to-clear, double-buffered, or valid only while the relevant DPP/scaler/color block is powered and clocked. This file only supplies bit locations; it does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies matching register offsets and base-index values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes both generated headers, creates `dpp_regs[4]`, `tf_shift`, and `tf_mask`, and constructs DPP instances from those tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines the DPP register list. It expects many register names covered here, especially `CM_GAMCOR_*`, `CM_HIST_*`, `DSCL_*`, `CNVC_CFG_*`, and `CM_CUR_*` fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h` defines `DPP_REG_LIST_SH_MASK_DCN42_COMMON(mask_sh)`, `struct dcn42_dpp_shift`, and `struct dcn42_dpp_mask`. The macro uses instance-0 generated names, and `SRI_ARR` register lists bind the same generic field layout to instances 0-3.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.c` uses these fields for histogram control/readout and inherits DPP setup behavior from earlier DCN DPP implementations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c` and related DPP code consume the gamma-correction fields by copying shifts/masks into transform/gamma helper structures and programming RAM A/B LUTs, offsets, starts, slopes, end points, and region descriptors.

Behaviorally, this chunk is part of the DPP path that transforms plane pixels before composition/output. It describes register fields for scaling, sharpening, format conversion, cursor blending/color conversion, color correction, gamma correction, histogram collection, CRC/debug readback, and DPP-local performance monitoring.

## Risks And Edge Cases

- These constants are untyped preprocessor metadata. A wrong shift or mask can compile cleanly while silently programming the wrong hardware bits.
- The file is generated. Manual edits risk divergence from the authoritative register database, companion offset header, firmware expectations, and hardware documentation.
- Chunk boundaries are not semantic. The first lines start after earlier `DSCL2` scaler/EASF fields, and the final lines stop inside the `CM3_CM_GAMCOR_RAMB_REGION_*` table. Whole-block claims require adjacent chunks.
- The DPP shift/mask tables use instance-0 field names as the generic field layout while register offsets select each instance. Per-instance generated copies must remain structurally consistent; an instance-only mismatch can affect only DPP2 or DPP3 planes.
- DSCL/EASF/iSharp fields are image-quality sensitive. Incorrect masks for PWL segments, ring-estimation gains, noise thresholds, soft clipping, or delta LUT access can produce visible ringing, blur, oversharpening, flicker, or format-specific artifacts rather than obvious failures.
- Scaler ratio/init/tap/memory fields are timing and format sensitive. Bad values can cause underflow, incorrect chroma placement, wrong recout size, corruption on interlaced/bottom-field paths, or failures only at high scaling ratios.
- Gamma-correction RAM fields are double-buffer and RAM-select sensitive. Wrong masks for `CM_GAMCOR_SELECT`, `*_CURRENT`, region descriptors, offsets, start/end slopes, or LUT host/index/data access can swap RAM A/B unexpectedly, corrupt color curves, or cause tearing during color updates.
- Histogram fields use lock/index/data/status sequencing. Incorrect status or lock masks can cause stale reads, mixed buffer data, missed ready status, or repeated accumulation of old bins.
- Memory-power control/status fields are sequencing-sensitive. Bad masks can leave LUT/line-buffer/output-buffer/gamma memories powered off while programming or prevent expected power savings.
- DPP_TOP3 clock/reset/CRC fields can break a single pipe. A wrong clock-enable or soft-reset bit can disable instance 3, while CRC masks can make debug validation misleading.
- Perfmon field mistakes often appear only in diagnostics. Wrong event-select or counter-state masks can produce plausible but invalid performance data.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display coverage:

- Build DCN42 AMDGPU display support. Missing or renamed macros should surface in `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_dpp.h`, and DPP color/scaler implementation files.
- Mechanically compare this range against the authoritative DCN 4.2.0 register-field database and ensure each `_MASK` has the expected paired `__SHIFT`.
- Cross-check every register family in this chunk against `dcn_4_2_0_offset.h` so each field group has a corresponding register offset/base-index entry.
- Run static repeated-instance checks across `DSCL2` versus `DSCL3`, `CM2` versus `CM3`, `CNVC_CFG3`, and `CM_CUR3`, allowing intentional instance prefixes but flagging missing or shape-mismatched fields.
- Exercise scaling on planes routed through DPP2 and DPP3: upscaling, downscaling, chroma formats, alpha-enabled formats, interlaced/bottom-field paths, high-resolution/high-refresh modes, and rapid plane size changes. Watch for corruption, underflow, wrong recout/MPC dimensions, or stuck update-pending state.
- Exercise EASF/iSharp controls with visual/CRC comparisons and register dumps. Look for ringing, blur, clipping, noise gain anomalies, and correct delta LUT memory-power state.
- Validate color-management programming with gamma ramps, HDR multiplier changes, pre/post CSC matrices, bias, dealpha, RAM A/B gamma selection flips, and suspend/resume. Expected signals are correct color output, stable current-selection readback, and no stale LUT RAM selection.
- Exercise cursor formats and matrix paths on DPP3 with alpha and FP scale/bias variations.
- Read DPP histograms using `dcn42_dpp.c` paths across RGB/luma modes. Expected signals are ready status, correct lock/index/data sequencing, and plausible channel bin accumulation.
- Validate `DPP_TOP3` CRC and soft-reset behavior with display CRC/debug tooling where available.
- Exercise `DC_PERFMON12` counters through existing debug/perf instrumentation and confirm counter state, high/low values, and event selection match the selected DPP pipeline.

## Cross-Chunk Notes

The previous chunk owns the earlier DSCL2 scaler/EASF definitions before `DSCL2_DSCL_EASF_RINGEST_FORCE`. This chunk owns the DSCL2 EASF tail, DSCL2 iSharp, all visible CM2/perfmon/DPP_TOP3/CNVC_CFG3/CM_CUR3/DSCL3 definitions, and the beginning of CM3 gamma-correction metadata. The next chunk must complete `CM3_CM_GAMCOR_RAMB_REGION_*` and any remaining CM3 fields before a final per-file document makes whole-block claims about DPP3 color management.
