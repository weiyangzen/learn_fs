<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atomic.h

## Purpose
This header implements m68k `atomic_t` operations for the Linux atomic API. It uses inline assembly for native memory operations and switches between CAS-based read-modify-write instructions and interrupt-disabled fallbacks depending on CPU capability.

## Important APIs, Types, And Functions
- `arch_atomic_read()` and `arch_atomic_set()` use `READ_ONCE` and `WRITE_ONCE`.
- Generated operations implement add, sub, and/or/xor plus return and fetch variants.
- `arch_atomic_inc()`, `arch_atomic_dec()`, `arch_atomic_dec_and_test()`, `arch_atomic_inc_and_test()`, `arch_atomic_sub_and_test()`, and `arch_atomic_add_negative()` use condition-code setting assembly.
- When `CONFIG_RMW_INSNS` is absent, `arch_atomic_cmpxchg()` and `arch_atomic_xchg()` are implemented under `local_irq_save()`.
- `ASM_DI` handles ColdFire immediate-to-memory instruction constraints.

## Control Flow
Most operations expand inline at call sites. CAS-capable builds loop around `casl` until the memory word updates successfully. Non-RMW builds disable local interrupts, update `v->counter`, and restore interrupts to provide uniprocessor atomicity.

## State And Persistence Behavior
The only state mutated is the target atomic counter. Local interrupt flags are temporarily saved/restored on fallback paths. The design assumes no SMP m68k systems.

## Dependencies And Integration Points
It depends on Linux atomic types, irqflags, m68k `cmpxchg`, and barrier definitions. It underpins reference counts, flags, and synchronization throughout the kernel on m68k.

## Risks And Edge Cases
The implementation relies on uniprocessor assumptions; it is not an SMP-safe design without hardware atomics. Inline assembly constraints differ for ColdFire. Missing memory clobbers or wrong output constraints would create subtle races.

## Test Signals
Cross-build ColdFire, non-RMW, and RMW configs. Run atomic API selftests, refcount stress, interrupt-heavy tests around fallback paths, and compare return/fetch semantics for add/sub/bitwise operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atomic.h -->
