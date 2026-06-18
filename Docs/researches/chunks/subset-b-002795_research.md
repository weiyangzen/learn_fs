# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h

Chunk: `subset-b-002795`
Covered source range: lines 7197-9714 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h`

## Purpose

This chunk is a generated AMDGPU MMHUB 2.3.0 shift/mask header section. It contains no executable code; it defines C preprocessor constants that describe bit positions and bit masks for fields in MMHUB memory-management registers.

The covered range is the central MMVM/MMUTCL2 portion of the header. It supplies field metadata for:

- L2 protection-fault control, status, fault address, and default fault address registers;
- context identity aperture and physical-offset registers;
- L2 cache control extensions, cache fragment sizing, real-time class assignment, reserved client-ID bank selection, parity/logging, clock-gating, GCR, and PTE cache dump controls;
- VM context control registers for contexts 0-15;
- per-PF/VF and per-context PTE cache fragment-size registers;
- MMVM L2 and MMUTCL2 performance counter configuration/result registers;
- shared virtualization, SR-IOV VF framebuffer size/offset, IOMMU, MARC relocation/window, ATS, PF aperture, cacheable DRAM, local HBM, harvest-bypass, and active-function registers;
- VM page-table base/start/end registers for contexts 0-15;
- invalidation engine semaphore/request/ack/address-range/register-reserve definitions for engines 0 through the beginning of engine 6.

The source range contains 2,518 lines and 2,102 `#define` lines. The range begins after the first `MMVM_L2_PROTECTION_FAULT_CNTL` comment but includes its mask fields, and it ends in the middle of the `MMVM_INVALIDATE_ENG6_REQ` field set. Earlier and later chunks are needed for a complete file-level view.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or exported symbols in this header chunk. The API surface is macro constants used by AMDGPU register helpers.

The naming convention is consistent:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address macros live in the paired `mmhub_2_3_0_offset.h` header, and reset defaults live in `mmhub_2_3_0_default.h`.

Important macro families in this range include:

- `MMVM_L2_PROTECTION_FAULT_CNTL`, `MMVM_L2_PROTECTION_FAULT_CNTL2`, `MMVM_L2_PROTECTION_FAULT_MM_CNTL3`, `MMVM_L2_PROTECTION_FAULT_MM_CNTL4`, `MMVM_L2_PROTECTION_FAULT_STATUS`, and fault-address/default-address registers. These describe which faults redirect to the default page, which client IDs raise interrupts, retry/no-retry handling, active page migration retry behavior, and status decoding fields such as `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, `MAPPING_ERROR`, `CID`, `RW`, `ATOMIC`, `VMID`, `VF`, and `VFID`.
- `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, which bound and offset identity-mapped context-1 access.
- `MMVM_L2_CNTL4`, `MMVM_L2_CNTL5`, `MMVM_L2_GCR_CNTL`, `MMVM_L2_CGTT_CLK_CTRL`, and `MMVM_L2_CGTT_BUSY_CTRL`, covering cache partitioning, physical request taps, multimedia IFIFO transaction limits, small/large page fragment size, global cache request bits, and L2 clock-gating controls.
- `MMVM_L2_MM_GROUP_RT_CLASSES`, a 32-bit per-group real-time class bitmap.
- `MMVM_L2_BANK_SELECT_RESERVED_CID` and `MMVM_L2_BANK_SELECT_RESERVED_CID2`, which encode reserved read/write client IDs, enable bits, invalidation mode, private invalidation, and fragment size.
- `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`, each with context enable, page-table depth, page-table block size, retry behavior, fault interrupt enables, and default fault behavior for range, dummy-page, PDE0, valid, read, write, execute, and secure faults.
- `MMVM_CONTEXTS_DISABLE`, which provides disable bits for contexts 0-15.
- `MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `MMVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`, which configure small-page fragment size, large-page fragment size, and bank select at PF/VF and context granularity.
- `MMMC_VM_L2_PERFCOUNTER*_CFG`, `MMUTCL2_PERFCOUNTER*_CFG`, result-control registers, and low/high result registers. These provide `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`, trigger, clear-all, stop-on-saturate, counter, and compare-value fields.
- `MMMC_VM_FB_SIZE_OFFSET_VF0` through `MMMC_VM_FB_SIZE_OFFSET_VF31`, where each VF register exposes `VF_FB_SIZE` and `VF_FB_OFFSET`.
- Shared virtualization/aperture registers such as `MMVM_IOMMU_MMIO_CNTRL_1`, `MMVM_IOMMU_CONTROL_REGISTER`, `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, `MMVM_PCIE_ATS_CNTL`, `MMVM_PCIE_ATS_CNTL_VF_*`, `MMMC_VM_NB_*`, `MMMC_VM_FB_OFFSET`, `MMMC_VM_SYSTEM_APERTURE_*`, `MMMC_VM_CACHEABLE_DRAM_ADDRESS_*`, `MMMC_VM_LOCAL_HBM_ADDRESS_*`, `MMMC_VM_FB_LOCATION_*`, `MMMC_VM_AGP_*`, and `MMMC_VM_MX_L1_TLB_CNTL`.
- `MMVM_CONTEXT0_PAGE_TABLE_*` through `MMVM_CONTEXT15_PAGE_TABLE_*`, which define base address, logical start/end page number, and reserve register fields for every VM context.
- `MMVM_INVALIDATE_ENG0_*` through `MMVM_INVALIDATE_ENG6_REQ`, covering invalidation engine semaphores, VMID request bitmaps, flush type, L2 PTE/PDE and L1 PTE invalidation bits, protection-fault status-address clearing, request logging, 4K-only invalidation, ack state, and address-range bounds.

The chunk boundary cuts off `MMVM_INVALIDATE_ENG6_REQ` after `FLUSH_TYPE_MASK`; the remaining ENG6 request masks and following ENG6 ack/range/reserve fields are outside this work item.

## Control Flow

The chunk has no local runtime control flow. It is compile-time data consumed by register access macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

The concrete runtime path in this source tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`, which includes:

- `mmhub/mmhub_2_3_0_offset.h`
- `mmhub/mmhub_2_3_0_sh_mask.h`
- `mmhub/mmhub_2_3_0_default.h`

`gmc_v10_0_set_mmhub_funcs()` selects `mmhub_v2_3_funcs` for MMHUB IP versions 2.3.0, 2.4.0, and 2.4.1. Once selected, `mmhub_v2_3_gart_enable()` programs the MMHUB in a fixed sequence:

1. Program GART page-table base/start/end registers for context 0.
2. Program system aperture, AGP aperture, default system page, and protection-fault default page registers.
3. Enable and configure the L1 TLB and L2 cache.
4. Enable the system-domain VM context.
5. Disable the context-1 identity aperture by writing an inverted low/high address range and zero physical offset.
6. Configure VMID contexts 1-15 with context-enable, page-table depth/block size, default protection-fault behavior, retry/no-retry behavior, and full page-table address ranges.
7. Program invalidation engine address ranges.

The important control pattern is read-modify-write:

- read a hardware register through `RREG32_SOC15()` or `RREG32_SOC15_OFFSET()`;
- insert fields with `REG_SET_FIELD()` using this header's mask/shift macros;
- write the result with `WREG32_SOC15()` or `WREG32_SOC15_OFFSET()`.

Fault reporting uses the inverse pattern: `mmhub_v2_3_print_l2_protection_fault_status()` decodes `MMVM_L2_PROTECTION_FAULT_STATUS` with `REG_GET_FIELD()` to identify the client ID, read/write bit, walker error, permission-fault class, mapping error, and multiple-fault state.

TLB/cache invalidation uses `mmhub_v2_3_get_invalidate_req()`, which builds a request value from `MMVM_INVALIDATE_ENG0_REQ` fields: VMID bitmap, flush type, L2 PTE invalidation, PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, and fault-status-address clearing.

## State And Persistence Behavior

The header has no mutable software state. Its constants are compiled into AMDGPU code and used to manipulate persistent hardware register state.

The state represented by this chunk is MMHUB memory-translation state:

- GART and per-VMID page-table base/start/end state persists in MMHUB context registers until overwritten, disabled, reset, or reinitialized during suspend/resume or GPU reset.
- Context control state determines whether a VMID is enabled, how many page-table levels are walked, how faults are classified, and whether faults retry, interrupt, redirect to a dummy/default page, or can become crash-triggering no-retry/retry faults.
- Protection-fault status and address registers retain fault evidence until cleared by driver action or hardware reset. The `CLEAR_PROTECTION_FAULT_STATUS_ADDR` fields are the explicit clearing hooks.
- Default fault address registers point faults to `adev->dummy_page_addr` when default handling is enabled.
- Invalidation engine semaphore/request/ack registers are transient synchronization state, but incorrect values can leave stale translations in L1/L2 TLB/cache state.
- SR-IOV VF framebuffer size/offset and ATS/IOMMU/shared virtualization registers participate in partitioning and address-translation state that must match PF/VF ownership and firmware policy.
- Perf-counter configuration and result registers hold diagnostic state until cleared, reset, or reprogrammed.

The default values referenced by `mmhub_v2_3.c` come from `mmhub_2_3_0_default.h`; this chunk provides the field layout used when those defaults are modified. Reset or power-management transitions can restore hardware defaults, so AMDGPU reprograms these registers during GART enable and clock-gating flows.

## Dependencies And Integration Points

Direct dependencies in the MMHUB 2.3.0 register family are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_offset.h`, which provides register offsets such as `mmMMVM_L2_PROTECTION_FAULT_CNTL`, `mmMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, and `mmMMVM_INVALIDATE_ENG0_REQ`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_default.h`, which provides reset/default values such as `mmMMVM_L2_CNTL4_DEFAULT`, `mmMMVM_L2_CNTL5_DEFAULT`, and protection-fault/invalidation defaults.
- AMDGPU register helper macros and SOC15 accessors, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

Primary source-tree consumers and integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`: includes this header and programs protection faults, context controls, page-table registers, cache/TLB controls, identity aperture, invalidation, clock gating, and fault-status reporting.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.h`: exposes `mmhub_v2_3_funcs`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`: chooses `mmhub_v2_3_funcs` for MMHUB IP 2.3.0/2.4.x and integrates MMHUB with the GMC v10 memory-management path.
- `amdgpu_vmhub` state: `mmhub_v2_3_init()` stores MMHUB register offsets, context distance, context-address distance, invalidation-engine distance, fault-status/control offsets, `vm_cntx_cntl_vm_fault` interrupt masks, and the VM hub callback table.
- `amdgpu_mmhub_client_name()` and `amdgpu_mmhub_init_client_info()`: fault-status `CID`/`RW` decoding is tied to the Vangogh MMHUB client-ID table in `mmhub_v2_3.c`.

This generated header must stay synchronized with the matching offset/default headers and the ASIC register database. Same-named fields exist in other MMHUB generations, but field presence and offsets can differ; for example later MMHUB 4.2 invalidation request fields add `INVALIDATE_L2_PDE3`, while this MMHUB 2.3.0 chunk only defines PDE0-PDE2 in the visible request fields.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. The compiler cannot verify that a mask belongs to the register being accessed, that a shift matches the mask, or that a field exists for this ASIC generation.

Fault handling fields are safety-critical. Incorrect `MMVM_L2_PROTECTION_FAULT_CNTL` or `MMVM_CONTEXT*_CNTL` values can turn recoverable faults into crashes, suppress needed interrupts, create VM fault storms, retry when the driver expects no-retry behavior, or redirect bad accesses to an unintended physical/default page.

Page-table address fields split 64-bit physical/logical page numbers into low and high registers. Wrong masks, shifts, high-bit widths, or context-address distances can point a VMID at the wrong page directory or make a valid address range appear truncated.

Context register families are repetitive. The header defines the same field shape for contexts 0-15, and driver code relies on distances between context 0 and context 1 registers. A regenerated offset/header mismatch can make looped `WREG32_SOC15_OFFSET()` programming hit the wrong VMID.

Invalidation engine fields are translation-coherency critical. Missing `INVALIDATE_L2_PTES`, PDE invalidation, L1 invalidation, or wrong VMID bitmap can leave stale translations active after page-table changes. Incorrect address-range low/high fields can also over-invalidate or under-invalidate.

The assigned chunk ends in the middle of `MMVM_INVALIDATE_ENG6_REQ`. Any analysis of ENG6 is partial here. The final file-level report should merge with the following chunk before claiming full invalidation-engine coverage.

SR-IOV and virtualization fields can affect PF/VF isolation. VF framebuffer offset/size, active function ID, shared reset request, ATS per-VF controls, IOMMU controls, and MARC relocation/window fields should not be changed casually because wrong programming can expose or deny memory ranges across functions.

Clock-gating and cache control fields affect power and liveness. Bad values in `MMVM_L2_CGTT_CLK_CTRL`, `MMUTCL2_CGTT_CLK_CTRL`, cache fragment-size, bank-select, or GCR fields can cause performance regressions, hangs, or incorrect cache/TLB behavior that only appears under load.

Generated constants use `L`-suffixed hexadecimal values intended for 32-bit registers. Callers should keep using the driver's unsigned register types and helper macros to avoid signed arithmetic or shift-width surprises.

## Test Signals

Useful validation is a mix of build coverage, static generated-header checks, and hardware behavior tests:

- Build AMDGPU with GMC v10/MMHUB v2.3 support enabled. Missing or renamed macros should fail in `mmhub_v2_3.c`, `gmc_v10_0.c`, and related VM/GMC paths.
- Static consistency checks that every complete `_MASK` has a matching `__SHIFT`, no duplicate macro names have conflicting values, and field prefixes match registers in `mmhub_2_3_0_offset.h`. This chunk intentionally has an incomplete `MMVM_INVALIDATE_ENG6_REQ` field set because of the line-range boundary.
- Boot an MMHUB 2.3.0/2.4.x ASIC path and verify GART enable succeeds without VM setup errors, GPU reset loops, or early page-fault storms.
- Exercise VM fault handling: trigger controlled invalid, read/write, range, dummy-page, and PDE/valid faults; verify `MMVM_L2_PROTECTION_FAULT_STATUS` decoding logs expected `CID`, `RW`, permission/mapping state, VMID, and VF/VFID bits.
- Toggle `set_fault_enable_default()` behavior and verify faults redirect to the dummy/default page when expected and crash/no-retry bits are set only in the intended mode.
- Run GPUVM workloads that allocate, update, and invalidate page tables across multiple VMIDs; verify TLB flushes complete and no stale translations remain after page migration or unmap.
- Cover SR-IOV VF paths where `mmhub_v2_3_gart_enable()` programs `MMMC_VM_FB_LOCATION_BASE/TOP`, and validate VF framebuffer sizing/offset isolation against PF policy.
- Check suspend/resume and GPU reset recovery: page-table bases, system aperture, default fault address, context controls, invalidation ranges, and cache/TLB controls should be reinitialized correctly.
- Use performance counter smoke tests for `MMMC_VM_L2_PERFCOUNTER*` and `MMUTCL2_PERFCOUNTER*`: configure, clear, enable, read low/high results, and confirm counters change under MMHUB traffic.
- Verify medium-grain clock-gating/light-sleep behavior around MMHUB accesses, especially when cache/TLB invalidation and VM faults happen under clock-gated states.
