# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.h

## Purpose
`amdgpu_gmc.h` defines the shared GMC, VM hub, retry-fault, memory-partition, and aperture state used by AMDGPU memory-management code. It is the contract between common GMC helpers, VM code, ASIC-specific hub implementations, TTM/GART, RAS, XGMI, and partition-management logic.

## Important APIs, types, and functions
Important definitions include VA hole macros, retry fault ring/hash sizing, `enum amdgpu_memory_partition`, `struct amdgpu_gmc_fault`, `struct amdgpu_vmhub_funcs`, `struct amdgpu_vmhub`, `struct amdgpu_gmc_funcs`, `struct amdgpu_mem_partition_info`, `struct amdgpu_gmc_memrange`, `enum amdgpu_gart_placement`, and the large `struct amdgpu_gmc`. Macros dispatch VM PTE/PDE and TLB packet hooks through `gmc_funcs`. Function prototypes expose aperture placement, PDB0, VM fault filtering, TLB flushing, TMZ/noretry selection, sysfs, NPS partition, and VRAM info helpers.

## Control flow
The header does not execute by itself. It defines function pointers called by common code when flushing TLBs, emitting VM packets, querying/requesting memory partition mode, and checking reset-on-init requirements. Its inline `amdgpu_gmc_vram_full_visible()` and sign-extension macro are used by memory placement and user-visible reporting paths.

## State and persistence behavior
`struct amdgpu_gmc` stores all live MC state: CPU BAR aperture, GPU VRAM/GART/AGP apertures, VRAM sizes/type/vendor, firmware metadata, VM fault IRQ state, page-fault filter ring/hash, TMZ/no-retry flags, memory partition arrays, XGMI state, PDB0 BO, MALL fields, mode2 restore registers, and TLB flush quirk flags. This is runtime state reconstructed from firmware, discovery tables, module parameters, and hardware registers.

## Dependencies and integration points
The header depends on AMDGPU IRQ, XGMI, RAS, firmware, VM, BO, and ring types. It integrates with TTM/GART allocation, VM page-table programming, IH fault processing, RAS reporting, PSP/NBIO partition switching, ACPI NUMA discovery, and generation-specific GMC implementations.

## Risks and edge cases
The fault ring stores timestamps in 48-bit bitfields and relies on wrap-aware comparison. Aperture fields have subtly different CPU, local GPU, hive FB, GART, and AGP meanings. `AMDGPU_ALL_NPS_MASK` uses mode enum values directly as bit positions, while some validation code uses `mode - 1`; edits need care. Function pointer macros do not guard against null hooks. Mode2 register caches must stay aligned with actual hardware save/restore needs.

## Test signals
Compile coverage across GC/MMHUB generations, VM fault injection, XGMI hive bring-up, NPS mode query/request, PDB0/sysvm tests, TLB flush tests, RAS registration, visible VRAM reporting, and mode2 reset coverage are the primary signals.
