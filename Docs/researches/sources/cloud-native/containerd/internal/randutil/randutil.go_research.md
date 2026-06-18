# sources/cloud-native/containerd/internal/randutil/randutil.go

## Purpose
Provides crypto-random integer helpers analogous to `math/rand` functions.

## Important APIs, Types, And Functions
`Int63n`, `Int63`, `Intn`, and `Int` read from `crypto/rand.Reader` through `rand.Int`.

## Control Flow
`Int63n` generates a random big integer below `n`, panicking on error. The other helpers delegate to it with max bounds or type conversions.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `crypto/rand`, `math`, and `math/big`. Used by tests such as keyed mutex stress tests to avoid deterministic math/rand global state.

## Risks
`Int63n` inherits `rand.Int` behavior and panics for invalid bounds or entropy errors. Converting to `int` may narrow on 32-bit platforms.

## Test Signals
No direct tests. Indirect use in concurrency tests provides light exercise.
