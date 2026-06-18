# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/fb.h

## Purpose

This header defines the framebuffer/RAM subdevice, including VRAM sizing, memory unlock, tiling/compression tag state, sysmem flush resources, VPR scrubber firmware, RAM heap management, RAM type metadata, and memory clock transition state.

## Important APIs, Types, and Functions

Important contracts include `struct nvkm_fb`, `struct nvkm_fb_tile`, `struct nvkm_ram`, `struct nvkm_ram_data`, `enum nvkm_ram_type`, `struct nvkm_ram_func`, `nvkm_fb_vidmem_size`, `nvkm_fb_mem_unlock`, `nvkm_fb_tile_init`, `nvkm_fb_tile_fini`, `nvkm_fb_tile_prog`, `nvkm_ram_wrap`, and `nvkm_ram_get`, plus framebuffer constructors through GB202.

## Control Flow

Framebuffer constructors probe VRAM/RAM type, initialize heap and compression-tag allocators, set tile regions, and provide memory allocation wrappers. RAM callers allocate from heaps with page/contiguity/backing constraints; memory reclocking calculates, programs, tidies, and records transition state.

## State and Persistence Behavior

The subdevice persists RAM size/type/frequency, VRAM allocator nodes, stolen memory, rank/part masks, mode registers, compression tag heap, tile regions, sysmem flush page, and VPR scrubber firmware. Hardware tiling and RAM timing state persists until reprogrammed or reset.

## Dependencies and Integration Points

It integrates BIOS RAM config tables, PMU memory scripts, MMU memory targets, GPU memory allocation, display tiling, and secure VPR scrubbing.

## Risks

Incorrect VRAM size or heap classification can corrupt memory allocations. Compression tag leaks reduce render compression capacity. RAM transition mistakes can hang memory access. Tile programming affects scanout and render layout.

## Test Signals

Use VRAM allocation/free stress, memory clock transitions, compression-tag allocation, tile init/fini/prog, VPR scrubber boot, suspend/resume, and per-generation framebuffer probe tests.
