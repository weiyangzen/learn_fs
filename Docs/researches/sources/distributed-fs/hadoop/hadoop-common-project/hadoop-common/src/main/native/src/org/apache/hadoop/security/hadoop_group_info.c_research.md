# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.c

## Purpose
`hadoop_group_info.c` provides a reusable C context for looking up Unix group records by gid with `getgrgid_r`. It wraps buffer management, retry behavior, and platform error normalization for Hadoop native security code.

## Important APIs, types, and functions
Public functions are `hadoop_group_info_alloc`, `hadoop_group_info_free`, and `hadoop_group_info_fetch`. `hadoop_group_info_clear` resets the embedded `struct group`, and `getgrgid_error_translate` maps platform-specific lookup failures to a narrower Hadoop-facing errno set. The allocation starts with an 8 KiB group buffer and can grow to 2 MiB.

## Control flow
Allocation creates the context and its initial scratch buffer. Fetch clears stale pointers, calls `getgrgid_r`, and loops on `EINTR`. On `ERANGE`, it doubles the buffer up to the maximum before retrying. Success requires both a zero return code and a non-null `struct group *`; a zero return with null group means not found. Other errors are translated so unknown groups become `ENOENT` while resource and I/O failures are preserved.

## State and persistence
The context owns one dynamically sized lookup buffer plus the embedded `struct group` whose string/member pointers point into that buffer. Data remains valid until the next fetch or free. No state is persisted outside the process.

## Dependencies and integration points
It depends on POSIX group database APIs and is used by native user/group mapping code that needs stable group names after discovering gids. The helper isolates libc buffer sizing quirks from JNI-facing code.

## Risks and test signals
Risks include very large group member lists exceeding the 2 MiB cap, callers retaining `struct group` pointers after the context is reused or freed, and platform-specific `getgrgid_r` error behavior. Test signals include nonexistent gids, gids with large membership lists, injected `ERANGE` growth, `EINTR` retry, and resource failures returning `ENOMEM`, `EMFILE`, `ENFILE`, or `EIO`.
