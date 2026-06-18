# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/RateLimitedRequest.java

Purpose: pairs a `PathLoaderTask`, `LoadRequest`, and rate limiter permit so delayed UFS load requests can be ordered by readiness.

Important APIs and types: constructor checks non-null task and request. `isReady` and `getWaitTime` query the task's `RateLimiter` for the stored permit. `compareTo` orders by permit value; `equals` and `hashCode` include permit, task, and load request.

Control flow: `LoadRequestExecutor` creates this when `RateLimiter.acquire` returns a delay permit instead of immediate execution. The runner keeps instances in a priority queue and later executes the request when `isReady` becomes true.

State and persistence behavior: in-memory scheduling state only; no direct metadata changes.

Dependencies and integration points: depends on `PathLoaderTask`, `LoadRequest`, Guava preconditions, and Alluxio rate limiter semantics.

Risks: ordering by permit assumes permit values are comparable by readiness time. If a task's rate limiter behavior changes, the priority queue may no longer wake requests in optimal order.

Test signals: tests should cover ready/not-ready transitions, wait time, priority ordering, equality, and integration with `LoadRequestExecutor`.
