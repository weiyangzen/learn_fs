# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_sh_mask.h lines 4753-6943

## Scope

This chunk is the final section of the generated MMHUB 4.1.0 shift/mask header. It starts at the tail of the `MMVM_L2_MM_GROUP_RT_CLASSES` field masks and continues through the closing `#endif` for `_mmhub_4_1_0_SH_MASK_HEADER`.

The covered register families span:

- L2 bank/client selection, cache parity, clock-gating, GCR, PTE-cache dump, bank-select masks, and credit-safety controls.
- MMHUB MC/UTCL2 L2 performance counter result and configuration registers.
- Shared memory aperture and L1 TLB controls for framebuffer, AGP, system aperture, and L1 TLB policy.
- VM context control registers for contexts 0 through 15.
- Context disable masks.
- VM invalidation request, acknowledgement, and logical page address range fields for engines 0 through 17.
- Per-context page-table base, page-table start, and page-table end address fields.
- Per-PF/VF PTE-cache fragment-size registers for the global setting and contexts 0 through 15.
- PSP/IOMMU-facing translation bypass, GPU-host translation, GPUVA VMID assist, IOMMU enable, default translation-fault address, and VSCH power-status fields.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only; it has no C functions, structs, enums, runtime variables, or executable branches.

## Purpose

`mmhub_4_1_0_sh_mask.h` supplies the bit-level ABI used by AMDGPU MMHUB 4.1.0 code to compose and decode 32-bit MMIO register values. Each field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the field mask in the register word.

The paired `mmhub_4_1_0_offset.h` header provides register addresses such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, and `regMMMC_VM_FB_LOCATION_BASE`. This header supplies the field layout used by helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

The direct runtime consumer in this source tree is `amdgpu/mmhub_v4_1_0.c`, which includes both the offset and mask headers and uses the fields in MMHUB GART enablement, VMID setup, TLB/cache programming, invalidation request construction, fault handling setup, and framebuffer-base discovery.

## Important Macro Families

### L2 Cache, Bank, Credit, and Diagnostics Controls

The chunk begins with the final `MMVM_L2_MM_GROUP_RT_CLASSES` masks for groups 27 through 31, then defines `MMVM_L2_BANK_SELECT_RESERVED_CID` and `MMVM_L2_BANK_SELECT_RESERVED_CID2`. These reserved-client-ID registers encode read/write client IDs, an enable bit, invalidation mode, private invalidation, and cache fragment-size controls. `mmhub_v4_1_0_init()` records `regMMVM_L2_BANK_SELECT_RESERVED_CID2` in `hub->vm_l2_bank_select_reserved_cid2`, making this register available to common VM/MMHUB code.

`MMVM_L2_CACHE_PARITY_CNTL` exposes parity-check enable bits for 4K PTE, big-page PTE, and PDE caches plus force-parity-mismatch controls. It also selects a target cache bank, cache number, and associativity way for parity injection or diagnostics.

`MMVM_L2_CGTT_CLK_CTRL` and `MMVM_L2_CGTT_BUSY_CTRL` describe clock gating and light-sleep timing controls: on delay, off hysteresis, LS assert hysteresis, minimum MGLS, CGLS/LS disable bits, busy override, read delay, and always-busy. The main v4.1.0 C file currently gates MMHUB through DAGB registers rather than these fields, but the masks remain part of the generated hardware surface.

`MMVM_L2_CNTL5` is actively used by `mmhub_v4_1_0_init_cache_regs()`. The driver starts from `regMMVM_L2_CNTL5_DEFAULT`, then sets `L2_CACHE_SMALLK_FRAGMENT_SIZE` with `REG_SET_FIELD()`. The register also includes walker priority client ID, PDE fetch no-allocate/MTYPE controls, fine-grain clock-gating overrides for MM client return and UTCL2 ATC request paths, and `UTCL2_ONE_OUTSTANDING_ATC_INVREQ`.

`MMVM_L2_GCR_CNTL` exposes GCR enable and GCR client ID. `MMVM_L2_PTE_CACHE_DUMP_CNTL` and `MMVM_L2_PTE_CACHE_DUMP_READ` provide a diagnostic path to select bank/cache/assoc/index and read PTE-cache dump data after a ready indication. `MMVM_L2_BANK_SELECT_MASKS` splits four 4-bit bank-select masks in a single register.

Credit-safety registers (`MMUTCL2_CREDIT_SAFETY_GROUP_RET_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_NOCDC`, `MMVML2_CREDIT_SAFETY_IH_FAULT_INTERRUPT`, and `MMVML2_WALKER_CREDIT_SAFETY_FETCH_RDREQ`) share a 10-bit `CREDITS` field and an `UPDATE` bit. These tune or report credit limits for UTCL2/MMVML2 return, invalidation request, interrupt, and walker-fetch paths.

### Performance Counter Registers

The `mmhub_mmutcl2_mmvml2prdec` block defines result registers for MC VM L2 and UTCL2 counters:

- `MMMC_VM_L2_PERFCOUNTER_LO` and `MMUTCL2_PERFCOUNTER_LO` expose full 32-bit low counter words.
- `MMMC_VM_L2_PERFCOUNTER_HI` and `MMUTCL2_PERFCOUNTER_HI` split bits 0-15 as `COUNTER_HI` and bits 16-31 as `COMPARE_VALUE`.

The `mmhub_mmutcl2_mmvml2pldec` block defines configuration for `MMMC_VM_L2_PERFCOUNTER0_CFG` through `MMMC_VM_L2_PERFCOUNTER7_CFG` and `MMUTCL2_PERFCOUNTER0_CFG` through `MMUTCL2_PERFCOUNTER3_CFG`. Each config register uses the same layout: `PERF_SEL` in bits 0-7, `PERF_SEL_END` in bits 8-15, `PERF_MODE` in bits 24-27, `ENABLE` at bit 28, and `CLEAR` at bit 29.

`MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL` and `MMUTCL2_PERFCOUNTER_RSLT_CNTL` select a counter and define start/stop trigger fields, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`. These are passive definitions unless a profiling or bring-up path programs the MMIO registers.

### Shared Aperture and L1 TLB Controls

The `mmhub_mmutcl2_mmvmsharedvcdec` block covers address-window and L1 TLB policy fields:

- `MMMC_VM_FB_LOCATION_BASE` and `MMMC_VM_FB_LOCATION_TOP` encode framebuffer base/top values. `mmhub_v4_1_0_get_fb_location()` reads `regMMMC_VM_FB_LOCATION_BASE`, applies `MMMC_VM_FB_LOCATION_BASE__FB_BASE_MASK`, then shifts by 24 bits.
- `MMMC_VM_AGP_TOP`, `MMMC_VM_AGP_BOT`, and `MMMC_VM_AGP_BASE` encode AGP aperture bounds. `mmhub_v4_1_0_init_system_aperture_regs()` writes these from `adev->gmc.agp_*` unless running as an SR-IOV VF.
- `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR` and `MMMC_VM_SYSTEM_APERTURE_HIGH_ADDR` encode logical system aperture bounds. The driver writes these from the min/max of framebuffer and AGP ranges.
- `MMMC_VM_MX_L1_TLB_CNTL` controls L1 TLB enablement, system access mode, unmapped system-aperture behavior, advanced driver model, ECO bits, and memory type. `mmhub_v4_1_0_init_tlb_regs()` enables the L1 TLB, sets system access mode to 3, enables advanced driver model, disables unmapped system-aperture access, clears ECO bits, and sets `MTYPE_UC`. `mmhub_v4_1_0_gart_disable()` later clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`.

### VM Context Controls

The `mmhub_mmutcl2_mmvml2vcdec` block defines `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`. All 16 contexts share the same field layout:

- `ENABLE_CONTEXT`
- `PAGE_TABLE_DEPTH`
- `PAGE_TABLE_BLOCK_SIZE`
- `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`
- `RETRY_OTHER_FAULT`
- interrupt/default handling bits for range, dummy-page, PDE0, valid, read, write, execute, and secure protection faults

`mmhub_v4_1_0_enable_system_domain()` programs context 0 with context enablement, depth 0, and no retry on permission/invalid-page faults. `mmhub_v4_1_0_setup_vmid_config()` programs contexts 1 through 15 by writing from `regMMVM_CONTEXT1_CNTL` with `hub->ctx_distance`; it enables the contexts, sets page-table depth from `adev->vm_manager.num_level`, sets default fault handling for multiple fault classes, derives `PAGE_TABLE_BLOCK_SIZE` from `adev->vm_manager.block_size - 9`, and sets retry behavior from `amdgpu_noretry`.

`MMVM_CONTEXTS_DISABLE` exposes one disable bit per context. `mmhub_v4_1_0_init()` stores its register address in `hub->vm_contexts_disable` for use by common MMHUB/VM paths.

### Invalidation Engines

The chunk defines invalidation request registers for engines 0 through 17. Every `MMVM_INVALIDATE_ENGn_REQ` register has the same layout:

- `PER_VMID_INVALIDATE_REQ` in bits 0-15.
- `FLUSH_TYPE` in bits 16-18.
- `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, and `INVALIDATE_L1_PTES` in bits 19-23.
- `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY` in bits 24-26.

`mmhub_v4_1_0_get_invalidate_req()` constructs an engine-0 request by setting one VMID bit, forcing legacy flush type 0, invalidating L2 PTEs/PDE0/PDE1/PDE2 and L1 PTEs, and leaving protection-fault-status address clear disabled. The common VM code can apply the resulting layout to other engines because `mmhub_v4_1_0_init()` records `hub->eng_distance` from engine 1 minus engine 0.

Each `MMVM_INVALIDATE_ENGn_ACK` register exposes `PER_VMID_INVALIDATE_ACK` in bits 0-15 and `SEMAPHORE` at bit 16. `mmhub_v4_1_0_init()` records the engine-0 semaphore, request, and acknowledgement addresses in `struct amdgpu_vmhub`.

Each engine also has `ADDR_RANGE_LO32` and `ADDR_RANGE_HI32` field definitions. The low register has `S_BIT` at bit 0 and `LOGI_PAGE_ADDR_RANGE_LO31` in bits 1-31; the high register has `LOGI_PAGE_ADDR_RANGE_HI5` in bits 0-4. `mmhub_v4_1_0_program_invalidation()` initializes all 18 engines to a full logical page range by writing low `0xffffffff` and high `0x1f` using `hub->eng_addr_distance`.

### Page Table Base and Range Registers

The chunk defines per-context page-table base address fields for contexts 0 through 15. Each context has:

- `MMVM_CONTEXTn_PAGE_TABLE_BASE_ADDR_LO32__PAGE_DIRECTORY_ENTRY_LO32`
- `MMVM_CONTEXTn_PAGE_TABLE_BASE_ADDR_HI32__PAGE_DIRECTORY_ENTRY_HI32`

`mmhub_v4_1_0_setup_vm_pt_regs()` writes these for a selected VMID using `hub->ctx_addr_distance`, splitting a 64-bit page-table base into low and high 32-bit words. `mmhub_v4_1_0_init_gart_aperture_regs()` uses it for VMID 0 and the GART page table base.

The chunk also defines per-context page-table start and end registers. Each low register exposes a full 32-bit logical page number low field. Each high register exposes a 4-bit high logical page number field. The driver writes context 0 start/end from `adev->gmc.gart_start` and `adev->gmc.gart_end`; for contexts 1 through 15 it programs start to 0 and end to `adev->vm_manager.max_pfn - 1`.

### Per-PF/VF PTE Cache Fragment Sizes

`MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `MMVM_L2_CONTEXT0_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` through `MMVM_L2_CONTEXT15_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` share three fields: `L2_CACHE_SMALLK_FRAGMENT_SIZE`, `L2_CACHE_BIGK_FRAGMENT_SIZE`, and `BANK_SELECT`. These masks allow global and per-context/PF/VF tuning of L2 PTE cache fragment sizing and bank selection.

The v4.1.0 C file does not directly program these per-PF/VF registers in the checked source, but the global L2 cache code does program related fragment-size and bank-select fields in `MMVM_L2_CNTL3` and `MMVM_L2_CNTL5`.

### PSP/IOMMU and Translation Controls

The `mmhub_mmutcl2_mmvml2pspdec` block exposes security/translation control registers:

- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID` has 16-bit masks for translation-bypass VMIDs and GPA-mode VMIDs.
- `MMVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE` has a single GPU-host translation enable bit.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` has a single assist enable bit.
- `MMVM_IOMMU_CONTROL_REGISTER` exposes the `IOMMUEN` bit.
- `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` exposes `PERFOPTEN`.
- `MMUTC_TRANSLATION_FAULT_CNTL0` and `MMUTC_TRANSLATION_FAULT_CNTL1` define a default physical page address and IO/SPA/snoop attributes used on translation fault handling paths.
- `MMUTCL2_VSCH_POWER_STATUS` exposes a `POWERED_DOWN` status bit.

These definitions are not directly referenced by `mmhub_v4_1_0.c` in the checked source, but they define the MMHUB 4.1.0 register ABI for PSP/IOMMU/translation bring-up or diagnostics.

## Control Flow

There is no local control flow in this header. Runtime sequencing is in `amdgpu/mmhub_v4_1_0.c`:

1. `mmhub_v4_1_0_init()` records key register addresses and register spacing values in `adev->vmhub[AMDGPU_MMHUB0(0)]`, including context base, invalidate engine base, fault status/control, context-disable, and bank-select-reserved-CID2 registers.
2. `mmhub_v4_1_0_gart_enable()` calls setup routines in order: GART aperture, system aperture, L1 TLB, L2 cache, system domain, identity aperture disablement, VMID context configuration, and invalidation engine range programming.
3. `mmhub_v4_1_0_get_invalidate_req()` composes a request word using the `MMVM_INVALIDATE_ENG0_REQ` field definitions. Common VM invalidation code then uses the recorded engine register addresses/distances and acknowledgement masks to drive hardware invalidation.
4. `mmhub_v4_1_0_gart_disable()` disables context registers, clears L1 TLB advanced-driver state, and disables L2 cache.
5. Fault-default behavior is controlled separately by `mmhub_v4_1_0_set_fault_enable_default()`, using protection-fault masks defined earlier in the same header, while this chunk supplies the per-context fault enable/default bits used in VMID setup.

## State and Persistence Behavior

The header itself persists no state. The state described by these macros resides in MMHUB hardware registers:

- Context control, page-table base, start, and end registers persist the active VMID translation configuration until reprogrammed or reset.
- Invalidation request registers are command-style MMIO surfaces. A write triggers invalidation for the selected VMID mask and cache/TLB scope. Acknowledgement registers expose completion state per VMID and semaphore state.
- Invalidation address-range registers persist per-engine logical-page range configuration. The driver initializes all 18 engines to the full range during GART enablement.
- L1 TLB, L2 cache, fragment-size, bank-select, GCR, and clock-gating registers persist hardware policy and performance/power settings.
- Performance counter config and result-control registers persist profiling setup. Counter result registers expose accumulated hardware counter state and compare values.
- Credit-safety registers persist credit limits or update state for UTCL2/MMVML2 paths.
- Translation bypass, IOMMU enable, GPU-host translation, translation fault default, and VSCH power status represent security/translation hardware state outside normal per-VM page-table setup.

Several fields are strobe or command-like rather than durable policy bits: invalidation request bits start hardware work, performance-counter `CLEAR` and `CLEAR_ALL` clear counters, credit-safety `UPDATE` commits credit changes, and cache dump `ENABLE` initiates a diagnostic read sequence.

## Dependencies and Integration Points

This chunk depends on the AMDGPU register access and generated-register infrastructure:

- `amdgpu/mmhub_v4_1_0.c` includes `mmhub/mmhub_4_1_0_offset.h` and `mmhub/mmhub_4_1_0_sh_mask.h`.
- `mmhub_4_1_0_offset.h` supplies register addresses; this file supplies fields. Either header alone is incomplete for MMIO programming.
- `REG_SET_FIELD()` and `REG_GET_FIELD()` depend on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_OFFSET()`, and `SOC15_REG_OFFSET()` perform the actual MMHUB instance register reads/writes.
- `struct amdgpu_vmhub` stores base addresses and spacing for contexts and invalidation engines so common VM code can operate on repeated register arrays without hard-coding every context or engine register name.
- Higher-level state comes from `struct amdgpu_device`: `adev->gmc` aperture bounds, GART object page directory address, dummy/default pages, `adev->vm_manager` page-table geometry, SR-IOV VF status, and clock-gating feature flags.

The file is source-tree-aligned with the Linux AMDGPU generated ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg/mmhub`. Hardware definition changes should be regenerated from AMD register descriptions rather than hand-edited.

## Risks and Edge Cases

- The chunk starts mid-family at `MMVM_L2_MM_GROUP_RT_CLASSES` masks. The merged per-file report should combine this with earlier chunk content before treating that register as complete.
- Field layout drift is high risk. Incorrect masks or shifts can silently produce wrong MMIO values via `REG_SET_FIELD()`, causing stale translations, missing invalidation acknowledgements, incorrect page-table bounds, or VM fault storms.
- MMHUB 4.1.0 has 18 invalidation engines in the driver loop. If a future ASIC changes engine count, spacing, or field layout, both generated headers and `mmhub_v4_1_0_program_invalidation()` assumptions need review.
- `PER_VMID_INVALIDATE_REQ` and `PER_VMID_INVALIDATE_ACK` are 16-bit fields. Callers must not shift a VMID outside the supported bit range.
- Context control fields are repeated across contexts 0 through 15, but the driver treats context 0 as the system/GART domain and contexts 1 through 15 as VMID contexts. Applying context-1 policy blindly to context 0 would change system-domain behavior.
- Page-table start/end high registers expose only four high bits in this chunk. Address calculations must match the driver shifts (`>> 12`, `>> 44`) and the hardware page-number width.
- `MMMC_VM_L2_PERFCOUNTER_HI` and `MMUTCL2_PERFCOUNTER_HI` are split between `COUNTER_HI` and `COMPARE_VALUE`; treating the high register as an unqualified 32-bit high counter word would corrupt profiling interpretation.
- SR-IOV VF mode intentionally skips several system aperture and cache registers because the PF programs them. New callers should preserve that access boundary.
- Reserved-client-ID, parity-injection, PTE-cache dump, credit-safety, translation bypass, IOMMU, and default translation-fault fields affect low-level memory translation behavior. Misprogramming can produce security isolation issues, data corruption, hangs, or hard-to-debug VM faults.
- Command bits such as invalidation request, performance-counter clear, and credit update require hardware sequencing and timeout handling in the consumer; the generated masks do not encode ordering guarantees.

## Test Signals

Useful validation signals are integration and hardware-facing:

- Build coverage for `amdgpu/mmhub_v4_1_0.c` confirms that `REG_SET_FIELD()` and `REG_GET_FIELD()` references still match generated mask names.
- GART enablement on MMHUB 4.1.0 hardware should successfully program aperture, L1 TLB, L2 cache, context, and invalidation-range registers without register access faults.
- GPUVM stress tests should complete TLB/cache invalidations with matching per-VMID acknowledgement bits and no timeout in VM flush paths.
- VM fault tests should report expected client IDs and fault classes, and toggling fault-default policy should redirect or interrupt faults according to driver settings.
- SR-IOV VF tests should verify that skipped PF-owned system aperture/cache registers are not accessed by the guest path.
- Suspend/resume and GPU reset tests should re-run GART/MMHUB initialization and restore context/page-table/invalidation state.
- Performance-counter diagnostics should validate the split low/high/compare register interpretation and the `ENABLE`, `CLEAR`, `CLEAR_ALL`, and saturation behavior.
- IOMMU/translation-bypass bring-up should verify VMID bypass/GPA bits, GPU-host translation enablement, default translation fault address, and VSCH power status against hardware documentation.
