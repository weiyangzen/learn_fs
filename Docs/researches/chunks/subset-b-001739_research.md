# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 42016-44533

## Scope

This chunk covers a generated DCN 3.0.1 shift/mask header slice for AMD display hardware registers. It contains only preprocessor constants and generated grouping comments; there are no C functions, structs, enums, or executable statements in this range.

The slice begins inside the `MPCC_OGAM3` output-gamma register family and then covers these address blocks:

- `dce_dc_mpc_mpc_cfg_dispdec`
- `dce_dc_mpc_mpc_ocsc_dispdec`
- `dce_dc_mpc_mpc_rmu_dispdec`
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_opp_abm0_dispdec`
- `dce_dc_opp_abm1_dispdec`

The chunk ends partway through the `ABM1_DC_ABM1_HG_MISC_CTRL` register, so final per-file reconciliation should merge it with the next chunk for the complete ABM1 block.

## Purpose

This region is part of the generated hardware ABI used by AMDGPU Display Core to program DCN 3.0.1 display-pipeline blocks. Each exported macro gives either the bit shift or bit mask for a named hardware register field. Runtime display code does not call into this file directly; instead, register helper macros such as `SF`, `ABM_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and related DC register-table builders concatenate register and field names to resolve these constants at compile time.

At a hardware level, this chunk describes:

- MPCC output-gamma RAM A/B region layout and gamut remap fields for MPCC/OGAM instance 3.
- MPC global configuration fields for clocks, soft reset, CRC capture, pending-update status, vupdate locks, and DWB muxing.
- MPC output path muxing, flow control, denormalization clamps, output color-space-conversion coefficient format, and per-output CSC matrices for outputs 0-3.
- MPC RMU routing, memory power controls, shaper LUT programming, shaper RAM A/B region descriptors, and 3D LUT programming for RMU instances 0 and 1.
- DC perfmon instance 21 counter control, state, interrupt, and readback fields.
- ABM0 and the beginning of ABM1 backlight/PWM, adaptive backlight, histogram, luma-statistics, sample-rate, and register-lock fields.

The main value of this file is keeping implementation code symbolic. Driver code can request fields like `MPC_OUT0_MUX__MPC_OUT_FLOW_CONTROL_COUNT_MASK` or `ABM0_DC_ABM1_HGLS_REG_READ_PROGRESS__ABM1_HG_REG_READ_MISSED_FRAME_CLEAR_MASK` without duplicating fragile numeric bit layouts.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The exported interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: numeric bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.
- Register comments such as `//MPC_CRC_CTRL` and address-block comments such as `// addressBlock: dce_dc_mpc_mpc_rmu_dispdec` preserve the generated register grouping.

Important macro families in this chunk are:

- `MPCC_OGAM3_MPCC_OGAM_RAMA_*` and `MPCC_OGAM3_MPCC_OGAM_RAMB_*`: output-gamma RAM A/B start, start slope, start base, end, offset, and region descriptor fields. Region registers pair two regions per register, with LUT offset fields and segment-count fields for regions 0-33.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_C*`: gamut-remap coefficient format, mode/current mode, and double-buffered A/B coefficient fields for a 3x4 style matrix.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, and `MPC_CRC_RESULT_*`: MPC clock/test-clock controls, resets for MPCC/SFR/SFT/global MPC blocks, CRC enable/update/source selection, CRC input selection, and CRC readback result fields.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC`: pending update status bits for DPP surface/config/cursor updates, OPP config updates, MPCC config updates, and DWB config updates.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET<n>`, `ADR_CFG_VUPDATE_LOCK_SET<n>`, `ADR_VUPDATE_LOCK_SET<n>`, `CFG_VUPDATE_LOCK_SET<n>`, and `CUR_VUPDATE_LOCK_SET<n>`: per-pipe vupdate lock request bits for coordinated address, config, and cursor updates.
- `MPC_DWB0_MUX`: DWB mux selection and readback/status fields.
- `MPC_OUT<n>_MUX`, `MPC_OUT<n>_DENORM_*`, and `MPC_OUT<n>_CSC_*`: output mux selection, rate/flow-control error and control bits, denormalization min/max clamp fields, CSC mode/current mode, coefficient format, and A/B double-buffered CSC matrix coefficients for outputs 0-3.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux selections/status and force/disable/state fields for RMU0/RMU1 shaper and 3D LUT memories.
- `MPC_RMU<n>_SHAPER_*`: shaper LUT mode/current mode, per-channel offsets/scales, LUT index/data/write controls, RAM A/B start/end descriptors, and RAM A/B region descriptors for RMU instances 0 and 1.
- `MPC_RMU<n>_3DLUT_*`: 3D LUT mode, size, current mode, index, 16-bit paired data, 30-bit data, read/write controls, output normalization factor, and per-channel output offset/scale fields.
- `DC_PERFMON21_*`: counter event selection, counted-value type, hardware start/stop selection, per-counter state, perfmon state/report count, counter-off interrupt controls, interrupt status/ack fields, high/low counter value readback, and read selector fields.
- `ABM0_BL1_PWM_*` and `ABM1_BL1_PWM_*`: ambient/user/target/current ABM levels, final/minimum PWM duty cycle, ABM enable policy, backlight update sample rate, and grouped register lock/update bits.
- `ABM0_DC_ABM1_*` and early `ABM1_DC_ABM1_*`: adaptive backlight controls, input CSC coefficient selection, HGLS register-read progress/missed-frame clear fields, histogram controls, luma-statistics readbacks, sample-rate controls, histogram bin shift/index masks, histogram results, and backlight master lock.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. ASIC-specific DCN 3.0.1 resource or block code includes the generated offset and shift/mask headers.
2. Register-list macros such as `SF(...)` and `ABM_SF(...)` expand a symbolic register and field pair into `.mask` and `.shift` table entries.
3. Runtime helpers use those generated tables to compose MMIO values, perform read/modify/write operations, poll status bits, or decode readback fields.
4. Hardware sequencing is implemented elsewhere, but it relies on these masks being correct for fields that must be programmed in a specific order, such as LUT index/data/write-enable sequences, double-buffered mode updates, register locks, and status/ack bits.

The ordering inside the chunk is generated and hardware-oriented. Most register comments are followed by all field `__SHIFT` defines and then all corresponding `_MASK` defines. Repeated instances are ordered numerically, such as MPC outputs 0-3 and RMU instances 0-1.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state that lives in DCN display registers:

- MPCC OGAM state includes output-gamma LUT selection/configuration, RAM A/B region layout, offsets, slopes, bases, and gamut-remap coefficient banks.
- MPC configuration state includes clock-gating/test-clock controls, soft reset bits, CRC capture state, CRC source selection, pending-update status, vupdate locks, and DWB mux routing.
- MPC output state includes OPP/MPCC muxing, flow-control and overflow/error acknowledgement bits, denormalization clamps, output CSC modes, active/current CSC bank selection, and matrix coefficients.
- RMU state includes mux routing, memory power-force/disable bits, memory power-state readbacks, shaper LUT contents, shaper region descriptors, 3D LUT mode/size/current mode, LUT memory contents, and output normalization/offset/scale fields.
- DC perfmon21 state includes event/counter configuration, counter active/state bits, interrupt enables/status/ack bits, and readback latch/select values.
- ABM state includes backlight target/current/final PWM levels, ABM enable policy, update sample rates, grouped update locks, histogram/luma-statistics controls and results, missed-frame indicators, and master locks.

Persistence is hardware-defined. Most programmed fields remain active until another MMIO write, a block reset, display reset, or ASIC reset. Status and readback fields can change asynchronously with frame timing, histogram collection, CRC capture, perfmon counting, or backlight processing. This header does not encode access permissions, volatility, locking requirements, or write-one-to-clear semantics; consumers must follow the relevant DC block programming model.

## Dependencies And Integration Points

This chunk depends on the generated DCN register model staying synchronized across companion headers and block code:

- The matching `dcn_3_0_1_offset.h` provides register offsets that pair with these field definitions.
- AMD Display Core register helpers consume these macros through generated tables in block headers, especially MPC code such as `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`.
- ABM tables in `drivers/gpu/drm/amd/display/dc/dce/dce_abm.h` consume the `ABM0_DC_ABM1_*` and `ABM0_BL1_PWM_*` field names through `ABM_SF(...)` lists.
- Resource files for DCN generations list shared MPC registers such as `MPC_CRC_CTRL`; this header supplies field placement for DCN 3.0.1-specific builds.
- Color management paths depend on the MPCC OGAM, gamut-remap, output CSC, shaper, and 3D LUT fields to upload curves and matrices.
- Diagnostics and validation paths depend on MPC CRC and DC perfmon masks to select sources, enable counters, acknowledge interrupts, and read results.
- Backlight and panel power/brightness paths depend on the ABM/PWM fields for target levels, update cadence, luma statistics, histogram readback, and lock sequencing.

The direct interface is the preprocessor name contract. If a macro is missing or renamed, users generally fail at compile time. If a numeric mask or shift is wrong, code can still compile and perform incorrect MMIO writes, which is a higher-risk failure mode.

## Risks And Edge Cases

- The chunk starts inside `MPCC_OGAM3_MPCC_OGAM_LUT_CONTROL` and ends inside `ABM1_DC_ABM1_HG_MISC_CTRL`. Per-file reconciliation must merge neighboring chunks before making completeness claims about either register family.
- The register families are highly repetitive. Generator drift in one MPCC/RMU RAM region, one MPC output, or one ABM instance can be hard to notice in review while affecting only a specific pipeline or output.
- Many color fields are double-buffered or banked (`A`/`B`, current-mode fields, LUT RAM selectors). A mask drift can cause updates to land in the wrong bank or report the wrong active bank, producing color-management failures that are hard to attribute to the generated header.
- Full-register and high-bit masks, such as histogram results, perfmon values, 30-bit LUT data, lock bits, interrupt acks, and master locks, require unsigned-width-safe handling by callers.
- Some fields are read-only status, some are control bits, and some are write-one-to-clear acknowledgements. The shift/mask header does not distinguish them, so caller misuse is possible even when the macro values are numerically correct.
- Reset and memory-power fields are sensitive. Incorrect `MPC_SOFT_RESET` or `MPC_RMU_MEM_PWR_CTRL` masks could leave MPC, RMU shaper, or 3D LUT memories disabled, reset, or powered unexpectedly.
- Pending-update and vupdate-lock masks participate in frame-synchronized programming. Wrong masks can create update races, stuck pending states, or missed cursor/address/config commits.
- Flow-control error acknowledgement bits in `MPC_OUT<n>_MUX` are adjacent to selection and rate-control fields. Incorrect read/modify/write composition could accidentally clear errors or alter output routing.
- DC perfmon interrupt status and ack fields share one register family. Bad masks can lose performance-counter interrupts or acknowledge the wrong counter.
- ABM HGLS missed-frame clear bits are high-bit fields in a register that also reports in-progress and missed-frame status. Wrong masks can leave stale missed-frame state or clear the wrong channel's state.
- Cross-ASIC reuse is risky. Similar field names exist in neighboring DCN headers, but this file is specifically for DCN 3.0.1 and should not be assumed identical to DCN 3.0.0, DCN 3.1, or later ASICs.

## Test Signals

Useful validation is mostly build-time, register-table, and hardware-integration oriented:

- Compile AMDGPU Display Core for DCN 3.0.1 with warning coverage enabled to catch missing field names in `SF`, `ABM_SF`, `REG_*`, and resource-table expansions.
- Preprocess or build MPC and ABM users that reference `MPC_OUT0_MUX`, `MPC_RMU0_3DLUT_*`, `MPCC_OGAM0/3_*`, `ABM0_DC_ABM1_*`, and related field names.
- Compare this header against the matching offset header and the upstream register-generation source to ensure every register field has a matching offset and that the generated masks are in the expected bit positions.
- Exercise color-management paths on DCN 3.0.1 hardware: output gamma LUT upload/readback, gamut remap, output CSC programming, shaper LUT upload, and 3D LUT upload, including bank-switch/current-mode validation.
- Run display CRC tests through the DRM debug/CRC paths to validate `MPC_CRC_CTRL`, source selection, update locking, one-shot/continuous capture, and result registers.
- Exercise multi-pipe updates with surface, cursor, and config commits, checking pending-status and vupdate-lock behavior across pipes 0-3.
- Validate DWB routing if supported by the platform, including mux status readback.
- Run perfmon smoke tests for DC perfmon21: event selection, counter enable, state reporting, interrupt status/ack, and high/low value readback.
- Exercise ABM/backlight behavior on panels that support it: user level, target/current ABM level, final duty cycle, sample-rate programming, register-lock updates, luma statistics, histogram result reads, missed-frame clear paths, suspend/resume, and display reset.

## Open Cross-Chunk Questions

- The final per-file report should merge adjacent chunks to represent the full `MPCC_OGAM3` and `ABM1` register families.
- Whole-file reconciliation should verify whether DCN 3.0.1 intentionally exposes only the RMU fields shown here for both instances or whether additional RMU controls live in adjacent chunks.
- If generation provenance is available, the final report should identify the source register database or import path because hand-editing these numeric masks would be unusually high risk.
