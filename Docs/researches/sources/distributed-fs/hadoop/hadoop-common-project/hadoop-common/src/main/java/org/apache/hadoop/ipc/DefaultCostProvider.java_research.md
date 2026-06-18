# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/DefaultCostProvider.java

## Purpose

`DefaultCostProvider` is the fallback cost model for `DecayRpcScheduler`. It assigns every completed call a constant cost of 1.

## Important APIs, control flow, and state

`init()` is a no-op. `getCost(ProcessingDetails)` ignores the details and returns 1. The class has no mutable state.

## Dependencies and integration points

`DecayRpcScheduler.parseCostProvider()` returns this provider when no configured provider is found. It depends only on `Configuration` and `ProcessingDetails` through the `CostProvider` interface.

## Risks and test signals

Constant cost treats all RPC methods equally regardless of lock, queue, or processing time. This is simple and predictable but can underweight expensive operations. `TestDecayRpcScheduler` default accumulation/decay/priority tests implicitly cover this provider; weighted provider tests cover the alternative path.
