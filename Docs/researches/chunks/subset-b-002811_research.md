# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 7199-7228

## Scope

This chunk is the final range of the generated AMDGPU MMHUB 3.0.2 shift/mask header. It contains only C preprocessor constants for register-field bit positions and masks, plus the closing `#endif` for `_mmhub_3_0_2_SH_MASK_HEADER`. There are no functions, structs, storage declarations, or executable branches in this range.

The visible lines finish the `MMMC_VM_MX_L1_TLB_CNTL` field masks, then define the `mmhub_mmutcl2_mmvml2pspdec` address block:

- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID`
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`
- `MMUTC_TRANSLATION_FAULT_CNTL0`
- `MMUTC_TRANSLATION_FAULT_CNTL1`

These masks are paired with register addresses in `mmhub_3_0_2_offset.h` and are consumed through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Purpose

The purpose of this chunk is to provide the bit-level software contract for MMHUB 3.0.2 memory-management control registers at the end of the generated header. MMHUB is the memory hub used by non-graphics GPU clients; this register block controls address translation policy, L1 TLB behavior, VMID-specific bypass behavior, GPUVA translation-assist enablement, and default physical-page routing for translation faults.

The macros are ABI-like generated data. Driver code depends on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names and values when composing or decoding 32-bit MMIO register values. A wrong mask can silently program the wrong hardware field.

## Important Macro Families

### `MMMC_VM_MX_L1_TLB_CNTL`

The chunk starts with the mask definitions for the shared MMVM L1 TLB control register:

- `SYSTEM_ACCESS_MODE_MASK` is `0x00000018L`, corresponding to bits 3:4.
- `SYSTEM_APERTURE_UNMAPPED_ACCESS_MASK` is `0x00000020L`, bit 5.
- `ENABLE_ADVANCED_DRIVER_MODEL_MASK` is `0x00000040L`, bit 6.
- `ECO_BITS_MASK` is `0x00000780L`, bits 7:10.
- `MTYPE_MASK` is `0x00003800L`, bits 11:13.

The immediately preceding lines in the same register definition provide the matching shifts and `ENABLE_L1_TLB_MASK`. In `amdgpu/mmhub_v3_0_2.c`, `mmhub_v3_0_2_init_tlb_regs()` reads `regMMMC_VM_MX_L1_TLB_CNTL`, sets `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `ENABLE_ADVANCED_DRIVER_MODEL`, clears `SYSTEM_APERTURE_UNMAPPED_ACCESS`, clears `ECO_BITS`, sets `MTYPE` to `MTYPE_UC`, and writes the register back. `mmhub_v3_0_2_gart_disable()` later clears `ENABLE_L1_TLB` and `ENABLE_ADVANCED_DRIVER_MODEL`.

### `MMUTCL2_TRANSLATION_BYPASS_BY_VMID`

This register is in the `mmhub_mmutcl2_mmvml2pspdec` address block. Its two 16-bit fields split the register by VMID:

- `TRANS_BYPASS_VMIDS` uses bits 0:15 (`SHIFT 0x0`, `MASK 0x0000FFFFL`).
- `GPA_MODE_VMIDS` uses bits 16:31 (`SHIFT 0x10`, `MASK 0xFFFF0000L`).

The companion offset header maps `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID` to offset `0x0a14` with base index 0 for MMHUB 3.0.2. This register is not directly programmed by `mmhub_v3_0_2.c` in the searched tree, but the generated field names expose PSP/MMUTCL2 policy control for firmware or future driver paths that need to select VMIDs whose translations bypass normal handling or run in GPA mode.

### `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`

This control register has a single enable field:

- `ENABLE` uses bit 0 (`SHIFT 0x0`, `MASK 0x00000001L`).

The matching offset is `regMMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` at `0x0a17`. In nearby MMHUB generations, this control belongs to a wider translation-assist register group with request/response registers. In MMHUB 3.0.2, this chunk only exposes the enable bit. The searched in-tree v3.0.2 runtime code does not toggle it directly.

### `MMUTC_TRANSLATION_FAULT_CNTL0` and `MMUTC_TRANSLATION_FAULT_CNTL1`

These registers define the default physical page attributes used by the MMUTC translation-fault path:

- `MMUTC_TRANSLATION_FAULT_CNTL0__DEFAULT_PHYSICAL_PAGE_ADDRESS_LSB` covers all 32 bits of CNTL0.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_PHYSICAL_PAGE_ADDRESS_MSB` covers bits 0:3 of CNTL1.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_IO` is bit 4.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_SPA` is bit 5.
- `MMUTC_TRANSLATION_FAULT_CNTL1__DEFAULT_SNOOP` is bit 6.

The companion offsets are `regMMUTC_TRANSLATION_FAULT_CNTL0` at `0x0a1a` and `regMMUTC_TRANSLATION_FAULT_CNTL1` at `0x0a1b`. These are distinct from the `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` and `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*` registers that `mmhub_v3_0_2.c` actively programs during GART enable; they describe a PSP/MMUTC-side translation-fault default page route.

## Control Flow and Runtime Use

There is no control flow in this header chunk. Runtime behavior comes from code that includes this generated header.

The main MMHUB 3.0.2 runtime consumer is `amdgpu/mmhub_v3_0_2.c`, which includes both `mmhub_3_0_2_offset.h` and `mmhub_3_0_2_sh_mask.h`. Relevant flows are:

1. `mmhub_v3_0_2_gart_enable()` initializes GART and VM translation by calling GART aperture setup, system aperture setup, TLB setup, L2 cache setup, system-domain enablement, identity-aperture disablement, VMID configuration, and invalidation range programming.
2. `mmhub_v3_0_2_init_tlb_regs()` is the direct runtime consumer of the `MMMC_VM_MX_L1_TLB_CNTL` fields covered by this chunk. It performs a read-modify-write sequence using `REG_SET_FIELD` so reserved fields remain preserved while required translation-cache policy bits are changed.
3. `mmhub_v3_0_2_gart_disable()` uses the same L1 TLB control register to disable the L1 TLB and advanced driver model after disabling VM contexts.
4. `mmhub_v3_0_2_init_system_aperture_regs()` programs related aperture and protection-fault default registers, but it uses earlier register definitions rather than the `MMUTC_TRANSLATION_FAULT_CNTL0/1` fields in this tail chunk.
5. No direct in-tree writes were found for the 3.0.2 `MMUTCL2_TRANSLATION_BYPASS_BY_VMID`, `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, or `MMUTC_TRANSLATION_FAULT_CNTL0/1` fields. Their presence still matters because the generated header exports the hardware contract for firmware-facing or debug paths.

## State and Persistence Behavior

This file stores no software state. The state represented by these constants lives in hardware MMIO registers and persists until GPU reset, power-domain loss, suspend/resume reinitialization, PF/firmware reprogramming, or explicit driver writes.

Important hardware state represented by this chunk:

- `MMMC_VM_MX_L1_TLB_CNTL` controls whether MMHUB's L1 TLB and advanced driver model are active. The driver intentionally changes this during GART enable and disable.
- `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, and `MTYPE` alter how untranslated or system-aperture memory traffic is handled.
- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID` is VMID-indexed state. If programmed, it changes translation behavior for selected VMIDs and should be treated as security-sensitive under virtualization.
- `MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL.ENABLE` gates translation-assist behavior. Incorrect persistence across reset or VF/PF transitions could leave assist handling unexpectedly active or inactive.
- `MMUTC_TRANSLATION_FAULT_CNTL0/1` represent a split physical page address plus IO/SPA/snoop attributes for default translation-fault handling.

The split default physical-page address fields require consistent page-number packing: CNTL0 carries the low 32 bits of the default physical page address field and CNTL1 carries four high bits plus attributes. A stale or badly shifted value can redirect faulting traffic to the wrong physical page.

## Dependencies and Integration Points

Generated-register dependencies:

- `mmhub_3_0_2_offset.h` provides the register offsets: `regMMMC_VM_MX_L1_TLB_CNTL` at `0x0873`, `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID` at `0x0a14`, `regMMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` at `0x0a17`, `regMMUTC_TRANSLATION_FAULT_CNTL0` at `0x0a1a`, and `regMMUTC_TRANSLATION_FAULT_CNTL1` at `0x0a1b`.
- Earlier chunks of `mmhub_3_0_2_sh_mask.h` define the matching shifts for `MMMC_VM_MX_L1_TLB_CNTL`, system aperture registers, VM context registers, L2 cache registers, protection-fault controls, and invalidation registers used by the same MMHUB setup flow.
- The SOC15 register helpers in AMDGPU compose these masks with offsets and per-instance base indices.

Driver integration:

- `amdgpu/mmhub_v3_0_2.c` is the primary consumer for this ASIC's MMHUB register definitions. It wires MMHUB functions into `mmhub_v3_0_2_funcs` and initializes `adev->vmhub[AMDGPU_MMHUB0(0)]` with register offsets and fault handling callbacks.
- `amdgpu_vmhub` integration uses this header indirectly through `hub->ctx_distance`, `hub->ctx_addr_distance`, invalidation offsets, and fault status/control offsets. The chunk's L1 TLB control participates in that broader GART/VM enablement sequence.
- SR-IOV integration is important because nearby setup code skips PF-only shared aperture/cache programming when `amdgpu_sriov_vf(adev)` is true. Any future use of the PSP/MMUTCL2 bypass or fault-default registers must observe the same PF/VF ownership constraints.
- Adjacent MMHUB generations expose similar names with different offsets and sometimes additional translation-assist fields. This chunk must remain paired with MMHUB 3.0.2 offsets, not 3.0.0, 3.0.1, 3.3.0, 4.1.0, or 4.2.0 definitions.

## Risks and Edge Cases

- Mixing this 3.0.2 mask header with another generation's offset header can silently target the wrong register or bit. The same field names recur across MMHUB generations, but offsets and register availability differ.
- `MMMC_VM_MX_L1_TLB_CNTL` is programmed by read-modify-write. A bad mask can damage unrelated reserved or policy bits, affecting translation correctness or performance.
- Enabling the L1 TLB or advanced driver model before apertures and page tables are initialized can expose stale translations; disabling them while VM contexts are active can cause translation failures or severe performance loss.
- `SYSTEM_APERTURE_UNMAPPED_ACCESS` and `SYSTEM_ACCESS_MODE` affect how unmapped system aperture accesses behave. Wrong values can turn expected faults into default-page accesses or vice versa.
- `MMUTCL2_TRANSLATION_BYPASS_BY_VMID` can alter translation behavior for up to 16 VMIDs in each field. Incorrect VMID bit selection is a virtualization and isolation risk.
- The translation-fault default page is split across CNTL0/CNTL1. Incorrect shifting, failure to update both halves, or stale IO/SPA/snoop attributes can redirect faulting requests incorrectly.
- The tail chunk ends the include guard. Any generator or merge error that drops the final `#endif` breaks downstream compilation for all consumers of the generated header.

## Test and Verification Signals

Useful validation signals for this chunk are build coverage, register readback, and GART/VM behavioral tests:

- Compile coverage for MMHUB 3.0.2 paths should include `mmhub_3_0_2_sh_mask.h` and verify all `REG_SET_FIELD` references in `mmhub_v3_0_2.c` resolve.
- Register readback after `mmhub_v3_0_2_gart_enable()` should show `MMMC_VM_MX_L1_TLB_CNTL.ENABLE_L1_TLB=1`, `SYSTEM_ACCESS_MODE=3`, `ENABLE_ADVANCED_DRIVER_MODEL=1`, `SYSTEM_APERTURE_UNMAPPED_ACCESS=0`, `ECO_BITS=0`, and `MTYPE=MTYPE_UC`.
- Register readback after `mmhub_v3_0_2_gart_disable()` should show `MMMC_VM_MX_L1_TLB_CNTL.ENABLE_L1_TLB=0` and `ENABLE_ADVANCED_DRIVER_MODEL=0`.
- GART smoke tests should exercise MMHUB clients such as HDP, JPEG, VCN, LSDMA, and display-related clients listed in `mmhub_client_ids_v3_0_2` and confirm translations work after enablement.
- VM fault tests should verify that L2 protection fault logging still reports sensible `CID`, `RW`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, and `MAPPING_ERROR` fields through the v3.0.2 fault callback.
- SR-IOV tests should verify VF paths do not program PF-owned shared MMHUB registers and that PF/firmware ownership is respected for translation bypass and translation-fault default policy.
- Suspend/resume and GPU reset tests should confirm that TLB policy and related aperture/fault registers are restored after hardware state loss.

## Cross-Chunk Notes

This chunk is only the tail of `mmhub_3_0_2_sh_mask.h`. The final per-file report should merge it with earlier chunks that define the rest of `MMMC_VM_MX_L1_TLB_CNTL`, the system aperture/default address registers, VM context registers, invalidation registers, L2 cache/protection-fault fields, and fault status fields used by `mmhub_v3_0_2.c`.
