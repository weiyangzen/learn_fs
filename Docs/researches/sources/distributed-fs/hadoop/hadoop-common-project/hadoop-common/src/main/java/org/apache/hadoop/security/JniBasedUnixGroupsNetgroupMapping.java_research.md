# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.java


Purpose: `JniBasedUnixGroupsNetgroupMapping` extends native Unix group resolution with netgroup support for ACLs.

Important APIs and types: It extends `JniBasedUnixGroupsMapping`, declares native `getUsersForNetgroupJNI(String)`, overrides `getGroups(String)`, and uses `NetgroupCache` for inverted user-to-netgroup lookup.

Control flow and state: `getGroups()` first obtains Unix groups from the parent, then appends cached netgroups for the user. Netgroup cache population is driven by `cacheGroupsAdd()`, which clears/rebuilds requested netgroup entries by calling synchronized `getUsersForNetgroup()` because libc netgroup iteration is not reentrant. Native calls strip leading `@` from netgroup names.

Dependencies and integration: It depends on native code, `NetgroupCache`, and the `Groups` refresh/add API. It integrates with ACL code that preloads netgroups of interest rather than trying to enumerate all netgroups for a user.

Risks and test signals: Tests should cover netgroup names versus Unix group names, cache refresh, synchronized JNI calls, and native failures returning empty users. The model only returns netgroups already cached, so ACL preload behavior is critical.
