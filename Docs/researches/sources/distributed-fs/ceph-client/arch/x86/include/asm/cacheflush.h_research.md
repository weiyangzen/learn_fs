
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cacheflush.h

Purpose: x86 cache flush interface wrapper.

Important APIs and control flow: includes generic cacheflush behavior and x86 special instructions, then declares `clflush_cache_range(void *addr, unsigned int size)` for explicit cache-line flushing over a range.

State, dependencies, and risks: state is CPU cache contents and memory attributes, not software storage. Dependencies include generic mm cacheflush APIs and x86 `clflush` support paths. Risks include flushing wrong ranges, assuming coherency effects for DMA or persistent memory beyond what the primitive guarantees, and CPU feature variation. Test signals are persistence/pmem flush tests, driver cache-maintenance users, and build coverage.
