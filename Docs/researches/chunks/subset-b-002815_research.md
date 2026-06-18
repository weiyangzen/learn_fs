# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_sh_mask.h lines 4743-6722

## Scope

This chunk is the final generated shift/mask section of the AMDGPU MMHUB 3.3.0 register mask header. It contains only C preprocessor constants plus generated register/address-block comments. There are no functions, structs, enums, variables, allocations, locks, branches, loops, or direct MMIO accesses in this range.

The range starts in the tail of `MMVM_CONTEXT7_CNTL`, covers complete `MMVM_CONTEXT8_CNTL` through `MMVM_CONTEXT15_CNTL`, and then covers VM context disable bits, 18 invalidation-engine semaphore/request/ack/address-range families, page-table base/start/end address fields for contexts 0-15, per-PF/VF PTE cache fragment-size fields, VM L2/MMUTCL2/ATC/MML2TLB performance-counter fields, shared VM aperture/system-memory controls, IOMMU and translation-fault fallback controls, GPUVA/VMID translation-assist request/response fields, TLB status/TMZ controls, and the closing `#endif`.

Although the repository path is under a `ceph-client` source mirror, this file is AMD GPU MMHUB hardware register metadata, not distributed filesystem logic.

## Purpose

The purpose of this chunk is to publish bit-level field metadata for MMHUB 3.3.0 VM and MMUTCL2 registers. Each register field uses the AMD generated-header convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit mask for extracting or composing the field.

The sibling `mmhub_3_3_0_offset.h` header provides register addresses such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, `regMMVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32`, and `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID`. This mask header provides the field packing used by AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and offset variants.

## Important Macro Families

### VM context control and context disable

The opening lines are a partial continuation of `MMVM_CONTEXT7_CNTL`, containing only the later protection-fault mask definitions. The complete definitions for context 7 start in the previous chunk.

`MMVM_CONTEXT8_CNTL` through `MMVM_CONTEXT15_CNTL` repeat the VM context-control layout: `ENABLE_CONTEXT`, page-table depth and block size, retry behavior for permission/invalid-page and other faults, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `MMVM_CONTEXTS_DISABLE` provides one disable bit for each VM context 0-15.

These fields are core VM setup ABI. In `amdgpu/mmhub_v3_3.c`, the driver programs context control with `REG_SET_FIELD(..., MMVM_CONTEXT0_CNTL, ...)` and `REG_SET_FIELD(..., MMVM_CONTEXT1_CNTL, ...)`, then derives the shared VM-fault enable mask from `MMVM_CONTEXT1_CNTL__*_PROTECTION_FAULT_ENABLE_INTERRUPT_MASK`.

### TLB invalidation engines

`MMVM_INVALIDATE_ENG0_SEM` through `MMVM_INVALIDATE_ENG17_SEM` define the single-bit semaphore field for each invalidation engine.

`MMVM_INVALIDATE_ENG0_REQ` through `MMVM_INVALIDATE_ENG17_REQ` define the invalidation request payload: a 16-bit per-VMID invalidate bitmap, flush type, L2 PTE/PDE0/PDE1/PDE2 invalidation bits, L1 PTE invalidation, protection-fault status-address clearing, and 4K-page-only invalidation. `MMVM_INVALIDATE_ENG0_ACK` through `MMVM_INVALIDATE_ENG17_ACK` expose the matching per-VMID ack bitmap and semaphore ack bit.

`MMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17 define optional address-range fields for range-limited invalidation. Low registers contain `S_BIT` and low logical-page-address bits; high registers contain the high logical-page-address field.

`mmhub_v3_3.c` uses the engine-0 names as the base template, then computes `eng_distance` and `eng_addr_distance` from adjacent offset-header registers so one implementation can address multiple engines. That makes the uniform mask layout in this chunk part of the runtime invalidation contract.

### VM context page-table address ranges

For contexts 0-15, the chunk defines:

- `MMVM_CONTEXT*_PAGE_TABLE_BASE_ADDR_LO32/HI32`: page-directory entry low and high halves.
- `MMVM_CONTEXT*_PAGE_TABLE_START_ADDR_LO32/HI32`: logical page-number start low and high fields.
- `MMVM_CONTEXT*_PAGE_TABLE_END_ADDR_LO32/HI32`: logical page-number end low and high fields.

The base-address fields are full 32-bit halves. Start/end low halves are full 32-bit logical page numbers, while high halves use the low 4 bits. These fields back the GPU VM page-table root and valid virtual-address aperture programmed by MMHUB initialization and resume code.

### PTE fragment-size controls

`MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` defines four-bit fragment-size fields for VMIDs 1-7 and 13-15. `MMVM_L2_CONTEXT0_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` through `CONTEXT15` provide per-context fragment-size variants with `FRAGMENT_SIZE` and `SYSTEM_ACCESS_MODE` fields. These influence how the VM L2 caches page-table fragments and how system access mode is represented for a context.

### VM L2, MMUTCL2, ATC, and MML2TLB performance counters

The `mmhub_mmutcl2_mmvml2pldec` and `mmhub_mmutcl2_mml2tlbpldec` blocks define performance-counter configuration registers:

- `MMMC_VM_L2_PERFCOUNTER0_CFG` through `7_CFG`.
- `MMUTCL2_PERFCOUNTER0_CFG` through `3_CFG`.
- `MM_ATC_L2_PERFCOUNTER0_CFG` and `1_CFG`.
- `MML2TLB_PERFCOUNTER0_CFG` through `3_CFG`.

Each config family follows the same pattern: event selection start/end fields, performance mode, enable bit, and clear bit. The corresponding result-control registers select a counter, specify start/stop triggers, enable any counter, clear all counters, and stop all counters on saturation. Result registers expose low 32 counter bits and high/compare-value fields.

These fields are debug/performance instrumentation ABI. They do not count anything by themselves; runtime code must program event selectors, clear/enable counters, trigger collection, and read result registers.

### Shared VM aperture, system-memory, and clock/power fields

The `mmhub_mmutcl2_mmvmsharedpfdec` and `mmhub_mmutcl2_mmvmsharedvcdec` blocks define shared VM configuration fields, including NB MMIO base/limit, PCI control/arbitration, top-of-DRAM slot fields, FB offset, system-aperture default address halves, VM steering, shared virtualization reset request, memory power light-sleep controls, cacheable DRAM and local system-memory address start/end fields, aperture control, local FB address start/end and lock, FB location base/top, AGP top/bottom/base, and system aperture low/high addresses.

`MMUTCL2_CGTT_CLK_CTRL` and `MMUTCL2_CGTT_BUSY_CTRL` define clock-gating and busy-status behavior for MMUTCL2. `MMMC_SHARED_ACTIVE_FCN_ID`, `MMMC_VM_FB_NOALLOC_CNTL`, `MMUTCL2_HARVEST_BYPASS_GROUPS`, and `MMUTCL2_GROUP_RET_FAULT_STATUS` expose active function, LLC/no-allocate behavior, harvest bypass, and group return-fault status.

`MMVM_PCIE_ATS_CNTL` controls PCIe ATS behavior with `ATC_ATS_BLOCK_CLIENTID` and `ATC_ATS_BLOCK_CLIENTID_EN`, while `MMMC_VM_MX_L1_TLB_CNTL` controls L1 TLB enable, system access, invalidation, fragment processing, and local work-item/group behavior.

### IOMMU, translation fallback, and GPUVA/VMID translation assist

`MMUTCL2_TRANSLATION_BYPASS_BY_VMID` defines per-VMID translation-bypass and GPA-mode bitmaps. `MMVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, `MMVM_IOMMU_CONTROL_REGISTER`, and `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` expose GPU-host translation, IOMMU enable, and performance optimization enable bits.

`MMUTC_TRANSLATION_FAULT_CNTL0/1` define the default physical page address and attributes used for translation faults: low address bits, high address bits, IO, SPA, and snoop flags. `MMUTCL2_VSCH_POWER_STATUS` exposes a powered-down status bit.

`MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` enables the translation-assist path. Request registers carry address bits, VMID, VFID, VF flag, GPA mode, read/write/execute permission request bits, client ID, and request bit. Response registers return translated address bits, permission bits, fragment size, snoop/SPA/IO/TMZ attributes, no-PTE indication, memory type, memlog, NACK status, LLC no-allocate, and ACK.

### TLB status, TMZ, and credit safety

`MML2TLB_TLB0_STATUS` exposes busy, parity-error, and aperture-fault status bits. `MML2TLB_TMZ_CNTL` defines TMZ modulation. `MMUTCL2_L2TLB_CREDIT_SAFETY_FETCH_RDREQ` exposes a credit value and write bit for L2 TLB fetch read-request credit safety.

## APIs, Types, and Functions

This chunk exports preprocessor macros only. There are no C APIs, normal types, or callable functions.

The effective API is the generated naming contract used by AMDGPU register helpers:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg__field__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg__field_MASK`.
- `REG_SET_FIELD(orig, reg, field, value)` clears the field mask in `orig`, shifts `value` by the field shift, masks it, and ORs it into the result.
- `REG_GET_FIELD(value, reg, field)` masks and right-shifts a register value.

Because those helpers token-paste macro names, spelling is ABI-significant. A missing shift, missing mask, renamed register token, or renamed field token becomes a compile-time break in consumers.

## Control Flow

There is no executable control flow in the header. Runtime sequencing is supplied by AMDGPU MMHUB code that includes this file with `mmhub_3_3_0_offset.h`.

The hardware-level flow implied by the macros is:

1. Program VM context control and page-table base/start/end address registers for context 0 and user VM contexts.
2. Program shared apertures, FB/AGP/system-memory ranges, L1/L2 TLB controls, ATS/IOMMU controls, and fallback fault addresses as required by the ASIC initialization path.
3. Issue TLB invalidations through an invalidation engine by setting address-range registers when needed, composing an `MMVM_INVALIDATE_ENG*_REQ` value, and polling or checking `MMVM_INVALIDATE_ENG*_ACK`.
4. Use performance-counter config/result fields only in debug or profiling paths.
5. Read status/fault/power fields and clear or reprogram related state according to hardware sequencing rules outside this header.

## State and Persistence Behavior

The macros themselves hold no state. They describe MMIO-backed hardware state in MMHUB 3.3.0.

Persistent or semi-persistent hardware configuration represented here includes VM context enable/depth/block/fault policy, context-disable bits, page-table roots and virtual address ranges, PTE cache fragment sizes, system/local/FB/AGP aperture ranges, L1 TLB controls, ATS/IOMMU controls, translation-bypass bitmaps, translation-fault default page attributes, clock-gating controls, and credit-safety settings. These values generally persist until driver reprogramming, reset, suspend/resume restore, power-gating loss, firmware action, or ASIC reset.

Transient or side-effecting state includes invalidation request/ack/semaphore fields, clear bits, performance-counter clear/enable/result controls, busy/status bits, power-status bits, return-fault status, and translation-assist request/response handshake fields. The mask definitions do not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, or sequencing-sensitive; consumers must follow the hardware specification and existing MMHUB code.

## Dependencies and Integration Points

This chunk is paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_offset.h`, which supplies matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_default.h`, where default/reset values are represented for this generation.
- AMDGPU SOC15 register helpers and field helpers from the surrounding driver tree.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c`, which includes this mask header and its offset/default siblings. That source uses the VM context, invalidation-engine, address-range, and fault-enable macros in MMHUB setup, GART setup, VM invalidation, and VM hub descriptor initialization. Similar MMHUB generations, such as 4.1.0 and 4.2.0, use analogous macro families, but field presence and bit positions must remain matched to the active ASIC generation.

## Risks and Edge Cases

- Bitfield drift is high impact. Incorrect shifts or masks can silently program wrong VM context, invalidation, aperture, ATS/IOMMU, or TLB fields, causing GPU VM faults, stale translations, hangs, or memory corruption.
- The chunk begins mid-register. `MMVM_CONTEXT7_CNTL` is incomplete here; the previous chunk owns the shifts and earlier masks. Whole-file research must merge adjacent chunks before treating context 7 as fully described.
- Invalidation engine families are repeated 18 times with identical field layouts. A one-engine typo can break only specific invalidation paths or rings, making failures workload-dependent.
- Request/ack semantics are sequencing-sensitive. Incorrect `PER_VMID_INVALIDATE_REQ`, flush type, L1/L2/PDE invalidation bits, range fields, or ack polling can leave stale TLB entries or spin waiting for an ack that never matches.
- VM page-table address fields are safety-critical. Wrong page-directory base or start/end aperture values can route GPU virtual addresses to the wrong physical pages or expose invalid ranges.
- Shared aperture and FB/AGP/system ranges are platform-sensitive. Bad values can misclassify local memory, system memory, cacheable DRAM, MMIO, or AGP apertures.
- Translation bypass, GPA mode, GPU-host translation, and IOMMU enable fields affect virtualization and passthrough behavior. Incorrect per-VMID bitmaps can bypass translation for the wrong context or force the wrong address mode.
- Performance-counter fields include clear and enable bits. Debug code must avoid leaving counters enabled unintentionally or clearing state that another diagnostic path expects.
- Translation-assist request/response fields implement a handshake. Consumers must treat `REQ`, `ACK`, `NACK`, permission, no-PTE, and attribute bits as protocol state, not as ordinary passive configuration.

## Test Signals

Useful validation signals are build-time, generated-header consistency, and hardware VM behavior:

- Build AMDGPU with MMHUB 3.3 support enabled. Direct consumers in `mmhub_v3_3.c` should compile, especially token-pasted uses of `MMVM_CONTEXT*_CNTL` and `MMVM_INVALIDATE_ENG*_REQ`.
- Mechanical header checks should verify every complete field in this chunk has both `__SHIFT` and `_MASK`, masks align with shifts and widths, and fields inside one register do not overlap unexpectedly.
- Offset/mask consistency checks should pair registers in this chunk with matching names in `mmhub_3_3_0_offset.h`.
- GPU boot, suspend/resume, and reset tests should cover MMHUB VM context programming, GART setup, aperture setup, and restoration of context/page-table registers.
- VM stress workloads should exercise many VMIDs, page-table updates, evictions, and invalidations; stale translations, VM faults, or hangs are strong signals of bad invalidation or context-field definitions.
- Range-limited invalidation tests should verify `MMVM_INVALIDATE_ENG*_ADDR_RANGE_LO32/HI32` packing and `INVALIDATE_4K_PAGES_ONLY` behavior where hardware supports it.
- Virtualization and IOMMU tests should cover translation-bypass-by-VMID, GPA mode, GPU-host translation, and translation-assist request/response behavior.
- Performance-counter smoke tests should program VM L2, MMUTCL2, ATC L2, and MML2TLB counters, clear/enable them, trigger collection, read low/high results, and verify stop-on-saturate behavior where available.

## Cross-Chunk Notes

The previous chunk contains the beginning of `MMVM_CONTEXT7_CNTL`. This chunk reaches the end of `mmhub_3_3_0_sh_mask.h` and closes the include guard, so there is no following chunk for this source file. The final per-file report should reconcile context-control coverage across chunks 2 and 3 and avoid treating the partial context-7 masks at this chunk boundary as a complete register definition.
