# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_native.c

Purpose: Implements the native bare-metal hash page table backend. It supplies the function table used by generic hash code to insert, remove, protect, invalidate, batch-flush, and clear HPTEs without hypervisor calls.

Important APIs and functions: `hpte_init_native()` registers `native_hpte_insert`, `native_hpte_remove`, `native_hpte_updatepp`, `native_hpte_updateboltedpp`, `native_hpte_removebolted`, `native_hpte_invalidate`, `native_hpte_clear`, `native_flush_hash_range`, and `native_hugepage_invalidate`. Local helpers include HPTE bit locking (`native_lock_hpte()`/`native_unlock_hpte()`), TLB invalidation primitives (`___tlbie()`, `__tlbie()`, `__tlbiel()`, `tlbie()`), `native_hpte_find()`, and `hpte_decode()`.

Control flow: Insert scans an HPTE group, locks an invalid entry, writes `r`, orders with `eieio()`, then writes valid `v` and releases the HPTE lock. Remove randomly scans a group for a valid non-bolted entry and clears it. Update-protection compares the encoded AVPN, locks and updates PPP/N/C bits, then invalidates the TLB unless suppressed. Invalidate clears a matching HPTE and always issues TLB invalidation because eviction may not flush. Batched flush first clears matching HPTEs for each recorded real PTE, then emits either local `tlbiel` or global `tlbie` operations with required barriers. Kexec clear walks the entire HPT and decodes entries without taking locks.

State and persistence: State is the global `htab_address` array and per-entry valid/bolted/lock bits. `native_tlbie_lock` serializes global TLB invalidation on CPUs lacking lockless `tlbie`. Lockdep state models HPTE locks.

Dependencies and integration: Depends on hash encoding helpers, CPU feature flags, tracepoints, `ppc64_tlb_batch`, and page-size definitions filled by `hash_utils.c`. It is selected during `hash__early_init_mmu()` when not using LPAR/PS3 backends.

Risks: Barrier placement is architecture-critical. Missing invalidation on remove/update can expose stale TLB entries. Kexec clear intentionally avoids locks and is unsafe outside the single-CPU/MMU-off context. POWER9 errata paths add extra invalidations and must track CPU feature bits.

Test signals: Boot native hash on POWER generations, kexec/crashdump, memory hotplug for bolted removal, THP invalidation, lockdep under HPTE contention, and TLB batching via `lazy_mmu_mode` are strong signals. Trace `tlbie` events can confirm expected flush scope.
