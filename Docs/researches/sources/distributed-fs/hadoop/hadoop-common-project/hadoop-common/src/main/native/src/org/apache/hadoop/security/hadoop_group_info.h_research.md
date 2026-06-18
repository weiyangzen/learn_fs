# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.h

## Purpose
`hadoop_group_info.h` declares the native group lookup context used by Hadoop's Unix security helpers. It exposes a small lifecycle and fetch API around `struct group` without exposing libc buffer-management details to callers.

## Important APIs, types, and functions
The central type is `struct hadoop_group_info`, containing `buf_sz`, an embedded `struct group`, and the backing `char *buf`. Declared functions are `hadoop_group_info_alloc`, `hadoop_group_info_free`, and `hadoop_group_info_fetch(struct hadoop_group_info *, gid_t)`.

## Control flow
Callers allocate one context, call `hadoop_group_info_fetch` for each gid to refresh the embedded group record, read `ginfo->group` on success, and free the context when finished. Each fetch overwrites previous lookup results.

## State and persistence
The header defines runtime-only state. `struct group` member pointers are valid only while the context and its current buffer remain alive. There is no persistent storage or global cache contract.

## Dependencies and integration points
The header depends on `<grp.h>` for `struct group` and `<unistd.h>` for `size_t`. It is included by `hadoop_group_info.c` and native security components that need gid-to-group-name translation.

## Risks and test signals
Risks are API misuse: dereferencing stale group pointers after a later fetch, freeing a context twice, or assuming fetch never reallocates. Test signals are compile coverage from all native security users plus lookup tests covering successful gid lookup, unknown gid, and large group records.
