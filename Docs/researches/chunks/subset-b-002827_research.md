# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 7156-9627

## Scope And Purpose

This chunk is a generated-style AMDGPU MMHUB 9.1 shift/mask header section. It exposes compile-time bitfield constants for MMHUB VM L2, ATC L2, virtual-memory context, invalidation, performance-counter, SR-IOV shared aperture, MARC, IOMMU, PCIe ATS, and UTCL2 clock-gating registers. The symbols follow the hardware-register convention `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; there are no C functions, structs, enums, variables, or executable branches in this range.

The range starts in the `VM_L2_SAW_*` block and then covers address blocks named by comments: `mmhub_utcl2_atcl2dec`, `mmhub_utcl2_vml2pfdec`, `mmhub_utcl2_vml2vcdec`, `mmhub_utcl2_vml2pldec`, `mmhub_utcl2_vml2prdec`, and `mmhub_utcl2_vmsharedhvdec`. The corresponding address constants live in `mmhub_9_1_offset.h`; this file supplies only bit positions and masks for packing and unpacking 32-bit MMIO register values.

The main purpose is to make driver register access type-safe at the preprocessor level. AMDGPU code can write `REG_SET_FIELD(tmp, VM_L2_CNTL, ENABLE_L2_CACHE, 1)` or extract fault fields with `REG_GET_FIELD(status, VM_L2_PROTECTION_FAULT_STATUS, CID)` because this header defines the exact mask and shift pairs.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The exported interface is the macro set consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, and register-list helpers.

Important register groups in this chunk include:

- `VM_L2_SAW_CNTL3`, `VM_L2_SAW_CNTL4`, `VM_L2_SAW_CONTEXT0_CNTL`, `VM_L2_SAW_CONTEXT0_CNTL2`, `VM_L2_SAW_CONTEXT0_PAGE_TABLE_*`, `VM_L2_SAW_CONTEXTS_DISABLE`, and `VM_L2_SAW_PIPES_BUSY`: SAW-side VM L2 cache configuration, context-0 page-table range programming, fault default/interrupt/save controls, context-disable bitmap, and pipe-busy status.
- `ATC_L2_CNTL`, `ATC_L2_CNTL2`, `ATC_L2_CACHE_DATA0/1/2`, `ATC_L2_CNTL3`, `ATC_L2_STATUS`, `ATC_L2_STATUS2`, `ATC_L2_MISC_CG`, `ATC_L2_MEM_POWER_LS`, and `ATC_L2_CGTT_CLK_CTRL`: ATC L2 translation request sizing, cache update mode, data window access, invalidation state, busy/state-change status, memory light-sleep, and clock-gating controls.
- `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, `VM_L2_CNTL4`, `VM_L2_STATUS`, and `VM_DUMMY_PAGE_FAULT_*`: MMHUB VM L2 cache enablement, fragment/cache modes, invalidation control, identity/tap behavior, busy status, and dummy-page fault address controls.
- `VM_L2_PROTECTION_FAULT_CNTL`, `VM_L2_PROTECTION_FAULT_CNTL2`, `VM_L2_PROTECTION_FAULT_MM_CNTL3/4`, `VM_L2_PROTECTION_FAULT_STATUS`, `VM_L2_PROTECTION_FAULT_ADDR_*`, and `VM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*`: fault routing, default-page behavior, crash-on-fault policy, per-client interrupt masks, retry/PRT controls, captured fault metadata, faulting logical page address, and default physical page address.
- `VM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `VM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: identity aperture bounds and physical offset used when context identity access is enabled or disabled.
- `VM_CONTEXT0_CNTL` through `VM_CONTEXT15_CNTL`: per-VMID context controls for enablement, page-table depth and block size, retry behavior, and interrupt/default handling for range, dummy, PDE0, valid, read, write, and execute protection faults.
- `VM_CONTEXTS_DISABLE`: a 16-bit bitmap that disables contexts 0 through 15.
- `VM_INVALIDATE_ENG0_SEM` through `VM_INVALIDATE_ENG17_SEM`, `VM_INVALIDATE_ENG0_REQ` through `VM_INVALIDATE_ENG17_REQ`, `VM_INVALIDATE_ENG0_ACK` through `VM_INVALIDATE_ENG17_ACK`, and `VM_INVALIDATE_ENG*_ADDR_RANGE_*`: eighteen invalidation engines with semaphore, request, acknowledge, and optional address-range fields. Request fields include per-VMID invalidation, flush type, invalidate-L2 PTE/PDE bits, invalidate-L1-PTEs, clear-protection-fault-status, and interrupt/ack controls.
- `VM_CONTEXT*_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXT*_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXT*_PAGE_TABLE_END_ADDR_*`: per-context page-table base and logical range fields split into low 32-bit and high 4-bit page-number fragments.
- `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MC_VM_L2_PERFCOUNTER_LO`, and `MC_VM_L2_PERFCOUNTER_HI`: eight VM L2 performance-counter config registers plus result control and low/high result/compare fields.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`: SR-IOV virtual-function framebuffer size and offset fields, with 16-bit size in the low half and 16-bit offset in the high half.
- `VM_IOMMU_MMIO_CNTRL_1`, `VM_IOMMU_CONTROL_REGISTER`, and `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`: MARC enable, IOMMU enable, and IOMMU performance optimization enable bits.
- `MC_VM_MARC_BASE_*`, `MC_VM_MARC_RELOC_*`, and `MC_VM_MARC_LEN_*`: four MARC aperture base, relocation, length, enable, and read-only register sets, using 4 KB-aligned low fragments and high fragments.
- `VM_PCIE_ATS_CNTL` and `VM_PCIE_ATS_CNTL_VF_0` through `VM_PCIE_ATS_CNTL_VF_15`: PCIe ATS state, including system translation unit (`STU`) for the physical function and `ATC_ENABLE` for PF/VF paths.
- `UTCL2_CGTT_CLK_CTRL`: UTCL2 clock-gating timing, soft override, medium-grain light-sleep override, and stall override fields.

## Control Flow And State Behavior

This header has no runtime control flow. Runtime effects happen only when consumers combine these constants with MMIO access helpers. The usual pattern is read-modify-write: read a 32-bit register with `RREG32_SOC15`, update named fields with `REG_SET_FIELD`, then write back with `WREG32_SOC15` or `WREG32_SOC15_OFFSET`.

The VM L2 and ATC L2 control fields persist as hardware register state. Driver initialization enables or disables L2 cache, fragment processing, L1/L2 invalidation behavior, cache update policies, tap physical/shared/snoop attributes, and clock-gating behavior. These settings remain active until a later register write, GPU reset, power transition, or firmware/hypervisor reprogramming.

Context registers model VMID state. Context-control fields decide whether a VMID is active, how deep its page table is, the block size used by the walker, and how protection faults are handled. Page-table base/start/end registers persist the page-number fragments used by the memory-management hardware to translate GPU virtual addresses.

Invalidation-engine registers implement an asynchronous request/acknowledge flow. Software writes a request register, optionally writes address-range registers, and waits for the matching acknowledge bit/register to show completion. The `*_SEM` fields serialize access to engines, and `PER_VMID_INVALIDATE_REQ` plus invalidate PTE/PDE/L1 bits define the scope of the flush.

Protection-fault status and address registers are hardware-owned diagnostic state. `VM_L2_PROTECTION_FAULT_STATUS` captures flags such as more faults, walker error, permission faults, mapping error, client ID, read/write, atomic, VMID, VF, and VFID. The address registers capture the faulting logical page number. Control bits decide whether later faults can update this state and whether faults are redirected to a default page, generate interrupts, retry, or crash.

Performance-counter fields expose hardware accumulation state. The config registers select events and modes; result-control fields globally enable, clear, trigger, and stop counters; result registers expose low/high counts and compare values. The header does not indicate read-clear behavior or counter access ordering.

The SR-IOV VF framebuffer and ATS fields represent virtualization-facing state. VF size/offset registers define guest-visible FB windows, while PF/VF ATS enable bits control whether address translation caching is allowed for PCIe requests. MARC registers define up to four relocation apertures and their read-only/enabled attributes when MARC is enabled.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_offset.h`, which provides the matching `mm*` register addresses and base indices. This `_sh_mask.h` file is unsafe to use with offsets from another MMHUB generation because cross-generation register names are similar while layouts and base-indexing can differ.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.c`, which includes `mmhub_9_1_offset.h` and `mmhub_9_1_sh_mask.h` alongside VCN 1.0 headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`, which includes this MMHUB 9.1 pair alongside DCN 1.0 and NBIO headers.

The broader MMHUB/GMC integration pattern is visible in adjacent-generation code. `mmhub_v1_0.c` and `mmhub_v1_8.c` program corresponding VM L2 and context fields during GART enablement, system aperture setup, cache initialization, VMID context setup, fault policy changes, invalidation setup, and clock-gating changes. `gmc_v9_0.c` uses same-family `VM_L2_PROTECTION_FAULT_STATUS` and `VM_INVALIDATE_ENG0_REQ` field names to decode VM faults and build invalidation requests.

These macros also integrate with `struct amdgpu_vmhub` setup. MMHUB initialization code records offsets such as context-0 page-table base, invalidation-engine request/ack registers, context control, fault status, and fault control; it also derives register spacing from `VM_CONTEXT1_* - VM_CONTEXT0_*` and `VM_INVALIDATE_ENG1_* - VM_INVALIDATE_ENG0_*`. The repeated context and engine macro groups in this chunk support that regular spacing model.

## Risks And Edge Cases

- This header is a hardware ABI. An incorrect mask or shift can compile cleanly while corrupting MMHUB translation, cache, invalidation, fault, virtualization, or power-management behavior.
- Many fields are address fragments rather than byte addresses. Page-table bases, start/end ranges, fault addresses, dummy/default page addresses, and MARC low registers use page-number or 4 KB-aligned fragments; callers must apply the generation-specific shifts consistently.
- The context and invalidation groups are repetitive. Copy/paste or generation drift can easily leave one VMID or engine with a wrong field definition while neighboring definitions look correct.
- `VM_INVALIDATE_ENG*_REQ` is densely packed with VMID, flush type, invalidate selectors, interrupt, and fault-status clear controls. A bad field boundary can cause partial TLB flushes, missed acknowledgements, or stale protection-fault state.
- Fault handling fields are policy-sensitive. Accidentally changing default-page, interrupt, retry, or crash-on-fault bits can convert recoverable GPUVM faults into hangs, silent data redirection, or excessive interrupt storms.
- Status, acknowledge, busy, and performance-counter fields may be volatile or write-one-to-clear depending on hardware semantics. The generated masks do not encode access type, reset value, side effects, or required ordering.
- `MC_VM_FB_SIZE_OFFSET_VF*`, `VM_PCIE_ATS_CNTL_VF_*`, and MARC fields are virtualization/security-sensitive. Wrong VF size/offset, ATS enablement, MARC enable, or read-only bits can expose the wrong framebuffer aperture or translate through the wrong address path.
- Full-width masks such as `0xFFFFFFFFL` should be handled as 32-bit unsigned hardware values. Signed promotion in diagnostics or helper changes can misrepresent status/counter values.
- Cross-generation headers contain many identical register and field names. Including `mmhub_9_1_sh_mask.h` with non-9.1 offsets, or reusing a newer MMHUB macro against these offsets, can silently program the wrong bit layout.

## Test And Validation Signals

There are no unit tests for this macro-only chunk. Useful validation signals are compile-time, static, and hardware-facing:

- Build AMDGPU configurations that compile the direct consumers `vcn_v1_0.c` and `dcn10_resource.c` with `mmhub_9_1_offset.h` plus `mmhub_9_1_sh_mask.h`.
- Run static mask/shift validation: single-bit masks should equal `1U << shift`; multi-bit masks should be contiguous at their shift; low/high address fragments should have shift zero or documented alignment shifts; repeated VM context, invalidation engine, VF, MARC, and perf-counter groups should have consistent field layouts.
- Compare each comment-delimited register group in this chunk against `mmhub_9_1_offset.h` to ensure a matching address definition exists and belongs to the expected address block.
- On supported MMHUB 9.1 hardware, validate GART and VM setup by checking context page-table base/start/end registers, VM L2 cache controls, fault default address programming, and identity aperture state after driver load and resume.
- Exercise VM invalidation paths and verify that request/ack registers transition as expected for all allocated engines, including per-VMID invalidation and address-range invalidation when enabled.
- Inject or observe GPUVM faults and confirm that decoded `CID`, `RW`, `ATOMIC`, `VMID`, `VF`, `VFID`, permission, walker, mapping, and more-fault fields match the faulting workload and kernel logs.
- In SR-IOV scenarios, inspect VF framebuffer size/offset registers and VF ATS enable bits across PF and VF initialization. Confirm that VFs cannot see outside their assigned aperture.
- For MARC/IOMMU/ATS features, validate enable/disable sequences against firmware policy and platform capabilities, including read-only MARC ranges and PCIe ATS behavior.
- For clock-gating and performance counters, verify that enabling/disabling clock-gating does not break register access and that perf-counter clear/enable/trigger/result fields behave consistently across suspend/resume and reset.

## Chunk Notes For Merge Lane

This chunk covers the lower MMHUB 9.1 VM and translation-control half: SAW VM L2 tail, ATC L2 controls, VM L2 protection fault and context controls, invalidation engines 0-17, per-context page-table registers, VM L2 performance counters, SR-IOV VF framebuffer windows, MARC/IOMMU/ATS controls, and the beginning of `UTCL2_CGTT_CLK_CTRL`. Whole-file reconciliation should merge this with earlier chunks that cover the opening DAGB/system-aperture blocks and later chunks, if any, that complete the trailing clock-gating fields and include guard.
