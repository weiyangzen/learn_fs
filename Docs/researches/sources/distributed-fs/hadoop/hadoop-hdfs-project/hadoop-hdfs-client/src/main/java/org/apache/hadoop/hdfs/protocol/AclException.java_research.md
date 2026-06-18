# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AclException.java

## Purpose
`AclException` is an HDFS private `IOException` subclass for failures while manipulating ACLs.

## Important APIs, types, and functions
It provides constructors for a message and for a message plus cause.

## Control flow
There is no behavior beyond exception construction.

## State and persistence behavior
State is standard exception message/cause plus `serialVersionUID`. No persistence occurs.

## Dependencies and integration points
It depends on `IOException` and Hadoop classification annotations. It is thrown by ACL-related HDFS protocol/client/server code.

## Risks and test signals
Tests should verify message/cause propagation and serialization compatibility if used across RPC boundaries. Behavioral risk is low.
