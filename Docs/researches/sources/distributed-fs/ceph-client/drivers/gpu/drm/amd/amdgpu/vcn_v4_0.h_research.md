# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0.h

## Purpose

This header declares the VCN 4.0 IP block descriptor and the sub-block enumeration used by VCN 4.0 RAS poison status code. It is the small public interface for `vcn_v4_0.c`.

## Important APIs, Types, And Functions

`enum amdgpu_vcn_v4_0_sub_block` defines `AMDGPU_VCN_V4_0_VCPU_VCODEC` and `AMDGPU_VCN_V4_0_MAX_SUB_BLOCK`. The implementation uses these values when iterating sub-blocks in poison status queries. `extern const struct amdgpu_ip_block_version vcn_v4_0_ip_block;` exposes the VCN 4.0 lifecycle descriptor. No functions are defined in the header.

## Control Flow

The enum constrains loops in the implementation that call `vcn_v4_0_query_poison_by_instance()` for every VCN instance/sub-block pair. The IP block descriptor declaration is consumed by ASIC discovery/registration code, which selects this VCN generation and then calls the function table defined in `vcn_v4_0.c`.

## State And Persistence

The header stores no state. It defines compile-time constants for sub-block IDs and declares the singleton block descriptor. Persistent state is managed by `adev->vcn`, firmware shared memory, IRQ sources, and RAS structures in the implementation.

## Dependencies And Integration Points

The header depends on external visibility of `struct amdgpu_ip_block_version`. Its enum values are part of the local contract between the VCN 4.0 implementation and RAS poison status handling. The declaration integrates with the AMDGPU IP block table.

## Risks

Adding new RAS sub-blocks requires updating both this enum and the switch in `vcn_v4_0_query_poison_by_instance()`. If `MAX_SUB_BLOCK` becomes inconsistent, poison polling may skip registers or read unsupported sub-blocks. Symbol declaration drift for `vcn_v4_0_ip_block` would break build/link integration.

## Test Signals

Build/link coverage verifies the exported descriptor declaration. Runtime RAS testing should confirm that `AMDGPU_VCN_V4_0_MAX_SUB_BLOCK` bounds exactly the implemented poison-status sub-blocks and that VCN 4.0 hardware selects `vcn_v4_0_ip_block`.
