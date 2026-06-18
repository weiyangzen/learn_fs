# sources/cloud-native/containerd/internal/kmutex/noop.go

## Purpose
Provides a `KeyedLocker` implementation that performs no synchronization.

## Important APIs, Types, And Functions
`NewNoop` returns `*noopMutex`. `Lock` always returns nil and `Unlock` does nothing.

## Control Flow
Callers can swap this implementation where serialization is disabled or unnecessary.

## State And Persistence
No state.

## Dependencies And Integration Points
Depends only on `context` and the local `KeyedLocker` interface.

## Risks
Using it in paths that require real serialization can introduce races. It intentionally does not detect unlock misuse.

## Test Signals
No direct tests. Compile-time interface compatibility is the main signal.
