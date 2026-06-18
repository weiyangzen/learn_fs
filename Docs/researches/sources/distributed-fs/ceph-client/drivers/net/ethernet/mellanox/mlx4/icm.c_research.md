# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.c

## Purpose
`icm.c` manages mlx4 ICM, the host memory backing firmware object tables. It allocates chunked DMA memory, maps and unmaps that memory into firmware address space, lazily backs ICM table chunks on demand, tracks references, finds lowmem table entries, and initializes/cleans reserved table ranges.

## Important APIs, Types, and Functions
Public APIs are `mlx4_alloc_icm()`, `mlx4_free_icm()`, `mlx4_MAP_ICM_AUX()`, `mlx4_UNMAP_ICM_AUX()`, `mlx4_table_get()`, `mlx4_table_put()`, `mlx4_table_find()`, `mlx4_table_get_range()`, `mlx4_table_put_range()`, `mlx4_init_icm_table()`, and `mlx4_cleanup_icm_table()`. Internal helpers include `mlx4_free_icm_pages()`, `mlx4_free_icm_coherent()`, `mlx4_alloc_icm_pages()`, `mlx4_alloc_icm_coherent()`, `mlx4_MAP_ICM()`, and `mlx4_UNMAP_ICM()`. Core structures come from `icm.h`: `struct mlx4_icm`, `struct mlx4_icm_chunk`, `struct mlx4_icm_buf`, and `struct mlx4_icm_table`.

## Control Flow
`mlx4_alloc_icm()` allocates an ICM container and then repeatedly allocates chunks up to 256 KiB, lowering allocation order on failure. Non-coherent allocations use pages and scatterlists that are DMA-mapped when a chunk fills or at the end. Coherent allocations use `dma_alloc_coherent()` and require page-aligned virtual addresses. On failure, all partially allocated chunks are freed.

`mlx4_table_get()` maps an object number to a table chunk, locks the table, increments the refcount if the chunk already exists, or allocates and firmware-maps a new 256 KiB ICM chunk at `table->virt + chunk_offset`. `mlx4_table_put()` decrements the chunk refcount and unmaps/frees the chunk at zero. Range helpers repeat this per chunk and unwind on failure. `mlx4_init_icm_table()` allocates the table pointer array, records table metadata, and preallocates/maps chunks that contain reserved firmware objects with a permanent reference. `mlx4_table_find()` returns a CPU pointer and optional DMA handle for lowmem-backed table objects by walking chunk DMA segments.

## State and Persistence
There is no filesystem persistence. Runtime state is the ICM chunk list, chunk page/scatterlist/coherent-buffer descriptors, DMA mappings, per-ICM refcount, and per-table metadata protected by `table->mutex`. Firmware mappings persist in the device until `UNMAP_ICM` or cleanup. Reserved chunks intentionally keep a positive refcount so they remain mapped for firmware-owned objects.

## Dependencies and Integration Points
The file depends on Linux page allocation, DMA mapping, scatterlists, mutexes, mlx4 command helpers in `fw.c`, PCI device DMA context, and table definitions in `mlx4.h`. It is used by core device initialization and resource subsystems for QP, CQ, SRQ, MPT, MTT, EQ, multicast, and auxiliary firmware tables.

## Risks
Risk areas include high-order allocation fallback, coherent allocation alignment, DMA map/unmap symmetry, refcount underflow if `put` exceeds `get`, object-to-chunk index calculations when object counts are not powers of two, lowmem-only pointer lookup assumptions, reserved range sizing near the end of a table, and firmware map/unmap failures leaving host and device views inconsistent. The code assumes DMA mapping may merge but not split pages when deriving DMA handles.

## Test Signals
Useful tests include allocation with coherent and non-coherent modes, fallback from high-order pages, DMA mapping failure injection, table get/put refcount behavior, range get unwind, reserved chunk preallocation, table lookup pointer and DMA-handle correctness for lowmem tables, cleanup after partial initialization failure, and map/unmap command error handling.
