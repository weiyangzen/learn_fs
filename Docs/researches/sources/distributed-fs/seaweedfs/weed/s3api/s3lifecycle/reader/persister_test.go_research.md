# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister_test.go

Purpose: verifies `InMemoryPersister` obeys the documented cursor persistence contract.

Important tests: unknown shard loads return non-nil empty maps; save/load round-trips; save copies input; load returns a copy; save replaces instead of merging; shard ids are isolated; saving an empty map clears prior state; concurrent save/load operations do not deadlock and are intended for race-detector validation.

Control flow/state: tests mutate input and loaded maps after calls to prove copy boundaries. Concurrent test launches paired goroutines across four shard ids.

Dependencies/integration: uses lifecycle action keys and context. This in-memory double underpins other lifecycle tests.

Risks/gaps: in-memory implementation ignores context cancellation, acceptable for tests but not a production persistence pattern. Concurrency test checks completion; data-race detection requires `go test -race`.

Test signals: strong signal for deep-copy and replace semantics, which are critical for cursor correctness.
