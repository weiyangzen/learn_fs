# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RetriableException.java

## Purpose
`RetriableException` signals a temporary server condition where clients may retry, such as startup or transient unavailability.

## Important APIs, Types, and Functions
It extends `IOException`, has constructors from `Exception` and `String`, and is marked evolving.

## Control Flow
Server code throws it; RPC wraps it remotely; client retry policies inspect the class name after `RemoteException` unwrapping and decide whether to retry.

## State and Persistence Behavior
Only normal exception state exists. It persists nothing.

## Dependencies and Integration Points
It integrates with Hadoop retry policies and RPC remote exception handling.

## Risks and Test Signals
Risks include retry storms if thrown for non-transient conditions and lost cause type when using the string constructor. Tests should cover retry policy classification and remote unwrap behavior.
