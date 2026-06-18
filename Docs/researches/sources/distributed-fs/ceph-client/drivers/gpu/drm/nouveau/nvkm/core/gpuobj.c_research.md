# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/gpuobj.c

## Purpose
This file implements NVKM GPU object allocation, suballocation, mapping, read/write access, and wrapping of existing memory.

## Important APIs, Types, and Functions
Public APIs include `nvkm_gpuobj_new`, `nvkm_gpuobj_del`, `nvkm_gpuobj_wrap`, `nvkm_gpuobj_memcpy_to`, and `nvkm_gpuobj_memcpy_from`. Internal function tables handle heap-backed objects, suballocated objects, fast kmap access, slow memory access, and VMM mapping.

## Control Flow
Constructor either suballocates from a parent GPU object heap using head/tail alignment rules or allocates instance memory directly. It sets function tables, address, size, optionally zeroes memory through kmap/write helpers, and initializes a child heap. Acquire tries to kmap the parent/memory and switches to fast direct IO access if successful; release restores the base table and drops the kmap. Delete frees parent heap nodes, child heap, memory refs, and the object.

## State and Persistence Behavior
State includes parent or instance memory reference, heap allocator, allocation node, GPU address, size, mapped pointer, and active function table.

## Dependencies and Integration Points
It depends on NVKM memory, instance memory, memory manager, BAR/kmap helpers, VMM mapping, and engines/subdevs that need GPU-visible objects.

## Risks
Suballocation alignment and zeroing must not write outside the parent node. Fast/slow function table switching must be balanced with acquire/release. `nvkm_gpuobj_memcpy_from` appears to write through `((u32 *)src)` instead of `dst`, which is suspicious.

## Test Signals
Signals include parent suballocation/free, direct instance allocation, kmap fast and slow paths, zeroing, VMM mapping, wrap behavior for legacy GART, and memcpy helper validation.
