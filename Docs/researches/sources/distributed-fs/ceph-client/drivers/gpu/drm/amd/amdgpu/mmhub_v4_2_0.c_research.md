# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.c

## Purpose

`mmhub_v4_2_0.c` is the MMHUB 4.2.0 backend for newer GMC v12 hardware with multiple addressable MMHUB/MID instances and XCP partition support. It generalizes VM hub initialization and GART programming across `adev->aid_mask`, handles VMID0 page-table mode, exposes XGMI fabric information for CPU-connected configurations, and provides standard MMHUB VM, fault, clock-gating, and page-table callbacks.

## Important APIs, Types, And Functions

The exported table is `mmhub_v4_2_0_funcs`; it includes `get_xgmi_info` in addition to the usual MMHUB callbacks. Local XCP callbacks are defined in `struct amdgpu_xcp_ip_funcs mmhub_v4_2_0_xcp_funcs`. Most hardware operations have a `mid_` variant that takes an instance mask: `mid_setup_vm_pt_regs`, `mid_init_gart_aperture_regs`, `mid_init_system_aperture_regs`, `mid_init_tlb_regs`, `mid_init_cache_regs`, `mid_enable_system_domain`, `mid_disable_identity_aperture`, `mid_setup_vmid_config`, `mid_program_invalidation`, `mid_gart_enable`, `mid_gart_disable`, `mid_set_fault_enable_default`, and `mid_init`.

## Control Flow

Top-level callbacks derive `mid_mask = adev->aid_mask` and call the MID helpers. Each helper iterates `for_each_inst(i, mid_mask)` and writes the corresponding `GET_INST(MMHUB, i)` registers. If `adev->gmc.pdb0_bo` exists, VMID0 page-table base comes from that BO and the VMID0 range starts at `fb_start`; system and AGP apertures are disabled because VMID0 page tables cover the path. Otherwise, it uses the normal GART BO and AGP/system aperture programming. `xcp_resume` restores fault defaults and GART setup for a partition mask; `xcp_suspend` disables GART for that mask.

## State And Persistence Behavior

State is per-MMHUB instance in `adev->vmhub[AMDGPU_MMHUB0(i)]` and hardware registers. `mmhub_v4_2_0_get_xgmi_info()` reads `MMMC_VM_XGMI_LFB_*` registers and persists `num_physical_nodes`, `physical_node_id`, and `node_segment_size` in `adev->gmc.xgmi`, returning `-EINVAL` if register values exceed the hard-coded four-node A+A limits. Fault control uses LO32 registers and sets `CRASH_ON_NO_RETRY_FAULT` when default redirection is disabled. `ENABLE_RETRY_FAULT_INTERRUPT` is enabled in CNTL2 during aperture setup.

## Dependencies And Integration Points

The file depends on generated `mmhub_4_2_0` registers, SOC24 enums, SOC15 macros, `for_each_inst`, `GET_INST`, XCP infrastructure, SR-IOV helpers, and GMC VMID0 page-table fields. `gmc_v12_0.c` selects `mmhub_v4_2_0_funcs`. XCP code may use `mmhub_v4_2_0_xcp_funcs` even though the matching header in this subset only declares the function table.

## Risks

Multi-instance code makes mask correctness critical; missing an AID leaves a hub uninitialized, while a bad mask writes nonexistent instances. `hub->vm_cntx_cntl = tmp` after nested loops stores only the final hub's final VMID control. Fault status has a TODO noting important fields moved to HI32, so current logging can omit newer critical fault details. Header/API mismatch around `mmhub_v4_2_0_xcp_funcs` should be checked against external declarations. XGMI limits are fixed at four nodes.

## Test Signals

Test on single- and multi-AID devices, with and without `pdb0_bo`, verifying VMID0 translations, GPUVM workloads, and per-instance invalidation. Exercise XCP suspend/resume with partial masks. Validate XGMI info on CPU-connected A+A systems, SR-IOV VF skip paths, MMHUB fault logging, retry-fault interrupts, and MC MGCG/LS toggling on instance 0.
