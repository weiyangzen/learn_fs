# sources/distributed-fs/ceph-client/tools/include/linux/atomic.h

## Purpose

This header adapts kernel-style atomic helper names for tools code.

## APIs, State, and Dependencies

It includes `<asm/atomic.h>`, declares `atomic_long_set`, maps relaxed/release cmpxchg names to `atomic_cmpxchg` when missing, and implements `atomic_try_cmpxchg` and `atomic_inc_unless_negative`. The latter loops reading the atomic value and compare-exchanging `c + 1` unless the current value is negative. State is caller-owned atomic variables.

## Risks and Test Signals

The header depends on the selected architecture atomic implementation and on a linked `atomic_long_set`. `atomic_inc_unless_negative` can spin under contention. Tests should compile and link atomic users and exercise cmpxchg success/failure and negative guard behavior.
