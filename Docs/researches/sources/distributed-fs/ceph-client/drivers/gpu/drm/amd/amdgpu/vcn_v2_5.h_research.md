# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_5.h

## Purpose

`vcn_v2_5.h` declares the VCN 2.5 and VCN 2.6 IP block descriptors and the VCN 2.6 RAS sub-block enumeration used by poison-status handling.

## Important APIs, Types, And Functions

`enum amdgpu_vcn_v2_6_sub_block` currently defines `AMDGPU_VCN_V2_6_VCPU_VCODEC` and `AMDGPU_VCN_V2_6_MAX_SUB_BLOCK`. The exported descriptors are `vcn_v2_5_ip_block` and `vcn_v2_6_ip_block`.

## Control Flow

The header has no executable flow. It makes the IP descriptors and RAS sub-block identifiers available to ASIC/IP selection and RAS code.

## State And Persistence

No state is stored here. Runtime VCN 2.5/2.6 state lives in `adev->vcn` and per-instance structures in the implementation.

## Dependencies And Integration Points

Consumers require `struct amdgpu_ip_block_version`. The enum is coupled to `vcn_v2_6_query_poison_by_instance()` in the implementation, which iterates from zero to `AMDGPU_VCN_V2_6_MAX_SUB_BLOCK`.

## Risks And Test Signals

Risk is mainly enum/implementation drift: adding sub-blocks requires updating poison status reads and tests. Test signals are compile/link coverage for ASIC files referencing the 2.5/2.6 block descriptors and RAS tests that iterate the enum range without missing supported poison sources.
