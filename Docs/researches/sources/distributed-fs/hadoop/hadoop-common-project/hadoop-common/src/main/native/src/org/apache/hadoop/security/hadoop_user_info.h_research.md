# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.h

## Purpose
`hadoop_user_info.h` declares Hadoop's native Unix user lookup context and its public API. It lets JNI security code share one contract for fetching passwd data and supplementary groups.

## Important APIs, types, and functions
`struct hadoop_user_info` contains `buf_sz`, embedded `struct passwd pwd`, scratch `buf`, supplementary `gid_t *gids`, `num_gids`, and `gids_size`. The API declares allocation/free, `hadoop_user_info_fetch(struct hadoop_user_info *, const char *)`, and `hadoop_user_info_getgroups`.

## Control flow
The intended sequence is allocate, fetch a username, call getgroups if group membership is needed, read `pwd` and `gids`, and free. Every fetch clears previous user and group membership state.

## State and persistence
All state is caller-owned runtime memory. `pwd` string pointers point into `buf`; `gids` is owned by the context and may be reallocated. No information is persisted outside the native process.

## Dependencies and integration points
The header depends on `<pwd.h>` and `<unistd.h>`. It is paired with `hadoop_group_info.h` for user-to-group-name resolution in Hadoop's native group mapping implementation.

## Risks and test signals
Risks include stale pointer use after fetch/free, assuming `gids` ordering beyond the primary-gid-first guarantee, and passing an unfetched context to `hadoop_user_info_getgroups`. Test signals are native builds across Unix platforms and user/group lookup tests with unknown users and high group counts.
