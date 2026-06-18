# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 30632-32178

## Scope

This chunk covers the final MMHUB 1.7 register shift/mask definitions in `mmhub_1_7_sh_mask.h`. It is generated hardware metadata: every item is a C preprocessor macro defining either a bit shift or a bit mask for a 32-bit MMHUB register field. There are no C functions, structs, enums, variables, allocations, locks, loops, or direct MMIO operations in this range.

The range starts in the middle of `VM_CONTEXT10_CNTL`, then covers:

- Full `VM_CONTEXT11_CNTL` through `VM_CONTEXT15_CNTL` field encodings.
- `VM_CONTEXTS_DISABLE` bits for disabling contexts 0 through 15.
- VM invalidate engine semaphore, request, acknowledge, and address-range registers for engines 0 through 17.
- VM context page-table base, start, and end address registers for contexts 0 through 15.
- The `mmhub_utcl2_vmsharedhvdec` block: per-VF framebuffer size/offset, MARC windows, PCIe ATS controls, active function ID, and XGMI GPU IOV enable masks.
- The `mmhub_utcl2_vmsharedpfdec` block: PF/shared framebuffer offset, system aperture default address, steering, virtual reset request, memory light-sleep timing, cacheable/local DRAM/HBM apertures, APT control, UTCL2 clock-gating timing, XGMI local framebuffer controls, cacheable DRAM enable, and host mapping mode.
- The `mmhub_utcl2_vmsharedvcdec` block: framebuffer and AGP locations, system aperture bounds, and `MC_VM_MX_L1_TLB_CNTL`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware register metadata and has no Ceph filesystem behavior.

## Purpose

The purpose of this header slice is to provide the bit-level ABI between MMHUB 1.7 driver code and AMD GPU memory-management hardware. The companion `mmhub_1_7_offset.h` file supplies symbolic register offsets such as `regVM_INVALIDATE_ENG0_REQ`, `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regMC_VM_MX_L1_TLB_CNTL`, and `regMC_VM_FB_LOCATION_BASE`; this file supplies the field positions and masks used to compose and decode those register values.

The exposed macro pattern is regular:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.

AMDGPU code consumes these definitions through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_SOC15_OFFSET`. The direct in-tree implementation for this header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, which includes both `mmhub_1_7_offset.h` and `mmhub_1_7_sh_mask.h`.

## Important Macro Families

### VM Context Control

The first part of the chunk completes `VM_CONTEXT10_CNTL` and defines complete `VM_CONTEXT11_CNTL` through `VM_CONTEXT15_CNTL` layouts. These context-control registers share the same field encoding:

- `ENABLE_CONTEXT`
- `PAGE_TABLE_DEPTH`
- `PAGE_TABLE_BLOCK_SIZE`
- `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`
- `RETRY_OTHER_FAULT`
- range, dummy-page, PDE0, valid, read, write, and execute protection-fault interrupt/default enable bits

`VM_CONTEXTS_DISABLE` then provides one disable bit per context from `DISABLE_CONTEXT_0` through `DISABLE_CONTEXT_15`.

These fields are used by MMHUB VM setup to enable address translation for VMIDs and determine how faults are handled. In `mmhub_v1_7_setup_vmid_config()`, the driver programs contexts 1 through 15 by offsetting from `regVM_CONTEXT1_CNTL`, setting `ENABLE_CONTEXT`, page-table depth, block size, default-fault routing bits, and retry behavior. In `mmhub_v1_7_enable_system_domain()`, context 0 is enabled with the VMID0 page-table depth and block size. In `mmhub_v1_7_gart_disable()`, the driver clears all 16 context-control registers.

### Invalidate Engine Semaphores, Requests, Acks, and Ranges

The chunk defines four repeated register groups for invalidate engines 0 through 17:

- `VM_INVALIDATE_ENGn_SEM`, with a single `SEMAPHORE` bit.
- `VM_INVALIDATE_ENGn_REQ`, with `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, and `LOG_REQUEST`.
- `VM_INVALIDATE_ENGn_ACK`, with `PER_VMID_INVALIDATE_ACK` and `SEMAPHORE`.
- `VM_INVALIDATE_ENGn_ADDR_RANGE_LO32/HI32`, with `S_BIT`, low logical page-address bits, and high logical page-address bits.

The request field layout is the core software contract for MMHUB TLB and page-walk-cache invalidation. Driver code selects a VMID bitmap, chooses the flush type, requests PTE/PDE/L1 invalidation, optionally clears fault status address state, and then waits for the matching acknowledgement bits. The macros also define the per-engine address-range encoding used for range-limited or full-range invalidation.

In `mmhub_v1_7_init()`, the driver records the SOC15 address for `regVM_INVALIDATE_ENG0_REQ` and `regVM_INVALIDATE_ENG0_ACK`, and computes `hub->eng_distance` from `regVM_INVALIDATE_ENG1_REQ - regVM_INVALIDATE_ENG0_REQ`. It also computes `hub->eng_addr_distance` from the address-range register spacing. `mmhub_v1_7_program_invalidation()` uses that spacing to initialize all 18 invalidate engine address ranges to the full supported range (`LO32 = 0xffffffff`, `HI32 = 0x1f`).

### VM Context Page-Table Addresses

The chunk defines page-table base address registers for contexts 0 through 15:

- `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_LO32`
- `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_HI32`

It also defines logical page-number aperture bounds for each context:

- `VM_CONTEXTn_PAGE_TABLE_START_ADDR_LO32/HI32`
- `VM_CONTEXTn_PAGE_TABLE_END_ADDR_LO32/HI32`

The base address fields are full 32-bit low/high pieces of the page-directory entry address. Start and end address fields use full low 32-bit logical page numbers and 4-bit high logical page-number fragments.

`mmhub_v1_7_setup_vm_pt_regs()` writes context page-table base registers using `hub->ctx_addr_distance` and the context 0 base-register pair. `mmhub_v1_7_init_gart_aperture_regs()` programs VMID0 start/end based on either the GART aperture or a combined VRAM-plus-GART aperture when `pdb0_bo` is used. `mmhub_v1_7_setup_vmid_config()` initializes contexts 1 through 15 with start address 0 and end address `adev->vm_manager.max_pfn - 1`.

### SR-IOV, VF Framebuffer Partitioning, and XGMI IOV

The `mmhub_utcl2_vmsharedhvdec` block defines hypervisor/shared fields that are relevant to virtualization and multi-function GPU operation:

- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`, each packing `VF_FB_SIZE` and `VF_FB_OFFSET`.
- `MC_SHARED_ACTIVE_FCN_ID`, with `VFID` and `VF` fields indicating the active virtual function identity.
- `MC_VM_XGMI_GPUIOV_ENABLE`, with one enable bit for each VF 0 through 15 and a high PF enable bit.
- `MC_SHARED_VIRT_RESET_REQ` in the PF block, with VF and PF reset request bits.

These definitions describe hardware partition state rather than normal process VM state. They are privilege-sensitive: the PF/hypervisor side can use these fields to isolate framebuffer apertures and XGMI GPU IOV access for virtual functions, while VF paths in `mmhub_v1_7.c` intentionally skip several privileged setup steps such as system aperture programming, L2 cache programming, and clock-gating changes.

### MARC Windows and Relocation

The same hypervisor/shared block defines four MARC windows:

- `MC_VM_MARC_BASE_LO/HI_0..3`
- `MC_VM_MARC_RELOC_LO/HI_0..3`
- `MC_VM_MARC_LEN_LO/HI_0..3`

The low base/relocation/length fields start at bit 12, indicating page-aligned quantities. Each relocation-low register also includes `MARC_ENABLE_n` and `MARC_READONLY_n`. These fields represent address-window remapping and optional read-only behavior. The macros do not encode when the windows are legal to program or how they interact with IOMMU/VM policy; that sequencing must come from the owning MMHUB, firmware, or virtualization code.

### PCIe ATS and ATC Enablement

`VM_PCIE_ATS_CNTL` defines `STU` and `ATC_ENABLE` for the PF/global path. `VM_PCIE_ATS_CNTL_VF_0` through `VM_PCIE_ATS_CNTL_VF_15` define per-VF `ATC_ENABLE` bits. The VC block's `MC_VM_MX_L1_TLB_CNTL` also contains `ATC_EN`, so ATS/ATC state is split across PCIe-facing and MMHUB L1 TLB controls.

`mmhub_v1_7_init_tlb_regs()` sets `MC_VM_MX_L1_TLB_CNTL__ATC_EN` along with L1 TLB enablement, system access mode, advanced driver model, unmapped system aperture handling, and MTYPE. Correct ATC/ATS state is important for coherent PCIe address translation and for virtualized configurations where VF enablement may be controlled separately from PF policy.

### PF/Shared Apertures, Cacheability, and Local Memory Controls

The `mmhub_utcl2_vmsharedpfdec` block defines fields for PF/shared memory mapping:

- `MC_VM_FB_OFFSET`
- `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`
- `MC_VM_STEERING`
- `MC_MEM_POWER_LS`
- `MC_VM_CACHEABLE_DRAM_ADDRESS_START/END`
- `MC_VM_APT_CNTL`
- `MC_VM_LOCAL_HBM_ADDRESS_START/END`
- `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`
- `MC_VM_XGMI_LFB_CNTL`
- `MC_VM_XGMI_LFB_SIZE`
- `MC_VM_CACHEABLE_DRAM_CNTL`
- `MC_VM_HOST_MAPPING`

`mmhub_v1_7_init_system_aperture_regs()` uses the system aperture default address fields to route unmapped/protected system aperture accesses to the scratch page. It also programs the protection fault default address and L2 fault-control state outside this chunk. Other fields in this block control cacheability, local HBM aperture bounds and lock state, XGMI local framebuffer region/size, and host-mapping mode.

`MC_VM_APT_CNTL` is a compact policy register with `FORCE_MTYPE_UC`, `DIRECT_SYSTEM_EN`, `CHECK_IS_LOCAL`, and `PERMS_GRANTED`. Although `mmhub_v1_7.c` does not directly program this specific register in the inspected lines, same-generation golden-value tables in the AMDGPU tree program related `*_VM_APT_CNTL` registers for GC/IMU paths. That makes these fields part of system/host-memory routing policy rather than an isolated debug register.

### UTCL2 Clock Gating and VC Apertures

`UTCL2_CGTT_CLK_CTRL` defines clock-gating timing and override fields:

- `ON_DELAY`
- `OFF_HYSTERESIS`
- `SOFT_OVERRIDE_EXTRA`
- `MGLS_OVERRIDE`
- `SOFT_STALL_OVERRIDE`
- `SOFT_OVERRIDE`

The final `mmhub_utcl2_vmsharedvcdec` block defines virtual-client visible aperture and L1 TLB fields:

- `MC_VM_FB_LOCATION_BASE/TOP`
- `MC_VM_AGP_TOP/BOT/BASE`
- `MC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`
- `MC_VM_MX_L1_TLB_CNTL`

`mmhub_v1_7_get_fb_location()` masks `MC_VM_FB_LOCATION_BASE__FB_BASE_MASK` and `MC_VM_FB_LOCATION_TOP__FB_TOP_MASK` and shifts the values by 24 to populate `adev->gmc.fb_start` and `adev->gmc.fb_end`. `mmhub_v1_7_init_system_aperture_regs()` programs AGP and system aperture bounds, with a special path disabling FB/AGP apertures when VRAM is squeezed into the GART aperture. `mmhub_v1_7_init_tlb_regs()` and `mmhub_v1_7_gart_disable()` use `MC_VM_MX_L1_TLB_CNTL` fields to enable or disable MMHUB L1 translation behavior.

## Control Flow

This header has no runtime control flow. Its only behavior is compile-time substitution of symbolic masks and shifts.

The implied runtime flow in the MMHUB 1.7 driver is:

1. `mmhub_v1_7.c` includes this shift/mask header and the matching offset header.
2. Initialization code computes register spacing and records hub register addresses in `adev->vmhub[AMDGPU_MMHUB0(0)]`.
3. GART/MMHUB setup writes page-table base/start/end registers, aperture registers, L1 TLB controls, L2 controls, context-control registers, and invalidate range registers.
4. VM invalidation paths use the recorded engine request/ack addresses and field encodings to request flushes and observe completion.
5. Suspend/resume, reset, SR-IOV, and clock/power-management paths preserve, skip, or reprogram subsets of this hardware state according to device mode.

The header does not encode ordering, polling, timeout, privilege, reset, or clear-on-write semantics. Those constraints live in driver code, firmware contracts, and the hardware specification.

## State and Persistence Behavior

The macros themselves are stateless. Persistent state exists in MMHUB hardware registers and in the memory objects whose addresses are programmed into those registers.

Hardware state represented by this chunk includes enabled VM contexts, page-table depth and block-size configuration, retry/default fault behavior, disabled-context bits, invalidate engine semaphore/request/ack state, invalidate address ranges, per-context page-table roots and aperture bounds, per-VF framebuffer partitions, MARC remap windows, PCIe ATS/ATC enables, active function selection, XGMI IOV enables, system/default aperture addresses, AGP and FB locations, cacheable/local memory aperture state, L1 TLB policy, clock-gating timing, and host mapping policy.

Some fields are durable configuration that persists until reset or reprogramming, such as context page-table bases, aperture bounds, L1 TLB control, VF framebuffer size/offset, and MARC windows. Other fields are transactional or status-like, especially invalidate `REQ`, `ACK`, and `SEM` fields, virtual reset request bits, and lock/control bits. Consumers must avoid treating all masks as ordinary persistent configuration.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB 1.7 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h` supplies register offsets for the names defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_default.h`, where present for the broader file, supplies reset/default values outside this chunk.
- AMDGPU SOC15 helpers provide the actual address calculation and MMIO access behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` is the direct consumer for MMHUB 1.7 VM setup, GART enable/disable, system aperture setup, L1 TLB setup, invalidation range initialization, and hub register address bookkeeping.
- Shared AMDGPU VM and GMC structures, especially `struct amdgpu_vmhub` and `adev->gmc`, provide the page-table roots, aperture bounds, VMID dimensions, and cached register addresses that are programmed with these masks.

Similar-looking macros exist in other MMHUB, GFXHUB, GMC, and DCN generation headers. They must not be substituted across ASIC families by name alone, because field names can remain stable while offsets, masks, widths, and privilege domains change.

## Risks and Edge Cases

- Generated bitfield drift is high impact. A wrong shift or mask can program the wrong MMHUB field while still compiling cleanly.
- This chunk starts mid-register at `VM_CONTEXT10_CNTL`; complete context-control coverage requires the previous chunk for contexts 0 through 10.
- Repeated families are easy to corrupt mechanically. Contexts 0 through 15, invalidate engines 0 through 17, VF registers 0 through 15, and MARC windows 0 through 3 rely on stable spacing and consistent naming.
- Invalidate request/ack fields are sequencing-sensitive. Missing `ACK` polling, using the wrong engine distance, or invalidating the wrong VMID bitmap can leave stale translations or cause VM faults after page-table updates.
- Page-table start/end fields have narrower high parts than base-address fields. Treating all high registers as full 32-bit quantities can produce incorrect logical aperture bounds.
- Fault behavior fields affect recovery policy. Incorrect default-fault, retry, read/write/execute, or clear-fault-status settings can convert recoverable faults into hangs, hide diagnostic fault addresses, or route accesses to an unexpected dummy page.
- SR-IOV and XGMI IOV fields are isolation-sensitive. Incorrect VF framebuffer size/offset, ATC enablement, active function ID, XGMI enable, or virtual reset fields can break PF/VF isolation or multi-GPU partitioning.
- MARC relocation and read-only fields describe address remapping. Incorrect programming can redirect memory traffic or grant writes where only reads should be permitted.
- Clock-gating and light-sleep timing fields can affect stability. Bad UTCL2 clock override or hysteresis settings may produce intermittent memory-translation failures that look like workload-specific hangs.
- The direct driver skips privileged setup in VF mode. Any future use of PF/shared fields must preserve those SR-IOV checks.

## Test and Validation Signals

Useful validation is mostly generated-data consistency plus MMHUB integration coverage:

- Build AMDGPU with MMHUB 1.7 support enabled; this catches missing or renamed macros in `mmhub_v1_7.c`.
- Mechanically compare shifts and masks in this chunk against AMD's authoritative MMHUB 1.7 register database.
- Boot on matching hardware and verify GART enablement, framebuffer location discovery, VMID0 setup, and contexts 1 through 15 setup complete without MMHUB VM faults.
- Exercise VM bind/unbind and page-table update paths that trigger invalidate engine requests, then verify acknowledgements arrive for the requested VMID bitmap.
- Test XNACK/retry-fault behavior, because `mmhub_v1_7_setup_vmid_config()` enables retry permission or invalid-page faults for contexts 1 through 15.
- Run suspend/resume and GPU reset paths to confirm page-table bases, L1 TLB control, system aperture, AGP/FB locations, and invalidation range setup are restored correctly.
- Run SR-IOV PF and VF configurations to verify privileged aperture/cache setup is skipped for VFs while VF-visible translation still works.
- Exercise PCIe ATS/ATC and XGMI-connected configurations where address translation and local framebuffer controls can differ from the non-virtualized, non-XGMI path.
- Use register dumps to decode `MC_VM_MX_L1_TLB_CNTL`, `VM_INVALIDATE_ENG*_REQ/ACK`, `VM_CONTEXT*_PAGE_TABLE_*`, and `MC_VM_FB_LOCATION_*` values with these masks and compare against expected driver state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002771`. The final per-file report should merge this with adjacent chunks for complete `mmhub_1_7_sh_mask.h` coverage. The previous chunk owns the beginning of the VM context-control family and earlier MMHUB L2/fault-control fields; this chunk owns the end of the file through `#endif`.
