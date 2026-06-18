# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/CuratorEventCatcher.java

Purpose: test callback utility for capturing asynchronous Curator events.

Important APIs and functions: implements `BackgroundCallback.processResult()`, increments an `AtomicInteger`, and enqueues the `CuratorEvent` into a single-capacity `LinkedBlockingQueue`; `getCount()` and `take()` expose event count and blocking retrieval.

Control flow: Curator invokes `processResult()` on background completion. The event is logged, counted, and put into the queue. Tests can block on `take()` until the event arrives.

State and persistence: state is in-memory only: one blocking queue and an atomic counter. Queue capacity of one can block callback threads if more than one event arrives before tests drain it.

Dependencies and integration: used by `TestCuratorService.testBackgroundDelete()` to verify background delete callbacks.

Risks and test signals: useful for single-event async tests. It is intentionally minimal and not safe as a general multi-event collector unless tests consume promptly.
