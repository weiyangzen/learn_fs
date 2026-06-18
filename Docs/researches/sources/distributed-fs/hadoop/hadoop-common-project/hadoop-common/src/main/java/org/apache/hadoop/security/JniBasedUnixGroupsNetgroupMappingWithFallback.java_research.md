# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMappingWithFallback.java


Purpose: `JniBasedUnixGroupsNetgroupMappingWithFallback` chooses native or shell-based netgroup-aware group resolution.

Important APIs and types: It implements `GroupMappingServiceProvider` and delegates to either `JniBasedUnixGroupsNetgroupMapping` or `ShellBasedUnixGroupsNetgroupMapping`.

Control flow and state: The constructor checks native code availability and creates the appropriate delegate. All public methods forward directly to that delegate.

Dependencies and integration: It depends on `NativeCodeLoader`, both native and shell netgroup providers, and `Groups` as the outer service.

Risks and test signals: Tests should cover native-present and native-absent selection and delegate forwarding. Production behavior can change across hosts if native Hadoop libraries are inconsistently installed.
