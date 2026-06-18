# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic-llsc.h

## Purpose

`atomic-llsc.h` implements LoongArch atomic operations using load-linked/store-conditional loops. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Macros generate `arch_atomic_*` add/sub and bitwise operations with retry loops and relaxed variants. Concrete declarations observed in the file: Includes: `linux/types.h`, `asm/barrier.h`, `asm/cmpxchg.h`. Macros: `_ASM_ATOMIC_LLSC_H`, `ATOMIC_OP`, `ATOMIC_OP_RETURN`, `ATOMIC_FETCH_OP`, `ATOMIC_OPS`, `arch_atomic_add_return_relaxed`, `arch_atomic_sub_return_relaxed`, `arch_atomic_fetch_add_relaxed`, `arch_atomic_fetch_sub_relaxed`, `arch_atomic_fetch_and_relaxed`, `arch_atomic_fetch_or_relaxed`, `arch_atomic_fetch_xor_relaxed`.

## Control Flow, State, And Persistence

Runtime flow loads the old value, computes a new value, attempts store-conditional, and retries until success; higher-level ordering is supplied through barriers/wrappers.

## Dependencies And Integration Points

It integrates with `atomic.h` as the fallback/alternative to AMO instructions.

## Risks And Test Signals

Risks are livelock under contention, missing clobbers, and ordering mismatch. Test signals are atomic torture tests, lock stress, and SMP contention benchmarks.
 A local static signal for this file is that it has 101 lines and 2964 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
