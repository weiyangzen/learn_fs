# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CallTracker.java

## Purpose
`CallTracker` abstracts cancellation detection for a master RPC or internal operation. It lets `OperationContext` and `RpcContext` discover that a client or state-lock tracker has cancelled the call.

## Important APIs, types, and functions
The interface declares `isCancelled()` and `getType()`. The nested `Type` enum distinguishes `GRPC_CLIENT_TRACKER` from `STATE_LOCK_TRACKER`.

## Control flow
Operation contexts collect trackers. `RpcContext.throwIfCancelled` asks the operation context for cancelled trackers and throws if any are cancelled.

## State and persistence behavior
The interface has no state and no persistence behavior. Implementations hold transport or lock-wait state.

## Dependencies and integration points
It is used by `OperationContext`, `GrpcCallTracker`, state-lock tracking, and long-running file-system operations such as metadata sync and list/status.

## Risks
The interface only reports a boolean, so cancellation reason and timing are limited to the tracker type. Callers must poll cancellation cooperatively; blocking UFS calls cannot be interrupted by this interface alone.

## Test signals
Tests should cover operation-context aggregation of trackers, `RpcContext.throwIfCancelled` messages, and handler attachment of `GrpcCallTracker` for long-running RPCs.
