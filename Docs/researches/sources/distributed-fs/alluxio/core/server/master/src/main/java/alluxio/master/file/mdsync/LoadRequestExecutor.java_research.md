# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/mdsync/LoadRequestExecutor.java

Purpose: schedules and executes UFS metadata load requests across active `PathLoaderTask`s with concurrency limits, per-UFS rate limiting, fair task polling, and handoff to result processing.

Important APIs and types: constructor starts a `LoadRequestRunner` thread. `addPathLoaderTask`, `hasNewLoadTask`, `onTaskComplete`, and `close` are the main lifecycle methods. Internal queues include active tasks map, task ids with pending loads, task id deque, load request queue, rate-limited priority queue, and ticket counter.

Control flow: the runner repeatedly waits until a load request is available and a ticket is free, pulls pending loads from path loader tasks, handles rate-limited permits, and calls `performListingAsync` on a UFS client. Successful UFS callbacks create `LoadResult`s and submit them to `LoadResultExecutor`; failures release tickets, record fail reasons, and ask the original request to retry or fail.

State and persistence behavior: in-memory concurrency and scheduling state only. It protects downstream persistence by limiting running or completed-but-not-processed UFS loads through `mRemainingTickets`.

Dependencies and integration points: depends on `PathLoaderTask`, `LoadRequest`, `LoadResultExecutor`, UFS client async listing API, `RateLimiter`, metrics gauges, `SamplingLogger`, and sync failure reasons.

Risks: the class mixes synchronized state with concurrent collections, so missed notifications or ticket leaks can stall sync. Rate-limited requests are removed outside the synchronized block after readiness checks, which depends on single runner thread safety. UFS callbacks must always release tickets through success or error paths.

Test signals: tests should cover concurrency cap, rate limiter delays, retryable load errors, task completion cleanup, queued-load metrics, runner shutdown, and result executor handoff.
