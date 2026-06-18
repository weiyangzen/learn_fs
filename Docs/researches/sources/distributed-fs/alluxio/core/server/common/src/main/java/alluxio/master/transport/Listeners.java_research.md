# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/transport/Listeners.java

## Purpose
`Listeners` is a small thread-safe listener registry that preserves the messaging context active at listener registration and replays events on that context when possible.

## Important APIs, Types, and Functions
It exposes `size()`, `add(Consumer<T>)`, `accept(T)`, and `iterator()`. Inner `ListenerHolder` implements `Listener<T>` with `accept(T)`, `close()`, `getContext()`, and `getListener()`. Storage is a `CopyOnWriteArrayList`.

## Control Flow, State, and Persistence
`add()` captures `GrpcMessagingContext.currentContext()` and returns a holder. `accept(T)` iterates listeners, executing callbacks on their captured context when present or inline otherwise, and returns a future aggregating context-executed callbacks. `ListenerHolder.accept()` similarly schedules or runs the callback and ignores rejected execution. `close()` removes the holder from the list.

## Dependencies and Integration Points
It depends on `GrpcMessagingContext`, `Listener`, Java futures, and Guava `Preconditions`. It is used for `GrpcMessagingConnection` close and exception listeners.

## Risks and Test Signals
Risks include inline listener exceptions interrupting dispatch, ignored rejected executions, raw generic use, and the aggregate future not representing inline callback failures. Signals are context capture, close removal, size changes, and callback execution order under concurrent modification.
