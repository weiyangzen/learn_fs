<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/jazzdma.c -->
## sources/distributed-fs/ceph-client/arch/mips/jazz/jazzdma.c

### Purpose
`jazzdma.c` implements the Jazz R4030 virtual DMA translation table, low-level channel programming helpers, and Linux `dma_map_ops` for noncoherent Jazz devices.

### Important APIs, Types, And Functions
Key state and APIs are `pgtbl`, `vdma_lock`, `vdma_init()`, `vdma_alloc()`, `vdma_free()`, `vdma_phys2log()`, `vdma_log2phys()`, `vdma_stats()`, `vdma_enable()`, `vdma_disable()`, `vdma_set_mode()`, `vdma_set_addr()`, `vdma_set_count()`, `vdma_get_residue()`, `vdma_get_enable()`, `jazz_dma_alloc/free/map_phys/unmap_phys/map_sg/unmap_sg/sync_*()`, and exported `jazz_dma_ops`.

### Control Flow
`vdma_init()` allocates uncached page-table memory, initializes entries, and points R4030 registers at it. `vdma_alloc()` validates physical range/size, first-fits empty VDMA pages under a spinlock, writes frames/owner tags, invalidates the translation table, and returns a logical DMA address. DMA map operations wrap cache synchronization around VDMA allocation/free. Channel helpers program R4030 mode, address, count, enable, and error bits.

### State, Persistence, And Dependencies
Persistent runtime state lives in the VDMA page table, R4030 translation/control registers, channel registers, and exported DMA mapping ops. Dependencies include noncoherent cache helpers, Jazz register accessors, scatterlist APIs, and DMA common helpers.

### Integration Points
Jazz SCSI and network platform devices use these mapping operations to translate CPU physical memory into R4030 logical DMA space. Generic DMA API callers reach this file through `jazz_dma_ops`.

### Risks
`vdma_free()` is not locked while mutating owner fields, unlike allocation. Scatter-gather mapping leaks earlier mappings if a later entry fails. `jazz_dma_free()` converts an uncached return address with `virt_to_page()`, which relies on MIPS address translation behavior. MMIO mapping is rejected due limited test confidence.

### Test Signals
Exercise coherent allocation/free, map/unmap single and scatter-gather with partial-failure injection, SCSI/network DMA I/O, cache coherency under read/write directions, channel enable/disable errors, and VDMA table exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/jazz/jazzdma.c -->
