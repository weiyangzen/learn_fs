# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.c

## Purpose
`hadoop_user_info.c` provides a reusable native context for resolving Unix user records and supplementary groups. It is the lower-level implementation behind JNI group mapping code that needs `passwd` fields, gids, and deterministic placement of the user's primary gid.

## Important APIs, types, and functions
Public functions are `hadoop_user_info_alloc`, `hadoop_user_info_free`, `hadoop_user_info_fetch`, and `hadoop_user_info_getgroups`. Helpers include `hadoop_user_info_clear`, `getpwnam_error_translate`, and `put_primary_gid_first`. Constants define an initial supplementary-gid array of 32 entries and a maximum passwd buffer size of 32 KiB.

## Control flow
Allocation sizes the passwd scratch buffer from `_SC_GETPW_R_SIZE_MAX`, with a 1 KiB floor. `hadoop_user_info_fetch` clears any previous result, calls `getpwnam_r`, retries `EINTR`, doubles the scratch buffer on `ERANGE`, and returns success only if libc supplies a non-null `struct passwd *`. `hadoop_user_info_getgroups` requires a valid fetched user, allocates or grows a gid array, calls `getgrouplist`, accounts for Linux versus FreeBSD return-code semantics, retries after resizing if necessary, and swaps the primary gid to index zero.

## State and persistence
The context owns a passwd buffer, an embedded `struct passwd`, and a dynamically allocated gid array. Lookup results persist until the next fetch, getgroups call, clear, or free. There is no disk persistence or global cache.

## Dependencies and integration points
It depends on POSIX passwd/group APIs and feeds Hadoop's JNI-based group mapping implementation. Java-facing code can use it to map usernames to group names by resolving a user, enumerating gids, then using `hadoop_group_info` for gid names.

## Risks and test signals
Risks include platform-specific `getgrouplist` return values, NSS backends that return zero or inconsistent group counts, primary gid missing from supplementary results, and callers keeping pointers after context reuse. Test signals include users with only primary group, users with more than 32 groups, unknown users, NSS failures, `ERANGE` passwd-buffer growth, and cross-platform Linux/BSD behavior.
