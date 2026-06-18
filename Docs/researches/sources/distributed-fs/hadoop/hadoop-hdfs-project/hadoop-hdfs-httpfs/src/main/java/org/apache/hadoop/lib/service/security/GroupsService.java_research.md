<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/security/GroupsService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/security/GroupsService.java

## Purpose
`GroupsService` is the concrete group lookup service for HttpFS. It adapts Hadoop's `org.apache.hadoop.security.Groups` to the local `Groups` service interface.

## Important APIs, Types, And Functions
It extends `BaseService` with prefix `groups`. `init` copies the trimmed service config into a Hadoop `Configuration(false)` and constructs `org.apache.hadoop.security.Groups`. `getInterface` returns `Groups.class`. `getGroups` delegates to Hadoop's list-returning method and is deprecated in favor of `getGroupsSet`, which delegates to the set-returning method.

## Control Flow
`Server` initializes this service from `httpfs.groups.*` properties. `HttpFSServer` uses it to check whether the requester belongs to the configured admin group before exposing instrumentation.

## State And Persistence
The service stores a Hadoop `Groups` instance, which may maintain its own in-memory cache according to Hadoop configuration. No state is persisted here.

## Dependencies And Integration Points
It depends on `BaseService`, `ConfigurationUtils`, local `Groups`, and Hadoop security group mapping.

## Risks
Group provider misconfiguration can deny admin access or allow stale membership until Hadoop cache refresh. The deprecated list method remains for compatibility. IOException propagates to REST error handling.

## Test Signals
Tests should cover service-config copying, delegate invocation for list and set forms, IOException propagation, and integration with the instrumentation admin group check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/service/security/GroupsService.java -->
