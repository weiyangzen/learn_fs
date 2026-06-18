# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.h

## Purpose
Defines the private VMM data structures, backend descriptor contracts, public internal VMM APIs, PFN encoding, page-size flags, and PTE write helper macros.

## Important APIs, Types, and Functions
Important types are `union nvkm_pte_tracker`, `struct nvkm_vmm_pt`, `struct nvkm_vmm_desc_func`, `struct nvkm_vmm_desc`, `struct nvkm_vmm_page`, `struct nvkm_vmm_func`, and `struct nvkm_vmm_join`. The header declares all common VMM operations and chip-specific constructors from NV04 through GH100.

## Control Flow, State, and Persistence
The header has inline range validation through `nvkm_vmm_in_managed_range` and macro-based PTE iteration/write helpers. Persistent VMM state defined here includes page directory tracking, dual-page-table refcounts, sparse PDE/PTE markers, backend page layouts, and joined instance-memory lists.

## Dependencies and Integration Points
Includes MMU private definitions and `core/memory.h`; consumed by common VMM code, chip-specific VMM implementations, user VMM code, and memory mapping code.

## Risks and Test Signals
Risks include macro side effects, PFN bit encoding drift, descriptor/layout mismatches, and incorrect managed-range checks on overflow. Build all VMM backends, run sparse/PFN/dual-page-size tests, and enable MMU debug tracing for page-table transitions.
