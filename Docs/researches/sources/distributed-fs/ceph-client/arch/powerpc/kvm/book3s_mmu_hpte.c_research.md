# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_mmu_hpte.c

Purpose: this file implements the PR Book3S shadow HPTE cache. It indexes translated guest mappings by effective address, virtual page, and physical range so KVM can invalidate shadow mappings efficiently when the guest or host memory state changes.

Important APIs: `kvmppc_mmu_hpte_cache_map()` inserts a `struct hpte_cache` into several RCU hlist hash tables. `kvmppc_mmu_pte_flush()`, `kvmppc_mmu_pte_vflush()`, and `kvmppc_mmu_pte_pflush()` invalidate by effective address mask, virtual page mask, or physical address range. `kvmppc_mmu_hpte_cache_next()` allocates cache entries and flushes everything when the per-vCPU cache reaches `HPTEG_CACHE_NUM`. `kvmppc_mmu_hpte_init()`, `destroy()`, `sysinit()`, and `sysexit()` initialize per-vCPU hash heads and the slab cache.

Control flow: mappings are hashed into short and long EA lists, short and long virtual-page lists, and on 64-bit builds a 64K VPTE list. Flush helpers compute the matching hash bucket, scan under RCU, and call `invalidate_pte()`. `invalidate_pte()` invokes the architecture MMU invalidation callback, removes every list node under `mmu_lock`, decrements `hpte_cache_count`, and releases the cache object through `kfree_rcu()`.

State and persistence: persistent state is per-vCPU in `struct kvmppc_vcpu_book3s`: hlist arrays, `mmu_lock`, and `hpte_cache_count`. Global state is the `hpte_cache` slab. The cached entries mirror active shadow mappings and are not guest-persistent state.

Dependencies and integration: it depends on Linux RCU lists, spinlocks, the Book3S MMU callback table, hash helpers, and tracepoints from `trace_pr.h`. It is used by PR fault handling, MMU notifier invalidation, dirty-log flushing, and HPT/TLB invalidation paths.

Risks: invalidation is RCU plus spinlock based; double invalidation is handled by checking `hlist_unhashed()`, but callback ordering must remain correct. Unsupported masks trigger `WARN_ON(1)`. Complete flush iterates the long VPTE hash and invalidates while traversing under RCU, so list deletion assumptions matter.

Test signals: guest TLB invalidation instructions, memslot unmap, dirty logging, physical range invalidation, 64K page guests, cache saturation, and concurrent vCPU faults should be exercised. Watch for stale translations, missing MMIO exits, RCU misuse warnings, and incorrect `hpte_cache_count`.
