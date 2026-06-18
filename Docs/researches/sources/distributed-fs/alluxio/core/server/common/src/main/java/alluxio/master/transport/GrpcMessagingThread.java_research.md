# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/GrpcMessagingThread.java

## Purpose
`GrpcMessagingThread` is a `Thread` subclass that can hold the `GrpcMessagingContext` associated with the current messaging execution thread.

## Important APIs, Types, and Functions
It defines a constructor, `setContext(GrpcMessagingContext)`, and `getContext()`. The context is stored as a `WeakReference`.

## Control Flow, State, and Persistence
The thread starts with no context. `GrpcMessagingContext` sets itself after the thread is obtained from the executor. `getContext()` returns `null` if the weak reference has not been set or has been cleared. There is no persistence.

## Dependencies and Integration Points
It is created by `GrpcMessagingThreadFactory` and inspected by `GrpcMessagingContext.currentContext()`.

## Risks and Test Signals
Risks include weak-reference clearing, accidental use of non-messaging threads, and a typo in documentation not affecting behavior. Signals are context lookup from within the executor thread and `currentContextOrThrow()` rejection on ordinary threads.
