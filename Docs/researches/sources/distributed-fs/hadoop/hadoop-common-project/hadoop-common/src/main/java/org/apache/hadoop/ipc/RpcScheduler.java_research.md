# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcScheduler.java

## Purpose
`RpcScheduler` defines the priority, backoff, and response-time feedback interface used by Hadoop RPC servers to schedule calls.

## Important APIs, Types, and Functions
`getPriorityLevel(Schedulable)` returns queue priority. `shouldBackOff(Schedulable)` advises overload rejection/backoff. `addResponseTime(String, Schedulable, ProcessingDetails)` records timing feedback. A deprecated integer overload remains for old implementations. `stop()` shuts down scheduler resources.

## Control Flow
Server call admission asks priority/backoff methods. After a response, the server reports timing details. The default modern `addResponseTime` converts `ProcessingDetails` queue/processing times to the metrics default unit and delegates to the deprecated method for backward compatibility.

## State and Persistence Behavior
The interface has no state. Implementations may maintain in-memory decay counters, costs, or metrics.

## Dependencies and Integration Points
It depends on `Schedulable`, `ProcessingDetails`, and `RpcMetrics.DEFAULT_METRIC_TIME_UNIT`; used by call queues and scheduler implementations.

## Risks and Test Signals
Risks include old implementations throwing `UnsupportedOperationException` if they do not override the modern method, integer truncation, and inconsistent priority ranges. Tests should cover priority mapping, backoff decisions, timing feedback, and `stop`.
