# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mem.c

## Purpose
This file constructs, maps, and destroys NVIF memory objects selected from MMU-advertised memory types.

## Important APIs, Types, and Functions
Public functions are `nvif_mem_ctor`, `nvif_mem_ctor_type`, `nvif_mem_ctor_map`, and `nvif_mem_dtor`.

## Control Flow
`nvif_mem_ctor` scans MMU memory types for one containing all requested flags and delegates to `nvif_mem_ctor_type`. The typed constructor builds variable-size args on stack or heap, creates the memory object, and records returned type/page/address/size. `nvif_mem_ctor_map` requests mappable memory and maps the object, destroying it on map failure.

## State and Persistence Behavior
State persists in `struct nvif_mem`: object handle, type flags, page shift, address, size, and optional object map.

## Dependencies and Integration Points
It depends on NVIF MMU type discovery, memory class constructors, object mapping, and callers such as TTM/Nouveau memory allocation.

## Risks
Type matching picks the last matching type if multiple matches continue while `ret` is nonzero. Variable argument sizing must avoid stack overflow and preserve backend data. Map failure cleanup must prevent leaked memory objects.

## Test Signals
Signals include VRAM/host/mappable/coherent type allocation, invalid type rejection, map failure cleanup, and constructor argument size boundary tests.
