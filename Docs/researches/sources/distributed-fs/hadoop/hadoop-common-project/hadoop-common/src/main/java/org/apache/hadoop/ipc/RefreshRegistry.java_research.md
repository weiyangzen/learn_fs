# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RefreshRegistry.java

## Purpose
`RefreshRegistry` is the in-memory registry that maps refresh identifiers to one or more `RefreshHandler` implementations and dispatches administrative refresh calls.

## Important APIs, Types, and Functions
`defaultRegistry` returns the singleton. `register`, `unregister`, and `unregisterAll` mutate the handler multimap. `dispatch` validates the identifier, invokes handlers, logs responses, wraps handler exceptions as failed `RefreshResponse` objects, and stamps sender names.

## Control Flow
All public registry operations are synchronized. `dispatch` gets handlers for the identifier, fails with valid option names when none exist, iterates handlers, enforces non-null responses, catches exceptions, and returns the collected responses.

## State and Persistence Behavior
State is the `HashMultimap<String, RefreshHandler>` and singleton holder. Registration prevents handler GC until unregistered. There is no durable persistence.

## Dependencies and Integration Points
It depends on shaded Guava `HashMultimap`/`Joiner`, `RefreshHandler`, `RefreshResponse`, and logging. It is a likely backend for `GenericRefreshProtocol` implementations.

## Risks and Test Signals
Risks include memory leaks from forgotten unregisters, synchronized handler execution blocking other refresh operations, and exposing handler class names. Tests should cover multiple handlers, missing identifiers, exception wrapping, null response handling, and unregister paths.
