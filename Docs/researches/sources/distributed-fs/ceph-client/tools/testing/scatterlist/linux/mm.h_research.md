# sources/distributed-fs/ceph-client/tools/testing/scatterlist/linux/mm.h

Purpose: minimal userspace replacement for Linux memory-management helpers needed by scatterlist tests.

Important APIs/types/functions: defines page constants, alignment macros, `virt_to_page()`, `page_address()`, PFN/page conversion macros, `min()`/`min_t()`, allocation helpers `__get_free_page()`, `free_page()`, `kmalloc()`, `kmalloc_array()`, `kfree`, error pointer helpers `ERR_PTR()`, `PTR_ERR()`, `IS_ERR()`, and no-op kmemleak/cache helpers.

Control flow: most functions are inline wrappers around `malloc()`/`free()` or assert-only stubs for unsupported kernel operations such as `page_to_phys()` and kmap/kunmap.

State and persistence: heap allocations are process-local; no persistence.

Dependencies/integration: included by the copied scatterlist code and local tests to satisfy kernel API references in userspace.

Risks and test signals: unsupported functions intentionally `assert(0)`, so tests only cover scatterlist paths that do not require real page mapping or physical address translation. The fake `struct page *` model is pointer/PFN arithmetic, not a full page allocator.
