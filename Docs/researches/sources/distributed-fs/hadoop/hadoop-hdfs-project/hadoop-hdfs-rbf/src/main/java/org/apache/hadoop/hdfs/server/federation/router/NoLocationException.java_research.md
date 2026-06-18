# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/NoLocationException.java

## Purpose
`NoLocationException` is a typed `IOException` thrown when the Router cannot map a federation path to any remote location, so it cannot forward the request to a subcluster.

## Important APIs, Types, And Functions
- Constructor `NoLocationException(String path, Class<?> t)` formats the path and calling class simple name into a diagnostic message.

## Control Flow
There is no internal branching. Callers create the exception at location-resolution failure points and propagate it through normal HDFS client RPC error handling.

## State And Persistence
The exception carries only the inherited message and serial version UID. It has no persistence behavior.

## Dependencies And Integration Points
It depends only on `IOException`. Router RPC modules and resolvers use it to distinguish "no mount/location" failures from downstream NameNode failures.

## Risks And Edge Cases
The message includes the class simple name but not resolver state or candidate mount table entries, so debugging may require surrounding logs. It does not store path/type as structured fields. Callers must avoid using it when locations exist but all NameNodes are unavailable; that condition has a separate exception type.

## Test Signals
Missing mount and path resolution behavior is exercised indirectly by router mount table, missing-folder, and RPC tests such as `TestRouterMissingFolderMulti`, `TestRouterMountTable`, and multi-destination router RPC tests.
