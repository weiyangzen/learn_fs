# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_2_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002821`: lines 1-2425, `Docs/researches/chunks/subset-b-002821_research.md`
- `subset-b-002822`: lines 2426-3013, `Docs/researches/chunks/subset-b-002822_research.md`

## Chunk Research

### subset-b-002821: lines 1-2425

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_2_0_sh_mask.h lines 1-2425

## Scope

This chunk covers the first 2425 lines of `mmhub_4_2_0_sh_mask.h`, an AMDGPU generated register field header for MMHUB 4.2.0. The chunk contains the MIT-style AMD copyright/license block, the include guard `_mmhub_4_2_0_SH_MASK_HEADER`, and 2140 `#define` entries for 232 register names. It is paired with `mmhub_4_2_0_offset.h`: this file supplies field shifts and bit masks, while the offset header supplies register addresses and base indices.

The chunk ends exactly at `//MMVM_CONTEXT13_PAGE_TABLE_BASE_ADDR_LO32`; the field definitions for that register and the remaining context page-table base/range registers continue after this chunk. Any whole-file reconciliation should treat this as a chunk boundary, not as the end of the logical register family.

## Purpose

The header gives C code symbolic names for individual MMHUB 4.2.0 register fields. The exported names follow the AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT` is the bit position used to right/left shift field values.
- `<REGISTER>__<FIELD>_MASK` is the already-positioned bit mask used to isolate or update the field.

AMDGPU code includes this header and uses these macros through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` to program MMHUB virtual memory, TLB/cache behavior, fault handling, invalidation engines, clock gating, and performance counters. This header has no executable logic by itself; its correctness is critical because it defines the bit contract between the driver and MMHUB hardware.

## Register Families Covered

The chunk is organized by generated `// addressBlock:` comments:

- `mmhub_dagb_dagbdec`: `DAGB0_CNTL_MISC2` and `DAGB1_CNTL_MISC2` masks for DAGB busy override, swap control, return FIFO behavior, and fine-grain clock-gating disable bits.
- `mmhub_mm_cane_mmcanedec`: `MM_CANE_ICG_CTRL` software override fields for request/return/register clock gating.
- `mmhub_mmutcl2_mmvmsharedpfdec`: default system aperture physical address fields, `MMUTCL2_CGTT_*` clock/busy controls, active function/VF metadata, and group return fault status.
- `mmhub_mmutcl2_mmvml2pfdec`: the largest early block, covering MMVM L2 cache controls, L2 invalidation controls, parity/debug controls, protection fault controls/status/address/default-page fields, identity aperture fields, credit-safety knobs, and IH poison/fault interrupt control.
- `mmhub_mmutcl2_mmvml2prdec`, `mmhub_mmutcl2_mmatcl2prdec`, `mmhub_mmutcl2_mmvml2pldec`, and `mmhub_mmutcl2_mmatcl2pldec`: read/result/config registers for MM VM L2, MMUTCL2, and ATC L2 performance counters.
- `mmhub_mmutcl2_mmvmsharedvcdec`: frame-buffer, AGP, system aperture, and L1 TLB control register fields.
- `mmhub_mmutcl2_mmvml2vcdec`: VM context controls for contexts 0-15, context disable bits, invalidate engine semaphores/requests/acknowledgements/address ranges for engines 0-17, and page-table base address fields through context 12 plus the context 13 boundary comment.

## Important APIs, Types, And Macro Contracts

This file exports preprocessor constants only. There are no C functions, structs, enums, or static data objects. Its important public API is the stable macro namespace consumed by MMHUB and VMHUB code:

- `DAGB0_CNTL_MISC2__DISABLE_RDRET_TAP_CHAIN_FGCG_MASK`, `DAGB0_CNTL_MISC2__DISABLE_WRRET_TAP_CHAIN_FGCG_MASK`, and the matching `DAGB1_*` masks are used by MMHUB clock-gating update paths to toggle DAGB fine-grain clock gating.
- `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB` fields encode the default physical page used for unmapped or faulting accesses.
- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` fields describe MMHUB L2 cache enablement, fragment processing, PDE/PTE cache modes, invalidation mode, queue sizing, bank selection, physical tap behavior, and ATC/MM client clock-gating controls.
- `MMVM_L2_PROTECTION_FAULT_CNTL_LO32`, `_HI32`, and `MMVM_L2_PROTECTION_FAULT_CNTL2` fields control default-page routing, retry/no-retry fault interrupt behavior, active page migration PTE behavior, and optional crash-on-fault policy.
- `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` fields expose status bits used by the driver to decode faults: `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, `MAPPING_ERROR`, `CID`, `RW`, `ATOMIC`, `VMID`, `VF`, and `VFID`. `MMVM_L2_PROTECTION_FAULT_STATUS_HI32` adds `PRT`, `UCE`, and `FED`; the v4.2.0 implementation currently has a TODO noting that some critical high-half fields are not fully plumbed into the existing VM hub status path.
- `MMMC_VM_MX_L1_TLB_CNTL` fields enable the L1 TLB, select system access behavior, advanced driver model mode, unmapped aperture behavior, ECO bits, and memory type (`MTYPE`).
- `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL` share the same layout: context enablement, page-table depth/block size, retry behavior, interrupt/default enable bits for range, dummy page, PDE0, valid, read, write, execute, and secure protection faults.
- `MMVM_CONTEXTS_DISABLE` provides one disable bit for each VM context 0-15.
- `MMVM_INVALIDATE_ENG0_REQ` through `MMVM_INVALIDATE_ENG17_REQ` share a uniform layout: a 16-bit per-VMID request mask, 3-bit `FLUSH_TYPE`, L2 PTE/PDE invalidation bits, L1 PTE invalidation, optional protection fault status clear, request logging, and a 4K-only invalidation selector.
- `MMVM_INVALIDATE_ENG0_ACK` through `MMVM_INVALIDATE_ENG17_ACK` expose the 16-bit per-VMID acknowledgement mask plus a semaphore bit.
- `MMVM_INVALIDATE_ENG0_ADDR_RANGE_*` through engine 17 encode invalidation address ranges. The low register carries `S_BIT` and low logical page address bits; the high register carries upper logical page address bits.
- `MMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through context 12 define 64-bit page directory entry fields. The context 13 block starts at the final line of this chunk and is completed later.

The masks use `L`-suffixed constants and assume a 32-bit register value. Full-width fields use `0xFFFFFFFFL`; high-half address fields use narrow masks such as `0x000000FFL`, `0x0000007FL`, `0x00001FFFL`, or `0x00003FFFL` depending on the address encoding width.

## Control Flow And Runtime Use

The header does not run control flow directly, but it shapes the control flow in `amdgpu/mmhub_v4_2_0.c`, which includes both `mmhub_4_2_0_offset.h` and this mask header.

Observed integration flows:

- `gmc_v12_0_set_mmhub_funcs()` selects `mmhub_v4_2_0_funcs` for `IP_VERSION(4, 2, 0)`, making the v4.2.0 MMHUB path active for matching devices.
- `mmhub_v4_2_0_mid_init_system_aperture_regs()` writes FB/AGP/system aperture registers and programs `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*`, `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*`, and `MMVM_L2_PROTECTION_FAULT_CNTL2` using fields from this chunk.
- `mmhub_v4_2_0_mid_init_tlb_regs()` programs `MMMC_VM_MX_L1_TLB_CNTL` with L1 TLB enablement, system access mode, advanced driver model, unmapped access policy, ECO bits, and memory type.
- `mmhub_v4_2_0_mid_init_cache_regs()` programs `MMVM_L2_CNTL*` fields to enable L2 cache, set default-page behavior, select PDE/PTE cache behavior, invalidate L1/L2, and tune cache bank/fragment behavior.
- `mmhub_v4_2_0_mid_enable_system_domain()` uses `MMVM_CONTEXT0_CNTL` fields to enable VMID0 and set its page-table depth/block size.
- `mmhub_v4_2_0_mid_setup_vmid_config()` walks VMIDs through context 1 register spacing, but uses the `MMVM_CONTEXT1_CNTL` field layout as the template for all nonzero VM contexts. It enables contexts, sets page-table depth/block size, enables default fault handling, and selects retry behavior.
- `mmhub_v4_2_0_mid_program_invalidation()` initializes invalidation engine address ranges for 18 engines using the engine address-range register stride derived from `regMMVM_INVALIDATE_ENG1_ADDR_RANGE_LO32 - regMMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`.
- `mmhub_v4_2_0_get_invalidate_req()` constructs a request using the `MMVM_INVALIDATE_ENG0_REQ` layout. Because every invalidate request register in this chunk shares the same field layout, engine 0 field macros are a template for all invalidate engines.
- `mmhub_v4_2_0_print_l2_protection_fault_status()` decodes fault status using `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` masks and shifts and maps the extracted `CID`/`RW` to an MMHUB client name.
- `mmhub_v4_2_0_mid_set_fault_enable_default()` updates `MMVM_L2_PROTECTION_FAULT_CNTL_LO32` fields to enable/disable default-page fault handling and optionally set crash-on-no-retry behavior.
- `mmhub_v4_2_0_update_medium_grain_clock_gating()` uses the DAGB0/DAGB1 `CNTL_MISC2` masks from this chunk when toggling DAGB return tap fine-grain clock gating.

The runtime sequencing in `mmhub_v4_2_0_mid_gart_enable()` is: program GART aperture registers, system aperture/default/fault registers, TLB control, L2 cache control, system context, identity aperture disable, nonzero VMID context configuration, and invalidation address ranges. Almost every step relies on this header for field placement.

## State And Persistence Behavior

This header has no persistent storage and no runtime state of its own. It defines how the driver reads and writes persistent hardware state in MMHUB registers. The hardware state controlled by these fields persists in MMHUB until reset, power management transitions, or explicit driver reprogramming.

Important state domains represented in this chunk:

- Aperture state: FB, AGP, system aperture low/high/default addresses.
- VM context state: enable bits, page-table layout, retry/default/interrupt fault policies, page-table base address registers.
- Cache/TLB state: L1 TLB enablement and memory type, L2 cache and PDE/PTE cache modes, parity and debug dump controls.
- Fault state: protection fault status fields, default fault address, clear/update controls, retry interrupt enablement, crash policy bits.
- Invalidation state: per-engine semaphore, request, acknowledgement, and address-range registers.
- Clock/power state: clock-gating and busy override fields in DAGB, CANE, MMUTCL2, and MMVM L2 control registers.
- Performance state: counter config, clear/enable/select/trigger fields, and counter result fields.

Because this file is included at compile time, any generated value mismatch becomes a baked-in driver behavior issue. The runtime driver generally has no schema validation for these constants beyond successful hardware bring-up and fault/invalidation behavior.

## Dependencies

Direct compile-time dependencies and consumers:

- `amdgpu/mmhub_v4_2_0.c` includes this header and the matching `mmhub_4_2_0_offset.h`.
- `amdgpu/gmc_v12_0.c` selects `mmhub_v4_2_0_funcs` for MMHUB IP 4.2.0, which makes this mask header relevant during GART/VM setup on supported ASICs.
- Generic register helper macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()` depend on each `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` pair being present and consistent.
- MMIO access helpers such as `RREG32_SOC15()`, `WREG32_SOC15()`, `RREG32_SOC15_OFFSET()`, `WREG32_SOC15_OFFSET()`, `SOC15_REG_OFFSET()`, and `GET_INST()` combine the offset header, instance selection, and these bitfield constants.
- `struct amdgpu_vmhub` initialization stores offsets for context, invalidate, fault, and disable registers; later VM update and invalidation paths depend on those offsets and on the field layouts in this header.
- `amdgpu_mmhub_init_client_info()` and fault printing depend indirectly on the `CID`/`RW` field extraction from `MMVM_L2_PROTECTION_FAULT_STATUS_LO32`.

The file also relies on consistent hardware documentation/generated register descriptions. There are no local includes in this header other than its own guard; consumers must include it in a context where register helper macros are available.

## Integration Points

Key source-tree integration points are:

- `drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_2_0_offset.h`: register offset/base-index companion for this field mask header.
- `drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.c`: primary runtime consumer for VM, GART, aperture, invalidation, fault, and clock-gating programming.
- `drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.h`: exposes `mmhub_v4_2_0_funcs`.
- `drivers/gpu/drm/amd/amdgpu/gmc_v12_0.c`: wires MMHUB IP version 4.2.0 to the v4.2.0 MMHUB implementation.
- Shared AMDGPU VM/GMC code: consumes initialized `adev->vmhub[AMDGPU_MMHUB0(i)]` offsets and `vmhub_funcs` for invalidations and fault decoding.

The repeated context and engine layouts are intentionally exploited by driver code through register distances:

- `ctx_distance = regMMVM_CONTEXT1_CNTL - regMMVM_CONTEXT0_CNTL`
- `ctx_addr_distance = regMMVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - regMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`
- `eng_distance = regMMVM_INVALIDATE_ENG1_REQ - regMMVM_INVALIDATE_ENG0_REQ`
- `eng_addr_distance = regMMVM_INVALIDATE_ENG1_ADDR_RANGE_LO32 - regMMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`

Any future generated offset or mask change that breaks these uniform strides would require corresponding driver logic changes.

## Risks And Maintenance Notes

- Mask/shift drift is high impact. A wrong mask in this header can silently program the wrong hardware bit while compiling cleanly.
- The chunk contains many repeated register layouts. Copy/generation errors are easy to miss by visual review, especially for contexts 0-15 and invalidate engines 0-17.
- The first DAGB blocks define `DAGB_BUSY_OVERRIDE__SHIFT` and `DISABLE_MCA_INTR_REQ_FGCG__SHIFT` but do not define corresponding masks in this chunk, while nearby fields do have masks. If consumers attempt `REG_SET_FIELD()` for those missing masks, compilation will fail. This may be intentional generated output if those fields are reserved/unconsumed, but it is a review signal.
- `MMVM_L2_PROTECTION_FAULT_STATUS_HI32` includes `PRT`, `UCE`, and `FED`; the v4.2.0 C file has a TODO saying the 64-bit L2 protection fault status is not fully accommodated by the current VM hub member layout. Fault diagnostics may be incomplete if high-half fields matter.
- Invalidation request field macros are defined per engine, but runtime code builds requests with the engine 0 layout. That is safe only while all engine request registers remain layout-compatible.
- VM context programming loops use `MMVM_CONTEXT1_CNTL` macros as the template for contexts 1-15. The generated context layouts in this chunk are identical; any future context-specific divergence would need code changes.
- Some registers are inaccessible to SR-IOV virtual functions and are skipped by v4.2.0 code. Hardware/firmware must program those PF-only fields correctly for VFs.
- The chunk boundary splits the context page-table base series at context 13. Merge/reconciliation must include later chunk output before making whole-file conclusions about the page-table base register family.
- The file is generated-style hardware ABI. Hand edits should be avoided unless regenerated from authoritative register sources or verified against AMD hardware documentation.

## Test Signals

Useful validation signals for changes touching this header or its companion offsets:

- Build test the AMDGPU driver with MMHUB 4.2.0 enabled. Missing masks/shifts used by `REG_SET_FIELD()` or `REG_GET_FIELD()` should fail compilation.
- Boot/probe on an MMHUB 4.2.0 device and confirm `gmc_v12_0_set_mmhub_funcs()` selects `mmhub_v4_2_0_funcs`.
- Exercise GART enable/disable and VMID setup paths; failures often appear as GPU memory faults, VM fault storms, hangs during VM invalidation, or display/media clients faulting through MMHUB.
- Trigger and inspect VM faults. Expected diagnostics should decode `CID`, `RW`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, and `MAPPING_ERROR` from `MMVM_L2_PROTECTION_FAULT_STATUS_LO32`.
- Exercise VM invalidation for multiple VMIDs and engines. Expected behavior is request/ack completion through the per-engine semaphore/request/ack registers, with L1 and L2 PTE/PDE invalidation bits set as constructed by `mmhub_v4_2_0_get_invalidate_req()`.
- Test SR-IOV VF mode, where aperture/cache/fault controls guarded by `amdgpu_sriov_vf()` are skipped and must be supplied by PF/host policy.
- Test XGMI-connected-to-CPU and APP APU cases, because `MMVM_L2_CNTL4` physical tap fields change when write-combining memory behavior is needed.
- Run suspend/resume or GPU reset tests to ensure register state reinitialization restores aperture, cache/TLB, context, and invalidation programming.
- If performance counter fields are changed, validate that MM VM L2, MMUTCL2, and ATC L2 perf counters can be selected, cleared, enabled, stopped on saturation, and read with expected low/high result behavior.

### subset-b-002822: lines 2426-3013

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_2_0_sh_mask.h lines 2426-3013

## Scope

This chunk is the closing section of the generated AMDGPU MMHUB 4.2.0 shift/mask header. It defines C preprocessor constants for MMHUB register fields, not executable functions. Each field is represented as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro; callers combine these names with register offsets from `mmhub_4_2_0_offset.h` and AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`.

The range begins at the tail of VM context page-table base-address definitions for contexts 13-15, then covers VM context start/end ranges for contexts 0-15, per-PF/VF PTE cache fragment-size programming, VF/HV shared decode registers, XGMI/GPUIOV aperture policy, ATC L2 control and clock-gating registers, PSP-visible IOMMU controls, the PSP-visible framebuffer offset, and the final `#endif`.

## Purpose

The macros provide the bit-level ABI between AMDGPU MMHUB 4.2.0 code and hardware registers. MMHUB is the memory-management hub used by non-graphics clients, and these fields support:

- Programming page-table roots and virtual address bounds for VM contexts/VMIDs.
- Selecting PTE cache fragment sizes per PF/VF and per VM context.
- Reporting PCIe atomic capability and controlling PCIe ATS/ATC behavior.
- Describing host MMIO, top-of-DRAM, XGMI local-framebuffer, GPUIOV, cacheable DRAM, local system-memory, and LPDDR aperture policy.
- Configuring ATC L2 translation request behavior, cache-bank selection, cache dump data, real-time fragment sizing, transaction limits, status, clock gating, and SDP port clock enables.
- Exposing IOMMU enable/performance controls and framebuffer offset fields to PSP decode blocks.

Because this is generated hardware metadata, correctness is primarily about exact names, shifts, masks, and generation pairing. The same register names appear in other MMHUB generations with different offsets or layouts, so these masks must be paired with `mmhub_4_2_0_offset.h`, where the relevant registers live mostly at base index 2.

## Important Macro Families

VM context page-table base tail:

- Lines 2426-2442 finish `MMVM_CONTEXT13_PAGE_TABLE_BASE_ADDR_{LO32,HI32}` through `MMVM_CONTEXT15_PAGE_TABLE_BASE_ADDR_{LO32,HI32}`.
- Both low and high page-directory-entry fragments use shift 0 and full 32-bit masks (`0xFFFFFFFFL`).
- The earlier base-address definitions for contexts 0-12 are outside this chunk, so whole-file consumers need adjacent chunks for the complete repeated family.

VM context start/end bounds:

- Lines 2443-2538 define `MMVM_CONTEXT0_PAGE_TABLE_START_ADDR_{LO32,HI32}` through `MMVM_CONTEXT15_PAGE_TABLE_START_ADDR_{LO32,HI32}`.
- Lines 2539-2634 define the matching `MMVM_CONTEXT0_PAGE_TABLE_END_ADDR_{LO32,HI32}` through `MMVM_CONTEXT15_PAGE_TABLE_END_ADDR_{LO32,HI32}`.
- Low halves expose a full 32-bit `LOGICAL_PAGE_NUMBER_LO32`; high halves expose `LOGICAL_PAGE_NUMBER_HI13` with mask `0x00001FFFL`.
- `mmhub_v4_2_0_mid_init_gart_aperture_regs()` writes context 0 start/end from `adev->gmc.fb_start`, `gart_start`, and `gart_end`; `mmhub_v4_2_0_mid_setup_vmid_config()` writes VMID1-15 start to zero and end to `adev->vm_manager.max_pfn - 1`.

Per-PF/VF PTE cache fragment sizes:

- Lines 2635-2753 define `MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` plus context-specific `MMVM_L2_CONTEXT0_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` through context 15.
- Each register has `L2_CACHE_SMALLK_FRAGMENT_SIZE` at bits 0-4, `L2_CACHE_BIGK_FRAGMENT_SIZE` at bits 5-9, and `BANK_SELECT` at bits 10-15.
- These fields allow the hardware to select cache fragment policy by PF/VF and by VM context. They are distinct from the L2 control fields programmed in `regMMVM_L2_CNTL3`/`regMMVM_L2_CNTL5`, but they share the same fragment-size theme.

Shared VF/HV MMVM decode registers:

- `MMMC_VM_PCIE_ATOMIC_SUPPORTED` exposes a single `PCIE_ATOMIC_SUPPORTED` bit.
- `MMVM_PCIE_ATS_CNTL` exposes `STU` in bits 16-20 and `ATC_ENABLE` at bit 31.
- `MMMC_VM_NB_MMIOBASE`, `MMMC_VM_NB_MMIOLIMIT`, `MMMC_VM_NB_PCI_CTRL`, `MMMC_VM_NB_PCI_ARB`, and TOM/TOM2 registers describe host MMIO and top-of-DRAM routing.
- `MMMC_VM_STEERING` has a 2-bit `DEFAULT_STEERING` field.
- `MMMC_SHARED_VIRT_RESET_REQ` has 8 VF request bits and one PF bit at bit 8 in this generation, unlike some older MMHUB layouts with wider VF bitmaps.

XGMI, GPUIOV, and aperture policy:

- `MMMC_VM_XGMI_LFB_CNTL` defines `PF_LFB_REGION` and `PF_MAX_REGION`; `MMMC_VM_XGMI_LFB_SIZE` defines a 17-bit `PF_LFB_SIZE`.
- `MMMC_VM_HOST_MAPPING` has a one-bit `MODE`.
- `MMMC_VM_XGMI_GPUIOV_ENABLE` has enable bits for VF0-VF7 and a PF enable bit at bit 31.
- `MMMC_VM_CACHEABLE_DRAM_ADDRESS_{START,END}`, `MMMC_VM_LOCAL_SYSMEM_ADDRESS_{START,END}`, and `MMMC_VM_LPDDR_ADDRESS_{START,END}` each expose a 28-bit address field.
- `MMMC_VM_APT_CNTL` controls system-memory aperture behavior: `FORCE_MTYPE_UC`, `DIRECT_SYSTEM_EN`, `FRAG_APT_INTXN_MODE`, `CHECK_IS_LOCAL`, `CAP_FRAG_SIZE_2M`, `LOCAL_SYSMEM_APERTURE_CNTL`, and `LPDDR_APERTURE_CNTL`.
- `MMUTCL2_HARVEST_BYPASS_GROUPS` is a full 32-bit bypass-group mask for harvested/disabled groups.

ATC L2 controls:

- `MM_ATC_L2_CNTL` configures translation read/write request counts, host translation request counts, address-mod dependency bits, cache invalidate mode, fragment aperture interaction mode, GPA/GVA request fragment sizes, and `FORCE_8T_CAP_ON_AT_RETURN`.
- `MM_ATC_L2_CNTL2` selects cache bank layout and update behavior with `BANK_SELECT`, `NUM_BANKS_LOG2`, update mode, write-driven LRU update, tag-index swap bits, VMID mode, and wildcard reference value.
- `MM_ATC_L2_CACHE_DATA0/1/2` expose cache dump/readback data validity, cached attributes, virtual page address, and physical page address fields.
- `MM_ATC_L2_CNTL3`, `CNTL4`, and `CNTL5` cover small/big fragment sizes, invalidation delay, ATS request credits, clock request hysteresis, real-time fragment sizes, and active transaction limits for non-real-time and soft-real-time MM interfaces.
- `MM_ATC_L2_STATUS` reports `BUSY` and `NO_OUTSTANDING_AT_REQUESTS`.
- `MM_ATC_L2_MISC_CG` exposes the bits that the MMHUB 4.2.0 driver actively toggles for medium-grain clock gating (`ENABLE`) and memory light sleep (`MEM_LS_ENABLE`), with `OFFDLY` timing.
- `MM_ATC_L2_CGTT_CLK_CTRL` defines timing and override bits for ATC L2 clock/light-sleep behavior.
- `MM_ATC_L2_SDPPORT_CTRL` defines request/response clock-enable and receive bits for the SDP VDCI port.

PSP decode tail:

- `MMVM_IOMMU_CONTROL_REGISTER` exposes `IOMMUEN`.
- `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` exposes `PERFOPTEN` at bit 13.
- `MMMC_VM_FB_OFFSET` exposes a 28-bit `FB_OFFSET` field. `mmhub_v4_2_0_get_mc_fb_offset()` reads the matching offset register through the MMHUB function table.

## Control Flow and Runtime Use

There is no local control flow in this header. Runtime behavior comes from code that includes it, chiefly `drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.c`, which includes both `mmhub_4_2_0_offset.h` and this mask header.

Key runtime flows supported by this chunk:

1. `gmc_v12_0.c` assigns `adev->mmhub.funcs = &mmhub_v4_2_0_funcs`, making these MMHUB 4.2.0 routines the device-facing implementation for the relevant GMC generation.
2. `mmhub_v4_2_0_mid_init()` computes VM hub register offsets and distances from generated offsets, including context base-address registers, context control spacing, invalidate-engine spacing, fault status/control registers, and context-disable registers.
3. `mmhub_v4_2_0_mid_setup_vm_pt_regs()` writes page-table base low/high registers for a VMID. This uses the same repeated context-address register family whose context 13-15 tail appears at the start of this chunk.
4. `mmhub_v4_2_0_mid_init_gart_aperture_regs()` programs VMID0 page-table start/end bounds using the start/end macros in this chunk. With a VMID0 page table (`pdb0_bo`), the range spans framebuffer start to GART end; otherwise it spans GART start to GART end.
5. `mmhub_v4_2_0_mid_setup_vmid_config()` enables contexts for VMID1-15, sets fault defaults and page-table depth/block size, and writes every VMID's start/end logical page range. The end range uses `adev->vm_manager.max_pfn - 1`.
6. `mmhub_v4_2_0_mid_gart_enable()` sequences aperture setup, system aperture setup, TLB setup, cache setup, system-domain enablement, identity-aperture disablement, VMID configuration, and invalidation range programming.
7. `mmhub_v4_2_0_mid_gart_disable()` clears all context control registers, disables the L1 TLB and advanced driver model, disables L2 cache, and clears `regMMVM_L2_CNTL3`.
8. `mmhub_v4_2_0_update_medium_grain_clock_gating()` reads `regMM_ATC_L2_MISC_CG` and toggles `MM_ATC_L2_MISC_CG__ENABLE_MASK`; it also coordinates DAGB tap-chain gating registers.
9. `mmhub_v4_2_0_update_medium_grain_light_sleep()` toggles `MM_ATC_L2_MISC_CG__MEM_LS_ENABLE_MASK`.
10. `mmhub_v4_2_0_get_clockgating()` reports `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS` based on the same ATC L2 `MISC_CG` bits.

Several macro families in this chunk are hardware contract definitions that are not directly manipulated by current in-tree MMHUB 4.2.0 code paths found during this pass. That includes per-PF/VF PTE cache fragment-size registers, XGMI GPUIOV enable policy, ATC L2 cache dump data registers, PSP IOMMU control fields, and many host-memory aperture controls. They remain integration surfaces for firmware, PF management, debug tooling, future driver paths, or code outside the searched MMHUB setup routines.

## State and Persistence Behavior

The header stores no state. It describes hardware MMIO state that persists until reset, power-domain loss, suspend/resume reinitialization, PF/firmware reprogramming, or explicit driver writes.

Important persistent hardware state represented by this chunk:

- VM context page-table base, start, and end registers define the legal logical page range for each VMID. If these survive unexpectedly across reset or are only partially reprogrammed, MMHUB can translate through stale page tables or fault valid addresses.
- Per-PF/VF PTE cache fragment-size registers and ATC L2 fragment-size controls affect cache locality, invalidation granularity, and request aggregation behavior.
- PCIe ATS/ATC enablement and STU state influence host IOMMU address-translation behavior.
- Shared VF/HV registers such as virtual reset request and GPUIOV enable bits are coordination state between PF, VF, firmware, and possibly PSP-visible management paths. They should not be treated as ordinary driver scratch registers.
- XGMI LFB and host mapping fields influence peer/CPU-visible memory routing.
- Cacheable DRAM, local sysmem, LPDDR, and APT control registers decide whether transactions are treated as local, cacheable, direct-system, or uncached.
- ATC L2 status, cache data, and clock-gating registers represent live hardware state; readback may change with outstanding translations, cache dumps, and power-management transitions.
- IOMMU enable and performance optimization bits are PSP decode surfaces and can affect whether MMHUB traffic participates in IOMMU translation or optimized translation paths.
- Framebuffer offset affects conversion between GPU-visible framebuffer addresses and memory-controller/system addresses.

The source tree contains `mmhub_4_2_0_offset.h` but no matching `mmhub_4_2_0_default.h` in this repository snapshot, so reset/default values for this generation are not available next to these masks.

## Dependencies and Integration Points

Generated-register dependencies:

- `mmhub_4_2_0_offset.h` supplies addresses such as `regMMVM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32` at `0x019b`, `regMMVM_CONTEXT15_PAGE_TABLE_END_ADDR_HI32` at `0x01da`, `regMMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` at `0x01db`, `regMMMC_VM_PCIE_ATOMIC_SUPPORTED` at `0x01f0`, `regMMVM_PCIE_ATS_CNTL` at `0x01f8`, `regMMMC_VM_XGMI_GPUIOV_ENABLE` at `0x0205`, `regMMMC_VM_APT_CNTL` at `0x020c`, `regMM_ATC_L2_CNTL` at `0x0274`, `regMM_ATC_L2_MISC_CG` at `0x0282`, `regMMVM_IOMMU_CONTROL_REGISTER` at `0x02d4`, and `regMMMC_VM_FB_OFFSET` at `0x02ec`.
- The same offset header marks these registers with base index 2, so consumers must use the correct SOC15 instance/base-index path.
- Earlier chunks of `mmhub_4_2_0_sh_mask.h` define the corresponding context control, L1 TLB, L2 cache, invalidation, fault control/status, AGP/framebuffer/system aperture, and page-table base fields that are programmed in the same MMHUB setup sequence.

Driver integration:

- `amdgpu/mmhub_v4_2_0.c` is the main consumer of these generated names for MMHUB 4.2.0 setup, teardown, fault handling, invalidation, and clock gating.
- `gmc_v12_0.c` selects `mmhub_v4_2_0_funcs`, so this header participates in the GMC v12 memory-management path.
- `amdgpu_vmhub` stores offsets derived from the matching offset header, including `ctx_distance`, `ctx_addr_distance`, invalidate-engine distances, context0 page-table base offsets, context control offset, fault status/control offsets, and contexts-disable offset.
- SR-IOV integration is visible in the implementation: VF mode skips PF-owned shared system aperture, cache, identity aperture, fault default, and clock-gating writes. That matches the shared HV/VF register families in this chunk, which are sensitive to PF/VF ownership.
- XCP suspend/resume hooks call the same mid-level GART/fault setup and teardown functions for selected instance masks, so any register-family change must work for partial MMHUB/AID masks, not just all instances.

## Risks and Edge Cases

- Generation mismatch is the largest risk. Similar macros exist in MMHUB 2.x, 3.x, 4.1, and 4.2 headers, but masks and offsets differ. Using a 4.2.0 mask with a non-4.2.0 offset can silently program the wrong bits.
- This chunk starts in the middle of the page-table base-address family. Treating it as the complete VM context base-address definition would miss contexts 0-12.
- High address fragments for VM context start/end are only 13 bits. Code must shift and mask page numbers consistently; writing byte addresses or unshifted physical addresses would corrupt aperture bounds.
- Context programming is repeated by calculated register distance. A wrong `ctx_addr_distance` or VMID loop bound can make one VMID overwrite another VMID's range.
- VMID0 range selection differs when `adev->gmc.pdb0_bo` exists. Tests and diagnostics must distinguish the framebuffer-to-GART span from the GART-only span.
- SR-IOV VF mode intentionally skips shared PF-managed registers. Removing or bypassing those checks can cause blocked register writes, host/VF policy conflicts, or isolation issues.
- ATS, GPUIOV, virtual reset, XGMI, and host mapping fields affect virtualization and host memory routing. Enabling the wrong function or mapping mode can break isolation or peer/CPU access semantics.
- ATC L2 status and clock-gating fields are live hardware state. Changing `MM_ATC_L2_MISC_CG` while translations are active, or misreading clock-gating status in VF mode, can produce hangs or misleading power-management state.
- `MMVM_IOMMU_CONTROL_REGISTER` and performance optimization controls are PSP-decode fields. Driver-side use must be coordinated with firmware ownership and platform IOMMU policy.
- The repository snapshot lacks a 4.2.0 default-value header, so initialization code should not assume generated reset macros exist for this generation.

## Test and Verification Signals

Useful validation signals for this chunk are build coverage, register readback, fault-path behavior, and power-management checks:

- Compile AMDGPU configurations that include `mmhub_v4_2_0.c` and the MMHUB 4.2.0 generated headers; this catches renamed or missing generated macros.
- After `mmhub_v4_2_0_gart_enable()`, read back VMID0 `regMMVM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `END_ADDR_*` for each enabled AID/MMHUB instance and compare them with `fb_start`/`gart_start`/`gart_end` shifted by page size as the code expects.
- For VMID1-15, read back start address zero and end address `adev->vm_manager.max_pfn - 1` after `mmhub_v4_2_0_mid_setup_vmid_config()`.
- Exercise VM fault handling and confirm `mmhub_v4_2_0_print_l2_protection_fault_status()` decodes CID/RW and low-status bits consistently with `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` masks from earlier in the same header.
- Toggle `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS` paths and verify `regMM_ATC_L2_MISC_CG` reflects `ENABLE` and `MEM_LS_ENABLE`; `mmhub_v4_2_0_get_clockgating()` should report matching flags.
- Run SR-IOV VF smoke tests and confirm PF-owned register programming paths are skipped without failed MMIO writes.
- Validate XCP suspend/resume with a restricted instance mask, because the same page-table range, cache, fault, and invalidation setup functions are reused with partial `mid_mask` values.
- If debug or firmware tools touch ATC L2 cache dump, ATS, GPUIOV, IOMMU, or APT fields, verify write/readback against the exact 4.2.0 masks rather than copying assumptions from older MMHUB generations.
