# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c

## Purpose
This file implements the GFXHUB 1.2 backend for GC 9.4.3-style multi-XCC hardware. It programs per-XCC VM context registers, GART/system apertures, TLB and L2 cache controls, fault behavior, XGMI topology, and XCP suspend/resume hooks.

## Important APIs, Types, and Functions
The public exports are `gfxhub_v1_2_funcs` and `gfxhub_v1_2_xcp_funcs`. Important callbacks include `get_mc_fb_offset`, `setup_vm_pt_regs`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `init`, and `get_xgmi_info`. Internal helpers are mostly `gfxhub_v1_2_xcc_*` variants that iterate an `xcc_mask` with `for_each_inst`.

## Control Flow and State
Initialization computes a mask from `adev->gfx.xcc_mask`, then seeds each `adev->vmhub[AMDGPU_GFXHUB(i)]` with page-table base, invalidate-engine, fault, and stride register offsets. GART enable programs VMID0 page-table base and aperture limits, system/AGP apertures, default scratch/dummy fault pages, L1 TLB settings, optional L2 cache controls, system-domain context 0, disabled identity apertures, contexts 1-15, and invalidate engine address ranges. `pdb0_bo` and `amdgpu_virt_xgmi_migrate_enabled()` alter VMID0 coverage so system memory and VRAM can share a translated aperture. `gart_disable` clears contexts and disables L1/L2 controls. Fault defaults are broadcast per XCC and can turn crash-on-retry/no-retry bits on when default handling is disabled.

## Dependencies and Integration Points
The file depends on GC 9.4.3 register headers, `amdgpu_xcp.h`, `soc15_common.h`, and shared GMC/VM helpers such as `amdgpu_gmc_pd_addr`, `amdgpu_gmc_vram_mc2pa`, and SR-IOV checks. `gfxhub_v1_2_xcp_funcs` is consumed by XCP partitioning code such as `aqua_vanjaram.c`, allowing partition-specific suspend/resume of selected XCC instances.

## Risks and Test Signals
Risks cluster around multi-XCC masking, `NUM_XCC()` assumptions, PDB0/GART aperture boundaries, SR-IOV register accessibility, and retry/XNACK fault policy. Test signals include boot and reset on GC 9.4.3, XCP partition suspend/resume, XGMI-connected CPU configurations, VM fault-stop modes, multi-XCC TLB invalidation, and KFD per-process XNACK workloads.
