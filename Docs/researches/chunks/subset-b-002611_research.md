# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h lines 2941-3866

## Scope

This chunk is the final generated segment of the AMD GC 9.0 default-register header. It contains C preprocessor constants only: each macro names a GC 9.0 register and gives its reset/default 32-bit value as `<REGISTER>_DEFAULT`. There are no functions, structs, enums, variables, includes, branches, allocations, locks, callbacks, or executable persistence logic in this range.

The range begins in a continued performance-monitoring block with RLC SPM sample-delay, RLC/RMI perf-counter, ATC L2, and MC VM L2 defaults. It then covers `gc_rlcpdec`, `gc_pwrdec`, `gc_ea_pwrdec`, `gc_utcl2_vmsharedhvdec`, `gc_hypdec`, `gccacind`, `secacind`, `sqind`, and `didtind`, and ends with the file's `#endif`.

Although the repository path is under a local `ceph-client` mirror, this is AMDGPU DRM graphics-core hardware metadata, not distributed filesystem logic.

## Purpose

`gc_9_0_default.h` records hardware reset/default values for GC 9.0 registers. Driver code includes it with the matching GC 9.0 offset and shift/mask headers so initialization, reset, power-management, virtualization, diagnostics, and register-dump paths can compare or seed register values without hand-maintaining literals.

This chunk focuses on these hardware surfaces:

- RLC and RMI performance-monitoring defaults, including SPM sample delays, RLC perfmon control/select registers, GPU IOV perf-counter access registers, and RMI counter controls.
- ATC L2 and MC VM L2 performance counter configuration defaults.
- RLC control, status, safe-mode, power-gating, clock-gating, load-balancing, GPM thread, SRM, SMU, UTCL1, semaphore, prewalker, R2I, and dynamic/static power-gating registers.
- Shader/graphics power-control defaults for `CGTS_*`, `CGTT_*`, SQ power-throttle, and per-CU clock/power control registers.
- UTCL2 VM shared hypervisor defaults for SR-IOV/VF framebuffer size offsets, MARC base/relocation/length registers, IOMMU controls, PCIe ATS controls, and UTCL2 clock gating.
- Hypervisor and GPU IOV defaults for CP/RLC microcode ports, GRBM save/restore and CAM access, VF enable/masks/doorbell status, scheduling state, virtual reset, interrupt control, SDMA busy state, and SMU/RLC responses.
- Indexed current/average current control (`CAC`) defaults for GC and SE blocks, including weight, accumulator, and override registers across graphics, cache, memory, and UTCL2 sub-blocks.
- SQ wave-state indexed register defaults and DIDT dynamic inductive droop throttling defaults for SQ, DB, TD, TCP, and DBR blocks.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `mm<REGISTER>_DEFAULT` names an MMIO-visible GC register default value.
- `ix<REGISTER>_DEFAULT` names an indexed-register default value.
- Matching register offsets live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`.
- Matching field layouts live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h`.
- Consumers typically pair these values with SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `REG_SET_FIELD`, `REG_GET_FIELD`, indexed-register accessors, firmware-loading paths, and register-dump/debug logic.

Important macro groups in this slice include:

- Continued performance counter defaults: `mmRLC_SPM_*_PERFMON_SAMPLE_DELAY_DEFAULT`, `mmRLC_PERFMON_*_DEFAULT`, `mmRLC_PERFCOUNTER*_SELECT_DEFAULT`, `mmRLC_GPU_IOV_PERF_CNT_*_DEFAULT`, `mmRMI_PERFCOUNTER*_DEFAULT`, and `mmRMI_PERF_COUNTER_CNTL_DEFAULT`.
- `gc_utcl2_atcl2pfcntldec` and `gc_utcl2_vml2pldec`: `mmATC_L2_PERFCOUNTER*_CFG_DEFAULT`, `mmATC_L2_PERFCOUNTER_RSLT_CNTL_DEFAULT`, `mmMC_VM_L2_PERFCOUNTER*_CFG_DEFAULT`, and `mmMC_VM_L2_PERFCOUNTER_RSLT_CNTL_DEFAULT`.
- `gc_rlcpdec`: dense RLC defaults for `mmRLC_CNTL`, `mmRLC_SAFE_MODE`, `mmRLC_MEM_SLP_CNTL`, `mmRLC_MGCG_CTRL`, `mmRLC_CGCG_CGLS_CTRL`, `mmRLC_CGCG_RAMP_CTRL`, CU load-balancing masks/params, power-gating delays/status/request masks, GPM scratch/general/thread/interrupt registers, SRM ARAM/DRAM/indexed command ports, SMU message/argument/command registers, UTCL1 controls/errors, prewalker controls, R2I controls, and RLCV spare interrupt.
- `gc_pwrdec`: `mmCGTS_*` and `mmCGTT_*` clock/power defaults for shader blocks, per-CU SP/LDS/SQ/TA/SQC/TD/TCP/TCPI controls, front-end and back-end clock-gating controls, SQ power throttle, and CP/RLC/RMI clock gates.
- `gc_utcl2_vmsharedhvdec`: `mmMC_VM_FB_SIZE_OFFSET_VF0..VF15`, `mmMC_VM_MARC_*`, `mmVM_IOMMU_*`, `mmVM_PCIE_ATS_CNTL*`, and `mmUTCL2_CGTT_CLK_CTRL_DEFAULT`.
- `gc_hypdec`: CP microcode address/data defaults, RLC GPM ucode ports, GRBM save/restore and CAM defaults, RLC GPU IOV VF, scheduling, scratch, reset, response, interrupt, and SDMA busy-status defaults.
- `gccacind` and `secacind`: indexed `ixGC_CAC_*` and `ixSE_CAC_*` defaults for current/average current control, weights, accumulators, and overrides.
- `sqind`: indexed SQ wave debug/state defaults, including wave mode/status/trap, HW ID, GPR/LDS allocation, PC, instruction, TTMP0-15, M0, EXEC, and interrupt-word registers.
- `didtind`: indexed DIDT control, stall, tuning, pattern, weight, EDC, overflow, rolling-power, and stall-event-counter defaults for SQ, DB, TD, TCP, and DBR.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is:

1. GC 9.0 AMDGPU code includes the generated offset, shift/mask, and default headers for the active ASIC family.
2. Initialization, reset, power-management, virtualization, or diagnostic code chooses a register address from the offset header.
3. It either emits a default value from this file directly, compares hardware against the default, or uses the default as a seed for `REG_SET_FIELD` updates.
4. The final value is written or read through SOC15 MMIO helpers, indexed-register helpers, RLC-safe accessors, firmware-loading mechanisms, or register-dump tooling.

For RLC and power registers, higher-level code sequences firmware loading, safe-mode entry/exit, power-gating, clock-gating, load-balancing, and suspend/resume restore around these defaults. For VM/IOMMU/ATS and GPU IOV registers, virtualization and gfxhub setup code programs context- and VF-specific state after reset defaults. For CAC, SQ, and DIDT indexed registers, debug, power, and throttling paths access indexed register windows; this file only provides reset values.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible register state after reset or in a default initialization image.

RLC defaults are persistent control-plane state once programmed: safe-mode, clock-gating, power-gating masks, CU load-balancing, GPM thread state, SMU command arguments, SRM ports, and UTCL1/prewalker controls remain in hardware until reprogrammed, reset, power-gated, or restored after suspend/resume. Several RLC status, timestamp, busy, interrupt, and error registers are hardware-updated even though their default value is zero.

Power-management defaults in `gc_pwrdec` set initial clock-gating and compute-unit control behavior. Many `CGTT_*` defaults use `0x00000100`, while per-CU `CGTS_CU*_*` defaults repeat with deliberate per-CU variation such as `TA_SQC` and `TCPI` values. Those values can affect power, latency, and whether shader sub-blocks are clocked or throttled.

UTCL2, VM, IOMMU, ATS, MARC, and GPU IOV defaults are sensitive virtualization state. VF framebuffer-size offsets, MARC windows, ATS controls, VF masks, doorbell status, scheduler state, virtual reset, and SDMA busy registers describe isolation and scheduling surfaces that are usually reprogrammed by host/guest or SR-IOV setup code.

CAC accumulator defaults are mostly zero, while CAC weight defaults are often `0x00010001` or `0x00000001`. Accumulators are hardware-updated measurement state; weights and overrides are persistent tuning state. SQ wave indexed registers describe per-wave execution/debug state and default to zero, but live hardware values change while waves execute. DIDT controls and stall patterns are persistent throttling configuration, while EDC status, overflow, rolling-power delta, and stall event counters are measurement/status state.

The header does not encode access permissions, read-only/write-only behavior, write-one-to-clear semantics, pulse semantics, indexed register selection requirements, or reserved-bit preservation rules. Those constraints live in hardware documentation and the AMDGPU call sites.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set staying synchronized:

- `gc_9_0_offset.h` must provide matching `mm*` and `ix*` register addresses/base indices.
- `gc_9_0_sh_mask.h` must provide matching field definitions for consumers that modify only selected bits of these defaults.
- AMDGPU SOC15 helpers and indexed-register helpers provide the actual MMIO access paths.
- Firmware and microcode loading paths rely on CP/RLC ucode address/data defaults and RLC safe-mode/control surfaces.
- Power-management and graphics initialization rely on RLC, CGTS, CGTT, SQ throttle, CAC, and DIDT defaults.
- Gfxhub, VM, SR-IOV, and GPU IOV paths integrate with the VM/IOMMU/ATS, VF, scheduler, doorbell, reset, and SDMA status defaults.

Observed include sites in this tree include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`. Those files are the main bridge from this generated metadata into GC 9.0 graphics initialization, gfxhub/VM setup, and power-management behavior.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong default value compiles cleanly but can produce bad hardware initialization, misleading register dumps, or incorrect reset/suspend/resume restore.
- The chunk starts inside a prior address block. The first 33 macros are continued RLC/RMI performance-monitoring defaults; the final per-file research should merge the preceding chunk before assigning that block's full scope.
- The chunk ends the file. The trailing `#endif` belongs to the whole `gc_9_0_default.h` include guard, not to any one address block.
- RLC control and power-gating defaults are high risk. Incorrect `RLC_CNTL`, safe-mode, CGCG/CGLS, ramp, CU mask, GPM thread, or SRM defaults can break firmware bring-up, context save/restore, power gating, or GPU reset recovery.
- Repeated per-CU `CGTS_CU0..CU15_*` values look regular but are not completely uniform. Mechanical checks should preserve intentional variations such as `TA_SQC` and `TCPI` defaults.
- VM/IOMMU/ATS and GPU IOV defaults are security-sensitive in virtualized configurations. Bad VF masks, doorbell defaults, scheduler state, MARC windows, or ATS controls can affect isolation, address translation, or guest reset behavior.
- CAC and DIDT indexed registers are repetitive across many sub-blocks. A misplaced weight, accumulator, override, stall pattern, or EDC default can skew power accounting or throttling in ways that appear as performance variance rather than a hard failure.
- SQ wave registers are debug/state registers. Defaulting them to zero is unsurprising, but consumers must not infer that live wave state is stable or safe to overwrite from these defaults alone.
- Several defaults use full masks such as `0xffffffff` for status/request/mask-style registers. Code must understand whether a default is an inactive state, an enabled mask, or a hardware-reset sentinel before issuing full-register writes.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and runtime hardware signals:

- Build AMDGPU GC 9.0 code that includes this header, especially `gfx_v9_0.c`, `gfxhub_v1_0.c`, and Vega10 power-management include paths.
- Mechanically compare every macro in lines 2941-3866 against AMD's authoritative GC 9.0 register database and check that each has a matching offset macro in `gc_9_0_offset.h`.
- Cross-check defaults with `gc_9_0_sh_mask.h` so field values fit defined masks, especially nonzero RLC, CGTS/CGTT, VM/IOMMU, CAC, and DIDT defaults.
- Run static repetition checks across per-CU `CGTS_CU*_*`, VF `MC_VM_FB_SIZE_OFFSET_VF*`, `VM_PCIE_ATS_CNTL_VF_*`, CAC accumulator/weight/override families, and DIDT SQ/DB/TD/TCP/DBR families. The signal should be structural consistency plus documented intentional exceptions.
- Exercise GC 9.0 GPU boot, firmware loading, RLC safe-mode transitions, graphics reset, suspend/resume, and runtime power-management. Watch for failed RLC firmware start, hangs during reset, bad power-gating state, or unexpected clock-gating disables.
- Run gfxhub VM and SR-IOV-oriented tests where available: page-table setup, ATS behavior, VF enable/masking, doorbell handling, virtual reset, and SDMA busy-status reporting.
- Use register dumps on known-good GC 9.0 hardware to compare reset/default values for RLC, power, VM, hypervisor, CAC, SQ, and DIDT blocks after cold boot and after driver initialization.
- Run performance/power tests that stress SQ, TCP, TD, DB, DBR, cache, and shader blocks while observing CAC accumulators and DIDT stall counters for plausible movement and no unexpected throttling cliffs.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002611`. It covers lines 2941-3866 of `gc_9_0_default.h` and reaches the end of the file. The final per-file document should merge the continued performance-monitoring block from the previous chunk, then describe this range as the closing section containing RLC, power, virtualization, CAC, SQ wave, and DIDT default register values.
