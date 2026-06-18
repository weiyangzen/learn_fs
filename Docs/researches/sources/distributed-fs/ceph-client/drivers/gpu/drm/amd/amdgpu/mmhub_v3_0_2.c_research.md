# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c

## Purpose

`mmhub_v3_0_2.c` implements the MMHUB 3.0.2 function table for GMC v11 devices. It follows the same core GART/VM programming model as v3.0.1 but adapts client IDs and adds explicit SR-IOV VF guards for registers owned by the PF. It initializes the MMHUB VM hub registers, names MMHUB fault clients, programs VMID contexts and invalidation engines, and supplies callbacks used by generic AMDGPU memory-management code.

## Important APIs, Types, And Functions

The exported table is `mmhub_v3_0_2_funcs`. Important functions are `mmhub_v3_0_2_init`, `mmhub_v3_0_2_gart_enable`, `mmhub_v3_0_2_gart_disable`, `mmhub_v3_0_2_set_fault_enable_default`, `mmhub_v3_0_2_setup_vm_pt_regs`, `mmhub_v3_0_2_get_fb_location`, and `mmhub_v3_0_2_get_mc_fb_offset`. The VM hub sub-interface is `mmhub_v3_0_2_vmhub_funcs`, with invalidation-request construction and fault-status printing. `mmhub_client_ids_v3_0_2` maps VMC, DCE, MP, MPIO, HDP, LSDMA, JPEG, VSCH, VCNU, and VCN clients for read/write fault decoding.

## Control Flow

Initialization fills `adev->vmhub[AMDGPU_MMHUB0(0)]` offsets for page-table base registers, invalidation sem/request/ack, context controls, L2 fault status/control, spacing between contexts/engines, VM fault interrupt masks, and `vm_l2_bank_select_reserved_cid2`. GART enable programs VMID0, system apertures, TLB, cache, context0, identity aperture, VMIDs, and invalidation ranges. Several stages return early on `amdgpu_sriov_vf(adev)`: system-aperture high/low programming, L2 cache programming, identity aperture disable, and L2 fault-control writes are skipped because the PF programs them.

## State And Persistence Behavior

Register programming persists until reset, suspend, or explicit `gart_disable`. The function stores register offsets and the last VM context control value in `adev->vmhub`. It updates page-table-base registers from `adev->gart.bo`, and page-table ranges from `adev->gmc` and `adev->vm_manager`. Fault default state is written into `MMVM_L2_PROTECTION_FAULT_CNTL`, but only when not running as a VF. Clock-gating helpers are present but intentionally empty TODOs, so this backend currently does not mutate clock-gating hardware.

## Dependencies And Integration Points

The file depends on generated `mmhub_3_0_2` register headers, `navi10_enum.h`, SOC15 macros, AMDGPU GMC/VM state, and SR-IOV helpers. It is included in the AMDGPU build and selected by `gmc_v11_0.c`. It also integrates with VM fault reporting through `amdgpu_mmhub_client_name` and `amdgpu_mmhub_init_client_info`.

## Risks

The SR-IOV guards are central: missing one can cause VF register access failures, while over-skipping could leave a PF path uninitialized. The no-op clock-gating callbacks can make feature reporting misleading if callers expect `set_clockgating` or `get_clockgating` to reflect actual state. The client map includes sparse indices such as `32+20`; mistakes here affect diagnosis rather than memory translation. As with v3.0.1, VMID loops and invalidation-engine counts are hardware assumptions.

## Test Signals

Probe tests should cover both bare-metal/PF and VF modes. On PF, verify GART enable, fault-default toggling, and MMHUB VM fault naming. On VF, verify no unauthorized writes occur and VM setup still succeeds with PF-owned registers skipped. Regression signals include successful GPUVM workloads, page faults that do not storm under no-retry settings, and build coverage for the exported function table.
