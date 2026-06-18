# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vcn_v3_0.h

## Purpose

This header is the public declaration surface for the VCN 3.0 AMDGPU IP block implementation. It lets the AMDGPU device/IP discovery code reference the VCN 3.0 block without exposing internal register programming or ring callbacks.

## Important APIs, Types, And Functions

The only API is `extern const struct amdgpu_ip_block_version vcn_v3_0_ip_block;`. That object is defined in `vcn_v3_0.c` and contains the IP block type, version tuple `3.0.0`, and the `amd_ip_funcs` table for lifecycle operations. The header has no local structs, helper functions, inline functions, or macros beyond its include guard.

## Control Flow

The header participates at compile/link time. Platform code includes it, selects `vcn_v3_0_ip_block` for matching hardware, and the function table in the `.c` file drives runtime init, suspend/resume, reset, power gating, and interrupt behavior. No runtime control flow is implemented in the header itself.

## State And Persistence

No state is stored here. The declaration points consumers to the singleton IP block descriptor defined by the implementation file. Persistent VCN state lives in `struct amdgpu_device`, `struct amdgpu_vcn`, and `struct amdgpu_vcn_inst`, not in this header.

## Dependencies And Integration Points

The declaration assumes `struct amdgpu_ip_block_version` is visible to including translation units through AMDGPU headers included before or around this header. The main integration point is the AMDGPU IP block table used during ASIC initialization.

## Risks

The risk surface is intentionally small. Renaming or removing the exported symbol without updating ASIC registration code would produce link or probe failures. Since the header does not include the type definition itself, include order must continue to provide `struct amdgpu_ip_block_version`.

## Test Signals

Build coverage is the key signal: objects that include this header must compile and link against `vcn_v3_0_ip_block`. Runtime confirmation comes indirectly when VCN 3.0 devices bind to the correct IP block and execute the lifecycle functions in `vcn_v3_0.c`.
