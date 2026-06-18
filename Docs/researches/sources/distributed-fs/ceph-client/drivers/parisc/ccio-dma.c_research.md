<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/ccio-dma.c -->
# sources/distributed-fs/ceph-client/drivers/parisc/ccio-dma.c

## Purpose
`ccio-dma.c` implements DMA mapping for first-generation PA-RISC cache-coherent systems with U2/UTurn I/O adapters. It programs the CCIO IOMMU in virtual mode, allocates I/O virtual pages, fills the I/O page directory, purges I/O TLB entries, provides PA-RISC DMA map ops, registers IOC MMIO resources, and supports Dino/LBA resource allocation under CCIO windows.

## Important APIs, Types, And Functions
`struct ioc` is the central controller state: MMIO registers, resource bitmap, I/O PDIR, pdir size, allocation hint, lock, Cujo workaround flag, chain ID shift, linked-list pointer, hardware path, fake PCI device, and two routed MMIO resources. Important functions include `ccio_alloc_range()`, `ccio_free_range()`, `ccio_io_pdir_entry()`, `ccio_clear_io_tlb()`, `ccio_mark_invalid()`, DMA ops `ccio_map_phys()`, `ccio_unmap_phys()`, `ccio_alloc()`, `ccio_free()`, `ccio_map_sg()`, `ccio_unmap_sg()`, lookup helpers `ccio_get_iommu()` and `ccio_find_ioc()`, `ccio_cujo20_fixup()`, `ccio_ioc_init()`, resource helpers `ccio_allocate_resource()` and `ccio_request_resource()`, and `ccio_probe()`.

## Control Flow
Probe allocates an IOC, links it into `ioc_list`, maps registers, initializes the I/O PDIR and resource map, switches hardware into virtual mode, initializes resource windows from IOA registers, installs global `hppa_dma_ops`, attaches an HBA-like platform data object, and optionally creates `/proc/bus/runway/ccio` entries.

Mapping a single DMA buffer computes the page offset, rounds to I/O pages, locks the IOC resource map, allocates a contiguous bitmap range, fills PDIR entries with physical addresses and DMA hints, flushes entries, and returns IOVA plus offset. Unmapping rounds back to pages, invalidates PDIR valid bits, purges matching I/O TLB entries, and frees the bitmap range. Scatter-gather mapping uses shared `iommu-helpers.h` to coalesce chunks and fill the PDIR in two passes, preserving virtual-coherence information.

Resource allocation first tries existing IOC windows, then expands one of the two IO ranges and writes updated low/high registers before allocating from that parent.

## State And Persistence
IOC state persists for the boot lifetime in `ioc_list`. The resource map tracks allocated IOVA pages; `pdir_base` holds hardware-consumed mappings. Hardware state includes IO chain ID mask, PDIR base, IO control virtual mode, TLB entries, IO low/high windows, and TLB purge commands. Optional procfs state reports controller and bitmap details.

## Dependencies And Integration Points
The file depends on PA-RISC device inventory, raw MMIO, DMA map ops, scatterlist/IOMMU helpers, PCI HBA data, procfs, resource management, cache flush/sync assembly helpers, and Dino through exported resource helpers and `ccio_get_iommu()`.

## Risks
Resource exhaustion and oversize mappings call `panic()`. The allocator intentionally allocates coarse bitmap units for small mappings, trading space for TLB locality. Mapping assumes 32-bit-or-better DMA masks. Cache/TLB correctness depends on architecture-specific `lci`, `fdc`, and `sync` sequences. `hppa_dma_ops` is global, so probe order matters. Cujo 2.0 workaround reserves repeating bad pages; missing it risks silent corruption. Resource expansion rewrites IOA windows and must not conflict with firmware-registered child resources.

## Test Signals
Test single and scatter-gather DMA map/unmap, sub-cacheline SAFE_DMA behavior, bidirectional consistent allocations, IOVA reuse after unmap, TLB purge coverage, procfs reporting, DMA mask rejection, resource allocation under both IOC windows, Cujo 2.0 bad-page reservation, multi-IOC lookup by hardware path, and stress tests for mapping exhaustion and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/parisc/ccio-dma.c -->
