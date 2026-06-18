# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.c

`panthor_heap.c` manages per-VM tiler heap pools, heap contexts, heap chunks, firmware-driven growth, return of unused chunks, lifetime, and memory accounting.

Private types are `struct panthor_heap_chunk_header`, `struct panthor_heap_chunk`, `struct panthor_heap`, and `struct panthor_heap_pool`. Public APIs are heap create/destroy, heap grow, return chunk, pool create/destroy/get/put, and pool size. A pool owns an xarray of up to 128 heaps, an rwsem, weak VM pointer, refcount, GPU context kernel BO, and atomic total size.

Pool creation allocates/vmaps the GPU heap-context BO. Heap creation validates initial count, max count, chunk size range and alignment, takes a VM ref, allocates initial no-mmap kernel BO chunks, xarray-allocates an ID, zeroes the aligned GPU context, and returns context and first chunk GPU VAs. Grow validates the heap VA, checks target in-flight and max chunk limits, allocates another chunk, and returns encoded VA plus size. Return chunk removes a chunk by VA when firmware could not link it.

Dependencies are Panthor GEM/kernel BO, VM mapping, L2 cache-line size, xarray, krefs, and heap ioctls. Risks are GPU VA-to-heap ID decoding, destroy races, blocking allocation in firmware OOM paths, chunk header linkage, and memory accounting drift. Tests should cover boundary chunk sizes/counts, grow limits, return chunk, pool destroy with refs, fdinfo heap size, and firmware tiler OOM events.
