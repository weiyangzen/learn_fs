# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/Error.java

## Purpose
`Error` is a small wrapper for communicating an `AlluxioStatusException` and a client-notification decision between gRPC event threads and worker data threads.

## Important APIs, Types, and Functions
The constructor stores the cause and `notifyClient` flag. `getCause()`, `isNotifyClient()`, and `toString()` are the only methods.

## Control Flow, State, and Persistence
The object is immutable and has no persistence behavior. It is used as terminal request state in read/write contexts where an internal error may or may not need to be sent back to the client.

## Dependencies and Integration Points
It depends on `AlluxioStatusException` and is referenced by `BlockReadRequestContext` and `WriteRequestContext`.

## Risks and Test Signals
The primary risk is semantic: callers must consistently honor `notifyClient`. Tests should verify that notify and non-notify errors produce the intended stream termination behavior.
