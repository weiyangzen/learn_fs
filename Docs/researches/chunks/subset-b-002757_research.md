# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h lines 4935-5125

## Scope

This chunk covers the final 191 lines of the generated AMD MMHUB 1.7 register offset header. It starts at the tail of the `VM_CONTEXT13/14/15_PAGE_TABLE_END_ADDR_*` context range, then covers the complete `mmhub_utcl2_vmsharedhvdec`, `mmhub_utcl2_vmsharedpfdec`, and `mmhub_utcl2_vmsharedvcdec` offset blocks before the closing `#endif`.

The range contains 177 `#define` macros. Each register offset is paired with a `_BASE_IDX` macro, and every `_BASE_IDX` in this slice is `0`. There are no C functions, types, inline helpers, storage objects, or executable statements.

## Purpose

`mmhub_1_7_offset.h` is a generated hardware-register map for the AMDGPU MMHUB 1.7 block. This tail slice provides symbolic register numbers for VM context address bounds, per-VF framebuffer sizing, MARC remap windows, PCIe ATS controls, virtualization/shared-function state, PF aperture setup, VC framebuffer/AGP/system aperture setup, and MMHUB L1 TLB control.

The header exists so MMHUB 1.7 driver code can use `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET` with named `reg...` constants instead of raw register offsets. The matching field definitions live in `mmhub_1_7_sh_mask.h`; this file supplies addresses only.

## Important APIs, Types, And Data

The exported API is the preprocessor namespace of register-offset constants:

- `regVM_CONTEXT14_PAGE_TABLE_END_ADDR_LO32/HI32` and `regVM_CONTEXT15_PAGE_TABLE_END_ADDR_LO32/HI32` finish the VMID page-table range-address register family. The first line is the `_BASE_IDX` for `regVM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32`, showing this chunk begins mid-family.
- `regMC_VM_FB_SIZE_OFFSET_VF0` through `regMC_VM_FB_SIZE_OFFSET_VF15` describe per-virtual-function framebuffer size/offset registers in `mmhub_utcl2_vmsharedhvdec`.
- `regMC_VM_MARC_BASE_LO/HI_0..3`, `regMC_VM_MARC_RELOC_LO/HI_0..3`, and `regMC_VM_MARC_LEN_LO/HI_0..3` define four MARC base, relocation, and length windows.
- `regVM_PCIE_ATS_CNTL` and `regVM_PCIE_ATS_CNTL_VF_0..15` define PF/global and per-VF PCIe ATS control registers. The companion mask header gives the global `STU` and `ATC_ENABLE` fields and per-VF `ATC_ENABLE` fields.
- `regMC_SHARED_ACTIVE_FCN_ID` and `regMC_VM_XGMI_GPUIOV_ENABLE` expose shared active-function identity and XGMI GPU-IOV enable state.
- `regMC_VM_FB_OFFSET`, `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, `regMC_VM_STEERING`, `regMC_SHARED_VIRT_RESET_REQ`, `regMC_MEM_POWER_LS`, `regMC_VM_CACHEABLE_DRAM_ADDRESS_START/END`, `regMC_VM_APT_CNTL`, `regMC_VM_LOCAL_HBM_ADDRESS_START/END`, `regMC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`, `regUTCL2_CGTT_CLK_CTRL`, `regMC_VM_XGMI_LFB_CNTL`, `regMC_VM_XGMI_LFB_SIZE`, `regMC_VM_CACHEABLE_DRAM_CNTL`, and `regMC_VM_HOST_MAPPING` are PF/shared aperture and memory-location controls.
- `regMC_VM_FB_LOCATION_BASE/TOP`, `regMC_VM_AGP_TOP/BOT/BASE`, `regMC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`, and `regMC_VM_MX_L1_TLB_CNTL` are VC aperture and L1 TLB control registers used by MMHUB setup paths.

The numeric offsets in this chunk run from the context tail near `0x0c87` through `0x0d1d`, with PF and VC blocks using lower offsets such as `0x0cab` through `0x0cc7`. The address-block comments identify the hardware decode domains and their base addresses: `0x6b380`, `0x6b290`, and `0x6b300`.

## Control Flow

This header has no runtime control flow. Runtime behavior appears when C code includes this offset header and combines the macros with SOC15 MMIO helpers:

1. `amdgpu/mmhub_v1_7.c` includes `mmhub/mmhub_1_7_offset.h` and `mmhub/mmhub_1_7_sh_mask.h`.
2. Initialization reads framebuffer location registers with `RREG32_SOC15(MMHUB, 0, regMC_VM_FB_LOCATION_BASE/TOP)` and stores the derived byte addresses in `adev->gmc.fb_start` and `adev->gmc.fb_end`.
3. GART/system aperture setup writes `regMC_VM_AGP_*`, `regMC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`, `regMC_VM_FB_LOCATION_*`, `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, and protection-fault defaults.
4. TLB setup reads and writes `regMC_VM_MX_L1_TLB_CNTL`, using fields from the companion mask header to enable L1 TLB, advanced driver model, MTYPE, system access mode, and ATC.
5. VMID setup loops over contexts through `WREG32_SOC15_OFFSET` using offsets and spacing computed elsewhere in `mmhub_v1_7_init()`. The `VM_CONTEXT14/15_PAGE_TABLE_END_ADDR_*` constants in this chunk are the tail of that contiguous context-address register layout.

Many macros in the hypervisor/PF shared blocks are not directly referenced by current `mmhub_v1_7.c`, but they are still part of the generated ABI for SR-IOV, ATS, XGMI, MARC, and aperture programming paths.

## State And Persistence Behavior

The macros are compile-time constants and do not persist state. The registers they name hold persistent GPU hardware state:

- VM context page-table end addresses bound the legal GPU virtual address range for VMIDs. MMHUB setup writes these during GART enable and leaves them active until reset, suspend/resume restore, GPU reset, or GART disable changes context state.
- Framebuffer, AGP, system aperture, default page, cacheable DRAM, local HBM, host-mapping, and XGMI LFB registers define address routing for MMHUB memory accesses. Incorrect values persist in hardware and affect translations until rewritten.
- `MC_VM_MX_L1_TLB_CNTL` controls TLB behavior and ATC participation. MMHUB enable programs it; GART disable clears key enable bits.
- Per-VF framebuffer offset/size, ATS, active-function, virtual-reset, and XGMI GPU-IOV registers describe virtualization state. They are hardware-visible isolation and routing controls, not normal kernel memory.
- MARC windows define base, relocation, and length state for memory remapping windows. These are long-lived aperture descriptors once programmed.

There is no disk state, reference counting, locking, allocation, or software-owned lifetime in this header. Ordering, locking, reset handling, and SR-IOV policy are responsibilities of the MMHUB/GMC/virtualization callers.

## Dependencies

This chunk depends on the generated MMHUB 1.7 register specification and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h`, which defines bit fields for the same register names, including `MC_VM_FB_SIZE_OFFSET_VF*`, `MC_VM_MARC_*`, `VM_PCIE_ATS_CNTL*`, `MC_VM_FB_OFFSET`, `MC_VM_XGMI_LFB_CNTL`, `MC_VM_HOST_MAPPING`, and `MC_VM_MX_L1_TLB_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`, the primary local MMHUB 1.7 consumer.
- AMDGPU SOC15 helpers and register-addressing macros such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- AMDGPU GMC state in `struct amdgpu_device`, especially `adev->gmc.fb_start`, `fb_end`, `agp_start`, `agp_end`, `gart_start`, `gart_end`, `pdb0_bo`, `translate_further`, `xgmi.connected_to_cpu`, and VM manager geometry.

The `_BASE_IDX` values are part of SOC15 register-address calculation. They are all zero in this slice, but callers still rely on the generated form being present and consistent.

## Integration Points

- `mmhub_v1_7_get_fb_location()` reads `regMC_VM_FB_LOCATION_BASE/TOP`, masks the 24-bit fields via the companion mask header, shifts by 24, and publishes the resulting VRAM aperture to `adev->gmc`.
- `mmhub_v1_7_init_system_aperture_regs()` programs `regMC_VM_AGP_BASE/BOT/TOP`, `regMC_VM_SYSTEM_APERTURE_LOW_ADDR/HIGH_ADDR`, optionally disables FB/AGP apertures when `pdb0_bo` is used, and writes `regMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`.
- `mmhub_v1_7_init_tlb_regs()` programs `regMC_VM_MX_L1_TLB_CNTL` for L1 TLB enablement, system access mode, advanced driver model, MTYPE, unmapped-access behavior, and ATC enable.
- `mmhub_v1_7_setup_vmid_config()` programs VM context page-table start/end registers for VMIDs 1-15 using contiguous context register spacing; the context end-address tail in this chunk is part of that range.
- SR-IOV and virtualization integration is represented by the per-VF framebuffer, ATS, active-function, virtual-reset, and XGMI GPU-IOV registers. Some of these are reserved for PF/hypervisor flows and may be programmed by firmware or host-side code rather than by normal VF driver paths.
- XGMI and large-framebuffer integration is represented by `regMC_VM_XGMI_LFB_CNTL`, `regMC_VM_XGMI_LFB_SIZE`, and `regMC_VM_XGMI_GPUIOV_ENABLE`, which describe large-framebuffer and GPU-IOV routing state for multi-GPU or CPU-connected fabrics.

## Risks

- Offset drift is the central risk. If a generated `reg...` value does not match the MMHUB 1.7 hardware spec, the driver can read or write the wrong register while still compiling cleanly.
- The chunk begins mid-register-family. Merge/reconciliation should not treat the `VM_CONTEXT13_PAGE_TABLE_END_ADDR_HI32` group as fully described by this chunk alone.
- Context end-address registers are split low/high page-number values. Unit mistakes between bytes, 4 KiB pages, and higher-address bits can silently widen or shrink VMID access ranges.
- Per-VF framebuffer, ATS, active-function, reset, and XGMI GPU-IOV controls affect SR-IOV isolation. Misprogramming them can route memory traffic to the wrong VF, break guest address translation, or strand a VF during reset.
- Aperture registers such as framebuffer location, AGP bounds, system aperture bounds, default address, local HBM, cacheable DRAM, and host mapping affect memory routing globally for the hub. Bad values can cause VM faults, poisoned default-page accesses, display/media failures, or hangs.
- MARC base/relocation/length registers define remap windows. Incorrect pairing of LO/HI/base/reloc/length indices can redirect an aperture even if each individual write is well formed.
- Cross-generation similarity is dangerous. MMHUB 1.7, MMHUB 1.8, GC 9.x, and later GC/MMHUB headers use similar names with different numeric offsets and sometimes different base indices; including or copying the wrong ASIC header can produce valid C that targets invalid hardware addresses.

## Test Signals

- Build AMDGPU with MMHUB 1.7 support so `mmhub_v1_7.c` compiles against this offset header and the companion mask header.
- Static generated-header validation should compare every register in this slice against the authoritative MMHUB 1.7 register source and verify matching field groups exist in `mmhub_1_7_sh_mask.h`.
- Boot/runtime smoke on MMHUB 1.7 hardware should confirm framebuffer location discovery, GART enable, VMID setup, TLB setup, suspend/resume, and GPU reset do not produce VM faults or register-access warnings.
- GPUVM stress should allocate and evict buffers across VMIDs, force page-table updates, and validate no stale translations or protection-fault storms occur after context range and invalidation setup.
- SR-IOV validation should exercise PF plus VF boot/reset paths, per-VF framebuffer aperture visibility, ATS enable behavior, virtual reset request handling, and active-function reporting.
- XGMI or large-framebuffer systems should verify LFB region/size and GPU-IOV state across boot, reset, and peer-memory workloads.
- Aperture diagnostics should compare `adev->gmc.fb_start/fb_end`, AGP/system aperture bounds, default-page programming, and L1 TLB control values against known-good traces from the same ASIC generation.
