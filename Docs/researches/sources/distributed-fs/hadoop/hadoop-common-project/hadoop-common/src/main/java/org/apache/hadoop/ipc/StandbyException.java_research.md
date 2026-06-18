<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/StandbyException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/StandbyException.java

## Purpose
`StandbyException` is an evolving `IOException` used when a contacted server is alive but not currently active in an HA group.

## Important APIs, Types, And Functions
- `public class StandbyException extends IOException`.
- `serialVersionUID` is fixed.
- Constructor `StandbyException(String msg)` stores the diagnostic message.

## Control Flow
There is no internal control flow beyond exception construction. Server-side code can throw or tunnel it, and `Server.Connection.getTrueCause` explicitly unwraps this type so clients see standby semantics instead of a generic wrapper.

## State And Persistence
State is the normal throwable message/cause stack held in memory and serialized through RPC exception handling when returned remotely.

## Dependencies And Integration Points
Used by HA-aware services and retry/failover logic. `Server` treats it as terse-log by default and as a true cause during SASL/token error unwrapping.

## Risks And Edge Cases
Changing the type hierarchy would affect failover policies that distinguish standby from other IO failures. Overly broad wrapping can hide this exception unless unwrapped.

## Test Signals
HA failover tests should verify standby responses are propagated to clients and logged tersely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/StandbyException.java -->
