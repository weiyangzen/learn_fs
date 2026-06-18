# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h lines 4983-7279

## Scope

This chunk is the final slice of AMD's generated GC 9.0 register-offset header. It starts in the tail of the main graphics MMIO offset namespace, spans multiple explicit address blocks, defines several indirect-register namespaces, and closes the `_gc_9_0_OFFSET_HEADER` guard.

The file is hardware metadata for AMDGPU GC 9.x devices. It contains preprocessor constants only; there are no functions, structs, variables, allocations, locks, or executable branches in these lines. Runtime behavior comes from AMDGPU and power-management consumers that use these constants with SOC15 MMIO helpers or indirect-register accessors.

## Purpose

The purpose of this range is to publish the numeric register addresses and indirect indices needed by GC 9 driver code for graphics debug, performance monitoring, power management, virtualization, and low-level diagnostics.

The main covered areas are:

- Tail graphics-context offsets for PA/SC trap-screen counters, SQ thread tracing, SQC cache controls, TA buffer base, DB occlusion/Z-pass counters, GDS read/write/atomic windows, GWS/OA state, and SPI configuration.
- `gc_perfddec` at base `0x34000`, covering many block-level performance counter low/high data registers and matching select/control registers for CPG, CPC, CPF, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA, TD, TCP, TCC, TCA, CB, DB, RLC, and RMI.
- UTCL2/ATCL2 and VM L2 performance counter blocks for counter result and selection programming.
- `gc_rlcpdec` at base `0x3b000`, covering RLC control/status, safe mode, GPM timers and scratch space, power-gating/load-balance controls, SPM controls, SRM command windows, SMU/RLC command mailboxes, UTCL1/UTCL2 error/status registers, semaphores, and prewalker controls.
- `gc_pwrdec` and `gc_ea_pwrdec` at base `0x3c000`, covering CGTS per-CU power controls and CGTT clock-gating controls for major GC blocks.
- `gc_utcl2_vmsharedhvdec` and `gc_hypdec`, covering SR-IOV/hypervisor VM aperture, MARC, retry-fault, VF, CP, KIQ, SDMA, scratch, reset, interrupt, and RLC/SMU response registers.
- Indirect `gccacind`, `secacind`, `sqind`, and `didtind` namespaces for GC CAC weights/accumulators/overrides, SE CAC control, SQ wave debug state, and DIDT/EDC throttle tuning.

## Important APIs, Types, And Macros

The exported interface is a set of untyped C preprocessor constants. `mm*` names are SOC15 GC register offsets paired with `_BASE_IDX` macros, almost all using base index `1` in this range. `ix*` names are indirect register indices and do not have `_BASE_IDX` companions.

Important macro families include:

- Trap, shader trace, and render counters: `mmPA_SC_*TRAP_SCREEN_*`, `mmSQ_THREAD_TRACE_*`, `mmDB_OCCLUSION_COUNT*_LOW/HI`, and `mmDB_ZPASS_COUNT_LOW/HI`.
- GDS/GWS/OA control windows: `mmGDS_RD_*`, `mmGDS_WR_*`, `mmGDS_ATOM_*`, `mmGDS_GWS_RESOURCE*`, and `mmGDS_OA_*`.
- Performance data registers: `mm*_PERFCOUNTER*_LO/HI` for CP, front-end, geometry, shader, texture, cache, color/depth, RLC, and memory-interface blocks.
- Performance selection/control registers: `mm*_PERFCOUNTER*_SELECT`, `mm*_PERFCOUNTER*_SELECT1`, `mm*_PERFCOUNTER_CTRL`, `mmGRBM_PERFCOUNTER_SELECT`, `mmCP_PERFMON_CNTL`, and `mmRLC_GPU_IOV_PERF_CNT_*`.
- Streaming performance monitor state: `mmRLC_SPM_PERFMON_CNTL`, ring base/size/segment registers, mux-select address/data pairs, per-block sample-delay registers, `mmRLC_SPM_RING_RDPTR`, and `mmRLC_SPM_MC_CNTL`.
- RLC firmware and power-management controls: `mmRLC_CNTL`, `mmRLC_STAT`, `mmRLC_SAFE_MODE`, `mmRLC_UCODE_CNTL`, `mmRLC_PG_CNTL`, `mmRLC_CGCG_CGLS_CTRL`, `mmRLC_DYN_PG_*`, `mmRLC_GPM_*`, `mmRLC_SRM_*`, `mmRLC_SMU_*`, and `mmSMU_RLC_RESPONSE`.
- CGTS/CGTT controls: `mmCGTS_SM_CTRL_REG`, `mmCGTS_CU0_*` through `mmCGTS_CU15_*`, `mmCGTS_CU*_TCPI_CTRL_REG`, `mmCGTT_*_CLK_CTRL`, `mmSQ_POWER_THROTTLE*`, `mmRLC_GFX_RM_CNTL`, and `mmGCEA_CGTT_CLK_CTRL`.
- Virtualization and hypervisor registers: `mmMC_VM_FB_SIZE_OFFSET_VF0` through `VF15`, `mmMC_VM_MARC_*`, `mmVM_IOMMU_MMIO_CNTRL_1`, `mmRLC_GPU_IOV_*`, `mmCP_*_VF*`, `mmCP_MEC_RS64_*`, and KIQ/SDMA status controls.
- Indirect CAC indices: `ixGC_CAC_CNTL`, `ixGC_CAC_WEIGHT_*`, `ixGC_CAC_ACC_*`, `ixGC_CAC_OVRD_*`, plus the minimal `ixSE_CAC_*` set.
- Indirect SQ wave indices: `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO/HI`, `ixSQ_WAVE_EXEC_LO/HI`, `ixSQ_WAVE_M0`, `ixSQ_WAVE_TTMP0` through `TTMP15`, and `ixSQ_INTERRUPT_WORD_*`.
- Indirect DIDT/EDC indices: repeated `ixDIDT_{SQ,DB,TD,TCP,DBR}_CTRL*`, stall-control, tuning, weight, EDC threshold/status/delay/overflow, and stall-event-counter registers.

This header is included by GC 9 driver and support files such as `amdgpu/gfx_v9_0.c`, `amdgpu/gfxhub_v1_0.c`, `amdgpu/mxgpu_ai.c`, `amdkfd/kfd_mqd_manager_v9.c`, PSP units, and the Vega10 powerplay include path.

## Control Flow

There is no in-file control flow. Consumer-side control flow follows hardware access protocols:

1. MMIO consumers pass `mm*` offsets into helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, or no-KIQ variants.
2. RLC safe-mode users read `mmRLC_CNTL`, write `mmRLC_SAFE_MODE`, and poll the corresponding command field before changing clock/power-gating state. `gfx_v9_0.c` uses this pattern around GC power-gating updates.
3. SQ debug users write `mmSQ_IND_INDEX` with wave, SIMD, thread, and indirect-index fields, then read `mmSQ_IND_DATA`; the `ixSQ_WAVE_*` constants from this chunk identify the requested per-wave state.
4. Powerplay DIDT/CAC programming uses indirect register interfaces, for example `cgs_read_ind_register()` and `cgs_write_ind_register()` with `CGS_IND_REG__DIDT` or `CGS_IND_REG_GC_CAC`, and uses `gc_9_0_sh_mask.h` field masks to update individual fields.
5. Performance monitoring code programs select/control registers, optionally configures RLC SPM ring/mux/sample-delay state, then reads counter low/high result registers or SPM ring data.
6. SR-IOV and hypervisor-aware paths use the VF, GPU IOV, KIQ, CP, RLC, SMU, and SDMA status registers to coordinate virtual functions, resets, interrupts, and virtualization-visible status.

## State And Persistence Behavior

The macros do not hold software state. They identify hardware registers whose state is stored in the GPU until reset, firmware reinitialization, power transition, or explicit driver/firmware writes.

Relevant state categories include:

- Counter state: performance counters, occlusion counters, Z-pass counters, CAC accumulators, DIDT event counters, and GDS/OA counters can change as hardware executes work. Low/high counter halves require ordered reads by consumers if a stable 64-bit sample is needed.
- Trace and debug state: SQ thread-trace base/size/mask/control/status and SQ wave indirect data reflect active GPU execution state. Wave state is volatile and can become stale or invalid if the wave exits between selection and read.
- RLC state: safe mode, firmware control, GPM scratch/log/register windows, SRM command status, power-gating, load-balance, and clock-count registers are persistent hardware/firmware coordination points during a boot or resume cycle, but are not durable across GPU reset.
- Power and clock state: CGTS and CGTT registers configure per-block clock-gating and power behavior. Incorrect writes can affect latency, hangs, performance, and power draw until the next corrective write or reset.
- Virtualization state: VM aperture, MARC, VF, GPU IOV, KIQ, and SDMA status/control registers expose per-virtual-function or hypervisor-mediated state. These registers are especially sensitive to function ownership and reset sequencing.

## Dependencies And Integration Points

This generated offset file must remain synchronized with related AMD register metadata:

- `gc_9_0_sh_mask.h` supplies bit masks and shifts for fields inside the offsets defined here.
- `gc_9_0_default.h` supplies default values for many corresponding registers.
- SOC15 access helpers translate `mm*` offsets and `_BASE_IDX` values into real MMIO addresses for the GC hardware block.
- CGS/Powerplay indirect access helpers translate `ixGC_CAC_*` and `ixDIDT_*` indices into the correct GC CAC and DIDT indirect register paths.
- SQ debug code in `gfx_v9_0.c` depends on `ixSQ_WAVE_*` values matching the hardware SQ indirect protocol.
- RLC, SPM, and power-gating code depends on these offsets matching firmware expectations for safe mode, GPM, SRM, SPM, and SMU mailboxes.
- SR-IOV and virtualization paths depend on the `mmRLC_GPU_IOV_*`, VF aperture, KIQ, CP, and SDMA status offsets being correct for the virtualized ASIC mode.

The enclosing source tree path includes `ceph-client`, but this file is AMD GPU driver metadata and has no distributed-filesystem control path.

## Risks And Edge Cases

- These are untyped constants. A wrong numeric value can compile cleanly and cause writes to the wrong hardware register.
- The chunk mixes direct MMIO offsets and indirect indices. Using an `ix*` index with SOC15 MMIO helpers, or an `mm*` offset with an indirect accessor, would target the wrong register path.
- `_BASE_IDX` values matter for SOC15 addressing. Most values here are `1`; changing them independently of generated block metadata can silently retarget a register.
- Low/high counter pairs can tear if sampled without the hardware-recommended sequence, especially for busy performance or occlusion counters.
- RLC safe-mode and firmware command registers require polling and timeout handling. Incorrect sequencing can leave power-gating or clock-gating transitions incomplete.
- Power and DIDT/EDC tuning registers can throttle or destabilize the GPU if programmed with values intended for a different ASIC, stepping, or firmware policy.
- SR-IOV/hypervisor registers are ownership-sensitive. Guest, host, and firmware code must not assume the same write authority for all offsets.
- The final `#endif` is part of this chunk. Removing or duplicating it would break inclusion of the entire generated header.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 9/Vega10 support enabled. Missing or renamed macros should fail in `gfx_v9_0.c`, KFD GC 9 MQD code, gfxhub, PSP, SR-IOV, or powerplay units that include this header.
- Compare this generated block against AMD's authoritative GC 9.0 register database and sibling generated files (`gc_9_0_sh_mask.h`, `gc_9_0_default.h`), allowing only expected generated-header formatting differences.
- Exercise GPU wave-debug dump paths and verify that `ixSQ_WAVE_EXEC_LO/HI`, `PC`, `STATUS`, allocation, trap, IB, `M0`, and mode fields correlate with active waves.
- Exercise perf counter and RLC SPM collection on GC 9 hardware; wrong offsets should show implausible zero/stuck counters, bad ring pointers, or mismatched select/data behavior.
- Test suspend/resume, runtime power management, and gfx clock/power gating. Failures around `mmRLC_SAFE_MODE`, `mmCGTT_*`, or `mmCGTS_*` offsets commonly appear as hangs, timeout logs, or bad power/performance behavior.
- Test Vega10 DIDT/EDC enable/disable and powerplay transitions. Bad `ixDIDT_*` or `ixGC_CAC_*` indices would surface as failed indirect writes, power-feature errors, or incorrect throttling behavior.
- Test SR-IOV reset and VF activity paths where `mmRLC_GPU_IOV_*`, VM aperture, CP, KIQ, and SDMA status registers are used.

## Cross-Chunk Notes

This is the tail chunk of `gc_9_0_offset.h`. The final per-file research document should merge it with earlier chunks that define the initial GC 9 global, GRBM, CP, queue, graphics pipeline, shader, texture/cache, and direct MMIO namespaces. In particular, this chunk starts mid-address-block before `gc_perfddec`, so the preceding chunk is needed to describe the complete graphics-context block that owns the PA/SC, SQ, SQC, TA, DB, GDS, and SPI offsets at the beginning of this range.
