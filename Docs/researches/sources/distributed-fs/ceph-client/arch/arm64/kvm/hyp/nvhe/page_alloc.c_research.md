<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/page_alloc.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/page_alloc.c

## Purpose
`page_alloc.c` implements the nVHE buddy page allocator over hyp-owned memory. It uses hyp vmemmap metadata and free-list nodes stored in free pages themselves to allocate zeroed pages for page tables, VM metadata, and other hyp pools.

## Important APIs, Types, and Functions
`__hyp_vmemmap` points at hyp `struct hyp_page` metadata. `hyp_pool_init()` initializes a pool range, marks metadata refcounted, and attaches free pages after reserved pages. `hyp_alloc_pages()` finds and splits a suitable free block, marks it refcounted, and returns its hyp VA. `hyp_put_page()` decrements refcount and coalesces on zero. `hyp_get_page()` increments refcount. `hyp_split_page()` converts a high-order allocation into individual refcounted order-0 pages. Internal helpers find buddies, add/remove list nodes, coalesce in `__hyp_attach_page()`, and split in `__hyp_extract_page()`.

## Control Flow, State, and Persistence
Each `struct hyp_pool` owns a lock, max order, range bounds, and free lists. Free pages are zeroed on the put path before list insertion, so allocation can return already-zeroed memory. Refcount and buddy-tree updates are done under the pool lock to avoid transient states visible to readers. Pages outside the pool range can be freed into the pool without coalescing, supporting external donated pages.

## Dependencies and Integration Points
It depends on hyp physical/virtual/page conversion helpers, list primitives, spinlocks, and `struct hyp_page` metadata. It is used by hyp stage-1 page tables (`setup.c`/`mm.c`), host and guest stage-2 page-table pools (`mem_protect.c`), and teardown/refill paths.

## Risks and Test Signals
Risks include list corruption, refcount underflow/overflow, wrong order metadata for tail pages, zeroing memory still in use, and fragmented pools failing high-order allocations. Test signals are ownership selftests, allocator exhaustion, split/coalesce sequences, reserved page handling, list debug checks, and page-table initialization/destruction under protected VM churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/page_alloc.c -->
