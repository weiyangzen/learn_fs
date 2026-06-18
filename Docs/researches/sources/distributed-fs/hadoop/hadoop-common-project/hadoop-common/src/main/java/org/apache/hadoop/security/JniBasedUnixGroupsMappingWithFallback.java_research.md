# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMappingWithFallback.java


Purpose: `JniBasedUnixGroupsMappingWithFallback` selects the native Unix group resolver when Hadoop native code is available and otherwise delegates to shell-based group lookup.

Important APIs and types: It implements `GroupMappingServiceProvider` and delegates all group lookup and cache calls to a private provider instance.

Control flow and state: Construction checks `NativeCodeLoader.isNativeCodeLoaded()`. Native availability creates `JniBasedUnixGroupsMapping`; absence logs a performance advisory and creates `ShellBasedUnixGroupsMapping`.

Dependencies and integration: It is the default provider used by `Groups` in this code path. It depends on native loader status, the JNI provider, shell provider, and Hadoop performance advisory logging.

Risks and test signals: Tests should verify provider selection, delegation for list/set paths, and cache method forwarding. Behavior can differ between environments depending on native library availability.
