# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/mem_protect.h

## Purpose

This header declares pKVM/nVHE memory ownership, sharing, donation, reclaim, host stage-2, and guest stage-2 protection interfaces.

## Important APIs, Types, And Functions

It defines `struct host_mmu`, `enum pkvm_component_id`, exports `host_mmu`, and declares many `__pkvm_*` host/hyp/guest share, unshare, donate, reclaim, permission, young-bit, VM teardown, and memcache functions. `__load_host_stage2()` loads host stage-2 or disables `VTTBR_EL2`.

## Control Flow

Callers finalize protection, prepare host/guest stage-2 tables, perform ownership transitions under locking, handle host memory aborts, pin/unpin shared memory, reclaim page-table pages, and refill hyp memcaches. `__load_host_stage2()` selects protected host stage-2 once protected mode is initialized.

## State And Persistence Behavior

Persistent state includes host stage-2 page tables, host MMU lock, hyp vmemmap ownership states, guest PTE software ownership bits, memcaches, and pKVM component ownership.

## Dependencies And Integration Points

It integrates with pKVM VM structures, hyp allocator, spinlocks, FFA sharing, host S2 loading, and KVM page-table walkers.

## Risks And Test Signals

Risks are ownership leaks, wrong lock order, stale host S2 mappings, reclaiming live guest pages, and mismatched permissions. Test signals are pKVM protected boot, host share/unshare/donate workflows, guest page reclaim, host abort handling, and ownership selftests under `CONFIG_NVHE_EL2_DEBUG`.
