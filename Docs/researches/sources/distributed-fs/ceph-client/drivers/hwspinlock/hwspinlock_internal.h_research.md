# sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_internal.h

## Purpose
This internal header defines the provider-facing hardware spinlock structures and callback contract used by the core and all platform provider drivers.

## Important APIs, Types, And Functions
- `struct hwspinlock_ops` defines provider callbacks: mandatory `trylock()` and `unlock()`, optional `bust()` and `relax()`.
- `struct hwspinlock` represents a single lock, with owning bank, local spinlock, and provider private pointer.
- `struct hwspinlock_device` represents a bank, with device pointer, ops, base ID, number of locks, and a flexible lock array.
- `hwlock_to_id()` computes the global ID from a lock pointer and bank base ID.

## Control Flow
Provider drivers allocate a `hwspinlock_device` large enough for all locks, fill each lock's `priv`, and register the bank with the core. The core fills the bank metadata and uses `hwlock_to_id()` for registry and client operations.

## State And Persistence
The structures define in-memory runtime state only. `priv` is owned by providers and usually points to MMIO addresses, regmap fields, or provider-specific lock resources.

## Dependencies And Integration Points
The header is included by `hwspinlock_core.c` and provider drivers. It depends on Linux spinlock and device types and complements the public `<linux/hwspinlock.h>` API.

## Risks
- `hwlock_to_id()` assumes `hwlock` points inside `bank->lock[]`; invalid pointers produce undefined IDs.
- Provider `trylock()` and `unlock()` must not sleep, but the type system cannot enforce that.
- The flexible array requires correct `struct_size()` allocation by providers.

## Test Signals
Provider compile tests should verify correct allocation sizes, `priv` initialization for every lock, base ID calculations, and static analysis for sleeping calls inside provider callbacks.
