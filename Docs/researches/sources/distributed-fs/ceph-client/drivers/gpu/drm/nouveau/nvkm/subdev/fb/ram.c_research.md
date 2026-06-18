<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.c

## Purpose
Common VRAM memory object and RAM allocator implementation. It wraps framebuffer VRAM allocations as `nvkm_memory`, allocates/free ranges from the RAM memory manager, and initializes/destroys `struct nvkm_ram`.

## Important APIs, Types, And Functions
`struct nvkm_vram` wraps `nvkm_memory`, RAM owner, page size, and MM nodes. Public functions are `nvkm_ram_get()`, `nvkm_ram_wrap()`, `nvkm_ram_init()`, `nvkm_ram_del()`, `nvkm_ram_ctor()`, and `nvkm_ram_new_()`. Memory callbacks implement target/page/address/size/map/kmap/dtor.

## Control Flow
`nvkm_ram_get()` validates framebuffer RAM, creates a VRAM object, allocates one or more MM nodes from head or tail according to contiguity and alignment, and unwinds on failure. `nvkm_ram_wrap()` creates a synthetic node for a fixed physical range. Destruction returns allocated nodes to `ram->vram` under lock, except synthetic wrapped nodes are simply freed.

## State And Persistence
RAM state persists in `struct nvkm_ram`: type, size, function table, mutex, and MM allocator. VRAM memory objects persist allocated MM nodes until the memory reference is dropped. `nvkm_ram_ctor()` logs size/type and initializes the default allocator if generation constructors have not already provided one.

## Dependencies And Integration Points
Depends on NVKM memory/VMM APIs, instmem wrapping for kernel maps, MM allocator, framebuffer ownership, and RAM generation constructors. All VRAM allocations used by other NVKM subsystems flow through this layer.

## Risks
Allocator locking and unwind paths are safety-critical. `nvkm_ram_wrap()` creates a synthetic node not inserted in the MM list, so dtor must distinguish it correctly. Address/size truncation to `NVKM_RAM_MM_SHIFT` can silently drop sub-page portions if callers pass unaligned ranges.

## Test Signals
Signals include successful VRAM allocation/free under stress, contiguous and fragmented allocation behavior, VMM mapping correctness, kernel map wrapping, and no MM leaks on constructor or allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ram.c -->
