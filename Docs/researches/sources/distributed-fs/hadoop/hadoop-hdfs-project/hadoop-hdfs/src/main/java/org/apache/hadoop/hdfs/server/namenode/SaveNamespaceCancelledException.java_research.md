# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/SaveNamespaceCancelledException.java

## Purpose
`SaveNamespaceCancelledException` is the package-private checked exception used to abort a running `saveNamespace` operation when cancellation is requested.

## Important APIs, types, and functions
It extends `IOException`, has a `serialVersionUID`, and a package-private constructor that stores the cancellation reason as the message.

## Control flow
`SaveNamespaceContext.checkCancelled()` throws it when the associated `Canceler` is set. Save workers can distinguish cancellation from storage failures.

## State and persistence behavior
The exception carries only a message and performs no persistence. Its effect is to interrupt fsimage save work.

## Dependencies and integration points
It depends on `IOException` and private audience annotations. It integrates with `SaveNamespaceContext` and FSImage save workflows.

## Risks and invariants
Because it is an `IOException`, callers must avoid treating user-requested cancellation as a failed storage directory or corruption. Package-private construction keeps use localized.

## Test signals
`TestSaveNamespace` and cancellation tests should verify reason propagation and that canceled saves do not mark storage failed unless a real I/O error occurred.
