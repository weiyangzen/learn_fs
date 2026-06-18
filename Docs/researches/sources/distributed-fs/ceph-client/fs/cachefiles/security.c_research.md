# sources/distributed-fs/ceph-client/fs/cachefiles/security.c

## Purpose
`security.c` prepares and validates credentials used by the kernel to access the CacheFiles backing filesystem.

## Important APIs, Types, and Functions
Public functions are `cachefiles_get_security_ID` and `cachefiles_determine_cache_security`. The local helper `cachefiles_check_cache_dir` probes LSM permission for directory and file creation.

## Control Flow
`cachefiles_get_security_ID` prepares kernel credentials from the current task and optionally applies a daemon-provided security context ID. `cachefiles_determine_cache_security` duplicates current creds, temporarily drops the override, derives file-creation security from the cache root inode with `set_create_files_as`, replaces `cache->cache_cred`, reinstalls the override, and checks whether mkdir/create are allowed in the root. `-EOPNOTSUPP` from permission probing is treated as acceptable.

## State and Persistence Behavior
The main runtime state is `cache->cache_cred`, plus optional `secid`/`have_secid` set by the daemon. These credentials do not persist on their own, but they determine labels and permission behavior for subsequently created backing directories and files.

## Dependencies and Integration Points
This file integrates LSM hooks, kernel credential APIs, daemon `secctx`, `cachefiles_begin_secure`/`cachefiles_end_secure`, and `cachefiles_add_cache` bind validation.

## Risks and Edge Cases
Credential override ordering is delicate: returning without reinstalling the override would break callers. Bad security contexts must fail bind before cache operations begin. LSMs that do not support create checks may return `-EOPNOTSUPP`, which is intentionally normalized.

## Test Signals
Test bind with and without `secctx`, invalid security contexts, SELinux/AppArmor create denials, backing directories with incompatible labels, and audit logs for created cache files.
