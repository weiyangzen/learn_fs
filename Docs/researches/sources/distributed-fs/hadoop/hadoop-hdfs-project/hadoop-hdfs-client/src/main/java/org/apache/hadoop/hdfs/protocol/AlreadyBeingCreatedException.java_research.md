# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AlreadyBeingCreatedException.java

## Purpose
`AlreadyBeingCreatedException` signals that a create request targeted a file that is already open for creation and not yet closed.

## Important APIs, types, and functions
It extends `IOException`, has a stable `serialVersionUID`, and exposes a single message constructor.

## Control flow
There is no behavior beyond exception construction.

## State and persistence behavior
State is the exception message. No local persistence occurs.

## Dependencies and integration points
It is private/evolving HDFS protocol exception used by create/lease-related NameNode and client paths.

## Risks and test signals
Tests should verify message propagation and caller handling in create/append conflict paths. RPC exception mapping should preserve the type where expected.
