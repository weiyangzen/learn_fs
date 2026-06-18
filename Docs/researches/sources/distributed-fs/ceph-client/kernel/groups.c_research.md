# sources/distributed-fs/ceph-client/kernel/groups.c

## Purpose
`groups.c` implements supplementary group ID storage and system call support. It allocates/refcounts `struct group_info`, copies group IDs between userspace and kernel credentials with namespace mapping, sorts and searches group arrays, and applies group changes through the credential and LSM frameworks.

## Important APIs, types, and functions
Exported helpers include `groups_alloc()`, `groups_free()`, `groups_sort()`, `groups_search()`, `set_groups()`, `set_current_groups()`, `in_group_p()`, and `in_egroup_p()`. Syscalls are `getgroups` and `setgroups`. Internal helpers include `groups_to_user()`, `groups_from_user()`, `gid_cmp()`, and `may_setgroups()`.

## Control flow
`setgroups()` checks namespace capability and `NGROUPS_MAX`, allocates a flexible `group_info`, copies and validates user GIDs as `kgid_t` values in the current user namespace, sorts them, then installs them through `set_current_groups()`. `set_current_groups()` prepares copy-on-write credentials, replaces the group pointer with proper refcounting, runs `security_task_fix_setgroups()`, and commits or aborts. `getgroups()` reports the current group count or copies mapped GIDs to userspace. Membership checks compare fsgid/egid first and fall back to binary search.

## State and persistence
Group membership is runtime credential state attached to `struct cred`; updates use copy-on-write credential replacement, not in-place mutation. `group_info` is refcounted elsewhere and freed with `kvfree()`. User namespace mapping affects the userspace representation, but group arrays store kernel IDs. There is no disk persistence.

## Dependencies and integration points
This file integrates with credentials, user namespaces, LSM hooks, syscall argument copying, kernel sorting, capability checks, and exported group helpers used by permission checks across filesystems and kernel subsystems. It relies on callers maintaining sorted supplementary groups for `groups_search()`.

## Risks and test signals
Risks include invalid namespace ID translation, unsorted group arrays causing false negatives, refcount leaks on credential errors, capability semantics around `userns_may_setgroups()`, and large allocations near `NGROUPS_MAX`. Test signals include `getgroups` size-probe behavior, `setgroups` permission denial in user namespaces, invalid GID rejection, sorted membership checks, LSM denial path cleanup, and fsgid/egid fast-path membership.
