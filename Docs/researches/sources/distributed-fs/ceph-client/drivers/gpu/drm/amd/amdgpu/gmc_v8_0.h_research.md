# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.h

## Purpose
`gmc_v8_0.h` declares the GMC v8 IP block versions exposed by the VI memory-controller implementation.

## Important APIs, Types, And Functions
The header exports `gmc_v8_0_ip_block`, `gmc_v8_1_ip_block`, and `gmc_v8_5_ip_block`, all `const struct amdgpu_ip_block_version`. The declarations let ASIC code select the correct minor version while sharing the implementation in `gmc_v8_0.c`.

## Control Flow, State, Dependencies, And Risks
There is no executable flow or state. The only dependency is the AMDGPU IP block type definition from broader headers. Risk is limited to declaration/definition drift, caught by build and link coverage. Runtime test signals are successful VI-family probe and IP block callback dispatch.
