# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.h

## Purpose
`ipu3-dmamap.h` declares the DMA mapping facade for internal CSS allocations and external scatterlist mappings.

## Important APIs, Types, and Functions
- `imgu_dmamap_alloc()` / `imgu_dmamap_free()` handle owned, CPU-vmapped buffers.
- `imgu_dmamap_map_sg()` / `imgu_dmamap_unmap()` handle borrowed scatterlist buffers.
- `imgu_dmamap_init()` / `imgu_dmamap_exit()` manage the per-device IOVA domain.

## Control Flow
The driver initializes DMA mapping after MMU setup, uses alloc/free for firmware-visible internal structures, uses map_sg/unmap for queued external buffers, and exits after all mappings are removed.

## State and Persistence Behavior
State is stored in caller-provided `imgu_css_map` objects and in the device IOVA domain.

## Dependencies and Integration Points
The header bridges CSS memory users to `ipu3-mmu.c` and relies on `imgu_css_map` from the pool header.

## Risks
Both owned and borrowed mappings use the same map type but different cleanup APIs, so ownership mistakes can leak or invalidly free memory.

## Test Signals
Audit every alloc/free and map_sg/unmap pair, and ensure exit occurs only after all mappings are released.
