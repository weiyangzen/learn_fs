# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vce_v4_0.h

## Purpose

`vce_v4_0.h` is the public declaration header for the VCE 4.0 AMDGPU IP block implementation. It lets ASIC discovery or IP block assembly code reference the VCE 4.0 block descriptor without exposing the private register programming and ring helper functions from `vce_v4_0.c`.

## Important APIs, Types, And Functions

The single API is `extern const struct amdgpu_ip_block_version vce_v4_0_ip_block;`. The type is provided by AMDGPU core headers included by users of this header, not by this file.

## Control Flow

There is no executable control flow. Inclusion makes the VCE 4.0 IP block descriptor visible to compilation units that select hardware IP versions.

## State And Persistence

The header declares no state and owns no persistence. Runtime state is allocated and managed by the implementation through `adev->vce`.

## Dependencies And Integration Points

The header relies on a prior or transitive declaration of `struct amdgpu_ip_block_version`. Its integration point is the AMDGPU device/IP initialization layer, which can include this header to add VCE 4.0 to an ASIC's IP block list.

## Risks And Test Signals

Risk is limited to declaration drift: if the implementation changes the symbol name or removes the block, users of this header fail to link. Test signals are compile/link coverage for ASIC files that reference `vce_v4_0_ip_block`.
