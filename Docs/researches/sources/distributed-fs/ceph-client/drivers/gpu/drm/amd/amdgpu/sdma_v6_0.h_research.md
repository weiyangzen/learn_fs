# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.h Research

## Purpose
`sdma_v6_0.h` declares the public symbols exported by the SDMA 6.0 implementation so AMDGPU ASIC and IP assembly code can reference the SDMA 6.0 function table and block descriptor.

## Important APIs, Types, And Functions
The header declares `extern const struct amd_ip_funcs sdma_v6_0_ip_funcs;` and `extern const struct amdgpu_ip_block_version sdma_v6_0_ip_block;`. Unlike the SDMA 5.x headers in this group, it exposes both the raw IP function table and the block-version wrapper.

## Control Flow
The header has no runtime control flow. Its include guard prevents duplicate declarations, and consumers use the symbols during static IP block registration or other compile-time linkage.

## State, Persistence, And Dependencies
There is no mutable state. The declarations depend on AMDGPU core definitions for `struct amd_ip_funcs` and `struct amdgpu_ip_block_version`. Runtime state is owned by `sdma_v6_0.c`.

## Integration Points
The `sdma_v6_0_ip_block` symbol integrates SDMA 6.0 into normal AMDGPU block enumeration. The separately declared `sdma_v6_0_ip_funcs` allows code to reference the function table directly when a full block-version wrapper is not the desired interface.

## Risks
Exporting the function table as well as the block descriptor creates a slightly wider linkage surface than the 5.x headers; external users can couple to the function table identity. Any signature/type mismatch with the implementation fails at build time.

## Test Signals
Compile/link success, correct IP table registration, and runtime invocation of SDMA 6.0 lifecycle methods through the selected descriptor are the main validation signals.
