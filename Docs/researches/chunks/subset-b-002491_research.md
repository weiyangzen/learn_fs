# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 37448-39877

## Scope

This chunk is part of the generated AMD GC 10.3.0 shift/mask register header. It contains only C preprocessor constants: each hardware field is represented by a `<REGISTER>__<FIELD>__SHIFT` value and a matching `<REGISTER>__<FIELD>_MASK` value. There are no functions, structs, enums, includes, memory allocations, locks, callbacks, runtime branches, or direct MMIO operations in this range.

The selected lines begin in the tail of the `SDMA1_PUB_REG_TYPE1` masks, cover SDMA1 public register type summaries 2 and 3, then define the visible GC SDMA2 and SDMA3 hypervisor decode summaries. The chunk continues through GCVM shared hypervisor/SR-IOV and MARC virtual-memory controls, PSP-facing firewall and translation-assist controls, and the start of the concrete `gc_sdma2_sdma2dec` register block through `SDMA2_PAGE_RB_WPTR_POLL_CNTL`. The range ends mid-register, so the matching `SDMA2_PAGE_RB_WPTR_POLL_CNTL` masks continue in the next source lines outside this chunk. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata and is not Ceph filesystem logic.

## Purpose

`gc_10_3_0_sh_mask.h` supplies bitfield layouts for AMD graphics IP version 10.3.0. Driver code includes it with the matching GC 10.3.0 offset and default headers so register helpers can compose, extract, or preserve field values for the active ASIC generation.

This chunk serves five main purposes:

- It finishes SDMA1 public register type masks and enumerates SDMA2/SDMA3 hypervisor-visible register-summary bitmaps. The `*_CONTEXT_REG_TYPE*` and `*_PUB_REG_TYPE*` registers act as compact capability/visibility maps for groups of SDMA context, public, VM, microcode, VF, and status registers.
- It describes virtualization state for SDMA2 and SDMA3 hypervisor decoders: microcode address/data windows, VM context low/high addresses, active VF identity, VF/PF reset requests, VF enable, VMID/privilege controls, and per-engine register availability summaries.
- It defines GCVM shared hypervisor fields used by SR-IOV and GPU virtual memory. These include framebuffer size/offset registers for VF0 through VF31, MARC aperture base/relocation/length registers for four regions, IOMMU MARC enable, IOMMU control/performance knobs, and XGMI GPU IOV enable bits for VFs and the PF.
- It defines PSP-facing security and translation fields: CPG/CPC PSP GPA override bits, first firewall violation address/op/aperture reporting for RLC and SRM, VMID/client/group fault status, VMID bypass/GPA controls, GPU-host translation enable, and GPUVA-to-VMID translation-assist request/response payload fields.
- It starts the concrete SDMA2 decode register layout used to initialize, control, monitor, and recover the second SDMA engine. Covered fields include power and clock gating, engine control, copy-engine tuning, address swizzle configuration, idle/status registers, error detection counters, UTCL1 translation controls, invalidation/XNACK details, public status registers, GFX ring/IB/doorbell/context state, mid-command preemption state, and the beginning of the PAGE ring controls.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding 32-bit field mask.
- Matching register addresses live in `gc_10_3_0_offset.h`; matching reset values, where generated, live in `gc_10_3_0_default.h`.
- Consumers normally use these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, SDMA MMIO helpers, PSP/VM accessors, and SR-IOV register programming paths.

The SDMA public summary macros in this chunk are grouped by engine:

- `SDMA1_PUB_REG_TYPE2` and `SDMA1_PUB_REG_TYPE3` enumerate SDMA1 public registers such as UTCL1 invalidate/XNACK/timeout/page controls, physical address capture, phase2 quantum, error logs, dummy registers, F32/performance counters, CRD control, AQL status, EA double-bit address capture, TLBI/GCR control, tiling configuration, interrupt/status registers, scratch RAM, timestamp, and queue reset.
- `SDMA2_CONTEXT_REG_TYPE0..3` and `SDMA3_CONTEXT_REG_TYPE0..3` enumerate GFX context register groups: ring base/read/write pointers, write-pointer polling, read-pointer writeback addresses, IB controls and base/size registers, context status/control, doorbell, watermark, CSA, preempt, AQL, minor pointer update, and mid-command data/control slots.
- `SDMA2_PUB_REG_TYPE0..3` and `SDMA3_PUB_REG_TYPE0..3` enumerate public engine registers such as reset/start, timestamps, power/clock/control/chicken bits, address configuration, status pages, UTCL1 status/invalidation/XNACK controls, TLBI/GCR, scratch/timestamp, status, and queue reset.

The GCVM and virtualization macros include these notable families:

- `GCMC_VM_FB_SIZE_OFFSET_VF0..VF31`: each has `VF_FB_SIZE` in bits `[15:0]` and `VF_FB_OFFSET` in bits `[31:16]`, giving a compact per-VF framebuffer aperture size/offset encoding.
- `GCVM_IOMMU_MMIO_CNTRL_1__MARC_EN`: controls MARC enablement.
- `GCMC_VM_MARC_BASE_LO/HI_0..3`, `GCMC_VM_MARC_RELOC_LO/HI_0..3`, and `GCMC_VM_MARC_LEN_LO/HI_0..3`: describe four MARC base, relocation, enable/read-only, and length windows. Low address fields commonly start at bit 12, reflecting page-aligned apertures.
- `GCVM_IOMMU_CONTROL_REGISTER`, `GCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, and `GCMC_VM_XGMI_GPUIOV_ENABLE`: control IOMMU behavior and per-function GPU IOV enablement.
- `GCVM_L2_ID_CTRL0..7`, `GCVM_L2_ID_CTRL_HI`, and `GCVM_L2_ID_STATUS`: define VMID enable vectors and fault reporting fields for VMID, client ID, group ID, and interrupt-on-fault status.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_*`: encode translation bypass/GPA mode, host translation enable, and request/response data for GPU virtual address translation assistance.

The SDMA2 concrete register macros include these major groups:

- Engine lifecycle and power: `SDMA2_DEC_START`, global timestamp registers, `SDMA2_PG_CNTL`, `SDMA2_PG_CTX_LO/HI`, `SDMA2_PG_CTX_CNTL`, `SDMA2_POWER_CNTL`, and `SDMA2_CLK_CTRL`.
- Global engine control and tuning: `SDMA2_CNTL`, `SDMA2_CHICKEN_BITS`, `SDMA2_GB_ADDR_CONFIG`, `SDMA2_GB_ADDR_CONFIG_READ`, burst and page-size controls, phase quantum registers, BA threshold, ID/version, and F32 control/counter/checksum registers.
- Runtime status and error reporting: `SDMA2_STATUS_REG`, `SDMA2_STATUS1_REG`, `SDMA2_STATUS2_REG`, `SDMA2_STATUS3_REG`, `SDMA2_STATUS4_REG`, `SDMA2_STATUS5_REG`, `SDMA2_EDC_CONFIG`, `SDMA2_EDC_COUNTER`, `SDMA2_EDC_COUNTER_CLEAR`, `SDMA2_ERROR_LOG`, `SDMA2_INT_STATUS`, and queue reset request bits.
- Translation and memory-system controls: `SDMA2_UTCL1_CNTL`, `SDMA2_UTCL1_WATERMK`, read/write UTCL1 status registers, invalidation registers, read/write XNACK registers, timeout/page registers, physical address registers, TLBI/GCR control, tiling config, and credit control.
- GFX queue context: `SDMA2_GFX_RB_CNTL`, ring base/RPTR/WPTR registers, WPTR polling and polling address registers, read-pointer writeback address registers, IB control/base/size/offset/read-pointer registers, context status/control, doorbell and doorbell log/offset, watermark, CSA address, IB sub-remaining, preempt, AQL, minor pointer update, and mid-command data/control registers.
- PAGE queue context begins with `SDMA2_PAGE_RB_CNTL`, ring base/RPTR/WPTR registers, and the first `SDMA2_PAGE_RB_WPTR_POLL_CNTL` shift definitions. The mask definitions for that final register are outside this chunk.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time substitution of numeric constants.

The implied driver flow is:

1. Include `gc_10_3_0_offset.h`, `gc_10_3_0_sh_mask.h`, and sometimes `gc_10_3_0_default.h` for the selected ASIC family.
2. Select the correct register address and base index for GC 10.3.0.
3. Read a 32-bit register value, or prepare a 32-bit value for writing.
4. Use the generated mask/shift pair, usually through `REG_GET_FIELD` or `REG_SET_FIELD`, to extract status fields or update a single field while preserving unrelated bits.
5. Execute the sequencing in higher-level AMDGPU code: SDMA engine init/resume, queue setup, VM programming, SR-IOV configuration, PSP firewall handling, reset recovery, or fault diagnostics.

For SDMA2 queue setup, the higher-level flow normally programs ring base addresses, writeback addresses, polling controls, doorbell offset/enable, VMID/privilege bits, and ring size, then enables the ring. For fault or hang diagnostics, code reads the status, UTCL1, XNACK, physical address, and queue-status fields to infer whether an SDMA queue is idle, stalled, faulted, preempted, or waiting on translation/memory-system resources. For virtualization, SR-IOV and hypervisor-facing code uses the VF identity, enable, reset, framebuffer aperture, MARC, and GPU IOV masks to isolate or expose GPU resources to guest functions.

## State And Persistence Behavior

The macros themselves are stateless and do not persist anything. They describe fields in GPU hardware registers.

SDMA public and context summary registers are hardware-visible metadata/capability bitmaps. Their values are generally fixed by the ASIC/register block or programmed by firmware/hypervisor control paths, not by normal per-command driver flow. They may be read to determine which context or public registers are available for a VF/PF or to build save/restore masks.

GCVM and virtualization registers represent persistent hardware configuration state: VF framebuffer apertures, MARC mappings, IOMMU policy, GPU IOV enablement, VMID fault behavior, and translation-assist control. These values may persist until GPU reset, graphics IP reset, suspend/resume reinitialization, virtualization teardown, or explicit hypervisor/driver writes. Fault status and translation-assist request/response fields are hardware-owned and volatile or handshake-driven.

Concrete SDMA2 registers mix configuration state with live hardware state. Ring base addresses, VMID/privilege bits, polling address, doorbell setup, AQL controls, timing knobs, and power/clock controls are driver-owned configuration that must be restored after reset or power loss. Ring pointers, status registers, UTCL1 status, XNACK details, error counters, timestamps, interrupt status, doorbell captured/log bits, and mid-command state are hardware-updated live state. Some fields may be sticky, self-clearing, write-one-to-clear, read-only, or side-effectful; this generated header does not encode access semantics.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` supplies matching register addresses such as `mmSDMA2_CONTEXT_REG_TYPE0`, `mmSDMA2_GFX_RB_CNTL`, and `mmSDMA2_PAGE_RB_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` supplies reset/default values such as `mmSDMA2_CONTEXT_REG_TYPE0_DEFAULT`, `mmSDMA2_GFX_RB_CNTL_DEFAULT`, and `mmSDMA2_PAGE_RB_CNTL_DEFAULT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`, `amdgpu_sdma.c`, `gfxhub_v2_1.c`, `amdgpu_amdkfd_gfx_v10_3.c`, and `pm/swsmu/smu11/vangogh_ppt.c` include this GC 10.3.0 mask header or depend on the same register namespace.
- The broader AMDGPU register-helper layer provides SOC15 MMIO access, read-modify-write helpers, and register-field extraction helpers.

Integration points include:

- SDMA v5.2 initialization, ring setup, queue preemption/reset, command submission, timeout/hang recovery, and suspend/resume restore.
- GFXHUB v2.1 and GCVM programming for address translation, VMID policy, translation bypass, GPU host translation, and page-fault diagnostics.
- KFD/GFX 10.3 compute integration, where SDMA queues, AQL controls, VMIDs, doorbells, and preemption state matter for user-mode queues.
- SR-IOV and hypervisor paths that manage VF identity, VF enable/reset, per-VF framebuffer aperture maps, MARC windows, GPU IOV enable masks, and PSP/firewall reporting.
- Power-management and clock-gating code that relies on SDMA power/clock control and status fields to gate or resume the engine safely.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Incorrect mask or shift values compile cleanly but can set the wrong hardware bit, causing queue setup failures, VM faults, virtualization isolation bugs, broken power gating, or misleading diagnostics.
- This chunk starts mid-`SDMA1_PUB_REG_TYPE1` and ends mid-`SDMA2_PAGE_RB_WPTR_POLL_CNTL`. The final per-file research must merge adjacent chunks before claiming complete coverage of those register families.
- The SDMA2 and SDMA3 hypervisor summary registers are highly repetitive. Copy/paste or generation mistakes can silently expose or omit the wrong register in a VF/PF context.
- SR-IOV and MARC fields are isolation-sensitive. Bad framebuffer offsets/sizes, relocation windows, read-only flags, or GPU IOV enable bits can break guest memory isolation or block legitimate VF access.
- Translation-assist request/response fields are handshake-style hardware state. Polling, acknowledging, or writing them with the wrong field width can lose requests, misreport permissions, or return stale translations.
- SDMA ring fields include 64-bit addresses split across low/high registers with alignment-implied low bits. Truncating high bits, forgetting low-bit shifts, or mixing GFX and PAGE ring fields can point the engine at the wrong memory.
- Ring pointer and doorbell state are live. Reads can race command submission, preemption, reset, or hardware writeback, so diagnostics must tolerate transient and partially updated values.
- Reserved fields appear throughout. Full-register writes that do not preserve reserved bits may alter undocumented behavior.
- The header does not express field access type. Some bits that look writable by name may be read-only status, self-clearing commands, write-one-to-clear status, sticky overflow flags, or firmware-owned values.
- Power, clock, and queue reset controls are sequencing-sensitive. Incorrect ordering around `SDMA2_POWER_CNTL`, `SDMA2_CLK_CTRL`, `SDMA2_FREEZE`, or `SDMA2_QUEUE_RESET_REQ` can leave rings hung or status bits inconsistent.

## Test Signals

Useful validation is mostly build, generated-data consistency, and hardware integration:

- Kernel build coverage for all GC 10.3.0 AMDGPU/KFD/SMU files that include `gc_10_3_0_sh_mask.h`.
- Static comparison against AMD's authoritative GC 10.3.0 register database to confirm every shift, mask, register family, and generated omission in this range.
- Mechanical checks that each field mask aligns with its shift, that each field in this chunk has a matching register address in `gc_10_3_0_offset.h`, and that available defaults in `gc_10_3_0_default.h` match the same register names.
- Consistency checks across SDMA2 and SDMA3 hypervisor summary families, allowing only documented engine-specific differences.
- SDMA queue tests on GC 10.3 hardware that exercise GFX and PAGE rings: ring enable/disable, doorbell updates, pointer writeback, IB submission, AQL packet mode, preemption, mid-command restore, and reset recovery.
- GPUVM and GFXHUB tests that trigger translation, invalidation, XNACK, page-fault, and translation-assist paths, then verify the decoded status fields are plausible.
- SR-IOV validation with multiple VFs to confirm framebuffer aperture, MARC, VF enable/reset, active function ID, and GPU IOV enable behavior.
- Suspend/resume, runtime power management, and GPU reset tests to confirm SDMA power/clock/ring configuration is restored and live status registers return to expected values.
- Runtime warning signals include SDMA ring timeouts, failed WPTR updates, unexpected doorbell captured/log data, persistent UTCL1 page fault/XNACK status, bad active queue IDs, EDC error counter growth, PSP firewall first-violation reports, VMID/client fault status, and guest VF access failures.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002491`. It covers lines 37448-39877 of `gc_10_3_0_sh_mask.h`. The final per-file research should merge it with neighboring chunks for complete SDMA1 public masks before line 37448 and the continuation of `SDMA2_PAGE_RB_WPTR_POLL_CNTL` plus the remaining SDMA2/PAGE/RLC and later GC register families after line 39877.
