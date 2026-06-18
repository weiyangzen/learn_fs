<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv49.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv49.c

## Purpose
NV49 RAM detector for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`nv49_ram_new()` decodes type from `0x100914`, delegates to NV40 reclocking support, and sets partition count.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
Unsupported type code 3 remains unknown; partition count still comes from legacy register bits. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv49.c -->
