# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.c

## Purpose
This file implements the shared Microchip Frame DMA descriptor-control-block helper API. It initializes DCB/DB rings, uses caller-provided callbacks to populate hardware pointer fields, allocates backing memory either as coherent DMA or physical memory, and reports allocation sizes.

## Important APIs, Types, and Functions
The exported functions are `fdma_db_add`, `__fdma_dcb_add`, `fdma_dcb_add`, `fdma_dcbs_init`, `fdma_alloc_coherent`, `fdma_alloc_phys`, `fdma_free_coherent`, `fdma_free_phys`, `fdma_get_size`, and `fdma_get_size_contiguous`. The internal `__fdma_db_add` writes a DB status value then calls a dataptr callback. `__fdma_dcb_add` initializes all DBs for a DCB, updates the previous `last_dcb->nextptr` through a nextptr callback, marks the new DCB as last, invalidates its next pointer, and sets its info.

## Control Flow
Callers initialize an `fdma` object with dimensions and callbacks, compute and set `fdma->size`, allocate memory, and call `fdma_dcbs_init`. Initialization sets `last_dcb`, `db_index`, and `dcb_index` to the start of the ring, then adds every DCB. Each added DCB fills every DB data pointer and links the prior DCB to the new DCB. The last initialized DCB remains with `FDMA_DCB_INVALID_DATA` as its next pointer, making later additions or consumer logic responsible for ring progression.

## State and Persistence
The mutable state is all in `struct fdma`: DCB memory, `dma`, `size`, indices, counts, DB size, channel ID, and callbacks. Memory lifetime is explicit via allocation/free helpers. No persistent storage exists beyond the allocated descriptor area shared with hardware.

## Dependencies and Integration Points
This file depends on DMA mapping, `kzalloc`, `virt_to_phys`, alignment macros, and the layout from `fdma_api.h`. It exports GPL symbols for Microchip switch drivers. Users must provide correct `dataptr_cb` and `nextptr_cb` callbacks for the addressing mode they use.

## Risks
The helpers do not validate `n_dbs <= FDMA_DB_MAX`, index bounds, callback presence, or that `fdma->size` was set before allocation. `fdma_alloc_phys` uses `virt_to_phys` on `kzalloc` memory, which is suitable only for hardware paths expecting CPU physical addresses and not general DMA API semantics. Failed initialization may leave partially populated descriptor memory. Callback errors are returned but no rollback is attempted.

## Test Signals
Unit-like tests can instantiate small `fdma` objects with callbacks that record expected pointer values. Integration tests should verify descriptor linkage, DB status/data pointers, DMA-coherent allocation and free, contiguous size calculations, and build/link visibility for switchcore drivers.
