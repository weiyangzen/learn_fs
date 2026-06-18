# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 37537-40041

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, variables, allocations, locks, callbacks, includes, or executable branches in this range.

The selected lines start in the tail of `ICG_SQ_CLK_CTRL`, with only the final shader-queue clock-override masks present in this chunk. The main body covers graphics clock-gating and power-related controls for SP, SX, TA, TD, DB, CB, RMI, PH, TCP, LDS, UTCL1, GRBMH, SC, and GL1 blocks; shader-array, render-backend, WGP/RB/SA remapping, and UTCL1 security fields; GC CAC accumulator and lookup-table status registers; then a long `rtavfs_rtavfs_ind_reg_blk` section from `RTAVFS_REG0` through the first fields of `RTAVFS_REG188`. The range ends before the remaining `RTAVFS_REG188` masks and later RTAVFS registers, so adjacent chunk research is required for the complete RTAVFS debug-bus block.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. AMDGPU code combines these masks with matching register-address macros from the GC 12.0.0 offset header and commonly accesses fields through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`. This lets ASIC-specific graphics, power, reset, debug, and performance code program or decode one hardware field without hard-coding raw bit positions.

This chunk focuses on low-level graphics power and topology metadata:

- ICG/CGTT clock-gating overrides for shader processor, shader export, texture/address/decompression, depth buffer, color buffer, RMI, primitive/geometry front-end, texture cache, LDS, UTCL1, GRBMH, scan converter, GL1C/GL1XC, GL1A/GL1XA, and GL1 internal return/source paths.
- Shader-array, WGP, render-backend, and shader-engine remap controls that expose inactive WGPs, disabled shader arrays, disabled RB backends, RMI redundancy repair bits, WGP-to-SA remapping, RB remapping, and SE-to-SA remapping.
- GL1 and GL1X pipe steering fields that select pipe mappings and steering mode.
- A UTCL1 security register with an identity-mode enable bit.
- GC CAC selection/control and full-width accumulator readouts for CP, EA, UTCL2 router/VML2/walker, GE, PMM, SDMA, CHC, RLC, GRBM, and GL2C blocks.
- Clock/power lookup-table fields for EDC/PCC stall-to-release, stall-to-power-break, power-break stall-to-release, and power-break release-to-stall patterns, fixed-pattern performance counters, and hardware LUT update done/error/error-step status.
- RTAVFS register fields for zone start/stop counts, zone enable masks, V/F anchor points, guard-band zones, CPO averaging and clock-divider settings, intercepts, PI controller coefficients, PSM and min/max sensing controls, AVFS/voltage regulator enables, override selectors, FSM counters, CPO start/stop/ripple counters, and target/current frequency count overrides.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 32-bit register value.
- Register-address symbols live in the companion GC 12.0.0 offset header, usually as `mm...` symbols with the same register name.
- AMDGPU callers normally combine these definitions with field-pack/extract helpers, MMIO accessors, indexed-register accessors, PM4 packet construction, power-management tables, register dumps, and reset/debug paths.

The main macro families in this chunk are:

- `ICG_SQ_CLK_CTRL`, `ICG_SP_CLK_CTRL`, `GFX_ICG_SX_CLK_CTRL0..4`, `GFX_ICG_TA_CTRL`, `GFX_ICG_TD_CTRL`, `DB_CGTT_CLK_CTRL_0`, `GFX_ICG_CB_CTRL`, `GFX_ICG_RMI_CTRL`, `GFX_ICG_SE_CAC_CLK_CTRL`, `CGTT_PH_CLK_CTRL0..3`, `GFX_ICG_TCP_CTRL`, `ICG_LDS_CLK_CTRL`, `GFX_ICG_UTCL1_CTRL`, and `GFX_ICG_GRBMH_CTRL`: clock-gating, soft-override, stall-override, debug-enable, off-hysteresis, and per-subunit override masks.
- `CGTT_SC_CLK_CTRL0..4`: scan-converter and primitive-binning clock/stall overrides, including VRC/HZC/HSC/HPF, PBB front/batch/raster/gather/output/passmem paths, DB/PKR/PA-SC interfaces, perfmon, dynamic, and register-clock override fields.
- `ICG_GL1C_CLK_CTRL`, `ICG_GL1XC_CLK_CTRL`, `GL1I_GL1R_MGCG_OVERRIDE`, `GL1XI_GL1XR_MGCG_OVERRIDE`, `ICG_GL1A_CTRL`, and `ICG_GL1XA_CTRL`: GL1/GL1X request, VM, UTCL0, GCR, source/return, GRBM, perf, and internal return/source DCLK override bits.
- `GL1_PIPE_STEER`, `GL1X_PIPE_STEER`, `GC_USER_SHADER_ARRAY_CONFIG`, `GRBMH_GC_USER_SA_UNIT_DISABLE`, `GC_USER_SA_UNIT_DISABLE_1`, `GC_USER_RB_BACKEND_DISABLE`, `GC_USER_RMI_REDUNDANCY`, and `GC_USER_SHADER_RATE_CONFIG*`: topology, repair, and shader-rate fields exposed through user or hypervisor-facing register blocks.
- `GRBMH_WGP_SA0_REMAP_CNTL`, `GRBMH_WGP_SA1_REMAP_CNTL`, `GRBMH_RB_SA0_REMAP_CNTL`, `GRBMH_RB_SA1_REMAP_CNTL`, and `GRBMH_GRBM_SA_REMAP_CNTL`: WGP, RB, and shader-array remap controls for harvesting, repair, or virtualization/topology presentation.
- `UTCL1_SECURITY`: UTCL1 identity-mode enable plus reserved high bits.
- `GC_CAC_ID`, `GC_CAC_CNTL`, and the many `GC_CAC_ACC_*` registers: CAC block/signal selection, threshold control, and 32-bit accumulator readback for named GC sub-blocks.
- `EDC_*`, `PCC_*`, `STALL_TO_PWRBRK_*`, `PWRBRK_STALL_TO_RELEASE_*`, and `PWRBRK_RELEASE_TO_STALL_*`: packed `FIRST_PATTERN_*` LUT entries, with 5-bit fields in release-oriented tables and 3-bit fields in power-break stall/release tables.
- `FIXED_PATTERN_PERF_COUNTER_1..10` and `HW_LUT_UPDATE_STATUS_1..2`: full-width counters and hardware LUT update status fields for tables 1-7.
- `RTAVFS_REG0..188` in this range: generated RTAVFS fields for five zones, four V/F points, guard bands, CPO averaging, PSM/min-max/PI controller configuration, voltage-code overrides, FSM timing counters, 64 CPO start/stop/ripple counters, and debug-bus selection.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU runtime flow is:

1. Select the GC 12.0.0 register headers for the active ASIC.
2. Select a matching register address from the companion offset header or an indexed-register access path.
3. Read an existing register value, prepare a new control value, build a command or firmware table entry, or decode a debug/status dump.
4. Use the `__SHIFT` and `__MASK` pair, commonly through register field helpers, to pack or extract the relevant field.
5. Write or decode the value in graphics clock-gating setup, power-management sequencing, topology/harvesting setup, CAC/performance diagnostics, RTAVFS calibration/control, reset recovery, suspend/resume restore, virtualization, or hang/debug paths.

For clock-gating and topology registers, the driver or firmware typically programs fields during ASIC initialization, power-state transitions, IP block bring-up, debug override, reset recovery, or virtualization partitioning. For CAC and LUT status registers, flows are diagnostic/performance oriented: select a block/signal, configure a threshold or lookup pattern, read accumulators, and check update-completion/error state. For RTAVFS, the implied flow is more state-machine oriented: configure zones, enable CPO/PSM sensing, define PI controller coefficients and guard bands, optionally override voltage/frequency-count values, run or observe AVFS logic, and read counters/status. The header itself does not encode sequencing, polling, locking, register-index selection, firmware ownership, or hardware side-effect rules.

## State And Persistence Behavior

The macros are stateless and persist nothing. They describe GPU registers whose state is owned by hardware, firmware, and AMDGPU runtime code.

Clock-gating and clock-stall override fields are persistent hardware control state while the corresponding IP block is powered. They may be reset to hardware defaults across GPU reset, power gating, BACO/suspend-resume, or IP block reinitialization. Setting soft overrides can deliberately keep clocks ungated for debug or workaround purposes, but can also increase power and hide power-management bugs.

Topology and remap registers represent hardware-presented resource layout: disabled WGPs, shader arrays, render backends, RMI repair selection, GL1/GL1X pipe steering, WGP-to-SA remapping, RB remapping, and SE-to-SA remapping. These values affect how work is routed through graphics resources and may be programmed from fuses, firmware tables, driver discovery, or virtualization policy. Incorrect persistence or restore ordering can expose unavailable resources or route traffic to the wrong physical unit.

`UTCL1_SECURITY__UTCL1_IDENTITY_MODE_ENABLE` is security-relevant configuration state. The header exposes the bit layout only; ownership and allowed transitions are enforced elsewhere by PSP/firmware/driver policy.

GC CAC accumulator registers are readback-style diagnostic/performance state. Accumulator values change with block activity and selected signals. `GC_CAC_ID` and `GC_CAC_CNTL` configure what is observed and how thresholds are applied; accumulator read timing and clearing/latching behavior are not described in this generated header.

Lookup-table and update-status fields persist hardware power/clock transition policy and expose whether hardware LUT updates completed or failed, including small error-step fields. These fields are sensitive to firmware and power-management sequencing; stale done/error bits or mismatched pattern widths can mislead diagnostics.

RTAVFS registers model a large stateful adaptive-voltage/frequency-control subsystem. Zone counts and enable masks define measurement windows, V/F point fields define anchor frequency-count and voltage-code pairs, CPO fields control oscillator measurement, PSM fields control voltage regulator/VDD sensing paths, PI fields control feedback loop behavior, and FSM counters/status expose runtime state. The 64 CPO start/stop/ripple-counter families are volatile measurements. Override fields such as voltage-code override, target/current frequency-count override, and selection bits can bypass normal hardware behavior and therefore should be treated as active controls rather than passive metadata.

Reserved and unused fields appear throughout. Their existence as macros does not make them safe to program arbitrarily; driver code should preserve reserved bits during read-modify-write unless the hardware sequence explicitly requires a full-register value.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` provides matching register addresses and indexed-register selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_default.h`, if present in the same generated family, provides reset/default values for many registers.
- AMDGPU register helper macros provide field packing/extraction and MMIO or indexed-register access mechanisms.
- AMDGPU GFX, RLC, GRBM, KFD/compute-adjacent, power-management, clock-gating, topology/harvesting, reset, virtualization, diagnostics, and debug dump paths can include these constants.
- Firmware/PSP/SMU/RLC interactions are likely for the security, power, RTAVFS, and LUT/CAC families, even though this header only supplies bit definitions.

Integration points include ASIC initialization clock-gating tables, debug paths that force clocks on, power-management or SMU-facing code that configures RTAVFS and LUT patterns, GRBM/topology setup that reflects harvested WGP/RB/SA resources, GL1/GL1X pipe steering, UTCL1 identity/security mode policy, CAC/performance counter collection, and GPU reset/suspend-resume restore code that must reapply or preserve control registers in the expected order.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading state.
- This chunk starts and ends mid-family. It begins after most `ICG_SQ_CLK_CTRL` shifts/masks and ends before the remaining `RTAVFS_REG188` fields, so adjacent chunks are needed for complete file-level conclusions.
- Many clock-gating fields are active controls. Accidentally setting a soft override or stall override can change power, timing, idle behavior, or debug visibility without producing a local software error.
- Reserved fields are explicitly named in several families, especially `CGTT_SC_CLK_CTRL3`, RTAVFS, and UTCL1 security. These should not be treated as normal programmable bits without hardware guidance.
- Repeated bitfield families are susceptible to single-index mistakes: TA/TD soft overrides, PH/TCP/LDS/UTCL1 overrides, SC PBB paths, WGP/RB remaps, LUT pattern tables, update-status tables, RTAVFS zones, V/F points, and 64 CPO counters all have repeated structures.
- Topology/remap fields can expose or route to harvested, disabled, or remapped physical units. Incorrect masks may cause hangs, incorrect wave scheduling, unavailable render backends, wrong cache steering, or invalid virtualized topology.
- UTCL1 identity mode is security-sensitive. Misprogramming could affect address identity behavior or isolation assumptions; this header gives no policy constraints.
- CAC accumulator fields are full-width readouts whose meaning depends on selected block/signal and timing. Misusing `GC_CAC_ID` or threshold fields can produce plausible but irrelevant performance data.
- LUT pattern fields have different widths across families: EDC/PCC and power-break stall-to-release use 5-bit masks, while stall-to-power-break and power-break release-to-stall use 3-bit masks. Reusing packing logic blindly can corrupt adjacent entries.
- RTAVFS override, PI, PSM, CPO, and FSM fields can affect voltage/frequency behavior. Errors here can cause instability, power regressions, thermal issues, or misleading AVFS telemetry rather than a simple render failure.
- CPO start/stop/ripple counters are volatile measurement state. Treating them as persistent configuration or comparing them without a controlled measurement window can produce false failures.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, hardware diagnostics, and power-management telemetry:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12.0.0 GFX, GRBM/RLC, clock-gating, power-management, topology, reset, and debug code.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 37537-40041.
- Cross-checks that registers in this chunk have matching address macros in `gc_12_0_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that masks align with shifts, full-width fields use `0xFFFFFFFFL`, repeated families remain structurally consistent across indices, and reserved masks do not overlap named programmable fields.
- Clock-gating tests that toggle debug/soft overrides under controlled conditions and verify idle clocks, power draw, wake latency, and hang-free graphics/compute activity.
- Topology and harvesting tests that confirm disabled WGP/SA/RB masks, remap controls, RMI repair bits, GL1/GL1X pipe steering, and shader-rate fields match discovered hardware and virtualized resource exposure.
- Security and firmware validation for `UTCL1_SECURITY` transitions, including checks that identity mode is only changed by the expected authority and restores correctly after reset/resume.
- CAC/performance diagnostics that select known GC blocks/signals, exercise CP/EA/UTCL2/SDMA/GRBM/GL2C activity, and verify accumulator behavior and threshold handling.
- LUT programming tests that update EDC/PCC/power-break tables, poll `HW_LUT_UPDATE_STATUS_1..2`, and confirm done/error/error-step bits match expected success or injected-failure cases.
- RTAVFS validation that covers zone enable/start/stop settings, V/F anchors, CPO averaging and counters, PI coefficient/anti-windup behavior, PSM min/max/average sensing, voltage-code overrides, target/current frequency-count overrides, and FSM counter progression under controlled workloads.
- Runtime warning signals include higher idle power, unexpected clock residency, GPU hangs during power transitions, invalid harvested-resource exposure, wrong performance counter data, LUT update errors, RTAVFS FSM stalls, voltage/frequency instability, or debug dumps with impossible CPO/ripple-counter state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002584`. It covers lines 37537-40041 of `gc_12_0_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the preceding `ICG_SQ_CLK_CTRL` family, the trailing `RTAVFS_REG188` debug-bus masks and later RTAVFS registers, and the broader GC 12.0.0 generated register-map context.
