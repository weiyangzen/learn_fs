# sources/cloud-native/moby/daemon/internal/stream/unbuffered_test.go

## Purpose
Tests the unbuffered broadcaster's delivery, failed-writer eviction, concurrent add/write safety, and benchmark fan-out cost.

## Important APIs, Types, And Functions
`dummyWriter` records writes and can fail on demand. `devNullCloser` accepts all bytes. `TestUnbuffered` exercises `Add`, `Write`, and `Clean`. `TestRaceUnbuffered` is specifically valuable under the race detector. `BenchmarkUnbuffered` measures repeated writes to hundreds of consumers.

## Control Flow
The main test adds writers, writes `"foo"` and `"bar"`, adds another writer midstream, forces failures, verifies failed writers stop receiving data, and checks multiple simultaneous evictions. Cleanup closes the broadcaster.

## State And Persistence
All writer state is local buffers. There is no external persistence.

## Dependencies And Integration Points
Uses standard testing and in-memory writer fakes. It protects the stream package's stdout/stderr broadcaster used by attach and DirectIO copying.

## Risks And Test Signals
The race test only detects issues when run with `-race`. The tests do not check close errors from `Clean`, matching production behavior where close errors are ignored. Strong signal is correct index handling when several writers are evicted in one pass.
