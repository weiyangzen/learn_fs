# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestGroupFallback.java

Purpose: Integration tests for shell, netgroup, JNI-with-fallback group mapping implementations against the current OS user.

Important APIs/types/functions: `Groups`, `ShellBasedUnixGroupsMapping`, `ShellBasedUnixGroupsNetgroupMapping`, `JniBasedUnixGroupsMappingWithFallback`, `JniBasedUnixGroupsNetgroupMappingWithFallback`, and `CommonConfigurationKeys.HADOOP_SECURITY_GROUP_MAPPING`.

Control flow: each test configures a group mapping class, creates `Groups`, looks up `System.getProperty("user.name")`, logs the result, and asserts at least one group is returned.

State and persistence: uses OS group database and optional native code; no file state.

Dependencies/integration points: Unix shell commands, netgroup lookup path, native JNI group mapper when available, Hadoop fallback wrappers.

Risks: environment-dependent: users without groups or platforms without netgroup support may fail; tests validate non-empty output rather than exact parity.

Test signals: indicates configured mapping classes can resolve the current user and fallback implementations return usable groups.
