# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/NetgroupCache.java


Purpose: `NetgroupCache` inverts cached netgroup-to-users data into a user-to-netgroups map for fast ACL membership checks.

Important APIs and types: Static APIs include `getNetgroups(user, List<String>)`, `getNetgroupNames()`, `isCached(group)`, `clear()`, and `add(group, users)`. The backing map is `ConcurrentHashMap<String, Set<String>>`.

Control flow and state: `add()` iterates users, creates a concurrent set for each absent user using `putIfAbsent`, and adds the group. `getNetgroups()` appends any cached groups for a user to a caller-supplied list. `getGroups()` scans all values to derive known netgroup names.

Dependencies and integration: It is used by netgroup-aware JNI and shell group mapping providers. ACL code calls provider cache-add paths to populate netgroups of interest.

Risks and test signals: Tests should cover concurrent adds for the same user, clear behavior, duplicate group handling, and `isCached()` derived from values. The cache is process-global and unbounded except for explicit clear/rebuild.
