# sources/cloud-native/containers-storage/pkg/locker/locker.go

Purpose: implements named in-process locks so callers can serialize work by resource key instead of holding a coarse global mutex.

Important APIs, types, and functions: `Locker`, `New`, `Lock`, `Unlock`, `ErrNoSuchLock`, and private `lockCtr` with atomic waiter count.

Control flow: `Locker.Lock` creates or finds a `lockCtr` under the global map mutex, increments its waiter count while protected, releases the map mutex, then blocks on the per-name mutex and decrements waiters after acquisition. `Unlock` finds the per-name lock, deletes it from the map when no waiters remain, unlocks the per-name mutex while still under the map mutex, and returns an error for unknown names.

State and persistence: state is purely in-memory: a map from lock names to counters and waiter counts. Entries are removed after the final holder unlocks when no waiters exist.

Dependencies and integration points: depends on `errors`, `sync`, and `sync/atomic`. It is suitable for process-local resource serialization but does not coordinate across processes.

Risks and edge cases: unlocking an existing but not-held per-name mutex would panic via `sync.Mutex`. Deleting before unlock relies on waiter counts to prevent concurrent lookup races. No fairness guarantee is provided beyond `sync.Mutex`.

Test signals: `locker_test.go` covers waiter counting, blocking behavior, cleanup after unlock, and high-concurrency lock/unlock loops.
