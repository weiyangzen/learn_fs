# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.c

## Purpose
`ipu3-css-pool.c` implements a four-entry circular pool of DMA-mapped CSS parameter buffers. It lets streaming keep recent parameter generations available for firmware and for copy-forward semantics.

## Important APIs, Types, and Functions
- `imgu_css_dma_buffer_resize()` grows an existing DMA map when needed.
- `imgu_css_pool_init()` allocates pool entries and initializes validity.
- `imgu_css_pool_cleanup()` frees all entry maps.
- `imgu_css_pool_get()` advances to the recycled oldest entry.
- `imgu_css_pool_put()` rolls back the newest entry after a failed submission.
- `imgu_css_pool_last()` returns the nth newest valid map or a static null map.

## Control Flow
Pipeline setup initializes pools for parameter-set descriptors, accelerator data, GDC, OB grid, and late-binding memory blocks. Parameter submission gets new entries for blocks that changed, reads `last(1)` for old state, and rolls back entries if configuration or queueing fails.

## State and Persistence Behavior
Each entry persists an `imgu_css_map` and `valid` bit. `last` points at the newest entry, initialized to the pool size sentinel. Invalid lookups return a zero map, signaling no prior state.

## Dependencies and Integration Points
The pool delegates memory ownership to `imgu_dmamap_alloc()`/`imgu_dmamap_free()` and is used by `ipu3-css.c` parameter handling.

## Risks
No internal locking is provided. Resize only grows already allocated maps. Correct rollback depends on balanced get/put calls. Out-of-range `last()` only warns.

## Test Signals
Test allocation failure cleanup, ring wraparound, get/put rollback, null-map behavior, and repeated parameter submissions beyond four generations.
