# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.h

## Purpose
Declares the SDMA v4.0 IP function table and IP block descriptor for use by AMDGPU IP discovery and registration code.

## APIs, Types, And Functions
The header exports `extern const struct amd_ip_funcs sdma_v4_0_ip_funcs;` and `extern const struct amdgpu_ip_block_version sdma_v4_0_ip_block;`. It adds no local types, packet helpers, register definitions, or inline logic.

## Control Flow
No control flow exists in the header. Runtime behavior is selected when other code binds `sdma_v4_0_ip_block` or directly refers to `sdma_v4_0_ip_funcs`.

## State And Persistence
The header is stateless. Persistent SDMA state is owned by `struct amdgpu_device` and initialized by `sdma_v4_0.c`.

## Dependencies And Integration
It assumes declarations for `struct amd_ip_funcs` and `struct amdgpu_ip_block_version` are visible to the includer. It serves as the public C interface between IP discovery code and the SDMA v4.0 implementation.

## Risks And Test Signals
Risk is limited to missing symbol definitions or ABI drift with the implementation. Build/link coverage and successful SDMA v4.0 IP registration are the relevant signals.
