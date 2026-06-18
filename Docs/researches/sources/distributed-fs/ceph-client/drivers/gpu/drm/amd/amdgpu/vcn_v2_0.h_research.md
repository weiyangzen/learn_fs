# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v2_0.h

## Purpose

`vcn_v2_0.h` exports VCN 2.0 ring packet helpers and the VCN 2.0 IP block descriptor. Later generation files reuse these helpers when their ring command protocol is compatible but their lifecycle, multi-instance, or RAS handling differs.

## Important APIs, Types, And Functions

The header declares decode helpers for start, end, NOP, fence, IB, register wait, VM flush, register write, and ring test. It also declares encode helpers for end, fence, IB, register wait, VM flush, and register write. The descriptor `vcn_v2_0_ip_block` exposes the complete VCN 2.0 IP implementation.

## Control Flow

There is no executable flow in the header. It defines the callable surface used by `vcn_v2_0.c` ring tables and by generation variants such as VCN 2.5 that reuse VCN 2.0 packet emitters.

## State And Persistence

No state is owned here. The declared functions operate on `struct amdgpu_ring`, `struct amdgpu_job`, and `struct amdgpu_ib`, updating ring command streams and hardware-visible write pointers in their implementation.

## Dependencies And Integration Points

Consumers need AMDGPU ring/job/IB type definitions and integer types. The header is an integration point between VCN generation implementations, common AMDGPU ring scheduling, and the ASIC IP block registry.

## Risks And Test Signals

Risk centers on ABI-like drift between the declarations and the implementation or unsafe reuse by a generation whose internal register offsets do not match the v2.0 helper assumptions. Test signals are compile/link coverage for v2.0 and v2.5 users plus runtime ring tests for every helper reused through a ring function table.
