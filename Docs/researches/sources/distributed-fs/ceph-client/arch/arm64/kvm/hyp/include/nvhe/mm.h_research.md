# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mm.h

## Purpose

This header declares nVHE/pKVM hypervisor virtual-memory setup and mapping APIs.

## Important APIs, Types, And Functions

It exports `pkvm_pgtable` and `pkvm_pgd_lock`, and declares fixmap/fixblock helpers, `hyp_create_idmap()`, `hyp_map_vectors()`, `hyp_back_vmemmap()`, `pkvm_cpu_set_vector()`, mapping creation helpers, `__pkvm_create_private_mapping()`, `pkvm_create_stack()`, and `pkvm_alloc_private_va_range()`.

## Control Flow

Callers create the hyp ID map, map vectors, back the vmemmap, allocate private VA ranges, create protected mappings, and temporarily map physical pages through per-CPU fixmap/fixblock slots.

## State And Persistence Behavior

Persistent state includes the protected hyp page table, page-table lock, private VA allocator state in implementation, vector mapping, fixmap slots, and vmemmap backing.

## Dependencies And Integration Points

It integrates with nVHE setup, pKVM stack creation, host/hyp sharing, protected mappings, and spectre vector selection.

## Risks And Test Signals

Risks are missing lock coverage, VA range exhaustion, stale fixmap entries, executable vector mapping mistakes, and private mapping permission errors. Test signals are pKVM init, per-CPU stack mappings, vector remap selection, fixmap map/unmap pairing, and vmemmap access during allocation.
