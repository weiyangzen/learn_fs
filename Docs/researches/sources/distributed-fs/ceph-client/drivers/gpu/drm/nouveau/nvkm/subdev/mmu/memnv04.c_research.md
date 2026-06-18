# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/memnv04.c

## Purpose
Implements legacy NV04 VRAM allocation and direct BAR1 mapping.

## Important APIs, Types, and Functions
`nv04_mem_new` parses legacy NVIF args, chooses NORMAL or NOMAP VRAM heap based on mappability, and calls `nvkm_ram_get`. `nv04_mem_map` returns BAR1 framebuffer resource address plus `nvkm_memory_addr`.

## Control Flow, State, and Persistence
Mapping does not allocate a VMA; it returns `ERR_PTR(-ENODEV)` for `pvma`, indicating direct fixed BAR1 access. Allocation persists as framebuffer RAM memory.

## Dependencies and Integration Points
Depends on device BAR1 resource callbacks, FB RAM allocator, and NV04 memory/VMM classes.

## Risks and Test Signals
Risks include direct BAR1 address assumptions, NOMAP heap mistakes, and no VMA cleanup path. Test legacy VRAM allocation, user mapping, BAR1 resource size/offset, AGP/PCI variants, and unmappable memory rejection.
