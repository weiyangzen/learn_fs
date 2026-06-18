# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-mmu.h

## Purpose
`ipu3-mmu.h` declares the IPU3 private MMU interface and aperture geometry.

## Important APIs, Types, and Functions
- `IPU3_PAGE_SHIFT` and `IPU3_PAGE_SIZE` define 4 KiB mapping granularity.
- `struct imgu_mmu_info` exposes aperture start/end.
- Lifecycle functions initialize, exit, suspend, and resume the MMU.
- Mapping functions map physical pages, unmap IOVAs, and map scatterlists.

## Control Flow
Device setup initializes the MMU and then the DMA-map IOVA domain. DMA mapping reserves IOVAs and calls map/unmap primitives. PM paths call suspend/resume around hardware power transitions.

## State and Persistence Behavior
Only aperture geometry is public; private page tables remain hidden behind `imgu_mmu_info`. Mappings persist until explicitly unmapped or the MMU exits.

## Dependencies and Integration Points
The header is consumed by `ipu3-dmamap.c` and device lifecycle code. It uses Linux device, scatterlist, DMA, and physical address types.

## Risks
All map/unmap sizes and addresses must be 4 KiB aligned. Return conventions differ between map (`int`) and unmap/map_sg (`size_t`), so callers must handle them correctly.

## Test Signals
Verify aperture use by the IOVA domain, alignment enforcement, mapping unwind before exit, and mapping survival across suspend/resume.
