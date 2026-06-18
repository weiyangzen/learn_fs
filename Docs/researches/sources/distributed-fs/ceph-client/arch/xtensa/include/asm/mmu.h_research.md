<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu.h

## Purpose
Defines the Xtensa per-mm context type for MMU builds and delegates noMMU builds to generic context support.

## Important APIs, Types, And Functions
For MMU builds, defines `mm_context_t` with `asid[NR_CPUS]` and `cpu`. For noMMU, includes `asm-generic/mmu.h`.

## Control Flow
No runtime control in this header.

## State And Persistence
`mm_context_t` persists in each `mm_struct`, tracking per-CPU ASIDs and the last CPU using the context.

## Dependencies And Integration Points
Used by `mmu_context.h`, scheduler context switching, TLB management, and generic MM.

## Risks And Edge Cases
ASID arrays must scale with `NR_CPUS`; stale CPU tracking can miss icache flushes or ASID refresh.

## Test Signals
Run process creation/exit, context-switch stress, SMP migration, and noMMU build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu.h -->
