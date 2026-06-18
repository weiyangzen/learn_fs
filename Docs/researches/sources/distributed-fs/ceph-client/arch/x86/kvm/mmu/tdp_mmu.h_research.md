# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_mmu.h

## Purpose
Declares the public TDP MMU interface used by KVM x86 MMU, memslot, notifier, dirty logging, fast page fault, and vendor code. It also defines root-type filters for direct versus mirrored/private roots.

## Important APIs, Types, and Functions
- Lifecycle declarations: `kvm_mmu_init_tdp_mmu()`, `kvm_mmu_uninit_tdp_mmu()`, `kvm_tdp_mmu_alloc_root()`, `kvm_tdp_mmu_get_root()`, and `kvm_tdp_mmu_put_root()`.
- `enum kvm_tdp_mmu_root_types` distinguishes invalid, direct, mirror, valid, and all roots.
- `kvm_gfn_range_filter_to_root_types()` maps memslot notifier private/shared filters to root classes.
- `tdp_mmu_get_root_for_fault()` and `tdp_mmu_get_root()` select normal or mirror root for a fault or operation.
- Declares zap, invalidate, map, unmap, age, write-protect, dirty clear, hugepage split/recovery, lockless walk, and fast-PF lookup APIs.
- `is_tdp_mmu_page()` is architecture-gated.

## Control Flow
Callers use the header to route operations by root type and address privacy. Fault handlers select the mirror root if the address is not direct; range invalidators use private/shared filters to process mirror and/or direct roots; lockless walkers must bracket with `kvm_tdp_mmu_walk_lockless_begin/end()`.

## State and Persistence
The header exposes root references via refcount increment/decrement and relies on implementation-managed RCU lifetime. No state is stored here, but the APIs define which operations require persistent root references and which can use current vCPU root pointers.

## Dependencies and Integration Points
Includes `linux/kvm_host.h` and `spte.h`. Integrated by x86 MMU core, memslot/MMU notifier code, dirty logging, fast page fault, TDX/private memory handling, and vendor modules.

## Risks
Misclassifying root filters can skip private or shared mappings, leaving stale translations. Lockless walk callers must obey the RCU lifetime contract and not use returned SPTE pointers after `walk_lockless_end`. Root references from `tdp_mmu_get_root_for_fault()` are raw page metadata pointers and depend on vCPU-held root lifetime.

## Test Signals
Exercise direct versus mirror root selection, GFN range filter mapping, lockless walk bracketing, root refcount get/put, invalidated-root processing, and build coverage on non-64-bit configurations where TDP pages are always false.
