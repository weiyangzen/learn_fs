# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gart.h

## Purpose
`amdgpu_gart.h` defines the AMDGPU GART page-size constants, `struct amdgpu_gart`, and the common GART allocation, mapping, unmapping, and TLB invalidation API.

## Important APIs, types, and functions
It defines 4 KiB GPU page constants, `AMDGPU_GPU_PAGE_ALIGN()`, `AMDGPU_GPU_PAGES_IN_CPU_PAGE`, and `struct amdgpu_gart` with the table BO, CPU pointer, page counts, table size, and default PTE flags. Prototypes cover RAM/VRAM table allocation/free, initialization, dummy page finalization, map/bind/unbind, gfx9 MQD mapping, VRAM range mapping, and TLB invalidation.

## Control flow
The header has no executable flow but defines the sequence used by ASIC code: initialize the GART, allocate a table in the appropriate memory domain, bind/unbind pages as BOs move, invalidate TLBs after changes, and free resources during teardown.

## State and persistence behavior
`struct amdgpu_gart` is runtime device state attached to `struct amdgpu_device`. It describes hardware-visible page-table memory, not durable storage.

## Dependencies and integration points
It depends on Linux integer types, DMA addresses via prototypes, AMDGPU device and BO forward declarations, and GMC/PTE implementation in the C file and ASIC-specific code.

## Risks and edge cases
The macro `AMDGPU_GPU_PAGES_IN_CPU_PAGE` assumes CPU pages are an integer multiple of 4 KiB; the implementation rejects smaller CPU pages. Callers must pass offsets and sizes aligned to GPU page granularity and correct PTE flags for the memory type.

## Test signals
Build coverage, GART page-count logging, BO mapping/unmapping tests, and ASIC-specific GART bring-up validate the header contract.
