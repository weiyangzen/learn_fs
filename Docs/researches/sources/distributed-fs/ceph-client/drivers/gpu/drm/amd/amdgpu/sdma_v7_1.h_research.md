# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v7_1.h

## Purpose

`sdma_v7_1.h` is the public header for the SDMA 7.1 AMDGPU IP block. It exposes the standard IP lifecycle descriptors plus the XCP-specific function table used to suspend and resume selected SDMA instance masks on partitioned devices.

## Important APIs, types, and functions

- `extern const struct amd_ip_funcs sdma_v7_1_ip_funcs;` declares the lifecycle callback table implemented in `sdma_v7_1.c`.
- `extern const struct amdgpu_ip_block_version sdma_v7_1_ip_block;` declares the SDMA 7.1 IP block metadata.
- `extern struct amdgpu_xcp_ip_funcs sdma_v7_1_xcp_funcs;` declares the XCP suspend/resume hook table implemented at the end of `sdma_v7_1.c`.

The header exposes no private ring, register, firmware, IRQ, or packet-emission helpers. Those remain static to the implementation file.

## Control flow

There is no executable control flow in the header. Consumers include it to wire SDMA 7.1 into device/IP discovery and, when relevant, XCP partition management. Runtime control enters the implementation through `sdma_v7_1_ip_funcs` for normal device lifecycle and through `sdma_v7_1_xcp_funcs` for partition-scoped suspend/resume.

## State and persistence behavior

The header owns no state. It declares global descriptor objects that point to implementation functions. Runtime state is held in the C file through `adev->sdma` instances, rings, firmware BOs, XCC IDs, reset-mask sysfs state, and IP dump buffers.

## Dependencies and integration points

The declarations depend on AMDGPU structure definitions for `struct amd_ip_funcs`, `struct amdgpu_ip_block_version`, and `struct amdgpu_xcp_ip_funcs`. The XCP declaration is the key difference from `sdma_v7_0.h`; it lets partition-aware AMDGPU code call SDMA 7.1 instance-mask suspend/resume without exposing lower-level helpers.

## Risks and edge cases

- The XCP function table is non-const in this header and implementation, so accidental mutation by external code would affect partition lifecycle behavior.
- Include ordering must provide the struct definitions or forward declarations expected by these extern declarations.
- The header must stay synchronized with implementation symbol names and storage qualifiers.
- Keeping the public surface small is important because the SDMA 7.1 implementation has many hardware-specific assumptions around XCC and instance masks.

## Test signals

Build coverage verifies symbol declaration/definition consistency and correct include dependencies. Runtime validation is indirect: successful IP registration, normal SDMA lifecycle tests, and XCP suspend/resume tests prove that the exported descriptors are correctly consumed by the rest of AMDGPU.
