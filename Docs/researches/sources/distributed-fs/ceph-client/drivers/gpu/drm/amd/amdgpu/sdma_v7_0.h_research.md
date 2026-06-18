# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_0.h

## Purpose

`sdma_v7_0.h` is the public header for the SDMA 7.0 AMDGPU IP block implementation. It provides the include guard and exposes the two global descriptors that other AMDGPU ASIC/IP discovery code needs to register or reference the SDMA 7.0 block.

## Important APIs, types, and functions

- `extern const struct amd_ip_funcs sdma_v7_0_ip_funcs;` exports the lifecycle callback table implemented in `sdma_v7_0.c`.
- `extern const struct amdgpu_ip_block_version sdma_v7_0_ip_block;` exports the IP block metadata, including block type and version.

The header deliberately does not expose implementation-private helpers such as ring emitters, reset functions, register offset helpers, or IRQ handlers. Those remain `static` inside `sdma_v7_0.c`.

## Control flow

There is no runtime control flow in this header. Its role is compile-time linkage: a translation unit includes it to gain declarations for the SDMA 7.0 IP function table and block-version record. Runtime control enters the implementation through the function pointers stored in `sdma_v7_0_ip_funcs`.

## State and persistence behavior

The header declares global const objects but owns no state. State is created and managed in the C implementation through `adev->sdma`, rings, firmware BOs, IRQ sources, and IP dump buffers.

## Dependencies and integration points

The declarations depend on `struct amd_ip_funcs` and `struct amdgpu_ip_block_version` being visible from surrounding AMDGPU headers before or alongside this header. It integrates with AMDGPU IP registration code that selects an IP block descriptor based on discovered hardware version.

## Risks and edge cases

- The public ABI surface is intentionally tiny; adding private helpers here would increase coupling.
- The include guard must remain unique to avoid collisions with other SDMA version headers.
- The exported declarations must stay synchronized with definitions in `sdma_v7_0.c`; mismatches produce build or link failures.

## Test signals

Build coverage is the primary signal. A successful kernel/module build verifies that the exported symbols match their definitions and that include ordering supplies compatible structure declarations. Runtime validation belongs to `sdma_v7_0.c` through IP block initialization, ring tests, reset tests, and interrupt handling.
