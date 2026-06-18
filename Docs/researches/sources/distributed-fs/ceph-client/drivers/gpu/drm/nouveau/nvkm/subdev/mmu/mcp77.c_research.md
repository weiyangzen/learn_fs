# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/mcp77.c

## Purpose
Defines MCP77 integrated-chipset MMU capabilities using NV50 memory classes with a dedicated VMM constructor and NV50-style PD offset.

## Important APIs, Types, and Functions
`mcp77_mmu` selects 40-bit DMA, NV50 NVIF classes, `nv50_mem_new`, `nv50_mem_map`, `mcp77_vmm_new`, `nv50_mmu_kind`, and `kind_sys=true`. `mcp77_mmu_new` registers it.

## Control Flow, State, and Persistence
Descriptor-only. Base.c turns this into memory types and VMM construction.

## Dependencies and Integration Points
Depends on NV50 memory/kind code and MCP77 VMM layout.

## Risks and Test Signals
Risks include integrated-chipset aperture differences and PD offset mismatch. Test MCP77 user VMM creation, host memory mappings, BAR1 behavior, and kind queries.
