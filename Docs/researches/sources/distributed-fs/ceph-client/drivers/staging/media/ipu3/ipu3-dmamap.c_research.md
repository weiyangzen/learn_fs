# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-dmamap.c

## Purpose
`ipu3-dmamap.c` allocates or maps buffers into the IPU3 private MMU aperture. It combines Linux IOVA allocation, page allocation/vmap, and `ipu3-mmu.c` page-table programming.

## Important APIs, Types, and Functions
- `imgu_dmamap_alloc()` reserves IOVA, allocates pages, maps each page through the MMU, vmaps pages, and fills `imgu_css_map`.
- `imgu_dmamap_free()` unmaps IOVA, unmaps CPU VA, frees pages, and clears `vaddr`.
- `imgu_dmamap_map_sg()` validates scatterlists and maps them to a contiguous IOVA.
- `imgu_dmamap_unmap()` releases an IOVA/MMU mapping.
- `imgu_dmamap_init()` and `imgu_dmamap_exit()` manage the IOVA domain.

## Control Flow
Internal CSS buffers use alloc/free. External scatterlists use map_sg/unmap. Allocation failure unwinds MMU mappings, page arrays, and IOVA reservations. Scatterlist mapping rejects offsets and non-page-aligned intermediate lengths before programming the MMU.

## State and Persistence Behavior
`struct imgu_css_map` stores size, IOVA, CPU vaddr, and pages for owned buffers. Scatterlist maps only use IOVA/size and must be unmapped rather than freed. The IOVA domain persists in `struct imgu_device`.

## Dependencies and Integration Points
Depends on Linux IOVA, vmalloc/vmap, page allocation, scatterlists, `imgu_device`, `imgu_css_map`, and IPU3 MMU mapping functions. Used by CSS pools, firmware maps, ABI buffers, and video-buffer mapping.

## Risks
Cleanup differs between owned allocations and scatterlist mappings. IOVA lookup failure in unmap warns and returns. Partial map/unmap behavior depends on the MMU layer's unwind contract. Backing page allocation/free logic is manual and failure-path sensitive.

## Test Signals
Inject failures at IOVA allocation, page allocation, MMU mapping, and vmap; validate scatterlist alignment rejection and map/unmap success; check for leaked pages/IOVAs after CSS cleanup.
