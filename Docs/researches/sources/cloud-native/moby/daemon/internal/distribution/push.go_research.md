# sources/cloud-native/moby/daemon/internal/distribution/push.go

## Purpose
Provides top-level image push orchestration and gzip compression helper.

## APIs, Control Flow, and Integration
`Push` trims the reference, looks up push endpoints, emits progress, verifies local references exist, iterates endpoints with TLS/plaintext fallback rules, invokes a v2 pusher, logs push events on success, and returns the last endpoint error when all fail. `compress` streams gzip-compressed data through a pipe with buffered writes and returns a completion channel so callers can wait before releasing the input.

## State, Dependencies, and Risks
State updates are delegated to pusher/refstore and event logger. Risks include requiring `ReferenceStore`, no digest-reference push, endpoint fallback complexity, and goroutine/pipe error propagation in compression. Tests for top-level push are indirect; push_v2 tests cover lower-level metadata behavior.
