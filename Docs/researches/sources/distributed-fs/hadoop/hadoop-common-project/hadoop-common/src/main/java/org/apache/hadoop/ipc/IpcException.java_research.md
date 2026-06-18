# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/IpcException.java

## Purpose
`IpcException` is a minimal checked exception for IPC-layer failures where an IPC connection cannot be established.

## Important APIs, Types, and Functions
It extends `IOException`, defines `serialVersionUID = 1L`, and exposes a single string-message constructor.

## Control Flow
There is no special control flow. Callers throw it to distinguish low-level IPC connection setup failures from service-side RPC errors.

## State and Persistence Behavior
Only the inherited exception message/cause state exists. Nothing is persisted.

## Dependencies and Integration Points
It integrates with Hadoop client/server connection code through the common `IOException` path.

## Risks and Test Signals
The risk is mostly semantic: callers may overuse this generic type and lose detailed diagnostics. Tests should verify connection-failure paths preserve the original message and are handled as IO failures.
