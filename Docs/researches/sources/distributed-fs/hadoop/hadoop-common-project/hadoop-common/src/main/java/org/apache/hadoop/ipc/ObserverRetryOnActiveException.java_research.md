# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ObserverRetryOnActiveException.java

## Purpose
This exception tells HDFS observer clients that a request failed on an ObserverNode and should be retried against the active NameNode directly rather than cycling through other observers.

## Important APIs, Types, and Functions
It extends `StandbyException`, is private/evolving, has `serialVersionUID = 1L`, and provides a single message constructor.

## Control Flow
Server-side observer code throws this when observer retry is inappropriate. Client retry policy detects the remote exception class and redirects to the active endpoint.

## State and Persistence Behavior
Only exception message state is stored. It has no persistence role.

## Dependencies and Integration Points
It depends on `StandbyException` and integrates with HDFS observer read retry/failover handling through Hadoop RPC remote exception wrapping.

## Risks and Test Signals
Risks are class-name compatibility across remote exception unwrapping and incorrect retry policy interpretation. Tests should cover wrapping/unwrapping through `RemoteException` and active-only retry behavior.
