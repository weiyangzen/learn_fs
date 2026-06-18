## sources/distributed-fs/ceph-client/include/linux/cacheflush.h

**Purpose:** This header supplies generic cache flush wrappers around architecture implementations.

**Important APIs/types/functions:** It includes `asm/cacheflush.h`, declares or stubs `flush_dcache_folio()` depending on `ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, provides a default no-op `flush_icache_pages()` if the architecture does not define it, and maps `flush_icache_page()` to a one-page call.

**Control flow, state, persistence:** Runtime behavior is architecture dependent. On non-implementing architectures the helpers are no-ops; on implementing architectures they synchronize data/instruction cache visibility for pages/folios.

**Dependencies/integration:** Integrates MM, filesystems, executable mappings, and architecture cache maintenance code. Uses `struct folio`, `struct vm_area_struct`, and `struct page` declarations from surrounding includes.

**Risks and test signals:** Risks are missing flushes on aliasing or non-coherent architectures, over-flushing hot paths, and assuming no-op behavior across all platforms. Test signals include executable mmap/write tests, D-cache aliasing tests, architecture cacheflush selftests, and cross-arch compile coverage.
