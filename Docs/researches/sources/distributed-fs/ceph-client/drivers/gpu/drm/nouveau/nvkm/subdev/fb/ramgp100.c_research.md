<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp100.c

## Purpose
GP100 RAM wrapper for the nouveau framebuffer subsystem. It detects or constructs VRAM information for a specific GPU family and connects that family to common RAM allocator/reclocking helpers.

## Important APIs, Types, And Functions
`gp100_ram_init()` runs RAMMAP init scripts selected around `0x9a065c`, `gp100_ram_probe_fbp()` reads HBM partition size, and `gp100_ram_new()` reuses GF100 construction with GP100 init only.

## Control Flow
The wrapper is entered from the owning framebuffer function table's `ram_new` hook. It reads generation-specific size, type, partition, FBP, or stolen-memory registers as needed, then delegates to `nvkm_ram_new_()`, `nv04_ram_func`, `nv40_ram_new_()`, `nv50_ram_ctor()`, `gf100_ram_ctor()`, or `gk104_ram_new_()` depending on the family.

## State And Persistence
Persistent state is stored in `struct nvkm_ram`: memory type, size, partition/topology metadata, allocator ranges, and any generation function table. Hardware register state is only read here unless the file also supplies init hooks.

## Dependencies And Integration Points
Depends on common RAM constructors in `ram.c`, private declarations in `ram.h`, MMIO or PCI config register access, and the matching framebuffer wrapper file.

## Risks
HBM init scripts and address registers are generation-specific; bad script selection can leave memory controller partially initialized. Risks center on hardware register sequencing, BIOS table interpretation, disabled-partition masks, and generation-specific function-table wiring. Most failures surface only on matching GPU generations, so compile coverage is necessary but not sufficient.

## Test Signals
Probe logs showing expected RAM size/type/topology, successful VRAM allocator initialization, and GPU-family boot tests are the main signals. Reclock-capable variants also need memory-clock transition and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramgp100.c -->
