# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c

## Purpose

`mmhub_v3_0_1.c` implements the `amdgpu_mmhub_funcs` backend for MMHUB 3.0.1 hardware selected by `gmc_v11_0.c`. It programs the multimedia memory hub side of GPU virtual memory: VMID0 GART aperture, system aperture, L1 TLB, L2 cache, protection-fault defaults, VMID context registers, invalidation engines, framebuffer location reads, page-table-base updates, and MMHUB clock-gating state. It also installs an MMHUB client-id table so VM fault logs name display, ISP, HDP, LSDMA, JPEG, VCN, and firmware clients rather than only numeric IDs.

## Important APIs, Types, And Functions

The exported API is `const struct amdgpu_mmhub_funcs mmhub_v3_0_1_funcs`. Its callbacks include `init`, `get_fb_location`, `get_mc_fb_offset`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `set_clockgating`, `get_clockgating`, and `setup_vm_pt_regs`. Internal helpers include `mmhub_v3_0_1_get_invalidate_req`, `mmhub_v3_0_1_print_l2_protection_fault_status`, `mmhub_v3_0_1_init_gart_aperture_regs`, `mmhub_v3_0_1_init_system_aperture_regs`, `mmhub_v3_0_1_init_tlb_regs`, `mmhub_v3_0_1_init_cache_regs`, `mmhub_v3_0_1_setup_vmid_config`, and `mmhub_v3_0_1_program_invalidation`.

## Control Flow

`mmhub_v3_0_1_init()` fills `adev->vmhub[AMDGPU_MMHUB0(0)]` register offsets and spacing values, sets VM fault interrupt masks, assigns `amdgpu_vmhub_funcs`, and registers the local client-id map. Runtime enable flows through `mmhub_v3_0_1_gart_enable()`: program VMID0 page-table base from `adev->gart.bo`, set GART start/end, program AGP/system apertures and default/fault pages, enable TLB and L2 cache, enable system-domain context0, disable identity aperture, configure VMIDs 1 through 15, and set all 18 invalidation engines to full-range invalidation. Disable reverses the critical hardware state by clearing context controls, disabling L1 TLB advanced model, disabling L2 cache, and clearing `MMVM_L2_CNTL3`.

## State And Persistence Behavior

This file persists hardware state in MMHUB registers, not on disk. It records derived register offsets and cached `hub->vm_cntx_cntl` in `adev->vmhub`. Aperture values come from persistent device setup fields such as `adev->gmc.gart_start`, `adev->gmc.gart_end`, `adev->gmc.fb_start`, `adev->gmc.agp_start`, `adev->mem_scratch.gpu_addr`, and `adev->dummy_page_addr`. Fault policy is controlled dynamically by `mmhub_v3_0_1_set_fault_enable_default()`, which redirects faults to the dummy/default page when enabled and sets crash-on-fault bits when disabled.

## Dependencies And Integration Points

The file depends on generated MMHUB 3.0.1 register offset/sh_mask headers, `navi10_enum.h` for MTYPE values, `soc15_common.h`, AMDGPU VM/GMC structures, and SOC15 register access macros. It integrates with the common VM invalidation path via `hub->vmhub_funcs->get_invalidate_req`, with fault logging through `print_l2_protection_fault_status`, with GMC discovery through `get_fb_location` and `get_mc_fb_offset`, and with power management through MC medium-grain clock gating and light-sleep flags.

## Risks

The register programming order is sensitive: enabling contexts before aperture/default-page setup can expose invalid translations. VMID programming assumes 15 user contexts and 18 invalidation engines. `PAGE_TABLE_BLOCK_SIZE` uses `adev->vm_manager.block_size - 9`, so invalid manager setup would underflow hardware fields. Unlike later variants, this file does not guard system-aperture, L2-cache, or fault-control writes for SR-IOV VFs, so using it on hardware where the PF owns those registers would cause access faults or ineffective programming. Fault handling also depends on the global `amdgpu_noretry`.

## Test Signals

Useful tests are boot/resume on a MMHUB 3.0.1 ASIC, GART allocation and GPU page-table access, VM fault injection verifying client names and fault bits, suspend/resume preserving `setup_vm_pt_regs`, SR-IOV negative coverage if this backend is accidentally selected for a VF, and clock-gating tests checking `MM_ATC_L2_MISC_CG` flags for `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`.
