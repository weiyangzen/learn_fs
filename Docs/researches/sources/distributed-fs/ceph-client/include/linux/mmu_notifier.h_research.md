# sources/distributed-fs/ceph-client/include/linux/mmu_notifier.h

## Purpose
`mmu_notifier.h` defines the callback contract that lets secondary MMUs and device page-table users stay coherent with CPU page-table changes. It covers notifier events, subscription ops, interval notifiers, invalidate range setup, young/accessed-bit callbacks, secondary TLB invalidation, registration/lifetime APIs, and no-op fallbacks when MMU notifier support is disabled.

## Important APIs, Types, And Functions
Key types are `enum mmu_notifier_event`, `struct mmu_notifier_ops`, `struct mmu_notifier`, `struct mmu_interval_notifier_finish`, `struct mmu_interval_notifier_ops`, `struct mmu_interval_notifier`, and `struct mmu_notifier_range`. APIs include `mmu_notifier_get_locked()`, `mmu_notifier_get()`, `mmu_notifier_put()`, `mmu_notifier_synchronize()`, register/unregister helpers, `mmu_interval_read_begin()`, interval insert/remove helpers, `mmu_interval_set_seq()`, `mmu_interval_read_retry()`, `mmu_interval_check_retry()`, release/subscription destroy helpers, clear/test young helpers, invalidate range start/end variants, architecture secondary TLB invalidation, range init helpers, `mm_has_notifiers()`, and `mmu_notifier_range_blockable()`.

## Control Flow And State
Subscribers register against an `mm_struct`. MM teardown calls `release()` before freeing pages. Page-table operations create a `mmu_notifier_range`, call invalidate start while pages are still mapped, modify CPU page tables, then call invalidate end after unmapping/freeing. Nonblock start clears `MMU_NOTIFIER_RANGE_BLOCKABLE` and returns an error if a notifier would need to sleep. Interval notifiers use sequence numbers: readers snapshot with `mmu_interval_read_begin()`, invalidation callbacks set the odd sequence under the user's lock, and readers retry if the sequence changed. Subscription lists are protected by mmap/RMAP locks, RCU, and SRCU lifetime rules.

## Dependencies And Integration Points
Dependencies include lists, spinlocks, `mm_types.h`, `mmap_lock.h`, SRCU, and interval trees. Integration points include KVM and other secondary MMUs, GPU/IOMMU/SVA drivers, HMM/device-private memory migration, device-exclusive entries, aging/reclaim, soft-dirty tracking, mprotect, munmap, mremap, OOM reaping, TLB invalidation, and `mm_struct::notifier_subscriptions`.

## Risks And Test Signals
Risks include failing to block new secondary mappings during invalidation, sleeping in nonblock callbacks, missing start/end pairing, freeing pages while devices retain DMA/SPTE references, sequence misuse in interval readers, callback lifetime races, and implementing both failing start and end callbacks incorrectly. Test signals include KVM/GPU notifier stress, munmap/mprotect/migrate/OOM invalidation tests, nonblock `-EAGAIN` paths, SRCU synchronization tests, interval notifier retry tests, accessed-bit aging tests, and builds with `CONFIG_MMU_NOTIFIER` disabled.
