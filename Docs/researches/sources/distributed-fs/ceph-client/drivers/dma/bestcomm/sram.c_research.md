# sources/distributed-fs/ceph-client/drivers/dma/bestcomm/sram.c

Purpose: Simple SRAM allocator for BestComm on-board SRAM, backed by the PowerPC reusable heap (`rheap`) allocator.

Important APIs/types/functions: Exported global `bcom_sram` and functions `bcom_sram_init`, `bcom_sram_cleanup`, `bcom_sram_alloc`, and `bcom_sram_free`. The state object tracks physical base, virtual mapping, size, heap handle, and a spinlock.

Control flow: init rejects double initialization, allocates state, resolves the SRAM OF resource, requests the memory region, maps it with `ioremap`, creates an rheap, attaches the whole region as free space, and initializes locking. Cleanup destroys the heap, unmaps, releases the region, and frees state. Alloc locks the heap, calls `rh_alloc_align`, returns both physical and virtual addresses, and free computes offset from virtual base before `rh_free`.

State and persistence: Singleton process-wide allocator state in `bcom_sram`. Allocations persist until explicitly freed or cleanup tears down the whole allocator. No disk persistence.

Dependencies/integration: OF address translation, IO memory resource management, PowerPC `rheap`, BestComm core/task users that allocate TDT/context/var/FDT areas and BD rings.

Risks: Comments warn non-irqsave locking, so IRQ handlers must not call the allocator. The inactive code path for partial SRAM zones leaves `regaddr_p`/`psize` null, so the whole SRAM is always attached. Pointer arithmetic assumes returned pointers belong to the mapped SRAM. Double init is blocked.

Test signals: probe/init with valid SRAM DT node, allocation/free alignment tests, exhaustion handling, cleanup after allocations, and BestComm task allocation under mixed BD sizes.
