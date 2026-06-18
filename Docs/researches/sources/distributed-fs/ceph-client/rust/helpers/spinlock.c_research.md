# sources/distributed-fs/ceph-client/rust/helpers/spinlock.c

## Purpose
Exposes spinlock initialization, lock/unlock, trylock, and lockdep assertion helpers to Rust.

## APIs, Types, and Functions
Exports `__spin_lock_init` wrapper with debug/PREEMPT_RT-specific initialization, plus `spin_lock`, `spin_unlock`, `spin_trylock`, and lock-held assertion.

## Control Flow, State, and Persistence
State is caller-owned spinlock and lockdep metadata; no local state.

## Dependencies and Integration
Depends on `linux/spinlock.h`, `CONFIG_DEBUG_SPINLOCK`, `CONFIG_PREEMPT_RT`, and Rust lock abstractions.

## Risks and Test Signals
Risks include sleeping/RT semantic differences, unbalanced locking, wrong lock class keys, and using raw spin assumptions on RT. Test signals are Rust spinlock tests, lockdep, and PREEMPT_RT config builds.
