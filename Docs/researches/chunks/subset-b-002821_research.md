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
