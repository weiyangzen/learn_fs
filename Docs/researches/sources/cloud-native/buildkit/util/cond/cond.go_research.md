# sources/cloud-native/buildkit/util/cond/cond.go

## Purpose
Stateful wrapper around sync.Cond. It remembers one pending signal so a Wait after Signal does not block.

## Important APIs, Types, And Functions
Package: `cond`. Build tags: `none`. Key declarations observed in the file: `NewStatefulCond, StatefulCond, Wait, Signal`.

## Control Flow, State, And Persistence
Wait unlocks the caller-provided main lock, waits under an internal mutex unless signalled is set, consumes the signal, then relocks main. Signal sets signalled and wakes one waiter.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are single-signal semantics and callers needing to hold the main lock correctly. cond_test.go covers initial blocking, pre-signal behavior, and signal between waits.
