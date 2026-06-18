# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-cred.c

Read completely: 151 lines.

This is the Linux SPL credential compatibility layer. It maps Solaris/OpenZFS credential helpers onto Linux `cred`, `group_info`, kuid/kgid, and idmap/user-namespace primitives.

Key responsibilities:
- Reference count credentials with `crhold()` and `crfree()`.
- Return effective uid, real uid, effective gid, supplemental group count, and supplemental group array.
- Check supplemental group membership with a binary search over Linux group info.
- Return the initial idmap abstraction as either `nop_mnt_idmap` or `init_user_ns`, depending on kernel API availability.

Important implementation details:
- `cr_groups_search()` compares converted scalar gids and assumes the Linux group list ordering used by `GROUP_AT()`.
- `crgetgroups()` returns a direct pointer into `group_info`; callers must hold a credential reference for safe use.
- UID/GID accessors use conversion macros (`KUID_TO_SUID`, `KGID_TO_SGID`, `SGID_TO_KGID`) to handle Linux namespace-aware types.

Dependencies and interactions:
- Provides exported symbols consumed by ZFS permission, ACL, and vnode/znode paths.
- The idmap helper abstracts kernel changes around inode `create` idmap support.

Reliability notes:
- The functions are thin wrappers and assume non-null, valid `cred_t` inputs.
- Group membership correctness depends on the group array being sorted as expected by Linux credentials.
