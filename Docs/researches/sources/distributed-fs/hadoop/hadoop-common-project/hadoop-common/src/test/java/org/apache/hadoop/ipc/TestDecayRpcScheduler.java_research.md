# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestDecayRpcScheduler.java

## Purpose
`TestDecayRpcScheduler` validates configuration parsing, decaying call-volume accounting, priority assignment, metrics/JMX summaries, weighted cost providers, service-user exemptions, and initialization safety for `DecayRpcScheduler`.

## Important APIs, Types, and Functions
The file uses `DecayRpcScheduler`, `Schedulable`, `IdentityProvider`, `CostProvider`, `WeightedTimeCostProvider`, `ProcessingDetails`, `DefaultMetricsSystem`, JMX `MBeanServer`, and JSON parsing. Helpers include `mockCall(String)`, `TestIdentityProvider`, `TestCostProvider`, `getSchedulerWithWeightedTimeCostProvider()`, and `getPriorityIncrementCallCount()`.

## Control Flow
Constructor tests reject nonpositive priority levels. Parsing tests validate default and namespace-specific period, factor, thresholds, and port-less provider configuration. Accumulation and decay tests add calls by identity, force decay, and assert call snapshots shrink and remove zero entries. Priority tests verify threshold-based levels and JMX call-volume summaries before and after decay. Weighted-cost tests rank callers by lock timing cost, then verify decay restores high priority after many cycles. Service-user tests assert configured service users remain priority zero and are accounted separately from normal users.

## State and Persistence
Scheduler state includes decaying per-identity call-cost maps, raw totals, service-user totals, priority cache after decay, metrics registration, and background periodic decay timers. No filesystem persistence is used.

## Dependencies and Integration Points
The tests integrate RPC scheduling config keys, metrics system initialization, JMX MBean attributes, Jetty JSON parsing, UGI identity extraction, and processing-detail timing categories used by server call accounting.

## Risks and Edge Cases
Periodic decay uses real sleeps and a two-second timeout. Metrics/JMX object names depend on namespace uniqueness. Some tests use deprecated FCQ-prefixed config keys to protect backward compatibility. Weighted duration assertions avoid exact timings but still depend on relative cost formulas.

## Test Signals
Signals include expected parse defaults and overrides, exact decayed totals, threshold-derived priority levels, valid JMX JSON summaries, no initialization `NullPointerException` with metrics already monitoring, weighted-cost priority ordering, zero-cost calls staying equal, service users excluded from normal-user totals, and service users always receiving priority zero.
