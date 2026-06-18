# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister.go

Purpose: defines cursor persistence contract and ships an in-memory implementation for tests.

Important APIs/types: `Persister` interface with `Load` and `Save`, `InMemoryPersister`, and `NewInMemoryPersister`. Contract: unknown shards load as empty maps; save replaces prior state atomically; callers serialize concurrent saves for the same shard in production.

Control flow: in-memory load locks, copies stored shard state into a new map, and returns it. Save locks, copies input state, and replaces the shard entry.

State/persistence: `InMemoryPersister` stores `map[int]map[ActionKey]int64` under a mutex. It is test-only; filer-backed persistence lives elsewhere.

Dependencies/integration: used by reader/daily-run tests as a cursor checkpoint double. Action keys are lifecycle identities.

Risks: production implementation must match deep-copy and replace-not-merge semantics or stale cursor positions and caller mutations could corrupt resume state. Context arguments are accepted but in-memory implementation does not inspect cancellation.

Test signals: persister tests cover unknown loads, round-trip, input/output copy isolation, replace semantics, shard isolation, empty save clearing, and concurrent save/load behavior.
