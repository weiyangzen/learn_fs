## sources/control-plane/longhorn-engine/pkg/util/once_test.go

### Purpose
`once_test.go` validates the retryable `Once` behavior implemented in `once.go`.

### Important APIs, Types, And Functions
`TestOnce` uses the shared gocheck `TestSuite`. It defines a counter and a function that fails only on the first call. It calls `once.Do` twice serially, then ten times concurrently through a `sync.WaitGroup`.

### Control Flow
The first `Do` call increments the counter and returns an error, proving failure does not set `done`. The second call succeeds and sets `done`. Concurrent calls then assert `Do` returns nil and the counter remains `1`, proving the successful execution is not repeated.

### State, Persistence, And Dependencies
The test uses in-memory state only. Dependencies are `fmt`, `sync`, and `gopkg.in/check.v1`.

### Integration Points
The test belongs to the shared util test suite initialized in `util_test.go`.

### Risks
The test relies on the counter being accessed only inside the guarded function before success; it does not stress multiple concurrent failing callers.

### Test Signals
Passing this test signals correct retry-after-failure and once-after-success behavior. Additional tests could cover high-concurrency first-call failure and recursive use deadlock expectations.
