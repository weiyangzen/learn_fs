# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v4_0_3.h

## Purpose

This header declares the VCN 4.0.3 IP block, its RAS sub-block IDs, and generation-specific ring emit helper APIs. Unlike the earlier headers in this work item, it exposes helper functions because other AMDGPU code needs VCN 4.0.3-specific register wait/write, VM flush, and HDP flush behavior.

## Important APIs, Types, And Functions

`enum amdgpu_vcn_v4_0_3_sub_block` defines `AMDGPU_VCN_V4_0_3_VCPU_VCODEC` and `AMDGPU_VCN_V4_0_3_MAX_SUB_BLOCK` for RAS poison scanning. `extern const struct amdgpu_ip_block_version vcn_v4_0_3_ip_block;` exposes the IP descriptor. The declared helpers are `vcn_v4_0_3_enc_ring_emit_reg_wait()`, `vcn_v4_0_3_enc_ring_emit_wreg()`, `vcn_v4_0_3_enc_ring_emit_vm_flush()`, and `vcn_v4_0_3_ring_emit_hdp_flush()`.

## Control Flow

AMDGPU ASIC registration selects `vcn_v4_0_3_ip_block`, whose function table is implemented in `vcn_v4_0_3.c`. Ring code can call the declared emit helpers through the VCN 4.0.3 `amdgpu_ring_funcs` table. VM flush emits a GMC TLB flush and waits on the page table base register; register wait/write helpers normalize register offsets when RRMT is not enabled; HDP flush intentionally emits no VCN packet as a workaround for RRMT behavior.

## State And Persistence

The header itself stores no mutable state. Its helper declarations operate on `struct amdgpu_ring`, whose `adev`, `vm_hub`, `me`, write pointer, and runtime VCN capabilities determine emitted packet contents. RAS enum values are compile-time constants used by poison query loops.

## Dependencies And Integration Points

The header depends on AMDGPU type declarations for `struct amdgpu_ip_block_version` and `struct amdgpu_ring`, plus integer typedefs such as `uint32_t` and `uint64_t` from kernel headers. It is integrated by the VCN 4.0.3 implementation and any code that needs these generation-specific ring operations.

## Risks

Because helpers are externally visible, their ABI must remain consistent with ring function expectations. VM flush callers depend on the wait register/mask semantics implemented in the `.c` file. HDP flush is a no-op by design; callers must tolerate that VCN 4.0.3 does not perform HDP flush through the VCN ring. Adding sub-block enum values requires matching implementation updates.

## Test Signals

Build/link tests should verify all declared helpers are defined exactly once and consumed by the VCN 4.0.3 ring function table. Runtime signals include successful VM flush waits with normalized register offsets, absence of VCN HDP flush packet failures under RRMT, and RAS poison scans bounded by `AMDGPU_VCN_V4_0_3_MAX_SUB_BLOCK`.
