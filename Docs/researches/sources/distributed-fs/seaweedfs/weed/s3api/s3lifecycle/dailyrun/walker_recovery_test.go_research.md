# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_recovery_test.go

Purpose: tests daily-run recovery branch behavior when persisted rule hashes differ from the current engine snapshot.

Important APIs/types: `memPersister`, `newMemPersister`, `snapshotWithRule`, and tests around `runShard`.

Control flow: tests seed stale cursors, inject walker functions, call `runShard`, and assert walker invocation, recovery view/shard id, cursor rewind to `runNow - maxTTL`, hash replacement, nil-walker compatibility, and error propagation without cursor advancement.

State and persistence behavior: validates recovery cursor rewrite and the guarantee that walker failure leaves old cursor untouched. This protects rule-change recovery from skipping already-due objects.

Dependencies and integration points: uses lifecycle engine, in-memory cursor persister, and direct `runShard` calls.

Risks: direct `runShard` invocation bypasses full `Run` setup and shared subscription. The matching-cursor/no-walker case is noted as implicit rather than fully tested here.

Test signals: strong focused coverage for rule-edit/partition-flip recovery, which is one of the riskiest cursor state transitions.
