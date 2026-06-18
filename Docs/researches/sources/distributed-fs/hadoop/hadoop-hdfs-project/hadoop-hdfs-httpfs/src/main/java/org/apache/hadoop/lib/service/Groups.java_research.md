<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Groups.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Groups.java

## Purpose
`Groups` is the service interface for resolving a user to Hadoop groups, used by HttpFS authorization decisions.

## Important APIs, Types, And Functions
It exposes `List<String> getGroups(String user)` and `Set<String> getGroupsSet(String user)`, both throwing `IOException`. The set form is used by admin group checks.

## Control Flow
`HttpFSServer` calls `getGroupsSet` during `INSTRUMENTATION` requests to require membership in the configured admin group. `GroupsService` implements this interface using Hadoop security groups.

## State And Persistence
The interface has no state. Implementation state is in Hadoop group mapping/cache.

## Dependencies And Integration Points
It depends on Java collections and `IOException`, and integrates with `GroupsService` and authorization logic.

## Risks
Group lookup failures surface as request failures. Set/list consistency depends on the implementation.

## Test Signals
Tests should cover admin membership checks, lookup failure propagation, and expected group cache behavior in `GroupsService`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/Groups.java -->
