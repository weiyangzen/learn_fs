# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ReviewerFactoryTest.java

Purpose: validates `Reviewer.Factory.create()` instantiates the configured reviewer class and the default reviewer.

Important APIs and helpers: `createProbabilisticBufferReviewer()` sets `WORKER_REVIEWER_CLASS` to `ProbabilisticBufferReviewer`. `createDefaultAllocator()` calls the factory without local setup and expects the default reviewer type.

Control flow and state: both tests assert the returned `Reviewer` is an instance of `ProbabilisticBufferReviewer`.

Dependencies and integration: uses Alluxio global `Configuration`, `PropertyKey.WORKER_REVIEWER_CLASS`, and JUnit assertions.

Risks and test signals: naming still says allocator in places, but the signal is reviewer factory behavior. The tests do not cover invalid class names or custom reviewer constructors.
