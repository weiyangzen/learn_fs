# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/policy.c

## Purpose

Maps illumos/ZFS security policy checks to Linux credentials, capabilities, user namespaces, UID/GID mappings, and VFS behavior. Many checks are no-ops because Linux VFS already enforces the corresponding rule.

## Core Helpers

- `priv_policy_ns(cr, capability, err, ns)`: checks a Linux capability, temporarily overriding current credentials when the supplied credentials differ from current and `kcred`.
- `priv_policy(cr, capability, err)`: capability check in `cr->user_ns`.
- `priv_policy_user(cr, capability, err)`: user-namespace-aware capability check intended after UID/GID mapping validation.

## Implemented Policy Checks

- `secpolicy_nfs()`: `CAP_SYS_ADMIN`.
- `secpolicy_sys_config()`: `CAP_SYS_ADMIN`.
- `secpolicy_vnode_any_access()`: owner, inode-owner/capable, UID mapping, `CAP_DAC_OVERRIDE`, or `CAP_DAC_READ_SEARCH`.
- `secpolicy_vnode_chown()`: owner or `CAP_FOWNER`, with UID mapping check.
- `secpolicy_vnode_create_gid()`: `CAP_SETGID`.
- `secpolicy_vnode_remove()`: `CAP_FOWNER`.
- `secpolicy_vnode_setdac()`: owner or `CAP_FOWNER`, with UID mapping check.
- `secpolicy_vnode_setid_retain()`: `CAP_FSETID`.
- `secpolicy_vnode_setids_setgids()`: translated GID ownership/group membership or `CAP_FSETID`.
- `secpolicy_zinject()`: `CAP_SYS_ADMIN`, returning `EACCES` on denial.
- `secpolicy_zfs()`: `CAP_SYS_ADMIN`, returning `EACCES` on denial.
- `secpolicy_setid_clear()`: clears setuid/setgid bits when caller lacks retain privilege.
- `secpolicy_setid_setsticky_clear()`: validates setuid and setgid changes and clears sticky/setgid bits as needed.
- `secpolicy_xvattr()`: delegates to chown policy.

## Linux-VFS-Enforced No-Ops

These return success because Linux VFS handles them elsewhere:

- `secpolicy_vnode_access2()`
- `secpolicy_vnode_setattr()`
- `secpolicy_basic_link()`
- Sticky-bit modification helper returns success.

## Notes

The file is heavily user-namespace aware. It avoids namespace capability checks when UID/GID mapping cannot be established.
