<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.h

## Purpose
Declares the public interface for the VCN 4.0.5 implementation. It gives other AMDGPU IP discovery and RAS code a stable symbol for the VCN 4.0.5 IP block and names the RAS-queryable VCN sub-blocks for this generation.

## Important APIs, Types, And Functions
`enum amdgpu_vcn_v4_0_5_sub_block` currently defines `AMDGPU_VCN_V4_0_5_VCPU_VCODEC` and the `AMDGPU_VCN_V4_0_5_MAX_SUB_BLOCK` sentinel. `extern const struct amdgpu_ip_block_version vcn_v4_0_5_ip_block` exposes the implementation object defined in `vcn_v4_0_5.c`.

## Control Flow
This header has no executable control flow. At compile time, device-family tables can reference `vcn_v4_0_5_ip_block`; at runtime, the AMDGPU IP framework invokes the function table attached to that object. The enum is intended for bounded iteration or switch statements over VCN RAS sub-blocks.

## State And Persistence
No state is stored by the header. The enum values become ABI-like constants within the driver build, and the external IP block symbol resolves to the lifecycle state machine in the C file.

## Dependencies And Integration Points
The header assumes consumers have the definition of `struct amdgpu_ip_block_version` from AMDGPU core headers. It integrates with the source file that defines the object and with ASIC tables that select the VCN implementation.

## Risks And Test Signals
The main risk is enum drift: RAS/status code must update `MAX_SUB_BLOCK` if new sub-blocks are added. Build coverage is the primary signal: missing `amdgpu_ip_block_version` declarations or mismatched symbol names fail compilation. Runtime signal comes indirectly when the selected VCN IP block probes and initializes successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.h -->
