# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewerTest.java

Purpose: verifies the probability curve used by `ProbabilisticBufferReviewer` as available bytes fall between soft and hard limits.

Important APIs and helpers: setup configures `WORKER_REVIEWER_CLASS`, hard limit, and soft limit, then obtains the reviewer through `Reviewer.Factory.create()`. `testProbabilityFunction()` calls `getProbability(StorageDirView)` on mocked directory views.

Control flow and state: cases cover empty disk, above soft limit, just below soft limit, midpoint between hard and soft, exactly at hard limit, below hard limit, and full disk. Assertions check 1.0, linearly reduced values, and 0.0.

Dependencies and integration: depends on global `Configuration`, `FormatUtils.parseSpaceSize`, Mockito `StorageDirView` mocks, and reviewer factory behavior.

Risks and test signals: global configuration is reset in `@After`. Random acceptance is not tested; this isolates the deterministic probability function and factory wiring for buffer preservation.
