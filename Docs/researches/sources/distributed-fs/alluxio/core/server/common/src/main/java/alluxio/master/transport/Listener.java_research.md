# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listener.java

## Purpose
`Listener` represents a registered event consumer that can unregister itself through `close()`.

## Important APIs, Types, and Functions
It extends `Consumer<T>` and `AutoCloseable`, defining `close()` with no checked exception.

## Control Flow, State, and Persistence
The interface has no state. Implementations consume events and remove themselves from their owner when closed.

## Dependencies and Integration Points
It depends on `Consumer` and is implemented by `Listeners.ListenerHolder`. `GrpcMessagingConnection` returns listener handles for exception and close events.

## Risks and Test Signals
Risks include forgetting to close listener handles and listener callbacks throwing. Signals are unregister behavior and no further events after close.
