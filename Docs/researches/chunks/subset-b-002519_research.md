# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 37568-40147

## Scope

This chunk is part of AMDGPU's generated GC 11.0.0 register bitfield header. It contains C preprocessor definitions for hardware register field shifts and masks, not executable functions. The definitions are consumed by the driver through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and indirect-register accessors, together with matching register offsets from the sibling `gc_11_0_0_offset.h` header.

The chunk starts in the middle of the `ICG_GL1C_CLK_CTRL` bitfield group and then covers several address blocks: front-end/interconnect clock-gating controls, `gc_hypdec`, `gc_pspdec`, `gc_gfx_imu_gfx_imudec`, `gc_gfx_imu_gfx_imu_pspdec`, and `gccacind`.

## Purpose

The header gives the GC 11 driver a single source of truth for bit layouts in 32-bit GPU registers. Each register field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position.
- `<REGISTER>__<FIELD>_MASK`, the already-positioned bit mask.

This lets driver code update fields without embedding magic constants, and it keeps ASIC-specific bit encodings separate from higher-level logic in the gfx, KFD, power-management, RLC, PSP, and virtualization paths.

## Important Register Families

- Clock-gating and idle-clock override registers: `ICG_GL1C_CLK_CTRL`, `ICG_GL1A_CTRL`, `ICG_CHA_CTRL`, `GUS_ICG_CTRL`, `CGTT_PH_CLK_CTRL0..3`, `GFX_ICG_GL2C_CTRL`, `GFX_ICG_GL2C_CTRL1`, `ICG_LDS_CLK_CTRL`, `ICG_CHC_CLK_CTRL`, `ICG_CHCG_CLK_CTRL`, `RLC_BUSY_CLK_CNTL`, and `RLC_CLK_CNTL`. These define software override bits, on-delay fields, off-hysteresis fields, and per-subblock clock override bits.
- Hypervisor/virtualization register fields under `gc_hypdec`: `GFX_PIPE_PRIORITY`, `GRBM_GFX_INDEX_SR_SELECT`, `GRBM_GFX_INDEX_SR_DATA`, `GRBM_GFX_CNTL_SR_SELECT`, `GRBM_GFX_CNTL_SR_DATA`, `GRBM_SE_REMAP_CNTL`, `RLC_GPU_IOV_*`, `RLC_HYP_SEMAPHORE_*`, `RLC_RLCV_TIMER_*`, `RLC_PACE_*`, and SDMA status mirrors. These describe VF/PF selection, shader-engine remapping, VM busy state, doorbell status, IOV scheduler state, timer status, and scratch/ucode address-data windows.
- PSP/security-facing register fields under `gc_pspdec`: `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, `CP_GFX_RS64_DM_INDEX_*`, `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, GRBM CAM and hypervisor CAM fields, and `RLC_FWL_FIRST_VIOL_ADDR`. These support firmware/debug access, privilege/TMZ override controls, CAM remapping, and first firewall violation reporting.
- GFX IMU fields under `gc_gfx_imu_gfx_imudec`: 48 `GFX_IMU_C2PMSG_*` mailboxes, mailbox access-control registers, IMU/RLC command and data registers, message-status handshakes, IMU status, interrupt controller mask/level/edge/priority/status bits, interrupt ID, IH controls, power-management interrupt request, telemetry, scratch registers, timestamp/offset registers, clock/reset/isolation controls, three timer blocks, fuse controls, and IMU data RAM access.
- GFX IMU PSP-visible RAM fields under `gc_gfx_imu_gfx_imu_pspdec`: `GFX_IMU_I_RAM_ADDR` and `GFX_IMU_I_RAM_DATA`.
- GC CAC indirect fields under `gccacind`: `GC_CAC_ID`, `GC_CAC_CNTL`, many `GC_CAC_ACC_*` accumulator registers for CP, EA, UTCL2 router/VML2/walker, GDS, GE, PMM, GL2C, PH, SDMA, CHC, GUS, and RLC blocks, plus stall/power-break LUT fields, fixed-pattern performance counters, and `HW_LUT_UPDATE_STATUS`.

## APIs, Types, and Functions

This chunk defines no C types or functions. Its public API is the macro naming contract used by AMDGPU register helpers:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` expands against `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- `REG_GET_FIELD(value, REGISTER, FIELD)` reads using the same pair.
- MMIO helpers such as `WREG32_SOC15(GC, inst, reg, value)` and `RREG32_SOC15(GC, inst, reg)` use offset macros from `gc_11_0_0_offset.h`; these mask macros are the field-level companion.
- Indirect CAC access is mediated through `GC_CAC_IND_INDEX`/`GC_CAC_IND_DATA` style register windows in the broader driver. The `GC_CAC_ACC_*`, LUT, and counter masks in this chunk define the payload layout after the indirect index selects a CAC register.

## Control Flow and State Behavior

There is no local control flow. The runtime flow appears in callers that include this header:

1. Driver code selects a register by using a `reg*`, `mm*`, or `ix*` offset macro from the generated offset header.
2. It reads a 32-bit register value or creates one from zero.
3. It applies these `*_MASK` and `*_SHIFT` macros through field helpers.
4. It writes the updated value to MMIO or to an indirect data window.

The state represented by these macros lives entirely in GPU hardware registers and firmware-visible register windows. Persistent effects depend on the register family:

- Clock-gating override bits affect hardware clock behavior until reset, power-gating transition, firmware reprogramming, or driver reinitialization.
- RLC/GPU IOV fields represent virtualization state, VF/PF doorbell state, scheduler blocks, VM busy state, scratch windows, timer enable/status bits, and microcode access windows.
- GFX IMU registers model firmware mailbox state, command/data handshakes with RLC, interrupt controller configuration, timers, reset and isolation controls, telemetry, scratch registers, and instruction/data RAM access.
- GC CAC accumulator and LUT fields represent power/activity counter state and transition tables accessed through an indirect register interface.

## Dependencies and Integration Points

- Depends on generated offset headers for register addresses. This file only describes bit layouts.
- Integrates with AMDGPU's common bitfield helpers; the macro naming must match the helper token-pasting pattern exactly.
- Integrated by GC 11 code paths such as gfx v11 and KFD support, and by shared SOC15 register read/write helpers for MMIO access.
- The RLC/GPU IOV definitions are integration points with SR-IOV and hypervisor flows; wrong masks can expose or hide VF/PF state incorrectly.
- PSP/security and CAM definitions integrate with firmware debug, protected register access, TMZ/secure overrides, and firewall violation reporting.
- GFX IMU mailbox, interrupt, timer, reset, and RAM definitions integrate with firmware boot, power management, RLC coordination, interrupt routing, and telemetry.
- GC CAC definitions integrate with power-management/CAC activity accounting and indirect register access through index/data windows.

## Risks

- Mask/shift drift from the hardware specification is high impact. A one-bit error can program an adjacent control bit, especially in clock, reset, isolation, security, or virtualization registers.
- Some fields are full-register masks (`0xFFFFFFFFL`) and must not be treated as bounded small fields by callers.
- Reserved fields are explicitly defined in several registers. Callers should preserve reserved bits on read-modify-write unless the hardware spec requires a literal value.
- `GFX_IMU_PIC_INT_*` definitions contain many single-bit interrupt fields. Mismapping an interrupt mask, level, edge, priority, or status bit can cause missing interrupts or interrupt storms.
- Mailbox/status registers use handshake bits such as busy, done, change-toggle, and done-toggle. Callers must preserve protocol ordering; these macros do not enforce sequencing.
- RLC and IMU RAM address fields are shifted and masked address windows, not arbitrary byte pointers. Unaligned or out-of-range programming can target the wrong firmware memory word.
- GC CAC LUT fields pack several small pattern entries into one register. Incorrect packing can destabilize stall/release or power-break behavior.
- The file is generated; manual edits risk diverging from upstream generated register headers and should be avoided unless regenerating from the authoritative register database.

## Test and Validation Signals

- Build signal: any renamed or missing macro should fail compilation in code using `REG_SET_FIELD`/`REG_GET_FIELD` with GC 11 registers.
- Static review signal: field helper expansion should reference both `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT`; register groups should remain paired with matching offset-header entries.
- Runtime smoke signal: GC 11 ASIC initialization should complete without hangs in gfx/RLC/PSP/IMU setup paths.
- Power-management signal: clock-gating toggles, RLC busy-clock controls, CAC activity counters, and fixed-pattern counters should behave consistently across suspend/resume and runtime power transitions.
- Virtualization signal: SR-IOV paths should correctly report VF/PF enablement, VM busy status, SDMA busy/status mirrors, doorbell set/clear state, and scheduler block state.
- Firmware/IMU signal: mailbox commands should complete without stuck busy bits, IMU/RLC status should progress through expected alive/done states, interrupt status should clear, and timer compare interrupts should fire only when enabled.
- Security/debug signal: PSP debug override and firewall violation fields should only be used in intended privilege contexts, with readback matching expected bit positions.
