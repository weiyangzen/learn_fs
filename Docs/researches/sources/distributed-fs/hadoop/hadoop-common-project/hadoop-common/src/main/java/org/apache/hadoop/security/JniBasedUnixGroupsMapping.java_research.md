# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsMapping.java


Purpose: `JniBasedUnixGroupsMapping` uses Hadoop native code to resolve Unix group memberships for a user.

Important APIs and types: It implements `GroupMappingServiceProvider`, declares native `anchorNative()` and `getGroupsForUser(String)`, returns list and set forms, and has no-op cache methods.

Control flow and state: A static initializer requires `NativeCodeLoader.isNativeCodeLoaded()`, anchors JNI resources, and fails construction if native code is unavailable. Lookups call the native function, log exceptions, and return an empty group array on failure. `getGroupsSet()` preserves native order through `LinkedHashSet`.

Dependencies and integration: It depends on Hadoop native libraries, `NativeCodeLoader`, commons collection helpers, and `Groups` as the outer cache/service.

Risks and test signals: Tests should cover native-unavailable behavior through the fallback wrapper, native exceptions returning empty groups, and duplicate group removal. Operationally, empty results are later treated by `Groups` as no-groups failures and may populate the negative cache.
