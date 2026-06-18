# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/sram.h

Purpose: declares the SRAM allocator used by the BestComm engine for task descriptors, contexts, variables, and descriptor rings that must reside in a dedicated on-chip SRAM region.

Important APIs and types: `struct bcom_sram` records base physical address, base virtual address, size, region-heap allocator pointer, and spinlock. Global `bcom_sram` points to the active allocator. Public functions are `bcom_sram_init()`, `bcom_sram_cleanup()`, `bcom_sram_alloc()`, and `bcom_sram_free()`. Inline helpers `bcom_sram_va2pa()` and `bcom_sram_pa2va()` translate within the SRAM window.

Control flow: engine probe initializes the SRAM allocator from a device tree node and owner name, BestComm setup allocates aligned regions, and cleanup frees allocator state. Runtime code translates task table physical addresses to virtual pointers when inspecting or editing task images.

State and persistence: volatile SRAM allocations are tracked by an in-memory region heap. Contents are hardware DMA/task programming state only.

Dependencies and integration points: depends on PowerPC region heap and MMU types, spinlocks, OF device nodes, and BestComm private engine code.

Risks and test signals: risks include alignment mistakes, out-of-range translations, allocator leaks, freeing invalid pointers, and global `bcom_sram` use before init. Tests should cover allocator init/failure, aligned allocations, exhaustion, free/reallocate cycles, address translation boundaries, and engine teardown.
