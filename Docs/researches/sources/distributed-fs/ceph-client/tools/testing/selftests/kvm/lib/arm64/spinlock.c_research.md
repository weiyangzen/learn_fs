# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/spinlock.c

## Purpose
This file provides the guest-side arm64 spinlock primitive used by selftest guest libraries, notably the GIC initialization path.

## Important APIs, Types, and Functions
`spin_lock()` uses `ldaxr`/`stxr` to acquire `lock->v` with acquire semantics. `spin_unlock()` uses `stlr wzr` to release by storing zero with release ordering.

## Control Flow
The lock loops while the value is nonzero, then attempts an exclusive store of one. A failed exclusive store retries from the beginning. Unlock is a single ordered store.

## State, Dependencies, and Integration
The only state is the integer field in `struct spinlock`. It depends on `spinlock.h` and arm64 exclusive load/store instructions. It integrates with guest code that needs synchronization before shared guest globals are visible to other vCPUs.

## Risks and Test Signals
This is a simple busy-wait lock with no fairness or backoff. Bugs usually manifest as guest hangs or failed one-time initialization assertions, especially under multi-vCPU GIC tests.
