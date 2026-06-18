# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.h

## Purpose
`gmc_v6_0.h` is the public declaration header for the GMC v6 IP block. It contains only the include guard and the external `gmc_v6_0_ip_block` declaration used by AMDGPU device-discovery and ASIC setup code to bind Southern Islands-era memory-controller support into the common IP block lifecycle.

## Important APIs, Types, And Functions
The only exported symbol is `extern const struct amdgpu_ip_block_version gmc_v6_0_ip_block;`. The type comes from the wider AMDGPU IP framework and carries the block type, version tuple, and callback table for early/software/hardware init, suspend/resume, reset, and power management.

## Control Flow And Integration
This header has no executable control flow. Its integration point is compile-time inclusion by ASIC tables or driver initialization files that need to reference the v6 GMC IP block object without seeing the implementation. The actual behavior is provided by a matching `gmc_v6_0.c` elsewhere in the tree.

## State, Persistence, And Dependencies
The file declares no state and persists nothing. It depends on consumers including an AMDGPU core header that defines `struct amdgpu_ip_block_version` before using the declaration.

## Risks And Test Signals
The risk surface is symbol-contract drift: if the implementation renames or drops `gmc_v6_0_ip_block`, builds fail at link time. Useful test signals are allmodconfig or AMDGPU build coverage for SI support and successful probe paths on v6 hardware.
