# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummySharedResource.java

Purpose: small shared-resource simulator for HA failover tests. It models a resource such as a shared edit log that must be owned by at most one active service.

Important APIs and types: `DummyHAService`, synchronized `take`, `release`, and `assertNoViolations`, plus JUnit `assertEquals`.

Control flow: `take` accepts ownership when the resource is free or already held by the same service; otherwise it increments `violations` and throws `IllegalStateException`. `release` clears ownership only when the releasing service is the current holder. `assertNoViolations` asserts no double-owner attempt occurred.

State and persistence: in-memory `holder` and violation counter. All methods are synchronized to make ownership checks safe during multi-threaded failover tests.

Dependencies and integration: used by `DummyHAService` transitions and `DummyFencer` to validate active/standby/fencing flows. It is not a standalone test, but a correctness oracle for higher-level HA tests.

Risks and test signals: if callers forget to release during standby/fence paths, later `take` calls fail. Because repeated `take` by the same holder is allowed, it catches split-brain between different services rather than duplicate transition calls on one service.
