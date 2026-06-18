<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedTimeCostProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedTimeCostProvider.java

## Purpose
`WeightedTimeCostProvider` computes an RPC cost as the weighted sum of `ProcessingDetails` timing buckets for use by `DecayRpcScheduler`.

## Important APIs, Types, And Functions
- Config suffix prefix `WEIGHT_CONFIG_PREFIX = ".weighted-cost."`.
- Defaults: lock-free, response, and handler time weight 1; shared lock time weight 10; exclusive lock time weight 100; all other timings weight 0.
- `init(String namespace, Configuration conf)` builds one weight per `ProcessingDetails.Timing`.
- `getCost(ProcessingDetails details)` multiplies each timing value by its configured weight.

## Control Flow
Initialization iterates over all timing enum values, chooses defaults, reads optional integer overrides from `<namespace>.weighted-cost.<timing-lowercase>`, and stores them by ordinal. Cost computation iterates the same enum order and sums `details.get(timing) * weight`.

## State And Persistence
Only the initialized `long[] weights` is stored in memory. There is no persistence.

## Dependencies And Integration Points
Implements `CostProvider` and integrates with `DecayRpcScheduler`, `ProcessingDetails`, and IPC cost-provider configuration.

## Risks And Edge Cases
`getCost` relies on prior `init`; the guard is an `assert`, so production JVMs with assertions disabled could throw a null-pointer instead. Negative or very large weights are not rejected. Enum ordinal coupling is safe only while weights are rebuilt from the same enum order.

## Test Signals
Tests should verify default cost composition, per-timing overrides, ignored queue/wait timings by default, negative/large override behavior if supported, and call-before-init failure mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/WeightedTimeCostProvider.java -->
