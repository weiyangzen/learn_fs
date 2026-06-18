# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/cacheflush.h

This header defines Alpha instruction-cache flush behavior. Kernel/module `flush_icache_range` maps to `imb()` on UP or `smp_imb()` on SMP. User-page flushing uses a cheaper ASN-context strategy: for executable VMAs, reload the active mm context or clear the per-CPU mm context so the next use gets a new address-space number.

Important APIs are `flush_icache_range`, `flush_icache_user_page`, and `flush_icache_pages`. The implementation relies on Alpha icache entries being ASN-tagged; it avoids indiscriminate user `imb` where changing ASN suffices. Dependencies include `linux/mm.h`, `current`, `smp_processor_id`, and `__load_new_mm_context`.

State effects are mm context updates and global instruction-stream barriers. Risks are stale instructions after ptrace/breakpoint/module writes, especially on SMP where the function is external. Test signals include module loading, ptrace breakpoints, executable page writes, and SMP icache shootdown behavior.
