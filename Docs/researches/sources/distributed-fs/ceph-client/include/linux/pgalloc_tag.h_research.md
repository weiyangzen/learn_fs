<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc_tag.h -->
# sources/distributed-fs/ceph-client/include/linux/pgalloc_tag.h

## Purpose
Defines page-allocation tagging helpers used by memory allocation profiling to associate pages with allocation codetags, including compact page-extension references, module/kernel tag index conversion, and folio tag maintenance.

## Important APIs, Types, And Functions
- Under `CONFIG_MEM_ALLOC_PROFILING`, externs include `page_alloc_tagging_ops`, `alloc_tag_ref_mask`, `alloc_tag_ref_offs`, `kernel_tags`, and optional `module_tags`.
- `typedef u16 pgalloc_tag_idx` stores compact tag indexes. `union pgtag_ref_handle` carries a page extension and flags.
- Tag index constants are `CODETAG_ID_NULL`, `CODETAG_ID_EMPTY`, and `CODETAG_ID_FIRST`.
- Module/kernel conversion helpers include `module_idx_to_tag()`, `module_tag_to_idx()`, `idx_to_ref()`, and `ref_to_idx()`.
- Page reference helpers include `get_page_tag_ref()`, `put_page_tag_ref()`, `update_page_tag_ref()`, `__clear_page_tag_ref()`, `clear_page_tag_ref()`, `__pgalloc_tag_get()`, and `pgalloc_tag_get()`.
- Folio/lifecycle hooks include `pgalloc_tag_split()`, `pgalloc_tag_swap()`, and `alloc_tag_sec_init()`.
- Without `CONFIG_MEM_ALLOC_PROFILING`, all public helpers are no-op or return `NULL`.

## Control Flow
When profiling is enabled, page allocation paths acquire a page-extension codetag reference, encode or decode the allocation tag index, update the page reference, and release the handle. Clearing removes the tag reference from a page. Folio split/swap paths preserve or move tag accounting. Initialization sets up kernel and module tag sections. Disabled builds compile away the work.

## State And Persistence
Persistent profiling state lives in page extension records and allocation tag sections for kernel and modules. A page can carry a compact reference to the codetag that allocated it. Module tag indexes are offset from the kernel tag section and must remain valid while module tags exist.

## Dependencies And Integration Points
Depends on allocation tagging, page extensions, module support, folio/page types, and memory allocation profiling configuration. Integrates with page allocator instrumentation, module codetag sections, folio splitting/swapping, and allocation-profile reporting.

## Risks And Edge Cases
Risks include stale module tag references after module unload, index overflow in 16-bit `pgalloc_tag_idx`, incorrect kernel/module offset conversion, racing page-extension updates, leaked references if `put_page_tag_ref()` is missed, and losing tags across folio split/swap. Disabled stubs can hide missing profiling coverage in tests.

## Test Signals
Build with and without `CONFIG_MEM_ALLOC_PROFILING` and `CONFIG_MODULES`, allocate/free tagged pages, load/unload modules with allocation tags, split and swap folios, clear page tags, run page-extension debug checks, and verify reports attribute page allocations to expected codetags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgalloc_tag.h -->
