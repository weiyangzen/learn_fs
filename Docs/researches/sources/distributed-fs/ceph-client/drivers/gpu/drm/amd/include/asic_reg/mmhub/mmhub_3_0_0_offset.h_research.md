# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_offset.h

## Purpose

`mmhub_3_0_0_offset.h` is a generated-style AMDGPU register-offset header for the MMHUB 3.0.0 hardware block. It exports symbolic preprocessor constants for MMHUB MMIO registers plus a matching `_BASE_IDX` constant for each register. The values are register offsets within SOC15 MMHUB address spaces, not executable logic and not byte arrays owned by this file.

Although the source path is under a `ceph-client` source mirror, the content is AMD DRM GPU memory-management hardware metadata. Its main consumer in this tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes this header together with `mmhub_3_0_0_sh_mask.h` and uses the offsets with SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

The header maps the MMHUB registers that support GPU virtual memory, GART aperture programming, framebuffer/system/AGP apertures, L1 and L2 TLB/cache configuration, VMID context tables, TLB invalidation engines, protection-fault reporting, ATC L2 controls, clock gating, performance counters, power/deep-sleep control, and PSP/SRIOV-related translation controls.

## Important APIs, Types, And Macro Families

This file defines no C functions, structs, enums, storage, or inline helpers. Its public API is the set of `#define reg...` constants and corresponding `#define reg..._BASE_IDX 0` constants guarded by `_mmhub_3_0_0_OFFSET_HEADER`.

The major address blocks are:

- `mmhub_dagbdec`, base address `0x68000`, 272 register offsets. It covers `DAGB0` and `DAGB1` data/address gateway registers for read and write clients, control, virtual-channel mapping, TLB/data credits, pending-state diagnostics, snoop/noalloc overrides, FIFO/fullness status, fatal-error status/clear controls, SDP controls, performance counters, and L1 TLB gateway registers.
- `mmhub_pctldec`, base address `0x68e00`, 58 register offsets. It covers MMHUB power-control, deep-sleep override, per-slice busy/deep-sleep allow registers, register-save ranges, RENG RAM index/data registers, status, and PCTL performance counters.
- L1 TLB blocks at `0x69600`, `0x69670`, and `0x69690`, defining `regMMMC_VM_MX_L1_TLB0_STATUS` through `TLB5_STATUS` plus L1 performance counter config/result registers.
- `mmhub_mmutcl2_mmatcl2dec`, base address `0x69b00`, defining ATC L2 controls, cache-data registers, status, clock/memory-power controls, SDP port controls, and FFBM invalidate/config access registers.
- `mmhub_mmutcl2_mmvml2pfdec`, base address `0x69c00`, defining VM L2 controls, status, dummy-page fault registers, invalidation control, protection-fault controls/status/address/default-address registers, identity aperture registers, PTE cache dump registers, bank-selection masks, and credit-safety registers.
- `mmhub_mmutcl2_mmvml2vcdec`, base address `0x69d00`, 220 register offsets. This is the densest block: 16 `regMMVM_CONTEXT*_CNTL` registers, 18 invalidation engine semaphore/request/ack registers, 18 invalidation address-range pairs, 16 context page-table base address pairs, 16 page-table start pairs, 16 page-table end pairs, and per-context PTE cache fragment-size registers.
- VM L2 and UTCL2 performance blocks at `0x6a090` and `0x6a0e0`, including `regMMMC_VM_L2_PERFCOUNTER*` and `regMMUTCL2_PERFCOUNTER*`.
- Shared VM hypervisor/PF/VC blocks at `0x6a130`, `0x6a340`, and `0x6a3b0`, defining per-VF framebuffer size/offset registers, system aperture default address registers, framebuffer offset/location, cacheable/local memory aperture registers, AGP aperture registers, and `regMMMC_VM_MX_L1_TLB_CNTL`.
- ATC L2 performance and PSP-related blocks at `0x6a400`, `0x6a420`, `0x6aa50`, `0x6aa80`, and `0x6aa90`, defining ATC L2 counters, translation bypass/fault controls, GPUVA/VMID translation assist controls, FFBM enable, and ATC IOV mode.
- L2 TLB blocks at `0x6aac0`, `0x6ab00`, and `0x6ab20`, defining TLB status, TMZ control, translation-assist request/response registers, credit safety, and performance counters.

All `_BASE_IDX` values in this file are `0`, so the symbols are intended for MMHUB base index 0 when used by SOC15 address-calculation macros. The companion `mmhub_3_0_0_sh_mask.h` supplies the field masks and shifts used to compose or decode values written to the offsets defined here.

## Control Flow

The header has no direct control flow. The runtime flow appears in consumers:

1. `mmhub_v3_0.c` includes this offset header and the matching shift/mask header.
2. MMHUB initialization stores selected offsets into `adev->vmhub[AMDGPU_MMHUB0(0)]` with `SOC15_REG_OFFSET`.
3. GART enable code writes context 0 page-table base/start/end registers, programs AGP/system/default/protection-fault apertures, enables L1 TLB and L2 cache controls, enables VM context 0, disables the identity aperture, configures VMIDs 1 through 15, and initializes invalidation address ranges.
4. Fault handling and diagnostics read MMVM protection-fault status fields with masks from the companion header and print decoded client IDs through AMDGPU MMHUB client-info helpers.
5. Clock-gating callbacks read and update `regMM_ATC_L2_MISC_CG` to report or toggle medium-grain clock gating and light sleep.

Several flows depend on arithmetic relationships between offsets rather than just individual names. `mmhub_v3_0_init()` computes `ctx_distance` from `regMMVM_CONTEXT1_CNTL - regMMVM_CONTEXT0_CNTL`, `ctx_addr_distance` from adjacent page-table base registers, `eng_distance` from adjacent invalidate request registers, and `eng_addr_distance` from adjacent invalidate address-range registers. VMID and invalidate-engine loops then use these distances with `*_OFFSET` register helpers.

## State And Persistence Behavior

The file itself is stateless source metadata. It does not allocate memory, cache values, hold locks, or persist runtime data. The constants identify hardware registers whose state persists in the GPU MMHUB until reset, power management transitions, firmware/PF programming, or explicit driver writes.

Important hardware state affected through these offsets includes:

- GART and VM page-table base/start/end registers for context 0 and VMIDs 1-15.
- MMHUB system, AGP, framebuffer, local framebuffer, local sysmem, and cacheable DRAM aperture registers.
- L1 TLB enable and policy bits in `regMMMC_VM_MX_L1_TLB_CNTL`.
- VM L2 cache enable, invalidation, fragment-size, bank-selection, and default-page behavior in `regMMVM_L2_CNTL*`.
- Protection-fault control, status, fault address, and default-address registers.
- Invalidation engine semaphores, requests, acknowledgements, and address ranges.
- ATC L2 clock-gating/light-sleep and performance-counter state.
- PCTL deep-sleep/register-save state and DAGB credit, pending, virtual-channel, and fatal-error status registers.

Some registers are deliberately skipped by `mmhub_v3_0.c` for SRIOV virtual functions because the physical function or host programs them instead. That makes the offsets part of a PF/VF boundary: incorrect use could fail silently in guests or target registers they are not allowed to access.

## Dependencies And Integration Points

The offset values depend on the MMHUB 3.0.0 register database matching the target ASIC. They must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h`, which defines fields for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, the direct consumer for MMHUB 3.0 initialization, GART enable/disable, fault configuration, aperture queries, and clock gating.
- SOC15 access infrastructure in AMDGPU, because `reg...` offsets and `_BASE_IDX` values are meaningful only after SOC15 combines them with the MMHUB IP base and instance.
- AMDGPU GMC and VM managers, whose GART, VMID, page-table, invalidation, and protection-fault operations use `adev->vmhub` offsets initialized from this header.
- SRIOV paths, because host/PF ownership determines which MMHUB registers a guest should not program.
- Debug, RAS-like telemetry, and performance tooling that may use DAGB, PCTL, TLB, VM L2, ATC L2, and UTCL2 counter/status offsets.

The header also shares many macro names with other MMHUB versions. It must not be mixed with a mismatched `mmhub_v*_*.c` implementation or a mismatched shift/mask header in the same translation unit, because duplicate `reg...` names can compile into plausible but wrong MMIO accesses.

## Risks And Edge Cases

- Offset drift is the highest-risk failure mode. A stale or incorrect value still compiles, but the driver can read or write the wrong hardware register.
- The VMID and invalidation loops rely on adjacent register spacing. If `CONTEXT*`, page-table address, invalidate request, or invalidate address-range offsets are wrong or nonuniform, the driver may program the wrong VMID or invalidation engine.
- Aperture offsets are safety-critical for memory access. Wrong `MMMC_VM_*` or `MMVM_CONTEXT*` offsets can cause GART failures, invalid physical address translation, GPU VM faults, data corruption, or hangs.
- Fault-control/status offsets affect recovery and diagnostics. Bad `regMMVM_L2_PROTECTION_FAULT_*` mappings can hide faults, redirect faults to the wrong default page, misreport client IDs, or make fault storms harder to suppress.
- Clock-gating offsets affect power-management behavior. Wrong `regMM_ATC_L2_MISC_CG` access can report false clock-gating state or toggle unrelated MMHUB controls.
- SRIOV access rules are easy to violate if new code uses these offsets without preserving the existing VF guards in `mmhub_v3_0.c`.
- Because this is generated hardware metadata in the global macro namespace, accidental inclusion of multiple MMHUB offset versions can create macro collisions or version skew between offsets and masks.
- Many defined registers are diagnostic or performance-counter registers not directly used in the core v3.0 bring-up path. They may receive less runtime coverage while still being important for debug tooling.

## Test Signals

Useful validation signals include:

- Building AMDGPU with `mmhub_v3_0.c`, `mmhub_3_0_0_offset.h`, and `mmhub_3_0_0_sh_mask.h` together to catch missing or renamed symbols.
- Mechanical comparison of every offset and `_BASE_IDX` against AMD's authoritative MMHUB 3.0.0 register specification.
- Static checks that `regMMVM_CONTEXT1_CNTL - regMMVM_CONTEXT0_CNTL`, `regMMVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - regMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regMMVM_INVALIDATE_ENG1_REQ - regMMVM_INVALIDATE_ENG0_REQ`, and `regMMVM_INVALIDATE_ENG1_ADDR_RANGE_LO32 - regMMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32` match the spacing assumed by `mmhub_v3_0.c`.
- Boot and GART enable tests on MMHUB 3.0 hardware, checking that page-table base/start/end programming succeeds and GPU memory accesses work.
- VM fault tests that exercise protection-fault reporting, fault default-page behavior, and decoded MMHUB client IDs.
- TLB/cache invalidation tests that confirm invalidate requests are acknowledged for all expected invalidation engines.
- SRIOV VF tests confirming that guarded aperture/cache/fault-control writes are skipped and that the host/PF-provided MMHUB state remains valid.
- Clock-gating and light-sleep tests that toggle `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`, then verify stable MMHUB operation and correct state reporting.
- Performance-counter smoke tests for DAGB, PCTL, L1/L2 TLB, VM L2, UTCL2, and ATC L2 counters under memory traffic, looking for plausible nonzero movement rather than static or nonsensical values.
