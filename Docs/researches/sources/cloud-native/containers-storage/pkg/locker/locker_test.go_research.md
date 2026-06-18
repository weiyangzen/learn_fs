# sources/cloud-native/containers-storage/pkg/locker/locker_test.go

Purpose: tests the named-lock manager in `locker.go`.

Important APIs, types, and functions: `TestLockCounter`, `TestLockerLock`, `TestLockerUnlock`, and `TestLockerConcurrency`.

Control flow: tests increment/decrement counters, acquire a lock and verify a second goroutine blocks until unlock, confirm a released lock can be acquired again, and run 10001 goroutines that lock and unlock the same name.

State and persistence: no persistence. The tests inspect `Locker.locks` and `lockCtr.waiters` directly because they are in package scope.

Dependencies and integration points: depends on `sync`, `testing`, `time`, and `testify/require`. It validates expected behavior for users relying on key-scoped in-process locking.

Risks and edge cases: time-based waiting uses polling and timeouts. Tests do not check unknown unlock error or unlocking without a matching lock holder.

Test signals: confirms waiter counts, blocking semantics, release cleanup, and absence of obvious data races or panics under many goroutines.
