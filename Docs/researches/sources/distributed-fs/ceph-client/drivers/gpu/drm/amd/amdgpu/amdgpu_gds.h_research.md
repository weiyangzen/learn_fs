# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gds.h

## Purpose
`amdgpu_gds.h` defines small structures describing Global Data Share resource sizes and register offsets for GDS, GWS, and OA resources.

## Important APIs, types, and functions
It forward declares `struct amdgpu_ring` and `struct amdgpu_bo`, defines `struct amdgpu_gds` with GDS/GWS/OA sizes and compute max wave ID, and defines `struct amdgpu_gds_reg_offset` with register offsets for memory base, memory size, GWS, and OA.

## Control flow
The header has no executable control flow. It provides shared data layouts consumed by command submission, resource allocation, and ASIC programming paths elsewhere in AMDGPU.

## State and persistence behavior
Instances are runtime configuration state. They describe hardware resource capacities or register offsets and are not persisted.

## Dependencies and integration points
It integrates AMDGPU GDS resource accounting with ring/BO-related code via forward declarations while avoiding heavy includes.

## Risks and edge cases
The structures are compact and rely on callers to interpret units consistently. ASIC-specific register offsets must match hardware definitions or GDS/GWS/OA programming will target the wrong registers.

## Test signals
Build coverage, GDS/GWS/OA command submission, resource allocation limits, and ASIC register programming tests validate this header.
