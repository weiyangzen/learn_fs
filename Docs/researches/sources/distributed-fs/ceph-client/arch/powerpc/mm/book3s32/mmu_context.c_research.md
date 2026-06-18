<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu_context.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu_context.c

## Purpose
This file manages Book3S32 address-space context IDs and segment register switching.

## Important APIs, types, and functions
It defines `abatron_pteptrs`, `__init_new_context`, `init_new_context`, `__destroy_context`, `destroy_context`, `mmu_context_init`, and `switch_mmu_context`. Static state is `next_mmu_context` and `context_map`.

## Control flow
Context allocation scans a bitmap of 32768 possible contexts, reserves context zero for the kernel, assigns `mm->context.id` and `sr0`, sets KUEP/KUAP segment bits, and clears context bits on destroy under preempt disable. Switching updates user segment registers, optional BDI debug PTE pointers, SDR1 for nohash CPUs, and wraps with barriers/isync.

## State and persistence behavior
It persists context allocation bitmap state, each mm's context ID and segment base, debug PTE pointers, and SDR1 on nohash context switches.

## Dependencies and integration points
Integrated with fork/exec/mm teardown, scheduler context switch, segment register helpers, KUAP/KUEP, BDI debug support, and nohash/hash MMU feature detection.

## Risks and edge cases
Context bitmap exhaustion/wrap, missing preempt disable on destroy, invalid `NO_CONTEXT` switches, and segment-register synchronization are key risks.

## Test signals
Stable process creation/destruction, no context ID leaks, correct per-process address spaces, and no panic in `switch_mmu_context`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/mmu_context.c -->
