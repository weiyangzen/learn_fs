# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProcessingDetails.java

## Purpose
`ProcessingDetails` records per-RPC timing breakdowns and response status for queueing, handling, processing, locking, and response phases. It supports metrics, logging, scheduler feedback, and deferred-response accounting.

## Important APIs, Types, and Functions
The `Timing` enum covers `ENQUEUE`, `QUEUE`, `HANDLER`, `PROCESSING`, `LOCKFREE`, `LOCKWAIT`, `LOCKSHARED`, `LOCKEXCLUSIVE`, and `RESPONSE`. `get`, `set`, and `add` convert values through the instance `TimeUnit`. `setReturnStatus` and `getReturnStatus` track `RpcStatusProto`.

## Control Flow
Callers create a details object with a base unit, increment or set phase timings as an RPC moves through the server, then consume values for metrics. Negative values are clamped to zero on read to hide rare `nanoTime` regressions. Protobuf deferred callbacks update processing and lock-free time before setting the deferred response/error.

## State and Persistence Behavior
State is per-call and in-memory. No durable persistence is performed.

## Dependencies and Integration Points
It depends on protobuf RPC status enums and is used by `Server.Call`, `RpcScheduler.addResponseTime`, weighted cost providers, and tests such as `TestProcessingDetails`, `TestDecayRpcScheduler`, and `TestWeightedTimeCostProvider`.

## Risks and Test Signals
Risks include unit-conversion mistakes, overflow/truncation when schedulers cast to int, and inconsistent `PROCESSING` vs lock component accounting. Tests should assert conversions, `toString` format, negative clamping, and scheduler cost calculations.
