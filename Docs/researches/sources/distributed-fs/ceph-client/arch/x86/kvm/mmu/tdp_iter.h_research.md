# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.h

## Purpose
Declares the TDP MMU iterator and low-level RCU-aware SPTE read/write helpers. It is the contract between generic TDP MMU code and the traversal implementation.

## Important APIs, Types, and Functions
- `kvm_tdp_mmu_read_spte()`, `kvm_tdp_mmu_write_spte_atomic()`, `tdp_mmu_clear_spte_bits_atomic()`, and `__kvm_tdp_mmu_write_spte()` wrap RCU dereference and atomic/plain SPTE writes.
- `kvm_tdp_mmu_spte_need_atomic_update()`, `kvm_tdp_mmu_write_spte()`, and `tdp_mmu_clear_spte_bits()` select atomic updates when volatile leaf bits can be modified outside `mmu_lock`.
- `struct tdp_iter` stores traversal state.
- `for_each_tdp_pte_min_level()`, `for_each_tdp_pte_min_level_all()`, and `for_each_tdp_pte()` provide range-walk macros.

## Control Flow
Callers begin RCU protection, initialize an iterator with one of the macros, inspect `iter.old_spte`, modify SPTEs through the write helpers, and call `tdp_iter_next()` automatically through the loop macro. Update helpers choose `xchg`/atomic fetch-and or `WRITE_ONCE` depending on whether an SPTE is a shadow-present leaf with volatile dirty/writable/access-tracking state.

## State and Persistence
The header encodes the concurrency contract for persistent TDP page tables: non-leaf page tables are RCU-protected; zapping flows must flush pending TLBs before dropping RCU protection where needed; volatile leaf bits require atomic writes to preserve CPU/fast-fault updates.

## Dependencies and Integration Points
Includes KVM host headers, `mmu.h`, and `spte.h`. Used by TDP MMU mutation, fast page fault lookup, lockless walks, aging, dirty logging, and zapping code.

## Risks
Plain writes to SPTEs that need atomic updates can lose Dirty or writable transitions. Atomic writes warn on EPT #VE-possible encodings. The returned `old_spte` from write helpers may differ from the caller's snapshot and must be used for bookkeeping.

## Test Signals
Exercise atomic versus plain write selection, dirty-bit preservation, access-tracking restoration, clear-bit behavior, RCU walk contracts, and compile/runtime checks for EPT #VE-suppression invariants.
