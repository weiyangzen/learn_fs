# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm_page_track.h

## Purpose
Defines the optional external write-tracking notifier interface for x86 KVM memory pages. It lets external KVM subsystems observe guest writes to tracked GFNs and be notified when tracked regions disappear.

## Important APIs, Types, And Functions
When `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` is enabled, `struct kvm_page_track_notifier_head` owns an SRCU domain and notifier hlist, while `struct kvm_page_track_notifier_node` provides `track_write()` and `track_remove_region()` callbacks. Public helpers are `kvm_page_track_register_notifier()`, `kvm_page_track_unregister_notifier()`, `kvm_write_track_add_gfn()`, and `kvm_write_track_remove_gfn()`. With the config disabled, an empty notifier node preserves embeddability.

## Control Flow
Registration links a notifier into the VM head under KVM MMU protection. When a guest write to a write-protected tracked page is emulated, KVM invokes `track_write()` after the write completes. When a memslot is deleted, `track_remove_region()` reports the removed GFN range. Add/remove helpers adjust write tracking reference counts for individual GFNs.

## State And Persistence
State is transient VM metadata: the notifier list, SRCU tracking domain, and per-memslot write-track counters referenced through KVM architecture memory-slot state. There is no durable storage.

## Dependencies And Integration Points
Depends on `linux/kvm_types.h`, `struct kvm`, `gpa_t`, and `gfn_t`. It integrates with x86 KVM MMU write protection, memslot lifecycle, and optional consumers such as external shadow paging or accelerator modules.

## Risks And Edge Cases
Callbacks run in sensitive MMU/write-emulation paths and must respect SRCU and KVM lock ordering. Counter imbalance can leave pages over-protected or untracked. Region removal callbacks must tolerate large ranges and memslot teardown. The disabled-config empty struct must remain valid for direct header inclusion tests.

## Test Signals
Useful coverage includes KVM selftests or module tests that register a notifier, add and remove tracked GFNs, verify callback order after emulated writes, delete memslots, and build with `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` both enabled and disabled.
