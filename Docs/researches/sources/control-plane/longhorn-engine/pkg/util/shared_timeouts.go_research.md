## sources/control-plane/longhorn-engine/pkg/util/shared_timeouts.go

### Purpose
`shared_timeouts.go` implements a shared timeout policy for groups of goroutines where all workers may eventually time out, but the last remaining worker should be allowed a longer grace period.

### Important APIs, Types, And Functions
`SharedTimeouts` stores `shortTimeout`, `longTimeout`, and `numConsumers` under an `RWMutex`. `NewSharedTimeouts` constructs it. `Increment` and `Decrement` adjust consumers. `CheckAndDecrement(duration)` returns `longTimeout` if the duration exceeds the long limit, returns `shortTimeout` only when the duration exceeds the short limit and more than one consumer remains, and otherwise returns zero.

### Control Flow
Callers register with `Increment`, periodically compute their elapsed duration, and call `CheckAndDecrement`. A positive result means the caller must perform timeout handling and is removed from the consumer count. Short timeout is reserved for non-last consumers; the final consumer can wait until the long timeout.

### State, Persistence, And Dependencies
State is in-memory and protected by a mutex. Dependencies are `sync` and `time`. The concrete type implements the `types.SharedTimeouts` interface without importing engine types.

### Integration Points
The helper supports backend or IO flows where concurrent operations share failure budget. It is tested from `util_test.go`.

### Risks
`Decrement` and `CheckAndDecrement` can drive `numConsumers` negative if callers double-decrement or skip registration. The function does not record which consumer timed out, so correctness is caller-discipline based.

### Test Signals
Tests should cover short-timeout behavior with multiple consumers, long-timeout behavior for the final consumer, concurrent checks, and consumer count invariants.
