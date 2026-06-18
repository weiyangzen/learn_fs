<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMapping.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMapping.c

## Purpose
`JniBasedUnixGroupsMapping.c` implements Unix JNI group lookup for Hadoop security. It resolves the Unix groups associated with a user and returns Java string arrays.

## Important APIs, Types, and Functions
JNI exports are `anchorNative()` and `getGroupsForUser()`. It caches Java `logError(int,String)` and `java.lang.String` class references. Internal `logError()` reports group-id lookup failures back to Java. It uses `hadoop_user_info_*` and `hadoop_group_info_*` helper APIs.

## Control Flow
`anchorNative()` caches method/class references. `getGroupsForUser()` optionally enters the global `pw_lock_object`, converts the Java username, allocates user info, fetches passwd data, returns an empty array for unknown users, obtains group IDs, allocates an initial Java array sized to the gid count, resolves each gid to a group name, logs failures for individual gids, and compacts the Java array if some groups could not be resolved.

## State and Persistence
Static method/class references persist after anchoring. `pw_lock_object` is shared with NativeIO's password/group lookup workaround. User and group info allocations are per-call and freed before return.

## Dependencies and Integration Points
It depends on Unix passwd/group facilities through Hadoop helper wrappers, `exception.c`, and Java `JniBasedUnixGroupsMapping`. It integrates with Hadoop authorization and user/group mapping services.

## Risks and Edge Cases
Global `g_string_clazz` is not freed in this file. Some local references in compaction paths depend on JVM local-reference capacity. Partial group lookup failures are logged and omitted rather than failing the whole lookup. Thread safety depends on optional `pw_lock_object` initialization by NativeIO.

## Test Signals
Tests should cover existing users, unknown users, users with many groups, failed gid-to-name lookups, concurrent lookups with and without the lock workaround, and Java `logError` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMapping.c -->
