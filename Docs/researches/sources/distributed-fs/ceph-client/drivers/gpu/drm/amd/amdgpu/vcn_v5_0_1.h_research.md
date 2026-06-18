<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.h

## Purpose
Declares the VCN 5.0.1 IP block and generation-specific constants needed by the implementation, including the RRMT control register and RAS sub-block identifiers.

## Important APIs, Types, And Functions
Defines `regVCN_RRMT_CNTL` and `regVCN_RRMT_CNTL_BASE_IDX`, which are used to detect RRMT capability in VCN 5.0.1/5.0.2 paths. `enum amdgpu_vcn_v5_0_1_sub_block` currently contains `AMDGPU_VCN_V5_0_1_VCPU_VCODEC` plus a `MAX_SUB_BLOCK` sentinel for RAS iteration. The external symbol is `vcn_v5_0_1_ip_block`.

## Control Flow
No executable flow exists in the header. Runtime behavior occurs when VCN implementation code reads the RRMT register or iterates the enum-defined sub-block range in poison-status queries.

## State And Persistence
The header contributes constants only. Register reads using these constants may set persistent capability bits such as `AMDGPU_VCN_CAPS(RRMT_ENABLED)` in `adev->vcn.caps`, but that state is held outside the header.

## Dependencies And Integration Points
Assumes AMDGPU core declarations for the IP block type. It is included by both `vcn_v5_0_1.c` and `vcn_v5_0_2.c`, so the RRMT definitions are shared across nearby VCN revisions.

## Risks And Test Signals
Wrong RRMT register metadata can mis-detect firmware/hardware capability. RAS enum drift can cause missing sub-block scans. Build success validates declarations; runtime signals are RRMT capability bits and poison query coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v5_0_1.h -->
