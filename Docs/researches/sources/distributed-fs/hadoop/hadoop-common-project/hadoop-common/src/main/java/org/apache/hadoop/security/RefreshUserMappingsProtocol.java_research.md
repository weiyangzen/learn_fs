# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RefreshUserMappingsProtocol.java


Purpose: `RefreshUserMappingsProtocol` is the IPC protocol for refreshing user/group and superuser proxy-group mappings in running Hadoop daemons.

Important APIs and types: It declares protocol version `1L`, `refreshUserToGroupsMappings()`, and `refreshSuperUserGroupsConfiguration()`, both throwing `IOException`. The interface is annotated with `@KerberosInfo(serverPrincipal=HADOOP_SECURITY_SERVICE_USER_NAME_KEY)`, and both methods are marked `@Idempotent`.

Control flow and state: The interface contains no implementation state. Server implementations perform actual cache invalidation or configuration reload when invoked.

Dependencies and integration: It is annotated with `@KerberosInfo` in related Hadoop code and used by admin refresh commands against NameNode, ResourceManager, and other services that expose mapping refresh operations.

Risks and test signals: Implementations should test authorization, Kerberos service principal configuration, RPC compatibility, cache invalidation, idempotent retry behavior, and propagation of IO failures. The interface itself needs compile and protocol-version compatibility checks.
