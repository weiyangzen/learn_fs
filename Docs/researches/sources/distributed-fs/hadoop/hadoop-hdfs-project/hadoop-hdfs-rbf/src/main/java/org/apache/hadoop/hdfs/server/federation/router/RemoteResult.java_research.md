# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteResult.java

## Purpose
`RemoteResult` is a typed container for the outcome of invoking a remote operation against one `RemoteLocationContext`. It can hold either a result, including a void-style explicit result marker, or an `IOException`.

## Important APIs, Types, And Functions
- `RemoteResult(T location, R result)` records a successful result and sets `resultSet`.
- `RemoteResult(T location, IOException e)` records a failed result.
- `getLocation`, `hasResult`, `getResult`, `hasException`, and `getException` expose the outcome.
- `toString` includes location plus result and/or exception details.

## Control Flow
The class has no complex control flow. It encodes success and failure with constructor choice and boolean checks.

## State And Persistence
State is immutable after construction: location, result, result-present flag, and exception. It is process-local and not persisted.

## Dependencies And Integration Points
It depends on `IOException` and `RemoteLocationContext`. Router RPC fan-out code can use it to return partial results while preserving per-location failure details.

## Risks And Edge Cases
A successful result may itself be null while `hasResult` remains true, which is useful for void-like calls but requires callers to check `hasResult` rather than `getResult() != null`. The failure constructor sets `resultSet` false even if the failed operation might have produced partial side effects.

## Test Signals
Coverage is indirect through fan-out methods in `RouterRpcClient`, quota aggregation, cache admin, and multi-destination tests that inspect per-location results or exception handling.
