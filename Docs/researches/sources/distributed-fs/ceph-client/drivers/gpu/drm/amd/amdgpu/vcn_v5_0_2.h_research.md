<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.h

## Purpose
Declares the VCN 5.0.2 IP block object. This is the source-level hook that lets ASIC/IP discovery tables select the VCN 5.0.2 implementation.

## Important APIs, Types, And Functions
The single public declaration is `extern const struct amdgpu_ip_block_version vcn_v5_0_2_ip_block`, defined in `vcn_v5_0_2.c`.

## Control Flow
The header has no runtime control flow. When an ASIC table references `vcn_v5_0_2_ip_block`, the AMDGPU IP framework invokes the lifecycle function table bound to that object.

## State And Persistence
No state is stored here. Runtime state is held by the IP block object and the per-device `adev->vcn` structures initialized by the C file.

## Dependencies And Integration Points
Requires the core AMDGPU IP block type declaration to be visible to consumers. It integrates only through symbol linkage with the implementation and ASIC selection code.

## Risks And Test Signals
Risk is limited to declaration/symbol mismatch or incorrect ASIC table selection. Build success catches declaration issues; runtime probe, VCN ring tests, and interrupt delivery validate the chosen implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_2.h -->
