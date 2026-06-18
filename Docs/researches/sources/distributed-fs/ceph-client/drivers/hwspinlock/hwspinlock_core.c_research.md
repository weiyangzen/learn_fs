# sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_core.c

## Purpose
This file implements the generic Linux hardware spinlock framework. It registers provider banks, maps global lock IDs to `struct hwspinlock` objects, lets clients request/free locks, wraps platform `trylock`/`unlock` operations with local locking and memory barriers, provides DT translation helpers, and offers devm-managed registration/request APIs.

## Important APIs, Types, And Functions
- Global registry: `RADIX_TREE(hwspinlock_tree)` maps lock IDs to lock objects; `HWSPINLOCK_UNUSED` radix-tree tag marks available locks; `hwspinlock_tree_lock` serializes mutations.
- Lock operations: `__hwspin_trylock()`, `__hwspin_lock_timeout()`, `__hwspin_unlock()`, and `hwspin_lock_bust()`.
- OF helpers: `of_hwspin_lock_get_id()` and `of_hwspin_lock_get_id_byname()`.
- Provider APIs: `hwspin_lock_register()`, `hwspin_lock_unregister()`, `devm_hwspin_lock_register()`, and `devm_hwspin_lock_unregister()`.
- Client APIs: `hwspin_lock_request_specific()`, `hwspin_lock_free()`, `devm_hwspin_lock_request_specific()`, and `devm_hwspin_lock_free()`.

## Control Flow
Providers allocate a `struct hwspinlock_device` with an array of locks and call `hwspin_lock_register()`. The core initializes each local spinlock, sets the bank pointer, inserts each lock into the radix tree, and tags it unused. Clients request a lock by ID; the core checks existence and unused tag, gets the provider module, runtime-resumes the provider device, clears the unused tag, and returns the lock. Freeing reverses the runtime PM/module reference and sets the unused tag.

Lock acquisition first optionally takes a local spinlock according to the selected mode (`HWLOCK_IRQSTATE`, `HWLOCK_IRQ`, normal, raw, or in-atomic), then calls the provider's `trylock()`. On failure it undoes local locking and returns `-EBUSY`; on success it issues `mb()`. Timeout locking loops until success or timeout, using `udelay()` for `HWLOCK_IN_ATOMIC` and optional provider `relax()`. Unlock issues a memory barrier before provider `unlock()`, then releases the local spinlock according to mode.

## State And Persistence
The registry persists while the module/core is loaded. Lock allocation state is encoded solely in the radix-tree unused tag. Runtime PM state and module reference counts are held only while a client has requested a lock, not merely while the provider exists. No lock ownership persists across unregister; unregister fails if any lock is still requested.

## Dependencies And Integration Points
The core depends on radix tree, spinlocks, mutexes, PM runtime, module ownership, OF phandle parsing, and provider callbacks defined in `hwspinlock_internal.h`. Public wrappers in `<linux/hwspinlock.h>` call the exported internal functions here.

## Risks
- `hwspin_lock_register_single()` computes `ret` from `radix_tree_insert()` but returns `0` even on insertion failure because it falls through `out` with a constant return. That can hide duplicate-ID or allocation failures and leave partial registration inconsistent.
- Lock request/free correctness depends on the radix-tree tag meaning "unused"; any path that forgets to update it breaks allocation and unregister safety.
- `HWLOCK_RAW` and `HWLOCK_IN_ATOMIC` skip local spinlock protection, pushing serialization responsibility to callers.
- Timeout arithmetic converts milliseconds to jiffies; very small timeouts in non-atomic mode are coarse.
- OF lookup iterates the radix tree under RCU while provider unregister uses the tree mutex; the code follows radix-tree RCU patterns but should be stress-tested with probe/remove races.

## Test Signals
Test provider registration/unregistration, duplicate ID handling, allocation failure injection in radix-tree insert, request/free reference and PM runtime accounting, unregister while locks are requested, all lock modes including IRQ save validation, timeout paths, provider `relax()` calls, bust support/no-support, OF ID and name translation including `-EPROBE_DEFER`, and devm cleanup ordering.
