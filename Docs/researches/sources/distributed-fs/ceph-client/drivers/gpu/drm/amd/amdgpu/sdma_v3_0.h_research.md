# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.h

## Purpose
Declares the public SDMA v3 IP block descriptors used by the AMDGPU device discovery and IP block registration code. It is the header-level handoff for SDMA v3.0 and v3.1 support implemented in `sdma_v3_0.c`.

## APIs, Types, And Functions
The header exports `extern const struct amdgpu_ip_block_version sdma_v3_0_ip_block;` and `sdma_v3_1_ip_block;`. It introduces no new types, inline helpers, macros, or functions beyond the include guard.

## Control Flow
There is no runtime control flow in the header. Consumers include it so platform/IP discovery code can reference the correct `amdgpu_ip_block_version` object and therefore bind the SDMA v3 lifecycle callbacks.

## State And Persistence
The declarations themselves are stateless. The actual persistent driver state is in the `amdgpu_device` SDMA fields initialized by the implementation file.

## Dependencies And Integration
It relies on the including translation unit already knowing `struct amdgpu_ip_block_version`. Integration is intentionally narrow: it exposes only the block descriptors, keeping all register and packet details private to the implementation.

## Risks And Test Signals
Risk is limited to declaration/definition drift or missing inclusion where IP discovery expects these symbols. Build/link success is the main test signal; runtime validation comes from the v3.0/v3.1 IP block registration and ring bring-up.
