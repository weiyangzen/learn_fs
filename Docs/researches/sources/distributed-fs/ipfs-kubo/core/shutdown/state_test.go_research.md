# sources/distributed-fs/ipfs-kubo/core/shutdown/state_test.go

Purpose: unit-tests shutdown state tracking. Important helpers/tests are `resetForTest`, `TestInProgressInitiallyFalse`, `TestMarkStartedFirstCallWins`, `TestMarkStartedPreservesFirstTimestamp`, and `TestMarkStartedConcurrent`.

Control flow: tests reset the package atomic, assert initial false/zero state, verify first mark wins, sleep briefly to ensure a later timestamp would differ, and launch 64 goroutines to assert exactly one concurrent winner.

State and persistence: mutates package-global atomic only; tests cannot run in parallel because they share global state.

Dependencies/integration: sync/atomic, testing, time. It protects health-check-visible shutdown semantics.

Risks signaled: replacing CAS with Store would corrupt the first timestamp and concurrent winner count; tests catch that.
