# sources/distributed-fs/ceph-client/virt/kvm/kvm_mm.h

## Purpose
This header centralizes common KVM memory-management helpers shared by `kvm_main.c`, guest_memfd, pfncache, and architecture code. It abstracts the MMU lock type, declares PFN-following state, exposes the common HVA-to-PFN resolver, and provides compile-time stubs for optional PFN cache and guest_memfd support.

## Important APIs, Types, And Functions
`KVM_MMU_LOCK_INIT`, `KVM_MMU_LOCK`, and `KVM_MMU_UNLOCK` map to either rwlock write locking or spinlock operations depending on `KVM_HAVE_MMU_RWLOCK`. `struct kvm_follow_pfn` describes a GFN/HVA lookup: source memslot/GFN, HVA, FOLL flags, whether the caller needs a pin, optional writable mapping reporting, and an output `struct page`. `hva_to_pfn()` is the common resolver implemented in `kvm_main.c`. `gfn_to_pfn_cache_invalidate_start()` is real only with `CONFIG_HAVE_KVM_PFNCACHE`. Guest_memfd functions are declared with `CONFIG_KVM_GUEST_MEMFD`, otherwise stubs return success for init/exit and warn/fail for bind/unbind.

## Control Flow And State
The header does not own persistent state, but it sets the locking contract for common MMU invalidation and the data contract for PFN resolution. Callers fill `struct kvm_follow_pfn`, call `hva_to_pfn()`, and then release or unpin the resulting page according to whether `pin` and `refcounted_page` were used.

## Dependencies And Integration Points
The macros depend on architecture configuration. The declarations couple `pfncache.c`, `guest_memfd.c`, and `kvm_main.c` without forcing optional code into builds where the feature is disabled.

## Risks And Test Signals
Risks include mismatched lock assumptions across architectures, incorrect page lifetime expectations for `pin`, and callers treating stubbed guest_memfd bind/unbind as usable. Build coverage should include rwlock and spinlock MMU-lock architectures, PFN cache enabled/disabled, and guest_memfd enabled/disabled configurations.
