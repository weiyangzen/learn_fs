# sources/distributed-fs/ceph-client/arch/powerpc/kernel/switch.S

## Purpose
Implements the low-level PowerPC context switch routine `_switch` plus Book3S 64-bit branch predictor/cache flush helpers and stack SLB pinning needed while switching kernel stacks.

## Important APIs, Types, and Functions
- `flush_branch_caches` is a patchable Book3S 64 helper for link stack/count cache flushing.
- `pin_stack_slb` bolts the next task stack SLB entry on hash MMU systems before switching SP.
- `do_switch_32` and `do_switch_64` macros update current/thread/PACA state and stack pointers.
- `_switch(prev_thread, next_thread)` saves nonvolatile GPRs, CCR, LR/NIP, old KSP, switches to the next stack/current, restores the next saved state, and returns previous task.

## Control Flow and State
On entry interrupts are disabled. `_switch` creates a switch frame on the old stack, saves nonvolatile state, updates architecture current pointers, optionally flushes branch prediction structures and user streams, pins the next stack mapping, then pivots `r1` to the new stack and restores the new task's saved frame.

## State and Persistence Behavior
Persists each task's kernel SP in `thread_struct.KSP` and updates PPC64 PACA fields for `current`, stack canary, and `PACAKSAVE`. The routine is the ordering point for task migration and relies on scheduler lock barriers for MMIO ordering.

## Dependencies and Integration Points
Depends on offsets generated in `asm-offsets.h`, PACA layout, KUAP checks, feature fixup patch sites, hash MMU SLB shadow structures, and `copy_thread()` creating frames compatible with `_switch`.

## Risks
Any offset/layout mismatch corrupts task stacks. Stack SLB handling is sensitive to hash versus radix MMU. Branch-cache flush patch sites mitigate speculation vulnerabilities and must stay aligned and correctly patched.

## Test Signals
Boot with stack protector, KUAP, hash/radix MMU, speculation mitigations, and heavy context-switch workloads. Verify forked tasks return through compatible frames and CPU migration preserves MMIO ordering assumptions.
