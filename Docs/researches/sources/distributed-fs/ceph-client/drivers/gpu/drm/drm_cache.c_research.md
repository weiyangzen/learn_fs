# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_cache.c

## Purpose
`drm_cache.c` provides DRM cache flushing, DMA swiotlb decision support, and optimized or fallback copies from write-combined memory.

## Important APIs, Types, And Functions
Exported APIs are `drm_clflush_pages()`, `drm_clflush_sg()`, `drm_clflush_virt_range()`, `drm_need_swiotlb()`, `drm_memcpy_from_wc()`, and `drm_memcpy_init_early()`. Internals include x86 CLFLUSH helpers, PowerPC dcache flushing, `memcpy_fallback()`, x86 `movntdqa` copy helpers, and the `has_movntdqa` static branch.

## Control Flow
On x86, flush helpers use CLFLUSH with full memory barriers or fall back to `wbinvd_on_all_cpus()`. On PowerPC, pages are temporarily mapped and flushed with `flush_dcache_range()`. `drm_need_swiotlb()` returns true for Xen PV, memory encryption, or physical memory exceeding the DMA bit limit. `drm_memcpy_from_wc()` rejects interrupt-context fast path, uses non-temporal SSE loads when the static key is enabled, and otherwise falls back across system/I/O memory combinations with a stack bounce buffer for I/O-to-I/O copies.

## State And Persistence
Only `has_movntdqa` persists as runtime feature state. Other behavior acts on CPU caches, pages, sg tables, resources, and `iosys_map` pointers without durable persistence.

## Dependencies And Integration Points
The file integrates with architecture CPU features, highmem mapping, sg iteration, `iosys_map`, Xen, confidential-computing memory encryption attributes, FPU sections, and DRM buffer/GEM code.

## Risks And Edge Cases
Cache ordering is architecture-sensitive. The x86 optimized copy cannot run safely in interrupt context. The I/O-to-I/O fallback tail copies a full bounce buffer from source before writing the remaining length, which deserves scrutiny near mapping boundaries. DMA limit math and unsupported-architecture warning behavior are important integration points.

## Test Signals
Build and runtime tests should cover x86/PowerPC/fallback paths, static-key enablement, system/I/O/mixed copies, aligned and misaligned WC copies, Xen/encrypted-memory swiotlb decisions, and device-visible coherency after flushes.
