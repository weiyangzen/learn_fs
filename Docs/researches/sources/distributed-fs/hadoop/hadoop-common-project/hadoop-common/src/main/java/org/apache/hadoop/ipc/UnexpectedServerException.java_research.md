<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UnexpectedServerException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UnexpectedServerException.java

## Purpose
`UnexpectedServerException` represents an undeclared exception thrown by an RPC service implementation and surfaced through Hadoop IPC as an `RpcException`.

## Important APIs, Types, And Functions
- Package-visible constructors accept a message or message plus cause.
- Inherits RPC exception behavior from `RpcException`.

## Control Flow
This is a data-bearing exception class. Creation is controlled by IPC exception translation code outside this file.

## State And Persistence
Stores message and optional cause in memory; may be serialized through Hadoop RPC exception handling.

## Dependencies And Integration Points
Depends on `RpcException` and integrates with RPC client/server exception translation for unexpected service-side failures.

## Risks And Edge Cases
Constructors are package-private, so public construction is intentionally constrained to IPC internals. Changing visibility or inheritance can alter client-visible exception compatibility.

## Test Signals
RPC tests that invoke service methods throwing undeclared runtime or checked exceptions should observe the expected wrapped exception type and cause.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UnexpectedServerException.java -->
