# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/page_track.h

## Purpose
Declares the KVM x86 page-tracking interface used by MMU code and optional external write-tracking users. It also provides disabled-configuration stubs so callers can keep simple control flow when `CONFIG_KVM_EXTERNAL_WRITE_TRACKING` is absent.

## Important APIs, Types, and Functions
- Declares memslot tracking allocation/free APIs and internal add/remove/query helpers.
- Under `CONFIG_KVM_EXTERNAL_WRITE_TRACKING`, declares VM init/cleanup, external write callback dispatch, and memslot delete notification.
- `kvm_page_track_has_external_user()` tests the notifier hlist.
- `kvm_page_track_write()` is the key inline integration point: it calls `__kvm_page_track_write()` for external users and always calls `kvm_mmu_track_write()` for internal shadow-MMU tracking.

## Control Flow
The header separates external-notifier support from core write tracking. When external tracking is disabled, `kvm_page_track_init()`, cleanup, write notification, deletion notification, and external-user detection compile to no-ops, while internal MMU write tracking through `kvm_page_track_write()` remains active.

## State and Persistence
No direct state is stored in the header, but it exposes `struct kvm_memory_slot` tracking storage and the VM notifier head used by `page_track.c`. The inline wrapper persists the contract that every tracked write reaches internal MMU logic regardless of external configuration.

## Dependencies and Integration Points
Includes `linux/kvm_host.h` and `asm/kvm_page_track.h`. Integrates with x86 MMU write emulation, memslot setup/teardown, and external notifier node definitions.

## Risks
The split between external tracking and always-on internal tracking means callers must use the wrapper `kvm_page_track_write()` rather than directly calling only the external hook. The disabled stubs intentionally hide external callbacks, so tests must cover both build configurations.

## Test Signals
Build coverage with and without `CONFIG_KVM_EXTERNAL_WRITE_TRACKING`, write-emulation paths invoking internal `kvm_mmu_track_write()`, notifier presence detection, and static analysis that memslot allocation/free declarations match implementation.
