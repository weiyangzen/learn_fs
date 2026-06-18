# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.h

## Purpose
This header declares the GMC v11 IP functions and IP-block descriptor.

## Important APIs, Types, and Functions
It exports `gmc_v11_0_ip_funcs` and `gmc_v11_0_ip_block`. These connect the implementation to the AMDGPU IP-block framework for GC 11 devices.

## Control Flow and State
The header is declaration-only. The implementation manages VM/GART/RAS/IRQ lifecycle, MMHUB/GFXHUB function selection, memory placement, and power management.

## Dependencies and Integration Points
Including code needs AMDGPU IP framework type declarations. The declarations are consumed by ASIC setup paths that register the GMC v11 block.

## Risks and Test Signals
Compile/link coverage validates header correctness. Runtime testing should exercise the corresponding IP-block lifecycle on GC 11 devices, including page faults, KFD, GART, reset, and clock gating.
