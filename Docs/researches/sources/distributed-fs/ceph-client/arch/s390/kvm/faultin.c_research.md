# sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.c

## Purpose
Resolves guest frame faults into host PFNs and links them into the s390 gmap. It centralizes the slow path that faults host userspace memory in, handles async pfault setup, coordinates with KVM MMU invalidation sequencing, and releases pinned pages correctly.

## Important APIs, Types, And Functions
Exports `kvm_s390_faultin_gfn` and `kvm_s390_get_guest_page`. It uses `struct guest_fault` from `dat.h`, `gmap_try_fixup_minor`, `gmap_link`, `kvm_s390_new_mmu_cache`, `kvm_s390_mmu_cache_topup`, `__kvm_faultin_pfn`, `kvm_release_faultin_page`, `mmu_invalidate_retry_gfn_unsafe`, and `mmu_invalidate_retry_gfn`. It calls architecture async-page-fault setup via `kvm_arch_setup_async_pf`.

## Control Flow
`kvm_s390_faultin_gfn` first attempts a minor gmap fixup under `kvm->mmu_lock` read lock. If that fails, it repeatedly faults the GFN through the appropriate memslot, optionally using `FOLL_NOWAIT` for pfault attempts. `KVM_PFN_ERR_NEEDS_IO` either establishes async pfault for a vCPU or falls back to synchronous faulting. Addressing, signal, read-only, and generic error PFNs are converted to guest exception or kernel error returns. Once a PFN is available, the function checks invalidation sequence races, links the mapping under `mmu_lock`, releases the faulted page with the right dirty/error semantics, tops up the MMU cache on `-ENOMEM`, and retries on `-EAGAIN`.

`kvm_s390_get_guest_page` is a lighter helper that faults and pins a page for explicit users such as shadow-table walks without linking it into the gmap.

## State And Persistence
State is transient fault state in `struct guest_fault`: `gfn`, `pfn`, `page`, `writable`, `write_attempt`, `attempt_pfault`, `valid`, and optional callback/private data. The function mutates the VM gmap by calling `gmap_link`; it also updates vCPU pfault statistics. No durable persistence is involved.

## Dependencies And Integration Points
Depends on KVM memslots, SRCU protection, KVM MMU invalidation sequence barriers, s390 gmap mapping code, async pfault support, and page-release accounting. It is used by ordinary DAT fault handling, absolute guest access helpers, atomic guest cmpxchg, and vSIE shadow construction.

## Risks And Edge Cases
The caller must hold `kvm->srcu` and must not hold the mm lock. Missing invalidation retries can link stale PFNs. Page release must match whether the page was consumed, dirtied, or abandoned. Async pfault is only valid for vCPU context and `FOLL_NOWAIT`. `KVM_PFN_ERR_RO_FAULT` intentionally returns `-EOPNOTSUPP`; higher layers must decide how to handle read-only mappings.

## Test Signals
Useful coverage includes guest page faults, async pfault enabled/disabled cases, memslot deletion races, MMU notifier invalidations during fault-in, read-only memslot writes, signal interruption, dirty writeback on release, gmap minor-fault fast path, and nested/vSIE shadow faults that pin multiple pages.
