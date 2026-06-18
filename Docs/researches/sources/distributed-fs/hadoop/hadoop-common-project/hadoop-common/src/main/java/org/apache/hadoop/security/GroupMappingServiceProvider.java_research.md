# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/GroupMappingServiceProvider.java


Purpose: `GroupMappingServiceProvider` defines the pluggable contract for mapping users to operating-system, LDAP, or netgroup memberships.

Important APIs and types: Implementations must provide `getGroups(String)`, `cacheGroupsRefresh()`, and `cacheGroupsAdd(List<String>)`. The default `getGroupsSet(String)` converts the list result into a `LinkedHashSet` to preserve order while removing duplicates.

Control flow and state: The interface has no state. The default method is a convenience path that avoids forcing every legacy provider to implement a set-returning method.

Dependencies and integration: It exposes the shared prefix `CommonConfigurationKeysPublic.HADOOP_SECURITY_GROUP_MAPPING` and is consumed by `Groups`, `CompositeGroupsMapping`, JNI/shell providers, and LDAP providers.

Risks and test signals: Provider tests should verify empty results for unknown users, IOException behavior, and cache refresh/add semantics. High-cardinality group users should prefer implementations overriding `getGroupsSet()` directly.
