## sources/control-plane/juicefs-csi-driver/pkg/util/dispatch/pool.go

### Purpose
`pool.go` provides a tiny bounded concurrency helper. It limits worker goroutines using a buffered channel and offers both synchronous wait-for-result and fire-and-forget modes.

### Important APIs, Types, And Functions
`Pool` has `Num` and `PoolCh`. `NewPool(num)` clamps num to at least one. `RunAndWait(ctx, worker)` acquires a slot, runs the worker in a goroutine, and waits for either context cancellation or the worker error. `Run(ctx, worker)` starts a goroutine that acquires a slot and invokes the worker without returning a result.

### Control Flow
`RunAndWait` sends to `PoolCh` before starting the goroutine, defers slot release inside the goroutine, and selects between `ctx.Done()` and `errCh`. `Run` starts a goroutine first, then acquires a slot inside it, so callers do not block on pool capacity.

### State, Persistence, And Dependencies
State is in-memory channel occupancy. There is no persistence. Dependencies are only `context` and `fmt`.

### Integration Points
Any driver code needing bounded dispatch can use it. The helper is generic and not JuiceFS-specific.

### Risks
`RunAndWait` closes `errCh` with a defer in the caller after receiving; if context returns first, the worker goroutine may later send to a closed channel, causing a panic. `Run` has no error propagation and can accumulate blocked goroutines waiting for slots. Returned context errors are collapsed to `fmt.Errorf("context timeout")`, losing cancellation details.

### Test Signals
No tests are listed. Useful tests should cover cancellation before worker completion, slot release, num clamping, and the potential send-on-closed-channel race.
