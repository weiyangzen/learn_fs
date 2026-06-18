# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-amo.h

## Purpose

`atomic-amo.h` implements LoongArch atomic operations using AMO instructions. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Macros generate `arch_atomic_*` add/sub/and/or/xor operations, return variants, fetch variants, and relaxed/acquire/release/full-barrier forms. Concrete declarations observed in the file: Includes: `linux/types.h`, `asm/barrier.h`, `asm/cmpxchg.h`. Macros: `_ASM_ATOMIC_AMO_H`, `ATOMIC_OP`, `ATOMIC_OP_RETURN`, `ATOMIC_FETCH_OP`, `ATOMIC_OPS`, `arch_atomic_add_return`, `arch_atomic_add_return_acquire`, `arch_atomic_add_return_release`, `arch_atomic_add_return_relaxed`, `arch_atomic_sub_return`, `arch_atomic_sub_return_acquire`, `arch_atomic_sub_return_release`, `arch_atomic_sub_return_relaxed`, `arch_atomic_fetch_add`, `arch_atomic_fetch_add_acquire`, `arch_atomic_fetch_add_release`, `arch_atomic_fetch_add_relaxed`, `arch_atomic_fetch_sub`, `arch_atomic_fetch_sub_acquire`, `arch_atomic_fetch_sub_release`, `arch_atomic_fetch_sub_relaxed`, `arch_atomic_fetch_and`, `arch_atomic_fetch_and_acquire`, `arch_atomic_fetch_and_release`, and 41 more.

## Control Flow, State, And Persistence

Runtime flow is a single AMO-based read-modify-write sequence with optional barriers selected by the generated variant.

## Dependencies And Integration Points

It integrates with `atomic.h`, barrier primitives, cmpxchg support, locking, refcounts, and generic atomic APIs.

## Risks And Test Signals

Risks are missing memory ordering, incorrect old/new return values, and CPU support assumptions. Test signals are atomic selftests, lock/refcount stress, KCSAN, and SMP boot.
 A local static signal for this file is that it has 207 lines and 7349 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
