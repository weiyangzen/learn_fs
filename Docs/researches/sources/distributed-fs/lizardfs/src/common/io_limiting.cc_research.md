# sources/distributed-fs/lizardfs/src/common/io_limiting.cc

Purpose: implements the core runtime behavior for per-group I/O bandwidth limiting.

Important APIs/types/functions: `Limiter::registerReconfigure`, `RTClock::now`, `RTClock::sleepUntil`, and `Group` internals: `attempt`, `enqueue`, `dequeue`, `notifyQueue`, `isFirst`, `askMaster`, `wait`, and `die`.

Control flow: `Group::wait` enqueues a request, waits until it is at the front, then loops until deadline. It returns `ENOENT` if the group dies, succeeds if reserve covers the request, sleeps until the next allowed master request after failed grants, or calls `askMaster` to request enough bytes for pending plus recent past requests. Completed requests are moved into `pastRequests_`, removed from pending, and the next waiter is notified.

State and persistence: per-group in-memory queue of pending requests, recent past requests, reserve bytes, last request timestamps, success flag, dead flag, and injected clock. Shared state references a `Limiter` and throttle delta. No persistence.

Dependencies and integration: depends on `io_limiting.h`, `io_limits_config_loader.h`, `massert`, protocol status constants, and `std::thread` sleep. It integrates local workers with a master/local limiter implementation through `Limiter::request`.

Risks: correctness depends on callers holding and passing the same mutex around `wait`. `die()` sets a flag but does not notify all pending waiters directly; callers must also arrange wakeups or rely on queue progression. Reserve accounting is time-window based and sensitive to clock behavior and limiter latency.

Test signals: no direct tests in this subset. The injectable `Clock` and abstract `Limiter` are designed for tests, but mapped files contain only implementation.
