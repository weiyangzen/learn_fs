# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.h

## Purpose
This header declares the GMC v10 IP-function table and IP-block descriptor used to register GC 10 memory-controller support with the AMDGPU IP-block framework.

## Important APIs, Types, and Functions
It exports `gmc_v10_0_ip_funcs` (`struct amd_ip_funcs`) and `gmc_v10_0_ip_block` (`struct amdgpu_ip_block_version`). Callers add the block to the device during ASIC discovery rather than invoking the static implementation functions directly.

## Control Flow and State
No runtime flow exists in the header. The implementation behind the declarations manages lifecycle callbacks such as early/sw/hw init, suspend/resume, idle checks, clock gating, VM/GART setup, and IRQ handling.

## Dependencies and Integration Points
Including files need AMDGPU IP framework type declarations. Integration is with ASIC setup code that registers GMC v10 for applicable devices.

## Risks and Test Signals
Compile/link tests validate declarations. Runtime coverage comes from the `gmc_v10_0.c` lifecycle: boot, GART enable, page faults, ECC IRQs, and power management.
