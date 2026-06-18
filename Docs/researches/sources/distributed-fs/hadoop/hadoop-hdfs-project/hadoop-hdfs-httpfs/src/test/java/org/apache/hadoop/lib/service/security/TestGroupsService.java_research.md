# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/security/TestGroupsService.java

Purpose: Unit/integration tests for `GroupsService` registration and invalid group-mapping configuration.

Important APIs/types/functions: tests `service` and `invalidGroupsMapping`; service classes `GroupsService` and `Groups`.

Control flow: the positive test initializes a server with `GroupsService`, retrieves `Groups`, asks for groups for the current OS user, and asserts the list is not empty. The negative test configures `server.groups.hadoop.security.group.mapping` to `String.class`, initializes the server, and expects a runtime failure.

State and persistence: only temporary server directories; group lookup depends on current user and OS/group mapping.

Dependencies/integration: Hadoop group mapping, server service container, `StringUtils` service-list construction.

Risks and test signals: catches service publication and invalid mapping failures. The positive test is environment-sensitive because current-user group resolution must return at least one group.
