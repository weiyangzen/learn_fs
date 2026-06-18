# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DecayRpcScheduler.java

## Purpose

`DecayRpcScheduler` is a priority scheduler for Hadoop IPC. It tracks per-identity call cost, periodically decays historical cost, and maps heavier users to lower-priority queues. It also exports scheduler metrics and can optionally trigger client backoff based on queue response times.

## Important APIs, control flow, and state

Construction validates priority levels, parses decay factor, period, thresholds, identity provider, cost provider, service users, response-time backoff settings, and top-user metric count. It initializes atomic arrays for current and previous response time windows, creates detailed metrics, schedules a daemon `TimerTask`, registers a namespace-specific `MetricsProxy`, and computes the initial scheduling cache.

Completed calls flow through `addResponseTime()`: the identity provider extracts a user identity, the cost provider computes cost from `ProcessingDetails`, `addCost()` updates decayed/raw per-user counters and totals, detailed metrics record queue and processing time, and current-window response arrays are updated. Periodically `decayCurrentCosts()` multiplies each decayed cost by the decay factor, removes zero-cost identities, recomputes total decayed/raw cost split by service users, swaps an unmodifiable scheduling cache, and updates response-time averages. `getPriorityLevel()` uses the cache or computes a level from identity cost divided by total decayed non-service-user cost. Service users always map to priority 0; test-visible static priorities can override computed levels.

Metrics are exposed through `DecayRpcSchedulerMXBean` and `MetricsSource`: scheduling decisions, decayed call volumes, unique identities, top callers, response times, raw/service-user totals, and detailed per-priority metrics. `stop()` unregisters the metrics proxy and shuts down detailed metrics.

## Dependencies and integration points

It is created by `CallQueueManager` and intended to work with `FairCallQueue`. It depends on `IdentityProvider`, `CostProvider`, `ProcessingDetails`, `DecayRpcSchedulerDetailedMetrics`, Metrics2, MBeans, Jackson JSON, `UserGroupInformation`, and `RpcMetrics` time-unit configuration.

## Risks and test signals

All identities are treated as strings in service-user checks; custom providers returning non-string identities would break casts. Threshold count must be `numLevels - 1`; response-time threshold count must be `numLevels`. The decay timer is daemon and uses a weak reference, but explicit `stop()` is still needed to unregister metrics. `MetricsProxy.getInstance()` replaces delegates for the same namespace, so multiple schedulers under one namespace share a proxy. Backoff checks lower-or-equal priority indexes up to the caller's level and may reject lower-priority calls when high-priority response times exceed thresholds. `TestDecayRpcScheduler` covers invalid levels, parsing period/factor/thresholds, accumulation, decay, priority, periodic decay, initialization NPE prevention, weighted cost providers, zero-cost/no-request cases, and service users.
