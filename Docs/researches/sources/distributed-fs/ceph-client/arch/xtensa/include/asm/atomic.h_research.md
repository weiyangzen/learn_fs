<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/atomic.h

## Purpose
Implements Xtensa 32-bit atomic integer operations used by the generic atomic API.

## Important APIs, Types, And Functions
Defines `arch_atomic_read`, `arch_atomic_set`, and generated `arch_atomic_add/sub/and/or/xor`, return variants for add/sub, and fetch variants. Implementations select `l32ex/s32ex`, `s32c1i`, or interrupt-level critical sections depending on core features.

## Control Flow
For exclusive-load cores, operations loop on `l32ex`, compute, `s32ex`, and `getex` until success. For `s32c1i`, they set `scompare1`, attempt conditional store, and retry on mismatch. For older cores, they raise interrupt level to `TOPLEVEL`, perform load/modify/store, restore PS, and `rsync`.

## State And Persistence
Only modifies target `atomic_t` values and CPU special registers transiently. No durable state.

## Dependencies And Integration Points
Depends on Xtensa core feature macros, barriers, cmpxchg, processor interrupt levels, and the generic atomic wrapper layer.

## Risks And Edge Cases
The interrupt-disabled fallback uses `a14` to avoid window overflow hazards and must not be interrupted by register-window traps. Memory clobbers and barriers must satisfy SMP semantics. S32C1I behavior depends on AtomCtl/cache configuration.

## Test Signals
Run atomic and locking selftests on exclusive, S32C1I, and fallback cores; stress SMP counters, qspinlocks, refcounts, and KCSAN/lockdep builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/atomic.h -->
