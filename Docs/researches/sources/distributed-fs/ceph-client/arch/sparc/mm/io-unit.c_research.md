# sources/distributed-fs/ceph-client/arch/sparc/mm/io-unit.c

Purpose: SUN4D IO-UNIT DVMA/IOMMU support and DMA mapping operations.

Important APIs/functions: `iounit_init` discovers `sbi` nodes and initializes IO-UNITs. `iounit_iommu_init` maps the external page table and installs `iounit_dma_ops`. DMA ops include `iounit_map_phys`, `iounit_unmap_phys`, `iounit_map_sg`, `iounit_unmap_sg`, and under `CONFIG_SBUS`, `iounit_alloc`/`iounit_free`. `iounit_get_area` allocates IO PTE slots and programs page-table entries.

Control flow: init allocates an `iounit_struct`, sets bitmap limits/rotors, maps the XPT resource, clears page-table entries, and attaches DMA ops to the platform device. Mapping acquires the IO-UNIT lock, chooses a bitmap range class based on required page count, scans for contiguous free slots with rotor wraparound, writes `MKIOPTE` entries, and returns an IOUNIT DMA address. Unmap clears bitmap bits. SBUS allocation allocates zeroed pages, reserves DVMA resources, maps CPU PTEs and IO PTEs, flushes cache/TLB, and returns the DVMA CPU address.

State and persistence: per-device `iounit_struct` persists in `dev.archdata.iommu`, including page table pointer, bitmap, limits, rotors, and spinlock. Hardware XPT entries persist until unmapped.

Dependencies/integration: uses OF/platform discovery, SBUS register access, DMA map ops, SPARC DMA resource allocator, cache/TLB flushes, and `mm_32.h`. `subsys_initcall` runs before drivers need DMA ops.

Risks: maximum mapping length is hard-limited to 256 KiB. `iounit_free` is unimplemented under `CONFIG_SBUS`, so consistent allocations may leak unless unused or handled elsewhere. Bitmap/page-table updates must be lock-protected. Mapping failure in scatter-gather after partial success lacks rollback.

Test signals: SUN4D/SBUS boot, DMA map/unmap for single and scatter-gather buffers around page boundaries, >256 KiB rejection, rotor wraparound, XPT programming validation, and consistent allocation/free behavior if SBUS alloc is exercised.
