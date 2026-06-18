# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestWeightedTimeCostProvider.java

## Purpose

`TestWeightedTimeCostProvider` validates cost calculation for IPC processing details when timing components are weighted. It protects RPC scheduler cost accounting for queue, lock-free, shared-lock, and exclusive-lock timing.

## Important APIs, Types, And Functions

The file uses `WeightedTimeCostProvider`, `ProcessingDetails`, `ProcessingDetails.Timing`, default weight constants, `init(namespace, conf)`, and `getCost(processingDetails)`.

## Control Flow

`setup()` creates a provider and a millisecond-based `ProcessingDetails` with queue, lock-free, lock-shared, and lock-exclusive values. One test asserts `getCost()` before `init()` throws `AssertionError`. The default test initializes empty config and computes cost from default lock weights. The configured test sets namespace-specific weights for queue, lock-free, and lock-shared, includes an unrelated `bar` lock-exclusive key, and asserts only `foo.*` keys apply.

## State And Persistence Behavior

The provider stores initialized weights in memory. `ProcessingDetails` stores timing values by enum in memory; no persistence is involved.

## Dependencies And Integration Points

This tests IPC scheduling cost providers that consume per-call `ProcessingDetails`. It integrates with Hadoop configuration naming under `<namespace>.weighted-cost.*`.

## Risks And Test Signals

Risks include allowing use before initialization, applying wrong namespace weights, ignoring queue weight, or changing default weight behavior. Signals are exact arithmetic expectations and namespace isolation for the unrelated `bar` setting.
