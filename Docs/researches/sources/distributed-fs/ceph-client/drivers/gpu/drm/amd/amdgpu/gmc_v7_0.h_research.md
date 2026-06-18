# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.h

## Purpose
`gmc_v7_0.h` declares the public GMC v7 IP block objects for AMDGPU CIK-era memory-controller integration.

## Important APIs, Types, And Functions
It exports `gmc_v7_0_ip_block` and `gmc_v7_4_ip_block`, both typed as `const struct amdgpu_ip_block_version`. These declarations allow ASIC setup code to bind either GMC minor version to the same implementation callback table in `gmc_v7_0.c`.

## Control Flow, State, And Dependencies
The header has no control flow or local state. It relies on a prior declaration of `struct amdgpu_ip_block_version` from AMDGPU core headers and is consumed by device/IP discovery code.

## Integration, Risks, And Test Signals
The file is an ABI-like internal compile contract. Link/build failures are the primary signal for declaration drift. Runtime validation belongs to the implementation: CIK probe should select the proper v7.0 or v7.4 IP block and execute the common GMC lifecycle callbacks.
