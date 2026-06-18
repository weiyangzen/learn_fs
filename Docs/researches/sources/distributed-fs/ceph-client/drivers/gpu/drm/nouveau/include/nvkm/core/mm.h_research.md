# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/mm.h

## Purpose

This header exposes NVKM's small range allocator for GPU-managed address spaces such as RAMHT slots, notifier heaps, VRAM heaps, tile/tag regions, and firmware-local heaps.

## Important APIs, Types, and Functions

The main types are `struct nvkm_mm` and `struct nvkm_mm_node`; APIs include `nvkm_mm_init`, `nvkm_mm_fini`, `nvkm_mm_head`, `nvkm_mm_tail`, `nvkm_mm_free`, `nvkm_mm_dump`, `nvkm_mm_heap_size`, `nvkm_mm_contiguous`, `nvkm_mm_addr`, and `nvkm_mm_size`.

## Control Flow

Callers initialize an allocator over an offset/length/block-size range, allocate from the head or tail with heap/type/size/alignment constraints, use returned node chains, then free them back into the allocator. Helpers verify whether allocations are contiguous before deriving a single address.

## State and Persistence Behavior

Allocator state lives in node and free lists plus the heap node count and block size. Allocation nodes persist until explicitly freed and may represent chained non-contiguous ranges.

## Dependencies and Integration Points

It underpins RAM heaps, channel notifier suballocations, compression tag heaps, GPU object child heaps, and legacy ABI16 notifier allocation.

## Risks

Callers that assume contiguity can program invalid hardware addresses for chained nodes. Alignment and min/max size mistakes fragment scarce GPU heaps. Leaked nodes keep resources unavailable until device teardown.

## Test Signals

Allocation/free stress, head/tail placement, alignment corner cases, heap/type filtering, chained allocation size calculations, and fini-time leak detection are the main signals.
