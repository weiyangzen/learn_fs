# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v1_0.h

## Purpose

`vcn_v1_0.h` exposes the small part of the VCN 1.0 implementation needed by adjacent code: the IP block descriptor and two power-management helpers used around ring submissions.

## Important APIs, Types, And Functions

It declares `vcn_v1_0_ring_end_use()`, `vcn_v1_0_set_pg_for_begin_use()`, and `vcn_v1_0_ip_block`. The helper prototypes operate on `struct amdgpu_ring` and allow related code, especially JPEG v1.0 coordination, to share the VCN 1.0 begin/end-use powergating behavior.

## Control Flow

The header has no executable flow. It enables callers to invoke implementation functions that cancel/reschedule idle work, ungate/gate VCN, and update DPG pause state around submissions.

## State And Persistence

No state is declared here. The implementation manipulates `adev->vcn.inst[0]`, DPG pause state, delayed idle work, and the VCN/JPEG workaround mutex.

## Dependencies And Integration Points

Consumers need AMDGPU ring and IP block type declarations. The header integrates VCN 1.0 with the broader IP block registration path and with any companion block that needs VCN-aware power management.

## Risks And Test Signals

Risks are API drift and incorrect external use of begin/end-use helpers without matching locking expectations. Test signals are compile coverage for VCN/JPEG v1.0 builds and runtime checks that JPEG and VCN submissions do not leave the shared block permanently ungated or gated while work is pending.
