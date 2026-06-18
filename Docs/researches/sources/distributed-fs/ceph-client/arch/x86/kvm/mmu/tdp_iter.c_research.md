# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu/tdp_iter.c

## Purpose
Implements the pre-order iterator over TDP MMU page tables. The iterator abstracts page-table descent, side-stepping, ascent, restart-after-yield, and SPTE refresh for code that zaps, maps, ages, write-protects, or scans TDP mappings.

## Important APIs, Types, and Functions
- `tdp_iter_start()` initializes a walk from a root, minimum level, start GFN, and root GFN mask bits.
- `tdp_iter_restart()` restarts the walk at the root after yielding.
- `tdp_iter_next()` advances to the next SPTE in pre-order.
- `spte_to_child_pt()` converts a present non-leaf SPTE to the child table virtual address.
- Internal helpers `tdp_iter_refresh_sptep()`, `try_step_down()`, `try_step_side()`, and `try_step_up()` implement traversal.

## Control Flow
Initialization validates the root level, records root metadata, stores the root page table in `pt_path`, and calls restart. Each advance first restarts if the walk yielded. Otherwise it attempts to descend into a present non-leaf SPTE, then moves sideways within the current page table, and finally walks up until a sideways move is possible. If no move remains, the iterator becomes invalid.

## State and Persistence
The iterator state is transient: current `sptep`, `old_spte`, `gfn`, level, root level, minimum level, ASID, path of page-table pointers, yielded markers, and optional GFN mask bits. Persistent state is only read through RCU-safe SPTE loads.

## Dependencies and Integration Points
Depends on `mmu_internal.h`, `tdp_iter.h`, and `spte.h`. It is the traversal core for `tdp_mmu.c` macros and functions such as mapping, zapping, aging, dirty clearing, hugepage split/recovery, and lockless walks.

## Risks
The iterator deliberately rereads SPTEs before descent to avoid walking into unlinked page tables. Incorrect `gfn_bits` or rounding can break mirrored/private address-space walks. Yield/restart semantics require callers to skip the current loop body after `tdp_mmu_iter_cond_resched()` sets `iter->yielded`.

## Test Signals
Validate traversal order across sparse and populated page tables, range boundaries, min-level stopping, huge leaf handling, restart-after-yield progress, root-level validation warnings, and lockless scans under concurrent SPTE changes.
