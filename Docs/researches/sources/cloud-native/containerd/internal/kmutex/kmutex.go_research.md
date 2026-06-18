# sources/cloud-native/containerd/internal/kmutex/kmutex.go

## Purpose
Implements keyed mutual exclusion so callers can serialize operations per resource ID while allowing different keys to proceed concurrently.

## Important APIs, Types, And Functions
`KeyedLocker` exposes `Lock(ctx, key)` and `Unlock(key)`. `New` returns a `keyMutex`. Internally each key maps to `klock`, a one-permit weighted semaphore plus reference count.

## Control Flow
`Lock` creates or finds a per-key semaphore under a map mutex, increments refcount, then waits on the semaphore with caller context. If waiting is canceled, it decrements refcount and removes the key if unused. `Unlock` releases the semaphore and removes the key when the refcount reaches zero.

## State And Persistence
State is an in-memory map from key to semaphore/refcount. It is cleaned up after the last waiter/holder leaves.

## Dependencies And Integration Points
Uses `sync`, `context`, and `golang.org/x/sync/semaphore`. It supports CRI/container operations keyed by container or sandbox ID.

## Risks
Unlocking an unheld key panics. Callers must pair successful `Lock` calls with `Unlock`; calling `Unlock` after a canceled `Lock` would corrupt semantics and panic or release another waiter.

## Test Signals
`kmutex_test.go` covers basic blocking, context cancellation, panic on unlock, same-key serialization, and different-key concurrency.
