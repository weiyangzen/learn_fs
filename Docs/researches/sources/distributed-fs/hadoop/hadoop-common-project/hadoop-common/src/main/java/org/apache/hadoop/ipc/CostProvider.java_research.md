# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CostProvider.java

## Purpose

`CostProvider` is the pluggable cost model used by `DecayRpcScheduler` to convert `ProcessingDetails` into a numeric scheduling cost.

## Important APIs, control flow, and state

The interface defines `init(String namespace, Configuration conf)` and `getCost(ProcessingDetails details)`. Implementations decide whether cost is constant, weighted by queue/lock/processing time, or based on other timing details.

## Dependencies and integration points

`DecayRpcScheduler.parseCostProvider()` loads implementations from `ipc.cost-provider.impl` or port-scoped variants, initializes the selected provider, and calls `getCost()` for completed calls in `addResponseTime()`. `DefaultCostProvider` is the fallback.

## Risks and test signals

Bad cost providers can starve users, overflow counters, or return zero/negative costs that change scheduler behavior. Tests should cover provider loading, namespace fallback, weighted providers, zero-cost calls, and no-request windows; `TestDecayRpcScheduler` includes weighted-cost provider cases.
