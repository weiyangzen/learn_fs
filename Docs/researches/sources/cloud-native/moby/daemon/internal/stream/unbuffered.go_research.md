# sources/cloud-native/moby/daemon/internal/stream/unbuffered.go

## Purpose
Implements a simple synchronized broadcaster for stdout and stderr. Each write is delivered to all registered `io.WriteCloser` consumers, and failed consumers are removed.

## Important APIs, Types, And Functions
`unbuffered` holds a mutex and slice of writers. `Add` appends a consumer. `Write` locks, writes the full byte slice to each writer, records writers that returned an error or short count, evicts them, and reports success for the original length. `Clean` closes all writers and clears the slice.

## Control Flow
Writes are synchronous under a single lock, so every active writer receives data serially. Eviction is deferred until after the loop and index-adjusted while removing multiple failed writers.

## State And Persistence
The writer list is in-memory. Failed or closed consumers disappear on the next write; `Clean` closes all current writers. No stream content is retained.

## Dependencies And Integration Points
Used by `stream.Config.Stdout` and `Stderr` to fan container output into all active attach/log consumers. Consumers are commonly `bytespipe.BytesPipe` instances.

## Risks And Test Signals
One slow writer blocks all writers and future `Add` calls while `Write` holds the lock. Write errors are swallowed after eviction, which favors continued fan-out over surfacing partial delivery. Tests cover multi-writer delivery, eviction, race behavior, and benchmark fan-out.
