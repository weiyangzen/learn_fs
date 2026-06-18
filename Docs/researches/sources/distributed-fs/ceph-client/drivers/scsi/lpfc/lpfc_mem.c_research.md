# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_mem.c

## Purpose
`lpfc_mem.c` owns the LPFC driver's memory-pool lifecycle and the allocation/free paths for control buffers, mailbox objects, node objects, receive buffers, NVMe target buffers, HBQ/RQ buffers, and teardown cleanup. It bridges Linux DMA pools/mempools with adapter-specific buffer formats used by SLI-3 HBQs and SLI-4 receive queues.

## Important APIs, Types, and Functions
- Pool sizing constants define safety and mempool depths: `LPFC_MBUF_POOL_SIZE`, `LPFC_MEM_POOL_SIZE`, `LPFC_DEVICE_DATA_POOL_SIZE`, `LPFC_RRQ_POOL_SIZE`, and `LPFC_MBX_POOL_SIZE`.
- `lpfc_mem_alloc()` creates the common `lpfc_mbuf_pool`, a preallocated DMA safety pool, mailbox and nodelist mempools, SLI-4 RRQ/header/data pools, SLI-3 HBQ pool, and optional ExpressLane device-data pool.
- `lpfc_mem_alloc_active_rrq_pool_s4()` creates a kmalloc-backed mempool sized to the SLI-4 maximum XRI bitmap.
- `lpfc_nvmet_mem_alloc()` creates the larger NVMe target data receive buffer pool.
- `lpfc_mem_free()` tears down pools created by `lpfc_mem_alloc()` and drains device-data list entries.
- `lpfc_mem_free_all()` additionally frees queued/completed/active mailbox commands, SCSI DMA pools, congestion information DMA memory, RX monitor ring, and IOCB lookup arrays.
- `lpfc_mbuf_alloc()`, `__lpfc_mbuf_free()`, and `lpfc_mbuf_free()` provide DMA buffer allocation with a priority fallback safety pool protected by `phba->hbalock`.
- `lpfc_nvmet_buf_alloc()` and `lpfc_nvmet_buf_free()` allocate/free generic NVMe target DMA buffers from `lpfc_sg_dma_buf_pool`.
- `lpfc_els_hbq_alloc()`/`lpfc_els_hbq_free()` handle SLI-3 HBQ buffers.
- `lpfc_sli4_rb_alloc()`/`lpfc_sli4_rb_free()` allocate paired SLI-4 header and data receive buffers.
- `lpfc_sli4_nvmet_alloc()`/`lpfc_sli4_nvmet_free()` allocate paired SLI-4 header plus larger NVMe target data buffers.
- `lpfc_in_buf_free()` returns unsolicited input buffers through the right SLI-3 HBQ or generic mbuf path.
- `lpfc_rq_buf_free()` reposts an SLI-4 RQ buffer pair to hardware queues or frees it through the RQB free callback if repost fails.

## Control Flow and State
Allocation is staged. `lpfc_mem_alloc()` starts with the common BPL-sized DMA pool and pre-fills `phba->lpfc_mbuf_safety_pool` with 64 coherent buffers. It then creates mailbox and node mempools. SLI-4 adapters receive RRQ, header receive, and data receive pools; older SLI adapters receive an HBQ pool. Optional ExpressLane support creates a device-data mempool. Every failure label unwinds only the pools already created and resets relevant pointers.

Teardown is two-layered. `lpfc_mem_free_all()` first drains live mailbox queues and the active mailbox, choosing `lpfc_sli4_mbox_cmd_free()` for SLI-4 config mailboxes and `lpfc_mbox_rsrc_cleanup()` for ordinary mailbox commands. It clears `LPFC_SLI_MBOX_ACTIVE` under `hbalock`, then delegates to `lpfc_mem_free()` for normal pools and finally destroys broader SCSI/control allocations. `lpfc_mem_free()` calls `lpfc_sli_hbqbuf_free_all()` before destroying receive pools and drains `phba->luns` before destroying the optional device-data pool.

Receive-buffer free paths are reuse-oriented. SLI-3 HBQ buffers are either returned to HBQ firmware accounting or freed through the configured HBQ free callback depending on the tag. SLI-4 RQ buffers are removed from the software list, converted into HRQE/DRQE physical addresses, reposted with `lpfc_sli4_rq_put()`, then re-linked and counted on success; failure logs details and calls the RQB free callback.

## State and Persistence Behavior
All state is in kernel memory and DMA-coherent buffers owned by `struct lpfc_hba`. Persistent fields include DMA pool pointers, mempool pointers, safety-pool element arrays/counts, active RRQ bitmap size, RQ/HBQ buffer lists, LUN device-data list, queued mailbox lists, active mailbox pointer, congestion info buffer, RX monitor pointer, and IOCB lookup table. No on-disk persistence occurs, but DMA buffers remain firmware-visible until returned, reposted, or freed.

## Dependencies and Integration Points
The file uses Linux `dma_pool_create/alloc/free/destroy`, coherent DMA APIs, mempool APIs, spinlocks, list primitives, and PCI device DMA context. Driver-local integration includes mailbox cleanup from `lpfc_mbox.c`, SLI/HBQ/RQ queue helpers, NVMe target support, SCSI buffer pools, congestion-management data, RX monitoring, and nodelist allocation. Discovery, ELS, unsolicited receive, NVMe target, and SCSI paths all rely on these pools being initialized before use.

## Risks and Edge Cases
- `lpfc_mem_alloc()` has a long unwind chain; any added pool must be inserted at the right failure label or teardown will leak or destroy uninitialized pointers.
- `lpfc_mbuf_alloc()` uses `GFP_KERNEL` and takes `hbalock` only around the safety pool, so callers must respect the documented no-lock/no-interrupt context for allocation.
- `__lpfc_mbuf_free()` must only be called with `hbalock` held; using it from unlocked contexts corrupts safety-pool counters.
- `lpfc_mem_free_sli_mbox()` must detect SLI-4 config mailboxes correctly; freeing a non-embedded SLI-4 config mailbox as a generic mailbox would leak SGE DMA pages.
- `lpfc_in_buf_free()` returns early if HBQs are no longer in use, leaving ownership with teardown assumptions; ordering around `hbq_in_use` matters.
- `lpfc_rq_buf_free()` assumes the `lpfc_dmabuf` is the header buffer embedded in `struct rqb_dmabuf`; passing a data buffer or generic mbuf would compute the wrong container.
- Destroying DMA pools while firmware still owns posted buffers would be unsafe; callers must stop queues and drain receive paths first.

## Test Signals
Useful tests include forced allocation failure at each pool creation stage, teardown after partial initialization, mailbox queue drain with ordinary and SLI-4 config commands, priority mbuf fallback exhaustion/refill, SLI-3 HBQ free while `hbq_in_use` changes, SLI-4 RQ repost success and failure, NVMe target receive buffer allocation/free, and leak checks after probe/remove or PCI error recovery. Runtime counters to watch include safety-pool `current_count`, RQB `buffer_count`, empty mailbox queues after teardown, and absence of DMA API debug warnings.
