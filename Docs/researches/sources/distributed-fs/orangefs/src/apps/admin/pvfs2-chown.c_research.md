# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chown.c

## Purpose
`pvfs2-chown.c` implements an OrangeFS ownership-changing utility. It accepts a local user name, group name, and one or more target paths, resolves each target in OrangeFS, and updates `PVFS_ATTR_SYS_UID` and `PVFS_ATTR_SYS_GID`.

## Important APIs, Types, And Functions
Important functions are `main`, `parse_args`, `pvfs2_chown`, `usage`, `check_owner`, and `check_group`. The code uses POSIX account lookup (`getpwnam`, `getgrnam`) and PVFS APIs/helpers: `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PVFS_sys_lookup`, `PINT_remove_base_dir`, `PINT_lookup_parent`, `PVFS_sys_ref_lookup`, `PVFS_sys_getattr`, and `PVFS_sys_setattr`.

## Control Flow
`parse_args` handles `-v`, requires at least user, group, and one filename, resolves user/group names to numeric IDs, and copies target filenames. `main` initializes PVFS defaults and calls `pvfs2_chown` for each target until an error. `pvfs2_chown` resolves the path, generates credentials, locates the parent and target entry, gets current settable attributes, copies them, updates owner/group and mask, and writes the attributes back.

## State And Persistence
The persistent behavior is metadata mutation on OrangeFS objects. Runtime state mirrors `pvfs2-chmod`: path buffers, credentials, lookup responses, and copied attributes. The parsed target and option allocations are not explicitly freed before exit.

## Dependencies And Integration Points
The utility bridges local POSIX account/group databases to OrangeFS UID/GID fields. It depends on PVFS sysint/path helper libraries and is built with the rest of admin tools.

## Risks And Test Signals
Risks include accepting only names, not numeric IDs; no support for preserving one side with `user:` or `:group`; fixed path buffers; root-path handling; and stopping after the first target failure. Tests should cover valid and invalid local users/groups, multiple target paths, symlink final-component behavior, permission failures, and post-change stat output.
