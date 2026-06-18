# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestAccessControlList.java

Purpose: validates `AccessControlList` parsing, string rendering, mutation APIs, wildcard handling, user/group authorization, netgroup integration, and proxied-real-user ACL mode.

Important APIs and types: `AccessControlList`, `UserGroupInformation`, `Groups`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_GROUP_MAPPING`, `NativeCodeLoader`, Mockito spies, and AssertJ/JUnit assertions.

Control flow: the optional netgroup test exits early unless native code and a netgroup-capable group mapping class are configured. It populates ACLs with normal groups and netgroups, validates user group membership and ACL authorization before/after `Groups.refresh`. Core tests assert wildcard parsing for trimmed `*`, human-readable `toString`, round-trip `getAclString`, user/group parsing with spaces and commas, add/remove user/group behavior, illegal wildcard mutation, no-op add/remove on wildcard ACLs, authorization by explicit user and group, and empty ACL avoiding group lookup. The final test checks `USE_REAL_ACLS` so a proxied user's real user can be evaluated.

State and persistence: optional netgroup path depends on host `/etc/netgroup` and native code. Normal tests are in-memory but create UGI test users and may touch group mapping caches.

Dependencies and integration points: integrates ACL grammar, UGI short names/groups, group mapping services, netgroup providers, and proxy-user identity structure.

Risks: manual netgroup test is environment-specific. Empty ACL behavior is verified with a spy to ensure group lookup is skipped, which may be brittle if implementation changes. Wildcard ACL mutation intentionally preserves all-allowed state.

Test signals: strong coverage for ACL syntax, stable rendering/round-trip, mutation semantics, authorization evaluation, wildcard invariants, netgroup support when enabled, and real-user ACL mode.
