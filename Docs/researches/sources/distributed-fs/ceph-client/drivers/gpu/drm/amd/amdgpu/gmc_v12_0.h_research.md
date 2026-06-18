# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_0.h

## Purpose
This header declares the GMC v12 IP functions and IP-block descriptor.

## Important APIs, Types, and Functions
It exports `gmc_v12_0_ip_funcs` and `gmc_v12_0_ip_block`. These are the registration handles that expose GMC v12 lifecycle callbacks to the AMDGPU IP-block framework.

## Control Flow and State
The header is declaration-only. The implementation handles generation dispatch for v12.0/v12.1, VM/GART setup, IRQ handling, PDB0 allocation, and power management.

## Dependencies and Integration Points
Including code must have AMDGPU IP framework types in scope. ASIC setup code uses the exported IP-block descriptor to register GMC v12 support.

## Risks and Test Signals
Compile/link coverage catches header drift. Runtime validation belongs to `gmc_v12_0.c`: GC 12 boot, 12.1 helper dispatch, VM faults, GART/PDB0, and reset/resume.
