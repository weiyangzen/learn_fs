# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/SubClusterTimeoutException.java

## Purpose
`SubClusterTimeoutException` is a specific `IOException` type used when a Router operation times out waiting for a subcluster response.

## Important APIs and Types
It extends `IOException`, defines `serialVersionUID = 1L`, and provides a single `SubClusterTimeoutException(String msg)` constructor.

## Control Flow
The class has no internal control flow. Callers can throw it to let upstream code distinguish timeout failures from other IO failures.

## State and Persistence
It carries only the inherited exception message and stack trace. There is no persistence behavior.

## Dependencies and Integration Points
It integrates with router RPC exception handling and any timeout-aware caller logic. It may be used by concurrent invocation paths that apply per-subcluster timeouts.

## Risks
Because it is an `IOException`, generic catch blocks may erase the timeout distinction unless they check the concrete type. The message should include enough namespace/path context at throw sites.

## Test Signals
Tests should assert timeout paths throw this specific type where intended and that client-visible error handling treats it as retriable or partial according to the operation contract.
