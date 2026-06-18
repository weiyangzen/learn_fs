<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cred.h -->
# sources/distributed-fs/ceph-client/include/linux/cred.h

## Purpose

`cred.h` defines Linux task credential structures and helpers for UID/GID, capabilities, keyrings, LSM security, user namespaces, supplementary groups, copy-on-write credential replacement, override/revert credentials, and safe current/task credential access. The source was read as a complete 429-line file.

## Important APIs, Types, and Functions

`struct group_info` stores refcounted supplementary groups. `struct cred` stores real/saved/effective/fs UID/GID, securebits, capability sets, optional keyrings, optional LSM security pointer, user and namespace accounting, supplementary groups, and RCU deletion state. Group APIs include `get_group_info()`, `put_group_info()`, `groups_alloc()`, `groups_free()`, `in_group_p()`, `in_egroup_p()`, `groups_search()`, `set_current_groups()`, `set_groups()`, `may_setgroups()`, and `groups_sort()`. Credential APIs include `prepare_creds()`, `prepare_exec_creds()`, `commit_creds()`, `abort_creds()`, `prepare_kernel_cred()`, `kernel_cred()`, `set_security_override()`, `set_create_files_as()`, `cred_fscmp()`, `cred_init()`, `set_cred_ucounts()`, `override_creds()`, `revert_creds()`, `get_cred*()`, `put_cred*()`, current/task accessor macros, and namespace helpers.

## Control Flow

Credential updates follow copy-on-write: allocate or prepare a mutable credential, modify it, validate invariants such as ambient capabilities, then atomically commit it to the task. Temporary privilege changes use `override_creds()` and `revert_creds()` or scoped wrappers. Readers access current credentials directly or other tasks' objective credentials under RCU or by pinning with `get_task_cred()`.

## State and Persistence Behavior

Credentials are refcounted immutable objects once committed and freed through RCU unless marked non-RCU. Task `real_cred` and `cred` distinguish objective and subjective security context. Supplementary groups are separately refcounted. Keyrings, user namespace, user/ucounts, and LSM security pointers persist through the credential lifetime.

## Dependencies and Integration Points

It depends on capabilities, init, keys, atomic/refcount, uidgid, scheduler, and user accounting. It integrates with VFS permission checks, process management, exec/fork, LSMs, user namespaces, keyrings, capabilities, and multiuser/group management.

## Risks and Edge Cases

Committed credentials should be treated as immutable despite non-const internals for refcounts. Accessing another task's credentials without RCU or a pinned reference is unsafe. Ambient capabilities must remain a subset of permitted and inheritable. Override/revert pairs must be balanced or subjective credentials leak across operations. `CONFIG_MULTIUSER=n` stubs allow all group checks.

## Test Signals

Signals include credentials selftests, setuid/setgid/exec transitions, namespace capability tests, RCU credential lifetime tests, override/revert scoped cleanup tests, supplementary group sorting/search tests, keyring credential propagation, and LSM hook coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cred.h -->
