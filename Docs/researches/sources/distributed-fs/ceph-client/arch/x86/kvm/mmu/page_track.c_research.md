# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.c

## Purpose
Implements KVM x86 guest page write tracking. The file maintains per-memslot write-track reference counts, write-protects tracked GFNs, blocks large-page mappings for tracked pages, and optionally exposes an external notifier API under `CONFIG_KVM_EXTERNAL_WRITE_TRACKING`. Its immediate consumers are the MMU write-protection paths and external users that need callbacks when guest memory writes are emulated or memslots are removed.

## Important APIs, Types, and Functions
- `kvm_page_track_write_tracking_enabled()` enables tracking if external tracking is active, a shadow root exists, or TDP is disabled.
- `kvm_page_track_create_memslot()`, `kvm_page_track_write_tracking_alloc()`, and `kvm_page_track_free_memslot()` allocate/free `slot->arch.gfn_write_track`.
- `__kvm_write_track_add_gfn()` and `__kvm_write_track_remove_gfn()` update per-GFN counters under `mmu_lock`, adjust large-page eligibility, and write-protect mappings on add.
- `kvm_gfn_is_write_tracked()` reads the per-slot count with `READ_ONCE`.
- External-tracking-only APIs include `kvm_page_track_init()`, `kvm_page_track_cleanup()`, `kvm_page_track_register_notifier()`, `kvm_page_track_unregister_notifier()`, `__kvm_page_track_write()`, `kvm_page_track_delete_slot()`, `kvm_write_track_add_gfn()`, and `kvm_write_track_remove_gfn()`.

## Control Flow
Memslot creation calls `kvm_page_track_create_memslot()`, which allocates tracking storage only when tracking can be used. External registration first validates the VM belongs to the current mm, enables external write tracking by allocating metadata for all slots, then inserts a notifier into an RCU hlist under `mmu_lock`. Adding a tracked GFN increments the slot counter, disallows large pages for that GFN, and invokes `kvm_mmu_slot_gfn_write_protect()`, flushing remote TLBs if SPTEs changed. Emulated writes call the header wrapper `kvm_page_track_write()`, which first dispatches external notifier callbacks through SRCU and then notifies KVM's internal MMU tracking.

## State and Persistence
The persistent VM state is `kvm->arch.external_write_tracking_enabled`, `kvm->arch.track_notifier_head`, and each slot's `arch.gfn_write_track` array. Counts are reference counts, not booleans, so multiple users can track the same GFN. Memory survives failed enablement attempts until the slot is freed, intentionally avoiding partial-allocation rollback complexity. State is protected by `slots_arch_lock`, `mmu_lock`, `slots_lock`/SRCU, notifier SRCU, and RCU list primitives.

## Dependencies and Integration Points
Depends on `linux/kvm_host.h`, RCU/SRCU hlist helpers, `mmu.h`, `mmu_internal.h`, and `page_track.h`. It integrates with memslot lifecycle, shadow/TDP MMU write protection, large-page disallow accounting, external notifier nodes from `asm/kvm_page_track.h`, TDX restrictions (`KVM_X86_TDX_VM` cannot enable external tracking), and exported GPL APIs for external modules.

## Risks
Counter overflow/underflow is guarded by `WARN_ON_ONCE`, but callers still must pair add/remove operations. Missing `mmu_lock` or slot/SRCU protection would corrupt counts or race memslot teardown. Enabling external tracking after VM creation allocates metadata for every memslot; failure leaves allocations behind intentionally, which is safe but can surprise resource accounting. Notifier callbacks run under SRCU and must not assume MMU locks.

## Test Signals
Useful tests include write-track add/remove refcount pairing, write-protection and TLB flush observation, large-page split/disallow behavior for tracked GFNs, external notifier registration/unregistration lifetime with concurrent writes, memslot removal callback delivery, failure on TDX VMs, and no-op behavior when `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` is disabled.
