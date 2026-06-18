# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h lines 9969-12437

## Scope

This chunk is a generated register-offset segment from the AMD GC 10.3.0 ASIC register header. It covers line 9969 through line 12437 and contains 1,217 visible register offset macros plus their generated `_BASE_IDX` companion macros where the companion falls inside this range. The range starts in the tail of a CP/GC hypervisor register area, continues through SDMA hypervisor, GCVM shared hypervisor, PSP, GCVM L2 PSP, and SDMA2/SDMA3 decoder blocks, and ends inside the `SDMA3_RLC5` queue register family before the next line's `_BASE_IDX` companion.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, locks, or local side effects. Its public interface is the preprocessor namespace of `mm...` offset constants and `mm..._BASE_IDX` selector constants consumed by AMDGPU/KFD register access helpers.

## Purpose

`gc_10_3_0_offset.h` supplies symbolic MMIO register offsets for GC 10.3.0-class AMD GPU IP. Consumers combine these macros with SOC15 register-base tables and helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_ENTRY_STR` so driver code can address hardware registers without embedding raw offsets.

This chunk maps three broad hardware surfaces:

- Command processor, graphics register bus, RLC, SR-IOV, and GCVM hypervisor-visible registers under base index 1.
- SDMA0 through SDMA3 hypervisor decoder windows for microcode, VM context, active function, VF enable, and register-type classification.
- SDMA2 and SDMA3 public decoder windows under base index 2, including engine-global control/status registers and per-queue GFX/PAGE/RLC ring and indirect-buffer registers.

The chunk is especially important for virtualization and multi-SDMA support on GC 10.3.0. It names the offsets used to program CP firmware windows, classify and access virtualized SDMA registers, expose per-VF framebuffer and MARC ranges, service GCVM/IOMMU handshakes, and compute SDMA engine/queue register addresses for KFD and SDMA ring management.

## Exported API Surface

There are no callable APIs or local types. The exported surface is the generated macro set:

- CP and MES firmware/register windows: `mmCP_HYP_CE_UCODE_ADDR`, `mmCP_CE_UCODE_DATA`, `mmCP_HYP_MEC1_UCODE_ADDR`, `mmCP_MEC_ME1_UCODE_DATA`, `mmCP_HYP_MEC2_UCODE_ADDR`, `mmCP_MEC_ME2_UCODE_DATA`, plus PFP/ME/CE/CPC/MES instruction-cache base/control/op registers and MES instruction/data/local base, mask, bound, and aperture registers.
- GRBM and GC interrupt routing registers: `mmGFX_PIPE_PRIORITY`, `mmGRBM_GFX_INDEX_SR_SELECT`, `mmGRBM_GFX_INDEX_SR_DATA`, `mmGRBM_GFX_CNTL_SR_SELECT`, `mmGRBM_GFX_CNTL_SR_DATA`, GRBM CAM index/data/upper aliases including hypervisor names, `mmGC_IH_COOKIE_0_PTR`, and `mmGRBM_SE_REMAP_CNTL`.
- RLC GPU IOV and virtualization registers: `mmRLC_GPU_IOV_VF_ENABLE`, config registers, VM busy and scheduler registers, active function ID, VF doorbell status/set/clear/mask, hypervisor semaphores, pace/timer/interrupt controls, SRM/FW/host/SCP responses, scratch and ucode address/data registers, graphics idle/workload counters, and SDMA0 through SDMA7 status and busy-status mirrors.
- SDMA hypervisor decoder blocks: `gc_sdma0_sdma0hypdec` through `gc_sdma3_sdma3hypdec` provide `mmSDMA{0,1,2,3}_UCODE_ADDR`, `UCODE_DATA`, `VM_CTX_LO/HI`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, `VIRT_RESET_REQ`, `VF_ENABLE`, `CONTEXT_REG_TYPE0..3`, `PUB_REG_TYPE0..3`, and `VM_CNTL`; SDMA0 also includes broadcast ucode address/data.
- GCVM shared hypervisor registers: `mmGCMC_VM_FB_SIZE_OFFSET_VF0` through `VF31`, `mmGCVM_IOMMU_MMIO_CNTRL_1`, MARC base/reloc/length low/high registers for four ranges, `mmGCVM_IOMMU_CONTROL_REGISTER`, `mmGCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, and `mmGCMC_VM_XGMI_GPUIOV_ENABLE`.
- PSP-facing GC registers: `mmCPG_PSP_DEBUG`, `mmCPC_PSP_DEBUG`, `mmGRBM_SEC_CNTL`, `mmRLC_FWL_FIRST_VIOL_ADDR`, and `mmRLC_SRM_FWL_FIRST_VIOL_ADDR`.
- GCVM L2 PSP decoder registers: `mmGCVM_L2_ID_CTRL0..7`, `mmGCVM_L2_ID_CTRL_HI`, `mmGCVM_L2_ID_STATUS`, `mmGCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `mmGCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, and GPUVA VMID translation assist request/response low/high registers.
- SDMA2 public decoder registers: engine-wide control/status and telemetry (`DEC_START`, timestamps, power/clock/control/chicken bits, GB address config, status, burst, EDC, atomic, UTCL1, timeout, error log, scratch, timestamp, interrupt, queue reset), followed by GFX, PAGE, and RLC0 through RLC7 queue register families.
- SDMA3 public decoder registers: the same generated engine-wide and queue-family pattern as SDMA2, beginning at offset `0x0400`; this chunk covers GFX, PAGE, RLC0 through RLC4 completely and starts RLC5 through `mmSDMA3_RLC5_RB_RPTR_ADDR_LO`.

Most SDMA queue families follow the same register pattern: `RB_CNTL`, ring-buffer base low/high, read/write pointers low/high, write-pointer polling control and polling address, indirect-buffer control/read pointer/offset/base/size, skip control, context status, doorbell, status/log/watermark/doorbell offset, context-save-area address low/high, indirect-buffer sub-remain, preempt, dummy register, AQL control, minor pointer update, and `MIDCMD_DATA0..10` plus `MIDCMD_CNTL`.

## Control Flow And State Behavior

The header itself has no runtime control flow. It affects runtime behavior when included driver code resolves a symbolic register name to an MMIO address and reads or writes the hardware register.

The named registers describe several persistent hardware state areas:

- CP/MES microcode and cache programming registers persist firmware addressing and instruction/data-cache control state until reset, firmware reinitialization, power-domain loss, or explicit driver/firmware reprogramming.
- GRBM shadow-register and CAM controls steer which graphics instance, shadow register, or virtualized context is accessed. These registers are tied to register-indexing and virtualization state rather than process-owned memory.
- RLC GPU IOV registers hold SR-IOV/PF/VF scheduling, active-function, doorbell, interrupt, semaphore, VM-busy, and SDMA status state. Some are status/readback-oriented, while others are control or clear/set registers with side effects outside this header.
- SDMA hypervisor decoder registers expose per-engine virtualization controls: active function, VF enable, VM context, virtual reset request, and public/context register classification. Those settings determine what SDMA state is visible to guest functions and how SDMA MMIO is partitioned.
- GCVM shared hypervisor registers persist per-VF framebuffer size/offset and MARC base/relocation/length windows. These are global virtualization memory-controller settings, not per-process driver data.
- GCVM L2 PSP/IOMMU translation-assist registers participate in host translation, VMID bypass, and request/response handshakes. The macros do not encode ownership, ordering, or clear semantics; those must be inferred from register documentation and caller paths.
- SDMA2/SDMA3 public decoder registers represent live DMA engine state: ring-buffer and indirect-buffer pointers, base addresses, doorbell offsets, preemption, context-save addresses, UTCL1 translation status, queue reset requests, EDC/error counters, and mid-command capture/control state. These registers persist while the engine is powered and are restored or rebuilt during driver init, reset, suspend/resume, or queue recreation.

Repeated SDMA queue offsets are used arithmetically by callers. KFD code computes a queue's register window by taking the delta between `mmSDMA*_RLC1_RB_CNTL` and `mmSDMA*_RLC0_RB_CNTL`, while SDMA code maps instance IDs to SOC15 base-index windows. Incorrect spacing in this header changes runtime address calculation even if the caller never references every individual macro.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, these offsets must stay aligned with the matching GC 10.3.0 shift/mask and default headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h`

Important integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, which includes this offset header, builds SDMA register debug lists, computes SDMA instance offsets with base index 0/1/2 windows, and reads/writes GFX/PAGE/RLC ring pointers, doorbells, VM controls, and queue reset state through the generated SDMA names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, which includes this header and computes KFD SDMA RLC queue offsets for SDMA0 through SDMA3 using `mmSDMA*_RLC0_RB_CNTL` and the RLC queue stride.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`, which includes the GC 10.3.0 offset/sh_mask/default set for GFXHUB VM setup, system aperture/default-page programming, TLB/cache setup, VM invalidation, and fault reporting. This chunk contributes related GCMC/GCVM hypervisor and PSP-facing names, while earlier/later chunks hold many of the ordinary VM context offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`, which carries local definitions for `mmCP_HYP_CE_UCODE_ADDR` and writes that register during CE firmware version handling. The duplicate local definition signals that the CP hypervisor offset is a known integration point even in code paths not directly using this header name from the include.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`, which includes this header from a power-management path, making compile-time namespace stability relevant outside the graphics and KFD files.

At runtime, these macros integrate with AMDGPU's SOC15 register-offset tables, firmware loading, SR-IOV PF/VF handling, GFXHUB/GCVM memory management, SDMA ring and queue bring-up, KFD compute queue management, diagnostics/register dumps, suspend/resume restore, GPU reset, and hardware error/fault reporting.

## Risks

- Generated-header drift is the primary risk. A wrong offset or base index can silently direct reads or writes to the wrong MMIO register.
- The range mixes base index 1 hypervisor/GCVM/PSP registers with base index 2 SDMA2/SDMA3 public decoder registers. Misclassified `_BASE_IDX` values can make SOC15 helpers address the wrong register aperture.
- Several macros are aliases for the same offset, such as CP hypervisor and non-hypervisor CE/MEC ucode names, and GRBM CAM hypervisor aliases. Removing or changing aliases can break consumers that depend on either naming convention.
- SDMA queue families are highly repetitive and are used with computed strides. Any inconsistent offset inside `RLC0..RLC7`, GFX, or PAGE queues can cause only one queue or one engine to fail, which is harder to diagnose than a global compile failure.
- SDMA2 and SDMA3 offsets share the same base index but different internal offsets. Instance mapping in `sdma_v5_2_get_reg_offset()` depends on the relationship among SDMA0/1 and SDMA2/3 windows; wrong constants can corrupt the wrong engine's queue state.
- Ring pointer, polling-address, doorbell, and CSA address registers are live queue-control state. Bad addresses can hang queues, lose interrupts, corrupt context-save memory, or leave firmware polling stale pointers.
- RLC GPU IOV and SDMA hypervisor registers are ownership-sensitive. PF, VF, firmware, PSP, and host-driver responsibilities differ by mode; blind writes through a wrong macro can violate virtualization boundaries or collide with firmware-managed state.
- GCVM shared hypervisor and IOMMU/MARC registers affect address translation and per-VF memory windows. Incorrect programming can expose the wrong framebuffer range, break XGMI/GPUIOV isolation, or route DMA to unintended physical memory.
- PSP-facing security and firewall violation registers are likely security-sensitive. Misaddressed debug or violation-address registers can hide genuine protection faults or produce misleading diagnostics.
- This chunk starts and ends at generated-file boundaries inside larger groups. Merge-time validation should not treat the missing address-block comment before line 9969 or the missing `mmSDMA3_RLC5_RB_RPTR_ADDR_LO_BASE_IDX` line after 12437 as defects in this chunk alone.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU, KFD, and SW-SMU files that include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and `gc_10_3_0_default.h`.
- Generated-data checks that every register macro in the full header has the expected `_BASE_IDX` companion, allowing explicit chunk-boundary exceptions at line 12437.
- Cross-check the offsets and base indices against the GC 10.3.0 register database and the matching shift/mask/default headers.
- SDMA v5.2 bring-up tests on GC 10.3.0-class hardware: firmware load, ring creation, read/write pointer updates, doorbell and non-doorbell paths, indirect-buffer execution, queue reset, preemption, and register-dump readability across SDMA0 through SDMA3.
- KFD SDMA queue tests that create queues on multiple SDMA engines and RLC queue IDs, validating that queue stride arithmetic lands on the expected `RLCn` register windows.
- SR-IOV PF/VF tests that exercise active-function selection, VF enable/disable, virtual reset, doorbell status, SDMA status mirrors, and per-VF framebuffer/MARC window programming.
- VM and translation tests around GFXHUB/GCVM/IOMMU integration: GART/system aperture setup, VMID translation-assist request/response paths, invalidation, and protection-fault reporting.
- Suspend/resume and GPU reset tests that verify SDMA, RLC IOV, GCVM, and CP/MES state is restored by the correct owner or intentionally reinitialized.
- Fault-injection or diagnostics tests for SDMA UTCL1 status/XNACK, EDC/error counters, PSP/RLC firewall violation address reporting, and GCVM L2 ID/status registers.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 9969-12437 of `gc_10_3_0_offset.h`. Earlier chunks should cover the start of the surrounding CP/GC hypervisor address block and earlier SDMA0/SDMA1 public decoder families. Later chunks should continue `SDMA3_RLC5` after `mmSDMA3_RLC5_RB_RPTR_ADDR_LO`, then cover the rest of RLC5, RLC6/RLC7, and subsequent GC 10.3.0 register blocks. The final per-file report should describe the whole file as a generated GC 10.3.0 MMIO offset map consumed by AMDGPU, KFD, SDMA, GFXHUB, firmware, virtualization, and diagnostics paths.
