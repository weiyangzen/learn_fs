# sources/distributed-fs/ipfs-kubo/core/node/provider_test.go

Purpose: tests persistence helpers for unique reprovide cycle counts. Important tests cover `readLastUniqueCount` and `persistUniqueCount`.

Control flow: tests create a fresh in-memory datastore, assert missing counts read as zero, round-trip several counts including `math.MaxUint64`, verify overwrites replace previous values, and assert corrupt byte lengths return zero rather than panicking.

State and persistence: models repo datastore writes under `reprovideLastUniqueCountKey` using an in-memory datastore.

Dependencies/integration: go-datastore, context, math, testify. It protects the bloom sizing feedback loop used by `+unique` and `+entities` provide strategies.

Risks signaled: corrupt or truncated persisted counts must not crash startup/reprovide; stale counts must be overwritten every successful cycle.
