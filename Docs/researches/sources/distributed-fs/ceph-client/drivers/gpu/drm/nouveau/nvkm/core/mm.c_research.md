## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/mm.c

### Purpose
`mm.c` implements Nouveau's small internal range allocator for GPU-visible address spaces and heaps. It tracks ordered allocation nodes, separate free-list membership, heap identity, allocation type, block alignment, and explicit holes between appended regions.

### Important APIs, types, and functions
The public API is `nvkm_mm_init()`, `nvkm_mm_fini()`, `nvkm_mm_head()`, `nvkm_mm_tail()`, `nvkm_mm_free()`, and `nvkm_mm_dump()`. The state comes from `struct nvkm_mm` and `struct nvkm_mm_node` in `core/mm.h`. Internal helpers `region_head()` and `region_tail()` split a free node from the front or back while preserving node-list and free-list order.

### Control flow
`nvkm_mm_init()` initializes a new allocator or appends a contiguous later heap, inserting a `NVKM_MM_TYPE_HOLE` node if the next heap begins after the previous region. `nvkm_mm_head()` scans the free list forward and returns the first suitable aligned range. `nvkm_mm_tail()` scans backward and returns the highest suitable range. Both clamp usable starts/ends to `block_size` boundaries when adjacent nodes have different types, split off alignment slack, mark the allocated node with the caller's type, and remove it from the free list. `nvkm_mm_free()` merges with adjacent free nodes before re-inserting the resulting node into the free list in offset order.

### State and persistence behavior
Allocator state is purely in memory. The node list is the authoritative ordered map, while `mm->free` contains only nodes whose type is `NVKM_MM_TYPE_NONE`. `heap_nodes` counts real heap regions and is used by `nvkm_mm_fini()` to detect leaked allocations; holes are ignored. Allocated nodes can be chained by users through `node->next`, but this allocator itself returns contiguous nodes with `next = NULL`.

### Dependencies
The file depends on Linux list primitives, `kzalloc_obj`/`kmalloc_obj`, `roundup()`, `rounddown()`, `min()`, and Nouveau's type constants from `core/mm.h`.

### Integration points
It is used by Nouveau memory managers that need simple range accounting for VRAM, instance memory, GPU objects, and related suballocators. Callers must serialize access externally; there is no lock in `struct nvkm_mm`.

### Risks
The allocator assumes power-of-two nonzero alignment because it builds `mask = align - 1`. Incorrect external locking can corrupt both lists. Boundary rounding around unlike typed neighbors can unexpectedly reduce usable space. `nvkm_mm_fini()` returns `-EBUSY` if any non-hole allocations remain, making leak cleanup visible during driver teardown.

### Test signals
Useful signals are allocation/free stress tests with head and tail placement, heap-specific allocation, alignment edge cases, adjacent free-node coalescing, appended heaps with holes, fini leak detection, and GPU object allocation paths that exercise this allocator during device init and teardown.
