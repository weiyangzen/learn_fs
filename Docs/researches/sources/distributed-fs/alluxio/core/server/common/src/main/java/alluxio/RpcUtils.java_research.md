# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcUtils.java

## Purpose
`RpcUtils` centralizes server-side gRPC call wrapping for Alluxio masters: timing, in-progress/failure metrics, debug logging, sensitive argument masking, exception translation to gRPC status, and observer completion.

## Important APIs, Types, And Functions
The main entry points are `call`, `callAndReturn`, `invoke`, and `streamingRPCAndLog`. `RpcCallableThrowsIOException` models unary RPC bodies that throw Alluxio/IO exceptions, while `StreamingRpcCallable` adds an `exceptionCaught` hook for stream failure handling. Metric names are decorated with authenticated user tags when present.

## Control Flow, State, Dependencies, Risks, And Tests
Unary calls enter timers, increment in-progress counters, execute the callable, translate `AlluxioRuntimeException`, `AlluxioException`, and `IOException`, and always decrement the counter. Async `invoke` attaches a `whenComplete` callback to a future. Streaming calls optionally send and complete observer responses. State is limited to metrics and logging; no persistence occurs. Dependencies include gRPC observers/statuses, `MetricsSystem`, authentication context, and `SensitiveConfigMask`. Risks include missed counter balance if observer callbacks throw, masking gaps in non-debug streaming error formatting, and broad `RuntimeException | LinkageError` conversion to internal errors. Tests should assert observer events, metric increments/decrements, exception mapping, failure-ok behavior, and sensitive argument masking.
