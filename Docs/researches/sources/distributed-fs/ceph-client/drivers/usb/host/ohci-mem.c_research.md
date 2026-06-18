# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-mem.c

## Purpose

`ohci-mem.c` centralizes allocation and lookup for OHCI endpoint descriptors and transfer descriptors, plus basic initialization of controller-private lists and locks.

## Important APIs, Types, and Functions

Important helpers are `ohci_hcd_init()`, `ohci_mem_init()`, `ohci_mem_cleanup()`, `td_alloc()`, `td_free()`, `ed_alloc()`, `ed_free()`, and `dma_to_td()`. The file uses the `struct ed`, `struct td`, and TD hash table declared in `ohci.h`.

## Control Flow

Initialization sets `next_statechange`, initializes `ohci->lock`, and prepares pending and in-use ED lists. If the HCD does not provide a local memory pool, `ohci_mem_init()` creates DMA pools with OHCI-required TD and ED alignment. TD allocation returns a zeroed DMA-safe TD whose `hwNextTD` self-points until filled. ED allocation initializes the software TD list and stores the DMA address. TD free removes the TD from the DMA hash chain before returning memory to the pool.

## State and Persistence Behavior

State is entirely runtime memory: DMA pools, local memory allocations, TD hash chains, ED lists, and descriptor DMA addresses. Descriptors are coherent or local-memory-backed because hardware reads and writes them directly. No durable state exists.

## Dependencies and Integration Points

It depends on Linux DMA pool APIs, optional `usb_hcd.localmem_pool`, genalloc local memory helpers, and `ohci.h` descriptor layout. Queue handling uses `td_alloc()`/`ed_alloc()` during URB and endpoint setup, and done-list processing uses `dma_to_td()` to translate hardware done-head DMA values back to software TD objects.

## Risks and Test Signals

Risks include descriptor alignment mistakes, stale TD hash entries, freeing TDs still visible to hardware, local-memory pool address assumptions, and missing cleanup on partial initialization. Test signals include repeated endpoint enable/disable cycles, DMA API debugging, local-memory controllers such as SM501/SA1111, malformed done-head entries, and clean module unload after active URB churn.
