<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/nohash_low.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/nohash_low.S

## Purpose
This assembly file implements low-level TLB invalidation for 603/603e nohash Book3S32 CPUs.

## Important APIs, types, and functions
It defines `_GLOBAL(_tlbie)` on SMP and `_GLOBAL(_tlbia)` for full TLB invalidation. It uses `mmu_hash_lock`, `tlbie`, `TLBSYNC`, MSR EE/DR manipulation, and `TASK_CPU`.

## Control flow
`_tlbie` takes a physical lock with data relocation disabled, invalidates one address, synchronizes, releases the lock, restores MSR, and returns. `_tlbia` invalidates 32 page-sized entries starting at `KERNELBASE`, with SMP locking/synchronization when configured.

## State and persistence behavior
It changes hardware TLB state and temporarily changes MSR EE/DR. On SMP it mutates `mmu_hash_lock`.

## Dependencies and integration points
Called by nohash TLB flush code for 603-style processors.

## Risks and edge cases
The code must run safely with data relocation disabled and avoid SMP races. Full invalidation count/address range is processor-specific.

## Test signals
Stable TLB shootdowns, no stale translations after unmap, and correct SMP locking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/nohash_low.S -->
