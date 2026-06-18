# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/icm.h

## Purpose
`icm.h` defines mlx4 ICM data structures, constants, iterator helpers, and public APIs for firmware table backing memory. It is the shared contract between ICM allocation/mapping code and firmware initialization/resource table consumers.

## Important APIs, Types, and Functions
Important constants are `MLX4_ICM_CHUNK_LEN`, `MLX4_ICM_PAGE_SHIFT`, and `MLX4_ICM_PAGE_SIZE`. Key types are `struct mlx4_icm_buf` for coherent DMA buffers, `struct mlx4_icm_chunk` for a list node containing either scatterlist pages or coherent buffers, `struct mlx4_icm` for a refcounted list of chunks, and `struct mlx4_icm_iter` for walking mapped segments. Inline iterator APIs are `mlx4_icm_first()`, `mlx4_icm_last()`, `mlx4_icm_next()`, `mlx4_icm_addr()`, and `mlx4_icm_size()`.

Declared APIs include `mlx4_alloc_icm()`, `mlx4_free_icm()`, `mlx4_table_get()`, `mlx4_table_put()`, `mlx4_table_get_range()`, `mlx4_table_put_range()`, `mlx4_init_icm_table()`, `mlx4_cleanup_icm_table()`, `mlx4_table_find()`, `mlx4_MAP_ICM_AUX()`, and `mlx4_UNMAP_ICM_AUX()`.

## Control Flow
The inline iterator starts at the first chunk in an ICM list, advances through `nsg` segments in each chunk, moves to the next list entry, and ends when it wraps back to the list head. Address and size helpers select coherent-buffer DMA fields or scatterlist DMA fields based on `chunk->coherent`.

## State and Persistence
No state is created by the header itself. It defines the in-memory representation used by `icm.c`: chunk list membership, number of pages/segments, coherent-vs-scatterlist storage, and ICM refcount. Firmware visibility of that state is established by map commands outside the header.

## Dependencies and Integration Points
The header depends on Linux list, PCI, mutex, scatterlist/DMA types through included headers, and `struct mlx4_icm_table` from `mlx4.h`. It is included by `fw.h`, `fw.c`, `icm.c`, and mlx4 core initialization paths that allocate and map firmware tables.

## Risks
Iterator correctness depends on `nsg` being populated after DMA mapping and on chunk lists remaining stable while iterated. The union layout means callers must respect `chunk->coherent`. `MLX4_ICM_CHUNK_LEN` is sized to keep chunks compact; changes to structure fields can alter allocation density. Address/size helpers assume DMA mappings are valid.

## Test Signals
Compile tests catch structure and prototype mismatches. Runtime signals include successful ICM map command iteration over coherent and non-coherent chunks, correct end-of-list behavior, correct segment sizes, and clean table allocation/free cycles under resource stress.
