# sources/distributed-fs/ceph-client/arch/sparc/kernel/ioport.c

## Purpose
`ioport.c` implements sparc32 I/O virtual mapping allocation and DVMA resource reservation. It backs `ioremap()`, `iounmap()`, OF resource mapping, `/proc` map visibility, and limited DMA cache synchronization behavior.

## Important APIs, Types, and Functions
Public APIs are `ioremap()`, `iounmap()`, `of_ioremap()`, `of_iounmap()`, `sparc_dma_alloc_resource()`, `sparc_dma_free_resource()`, optional `sbus_set_sbus64()`, and `arch_sync_dma_for_cpu()`. Internal helpers are `_sparc_alloc_io()`, `_sparc_ioremap()`, `_sparc_free_io()`, `xres_alloc()`, and `xres_free()`.

## Control Flow and State
The file maintains root resources `sparc_iomap` and `_sparc_dvma`. Early mappings use a static `xresv` mini-allocator before falling back to `kmalloc`. `_sparc_ioremap()` allocates virtual space from `sparc_iomap`, maps physical bus pages with `srmmu_mapiorange()`, and returns the offset-adjusted virtual address. `iounmap()` looks up the resource by page-aligned virtual address, unmaps via `srmmu_unmapiorange()`, releases the resource, and frees static or dynamic storage. DVMA allocation creates a named resource under `_sparc_dvma`; free validates address alignment and size. Proc handlers list child resources.

## Persistence and Dependencies
Persistent state includes resource trees, static `xresv`, and proc entries. Dependencies include SRMMU IO-range mapping, Open Firmware resources, LEON cache-snooping helpers, Linux resource allocator, and procfs.

## Integration Points, Risks, and Test Signals
Integration points include PCI/SBUS drivers, early timers/interrupt controllers, OF device mapping, and DMA allocators. Risks include hard PROM halt on IO map exhaustion, linear lookup cost in `iounmap()`, static name truncation, resource leaks on invalid frees, and full D-cache flush for non-snooping LEON DMA. Test signals are successful early device MMIO, `/proc/io_map` and `/proc/dvma_map` content, ioremap/iounmap leak tests, and DMA coherency on LEON.
