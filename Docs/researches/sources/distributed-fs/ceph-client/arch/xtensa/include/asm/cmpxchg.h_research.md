<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cmpxchg.h

## Purpose
Implements Xtensa compare-exchange and exchange primitives for the generic atomic and locking APIs.

## Important APIs, Types, And Functions
Key functions/macros are `__cmpxchg_u32`, `arch_cmpxchg`, `arch_cmpxchg_local`, `arch_cmpxchg64_local`, `arch_cmpxchg64`, `xchg_u32`, `xchg_small`, `__arch_xchg`, and `arch_xchg`.

## Control Flow
For exclusive cores, compare/exchange loops use `l32ex/s32ex/getex`. For S32C1I cores they use `scompare1` and `s32c1i`. Fallback paths disable interrupts to `TOPLEVEL`. Small 1/2-byte exchanges update the containing word with a cmpxchg loop and endian-aware bit offsets.

## State And Persistence
Only target memory words and transient CPU special registers are modified.

## Dependencies And Integration Points
Depends on core feature macros, interrupt levels, generic cmpxchg-local helpers, and `READ_ONCE`.

## Risks And Edge Cases
S32C1I atomicity depends on AtomCtl/cache setup. Small exchange bit masks must match endianness. 64-bit cmpxchg is local/generic rather than truly inter-CPU atomic, so callers must respect API semantics.

## Test Signals
Run atomic/locking/futex selftests, stress byte and halfword xchg users, and test variants with exclusive, S32C1I, and interrupt-disabled fallback implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cmpxchg.h -->
