# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/atomic.h

## Purpose

`atomic.h` selects and completes LoongArch atomic APIs, providing basic read/set, AMO/LLSC includes, and specialized 32/64-bit helpers such as `sub_if_positive` and `fetch_add_unless`. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs include `ATOMIC_INIT`, `arch_atomic_read`, `arch_atomic_set`, `arch_atomic_sub_if_positive`, `arch_atomic64_fetch_add_unless`, and `arch_atomic64_sub_if_positive`. Concrete declarations observed in the file: Includes: `linux/types.h`, `asm/barrier.h`, `asm/cmpxchg.h`, `asm/atomic-amo.h`, `asm/atomic-llsc.h`, `asm-generic/atomic64.h`. Macros: `_ASM_ATOMIC_H`, `__LL`, `__SC`, `__AMADD`, `__AMOR`, `__AMAND_DB`, `__AMOR_DB`, `__AMXOR_DB`, `ATOMIC_INIT`, `arch_atomic_read`, `arch_atomic_set`, `arch_atomic_fetch_add_unless`, `arch_atomic_dec_if_positive`, `ATOMIC64_INIT`, `arch_atomic64_read`, `arch_atomic64_set`, `arch_atomic64_fetch_add_unless`, `arch_atomic64_dec_if_positive`. Functions/syscalls: `arch_atomic_fetch_add_unless`, `arch_atomic_sub_if_positive`, `arch_atomic64_fetch_add_unless`, `arch_atomic64_sub_if_positive`.

## Control Flow, State, And Persistence

Runtime flow depends on AMO or LLSC generated primitives plus custom loops for conditional operations.

## Dependencies And Integration Points

It integrates with generic atomic64 fallback on 32-bit, barriers, cmpxchg, locking, refcounting, and scheduler counters.

## Risks And Test Signals

Risks are memory ordering holes, 32/64-bit helper divergence, and conditional atomic races. Test signals are atomic selftests, refcount tests, locktorture, and 32-bit/64-bit builds.
 A local static signal for this file is that it has 175 lines and 3910 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
