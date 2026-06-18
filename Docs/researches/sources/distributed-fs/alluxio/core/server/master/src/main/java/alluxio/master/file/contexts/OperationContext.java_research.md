# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/OperationContext.java

Purpose: base class for master operation contexts that wrap mutable protobuf builders and carry call-cancellation trackers. It gives all specialized contexts a common `getOptions`, `withTracker`, `getOperationId`, and cancellation query API.

Important APIs and types: generic parameters bind the protobuf builder type and fluent context subtype. `getOptions` returns the wrapped builder, `withTracker` appends a `CallTracker`, `getOperationId` defaults to null, and `getCancelledTrackers` returns only trackers currently reporting cancellation.

Control flow: operation-specific contexts call the constructor with their options builder. RPC handlers add call trackers as needed. Long-running code calls `getCancelledTrackers`; the method first performs a cheap scan for any cancelled tracker, then builds and returns the cancelled subset only when needed.

State and persistence behavior: no persistent state. The mutable options builder drives downstream persistent operations, and cancellation state can stop work before additional journaled changes are made.

Dependencies and integration points: depends on protobuf builders and Alluxio `OperationId`. It is the base for file master contexts and is used by `RpcContext` plumbing.

Risks: annotated `@NotThreadSafe`; both options and tracker list are mutable. Raw generic casts in `withTracker` rely on subclasses using the intended self type. Contexts such as `InternalOperationContext` may pass null options, so generic callers must be defensive.

Test signals: tests should cover cancellation aggregation, empty cancellation fast path, subtype fluent return behavior, and operation-id overrides in specialized contexts.
