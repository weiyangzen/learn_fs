# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoNamenodesAvailableException.java

## Purpose
`NoNamenodesAvailableException` is a typed `IOException` for the case where a nameservice is known, but no usable NameNode is available for routing.

## Important APIs, Types, And Functions
- Constructor `NoNamenodesAvailableException(String nsId, IOException ioe)` wraps the underlying IO failure with a nameservice-specific message.

## Control Flow
The class has no internal control flow. Router client code throws it after resolver or connection attempts fail for a nameservice.

## State And Persistence
The exception stores the formatted message and cause via `IOException`. It carries no extra fields.

## Dependencies And Integration Points
It depends only on `IOException` and is consumed by router RPC error handling, fault-tolerant routing, and client-facing diagnostics.

## Risks And Edge Cases
Callers should preserve the underlying cause to avoid hiding whether the failure was resolver staleness, all NameNodes down, connection timeout, or access failure. Long-lived unavailable states need tests that verify retry/failover behavior rather than merely message formatting.

## Test Signals
`TestNoNamenodesAvailableLongTime`, `TestRouterFaultTolerant`, and failover/router RPC tests provide direct and indirect coverage of prolonged NameNode unavailability and error propagation.
