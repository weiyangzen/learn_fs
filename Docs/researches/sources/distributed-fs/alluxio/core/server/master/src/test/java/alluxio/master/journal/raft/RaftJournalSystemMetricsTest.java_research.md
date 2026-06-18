# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemMetricsTest.java

Purpose: validates metric registration and metric values for the embedded Raft journal system and its state machine.

Important APIs/types/functions: uses `RaftJournalSystem`, `JournalStateMachine`, `SnapshotDirStateMachineStorage`, `MetricsSystem.METRIC_REGISTRY`, `MetricKey`, Ratis `RoleInfoProto`, and Mockito spies. Helper accessors read the cluster leader index/id, local master role id, and dynamically generated per-master journal sequence-number gauges.

Control flow: `journalStateMachineMetrics` resets selected metrics, builds a Raft journal system, constructs and closes state machines twice, and verifies state-machine gauges are registered on construction and removed on close. `metrics` stubs sequence-number maps and Ratis role info across waiting-for-election, leader, follower, and leader-again states, while calling `startInternal`, `gainPrimacy`, and `losePrimacy`.

State and persistence behavior: no durable journal entries are asserted here; the observable state is global metric registry contents plus the Raft journal system's local role/primacy transitions. Temporary folders isolate embedded journal storage.

Dependencies and integration points: depends on test port allocation through `JournalTestUtils.createEmbeddedJournalTestPorts`, Alluxio configuration reload, Ratis role protobufs, and Alluxio metric key naming conventions.

Risks: global metric registry cleanup is manual and can leak between tests if metric names change. The follower leader-id parsing assumes peer IDs are encoded as `localhost_port`. Metrics are validated through direct gauge lookup, so missing gauge lifecycle changes are caught but gauge type changes may fail with casts.

Test signals: good regression coverage for metric lifecycle and role/leader gauge semantics; does not exercise a full multi-node Ratis cluster or real journal sequence-number progression.
