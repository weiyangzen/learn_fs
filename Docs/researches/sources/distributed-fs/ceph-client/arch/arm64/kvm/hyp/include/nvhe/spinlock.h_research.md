# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/spinlock.h

## Purpose

This header implements a standalone nVHE EL2 ticket spinlock, independent of normal kernel locking.

## Important APIs, Types, And Functions

It defines `hyp_spinlock_t`, `DEFINE_HYP_SPINLOCK`, `hyp_spin_lock_init()`, `hyp_spin_lock()`, `hyp_spin_unlock()`, `hyp_spin_is_locked()`, and debug-only `hyp_assert_lock_held()`.

## Control Flow

Lock acquisition atomically increments the next ticket using LSE or LL/SC, then waits with `wfe` until owner matches. Unlock increments owner with release semantics. Debug assertion checks lock state only after protected mode initialization.

## State And Persistence Behavior

Lock state is a 32-bit ticket word split into `owner` and `next`. It is persistent wherever embedded in hyp structures.

## Dependencies And Integration Points

It is used by pKVM pools, VM tables, memory-protection locks, and MM locks where normal kernel primitives cannot run at EL2.

## Risks And Test Signals

Risks are memory ordering bugs, endianness field mistakes, ticket overflow under extreme contention, and assertions before all CPUs enter EL2. Test signals are allocator and memory-protection stress, LSE and LL/SC builds, and `CONFIG_NVHE_EL2_DEBUG` lock assertions.
