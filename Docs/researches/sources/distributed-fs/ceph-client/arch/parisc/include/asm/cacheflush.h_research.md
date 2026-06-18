# sources/distributed-fs/ceph-client/arch/parisc/include/asm/cacheflush.h

Purpose: defines PA-RISC cache-flush interfaces used by memory management, vmalloc, folio/page writeback, and executable mapping updates.

Important APIs/types/functions: declares static keys for cache presence, assembly flush routines, `flush_cache_all`, `flush_cache_mm`, `flush_kernel_dcache_range`, `flush_kernel_vmap_range`, `invalidate_kernel_vmap_range`, `flush_dcache_folio`, `flush_dcache_page`, `flush_icache_range`, `flush_anon_page`, and `kunmap_flush_on_unmap`.

Control flow: callers select full-cache, mm, vmap, folio, page, or icache range flushing; static keys skip work on cacheless configurations.

State and persistence: no ordinary state, but cache contents and instruction visibility are affected. Dependencies and integration: depends on `mm.h`, `uaccess.h`, TLB flushing, jump labels, and page cache mappings.

Risks and test signals: missed D/I cache synchronization breaks newly generated code, modules, and userspace mappings. Test with module loading, JIT-like mprotect tests, mmap write/exec tests, and aliasing-cache workloads.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
