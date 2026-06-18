# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 17741-20296

## Purpose

This chunk is part of AMDGPU's generated GC 12.1.0 register field header. It contains C preprocessor constants for register bit shifts and masks, not executable code. Consumers pair these `*_SHIFT` and `*_MASK` definitions with register offsets from `gc_12_1_0_offset.h` and helper macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()` in `amdgpu.h` to program or decode memory-mapped GPU registers.

The span starts in the middle of `RLC_SPM_ACCUM_STATUS`, covers RLC streaming-performance-monitor, performance-counter, virtualization, clock/power, microcontroller memory, command-processor hypervisor, global-arbiter, shader-array disable, RLC firmware/control, RLC doorbell, UTCL1, SPP, residency-counter, and graphics interrupt-handler client register fields, and ends in the middle of `RLC_GFX_IH_CLIENT_SE_STAT_H`. Adjacent chunks are required to see the complete first and last registers.

## Important APIs, Types, And Macro Families

This header defines no functions, structs, classes, or runtime types. Its public interface is a generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset for `FIELD` within `REGISTER`.
- `REGISTER__FIELD_MASK`: bit mask for the same field.

The main consuming APIs are external:

- `REG_SET_FIELD(orig_val, reg, field, field_val)` token-pastes the generated shift and mask names to insert a field value.
- `REG_GET_FIELD(value, reg, field)` extracts a field from a register value.
- `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC_SHADOW_EX`, `WREG32_FIELD15_PREREG`, and related SOC15 helpers perform the actual MMIO accesses using `reg...` offset macros from the paired offset header.

Major register groups in this chunk:

- `RLC_SPM_ACCUM_*`, `RLC_SPM_*`, `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER*_SELECT`, `GCR_PERFCOUNTER*_SELECT*`, and `CHA_PERFCOUNTER*_SELECT*`: RLC SPM accumulation state, start/rearm/reset strobes, automatic accumulation/SPM modes, sample thresholds/counts, RSPM request/response op/data fields, pause/status bits, gfx clock counters, GTS trigger values, global user data, and performance-counter event selection.
- `XVMIN_XVMIN_WR_DATA`: generated field for a CPWD/GDFLL XVMIN write-data register.
- `RLC_GPU_IOV_*`, `RLC_FED_DRVR_STATUS`, `RLC_SDMA*_STATUS`, `RLC_SDMA*_BUSY_STATUS`, `RLC_HYP_SEMAPHORE_*`, and `RLC_IH_COOKIE*`: SR-IOV/hypervisor controls for VF enablement, command execution/status, function identifiers, VF/PF doorbell status set/clear/mask, SDMA save/restore/busy status, hypervisor semaphores, interrupt-cookie credit/reset, SMU/RLC responses, and virtual reset requests.
- `RLC_BUSY_CLK_CNTL`, `RLC_CLK_CNTL`, `GLARB_*`, `CH_*`, `GC_USER_*`: RLC clock-gating override/latency controls, global-arbiter/channel hashing and pipe steering, CAC selection, AID selection, and user-visible shader-array/HBM-disable masks.
- `CP_HYP_*`, `CP_PFP_*`, `CP_ME_*`, `CP_MEC*`, and `CP_MES_*` fields in the `cphypdec` block: command-processor context range, PFP/ME/MEC hypervisor and normal firmware-address/data registers, checksum/version fields, instruction-cache base/control/op controls, MES instruction/data bounds, and RS64 graphics/MEC base/bound registers.
- `GRBM_*` fields in the hypervisor GRBM block: shadow-register select/data and SE/SA remap controls, plus interrupt-cookie pointer fields.
- `RLC_CNTL`, `RLC_STAT`, `RLC_ACTIVE_MASK`, `RLC_GFX_SE_STATUS`, `RLC_GPM_TIMER_*`, `RLC_GPM_LEGACY_INT_*`, `RLC_INT_STAT`, `RLC_MGCG_CTRL`, and `RLC_MCA_*`: core RLC enable/step/cache/poison controls, busy flags, active shader-engine mask, thread timer programming/status/clear bits, interrupt status/clear fields, medium-grain clock-gating controls, and machine-check/RAS interrupt fields.
- `RLC_*CLOCK*`, `RLC_CAPTURE_GPU_CLOCK_COUNT*`, `RLC_CLK_COUNT_*`, and `RLC_GPU_CLOCK_32*`: GPU/reference clock counting, capture, status, and 32-bit clock selection registers.
- `RLC_UCODE_CNTL`, `RLC_GPM_*`, `RLC_LX6_*`, `RLC_SRM_*`, and `RLC_*UTCL1*`: RLC firmware loading/control, GPM thread reset/enable/priority/interrupt/CP-DMA-completion fields, LX6/GPM/SRM memory address/data windows, SRM command/indexed control/status fields, and UTCL1 control/status/error fields for LX6, GPM, SPM, SRM, DMA, and DLG paths.
- `RLC_RLCG_DOORBELL_*` and `RLC_RLCV_DOORBELL_*`: RLCG/RLCV doorbell range, enable, offset, FIFO/full/error/status, and four 64-bit data slots.
- `RLC_PG_*`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL*`, `RLC_DYN_PG_*`, `RLC_STATIC_PG_STATUS`, `RLC_AUTO_PG_CTRL`, `RLC_SERDES_*`: power-gating delays, dynamic/static power-gating status/request, always-on WGP masks, clock-gating/light-sleep controls, and SERDES indexed access control/status/data.
- `RLC_SPP_*`: shader profiler/performance-profile control, shader profile enablement by SIMD/WGP/SE, SSF capture/thresholds, inflight readback, global shader identifiers, status, private statistics, maximum levels, stall-state update, PBB information, and reset fields.
- `RLC_*RESIDENCY_*`: power, clock, deep-sleep, ultra-low-voltage, PCC, and general residency counter controls, event counters, and reference counters.
- `RLC_GFX_IH_*`: graphics interrupt-handler client masks, error-clear bits, halt control, arbiter granted-client status, and per-SE client buffer level/loading/protocol-error/overflow flags for SE0 through the partial SE5 fields included in this chunk.

## Control Flow

There is no local control flow because the file is only a macro database. The effective control flow is in AMDGPU users:

1. Include `gc_12_1_0_offset.h` and `gc_12_1_0_sh_mask.h`.
2. Read an MMIO register with a SOC15 helper or start from a literal/reset value.
3. Compose fields with `REG_SET_FIELD()` or direct `*_MASK` / `*_SHIFT` operations.
4. Write the register through `WREG32_SOC15()` or an RLC-shadowed/no-KIQ variant.
5. Poll status bits with `REG_GET_FIELD()` or mask tests when hardware exposes completion, busy, error, or acknowledgement flags.

Examples in this tree include `gfx_v12_1.c` enabling RLC GPM threads through `RLC_GPM_THREAD_ENABLE`, writing `RLC_CNTL__RLC_ENABLE_F32_MASK` to start RLC F32, clearing `RLC_CNTL.RLC_ENABLE_F32` to stop it, and reading `RLC_CNTL.RLC_ENABLE_F32` to report whether RLC is enabled. The same file updates SPM VMID through `RLC_SPM_MC_CNTL` and uses the same generated-header contract as this chunk's SPM and RLC fields.

## State And Persistence Behavior

The macros themselves are compile-time constants. The state they describe is hardware state held in GC 12.1.0 RLC, CP, GRBM, SPM, SPP, interrupt, and virtualization register files.

- Control bits such as RLC enable, RLC stepping, read-cache disable, clock-gating overrides, power-gating controls, SPP enablement, doorbell enablement, and IOV command execution persist until reset, power-management transitions, firmware reinitialization, or explicit driver writes.
- Status, busy, acknowledgement, interrupt, overflow, FIFO, residency, and performance-counter fields are updated by hardware and are commonly consumed by polling, diagnostics, interrupt handling, or performance tooling.
- Address/data windows for GPM, LX6, SRM, PFP, ME, MEC, MES, and RLCG firmware/scratch/memory regions are persistent register interfaces into firmware or microcontroller memory. Their values are meaningful only when used with the matching indexed register access protocol.
- Doorbell status/data fields and VF/PF function-selection fields are security- and isolation-sensitive because they affect SR-IOV scheduling, virtual resets, function ownership, and queue notification paths.
- SPM, SPP, residency, and clock counters are measurement state. They must be reset/armed/enabled in the correct order by driver or firmware code to avoid stale samples, overflows, or partial captures.

## Dependencies

This chunk depends on the paired generated offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h`; mask macros alone do not name MMIO addresses. It also depends on AMDGPU field helpers in `amdgpu.h` and SOC15 register access helpers for instance-aware GC register addressing.

Direct include sites for this GC 12.1.0 mask header include `gfx_v12_1.c`, `mes_v12_1.c`, `sdma_v7_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, and `soc_v1_0.c`. Not every include site uses every register in this chunk, but all rely on the generated naming ABI remaining consistent across offset, mask, default, packet, firmware-loading, scheduler, and diagnostics code.

## Integration Points

- GFX/RLC bring-up: `gfx_v12_1.c` programs `RLC_CNTL` and `RLC_GPM_THREAD_ENABLE` during RLC autoload/start/stop and checks RLC enable state during runtime decisions.
- Performance and profiling: SPM accumulation, RSPM request/response, performance-counter selection, SPP capture/status, clock-count, and residency-counter fields integrate with GPU profiling, debugfs/perf paths, and firmware-mediated collection.
- SR-IOV and hypervisor operation: `RLC_GPU_IOV_*`, VF doorbell status/mask/set/clear, active function ID, virtual reset request, SDMA save/restore/busy status, CP hypervisor context range, and hypervisor firmware register windows support PF/VF isolation and virtualization scheduling.
- Firmware loading and microcontroller control: CP PFP/ME/MEC/MES, RLC GPM, LX6, and SRM address/data/checksum/version fields are used by firmware load, validation, reset, and indexed memory operations.
- Power and clock management: RLC clock-gating overrides, busy-clock latency, CGCG/CGLS, dynamic/static power gating, SERDES access, and residency counters integrate with runtime power-management and GPU reset/resume flows.
- Interrupt/error handling: RLC GPM legacy interrupt status/clear, CP-RLC interrupt status, RLC MCA/RAS controls, poison interrupt controls, IH cookie handling, and GFX IH client masks/statistics provide hooks for error reporting, interrupt routing, and buffer overflow/protocol-error diagnosis.
- Topology and resource discovery: GRBM SE/SA remapping, `GC_USER_*_DISABLE`, HBM disable, pipe steering, hash configuration, and active-mask fields affect how driver code interprets active shader arrays, memory channels, and graphics instances.

## Risks

- Incorrect shift or mask values silently corrupt hardware programming. `REG_SET_FIELD()` and `REG_GET_FIELD()` will compile as long as names exist, even if the bit layout does not match GC 12.1.0 hardware.
- This chunk has split-register boundaries: it starts after the first `RLC_SPM_ACCUM_STATUS` fields and ends before all `RLC_GFX_IH_CLIENT_SE_STAT_H` masks. The merge lane must combine adjacent chunks before treating either register as fully researched.
- Cross-generation similarity is risky. RLC/SPM/IOV/CP fields appear in many GC generations, but GC 12.1.0 changes field widths and reserved regions, such as active function ID and virtualization fields. Copying masks from GC 9/10/11 can program the wrong bits.
- Repeated families are prone to generator or review mistakes: SDMA0-7 status/busy registers, doorbell data slots, GPM timers, SRM indexed data lanes, UTCL1 error pairs, residency counter groups, and SE0-7 IH client status fields should remain internally consistent unless hardware documentation says otherwise.
- Security and isolation fields, including VF enable/mask, PF/VF status, virtual reset request, CP hypervisor ranges, doorbell controls, privilege/poison interrupt controls, and function identifiers, can cause cross-function leakage, lost interrupts, failed FLR, or PF/VF hangs if wrong.
- Counter/control sequencing matters. SPM/SPP/residency reset, arm, start, sample, overflow, and acknowledgement bits can produce misleading profiling data or stuck polling loops when written in the wrong order.
- RLC power/clock-gating and firmware-control registers are boot-critical. Bad masks can leave RLC halted, prevent firmware startup, break GPU reset/resume, or cause command submission timeouts.

## Test Signals

Useful validation is mostly build and hardware integration:

- GC 12.1.0 AMDGPU build coverage with all token-pasted `REG_SET_FIELD()` / `REG_GET_FIELD()` names resolving for `gfx_v12_1.c`, `mes_v12_1.c`, `sdma_v7_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, and `soc_v1_0.c`.
- Boot on GC 12.1.0 hardware with successful RLC autoload, RLC F32 enable, CP/MES/MEC firmware loading, KIQ/MES queue bring-up, and no RLC/CP firmware checksum or halt errors.
- GPU reset, suspend/resume, and runtime power-management cycles without RLC stuck-busy, clock-gating, power-gating, or SERDES access timeouts.
- SR-IOV PF/VF validation covering VF enablement, active function switching, VF/PF doorbell status set/clear, virtual reset/FLR requests, SDMA status save/restore, and VM busy status reporting.
- Profiling workloads that exercise SPM accumulation, SPP capture, performance counters, clock counters, and residency counters, with sane sample counts, done/overflow/armed bits, and no unexpected aborts.
- Interrupt and RAS tests that exercise IH client masking/error clear, SE/SDMA/UTCL2/FED error paths, RLC GPM legacy interrupt clear/status, CP-RLC interrupt pending IDs, poison interrupt routing, and MCA/RAS controls.
- Register dump comparison against AMD-generated GC 12.1.0 headers or hardware specifications, especially for repeated SDMA, doorbell, timer, UTCL1, residency, and IH per-SE fields.
