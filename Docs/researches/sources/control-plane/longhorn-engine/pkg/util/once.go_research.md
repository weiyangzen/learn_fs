## sources/control-plane/longhorn-engine/pkg/util/once.go

### Purpose
`once.go` implements a retryable variant of `sync.Once`: the guarded function is considered done only after it returns nil.

### Important APIs, Types, And Functions
`Once` stores an atomic `done` flag and a mutex. `Do(f func() error) error` provides the fast path for already-successful execution. `doSlow` serializes callers, invokes `f` only while `done == 0`, and stores `done = 1` after successful execution.

### Control Flow
Concurrent callers first atomically check `done`. If not done, one caller enters the mutex and runs `f`. A non-nil error is returned and leaves `done` unset, allowing future calls to retry. A nil error schedules the atomic store before returning; later calls skip `f`.

### State, Persistence, And Dependencies
State is in-memory only. Dependencies are `sync` and `sync/atomic`.

### Integration Points
This helper is useful for initialization paths that may fail transiently and should be retried rather than permanently poisoning a `sync.Once`.

### Risks
`Once` must not be copied after use. The guarded function runs while holding the mutex, so it should avoid recursive calls to the same `Once` and long blocking operations unless intentional.

### Test Signals
Tests should prove failed first calls can retry, successful calls run only once, and concurrent callers do not race the guarded function.
