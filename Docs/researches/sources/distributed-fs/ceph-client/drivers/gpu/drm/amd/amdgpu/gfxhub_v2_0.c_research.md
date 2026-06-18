# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c

## Purpose
This file implements the GFXHUB 2.0 VM hub backend for Navi 1x-era GC 10.1 devices. It programs the GCVM/GCMC register set, exposes fault-status decoding, and provides callback operations used by GMC v10.

## Important APIs, Types, and Functions
The public table is `gfxhub_v2_0_funcs`. Its callbacks read FB location and MC FB offset, set VM page-table bases, enable/disable the GART, set fault-default behavior, and initialize `adev->vmhub[AMDGPU_GFXHUB(0)]`. A private `amdgpu_vmhub_funcs` table supplies `print_l2_protection_fault_status` and `get_invalidate_req`. `gfxhub_client_ids[]` maps GCVM fault client IDs to readable names.

## Control Flow and State
`init()` writes register offsets, context/invalidate strides, fault interrupt masks, `sdma_invalidation_workaround`, and the VM hub function table into `adev->vmhub`. GART enable programs VMID0 page-table base/range from `adev->gart.bo`, system and AGP apertures, scratch/default fault addresses, L1 TLB controls, L2 cache and fragment defaults, context0, disabled identity aperture, contexts 1-15, and invalidate ranges for 18 engines. VMID user contexts use `adev->vm_manager.num_level`, `block_size - 9`, and `max_pfn`. Fault default toggling updates every protection-fault default bit and sets crash-on-fault bits when disabled.

## Dependencies and Integration Points
The implementation depends on GC 10.1 offset/mask/default headers, `navi10_enum.h`, and SOC15 register helpers. It is selected by `gmc_v10_0_set_gfxhub_funcs()` for older GC 10 variants. GMC TLB flushing calls the VM hub `get_invalidate_req` callback generated here.

## Risks and Test Signals
Risks include off-by-one VMID context programming, stale invalidate ranges, SR-IOV register access, and fault-status interpretation. Test signals include Navi10 boot/resume, GART log line, page-fault logging with decoded CID, VM update workloads, SDMA invalidation behavior, and suspend/resume with VM faults enabled and disabled.
