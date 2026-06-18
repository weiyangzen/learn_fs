# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-chmod.c

## Purpose
`pvfs2-chmod.c` implements an OrangeFS chmod-like admin utility. It parses an octal mode and one or more PVFS pathnames, resolves each path, looks up the target object without following the final symlink, and updates the target's `PVFS_ATTR_SYS_PERM` attribute.

## Important APIs, Types, And Functions
Important functions are `main`, `parse_args`, `pvfs2_chmod`, `usage`, and `check_perm`. The implementation uses `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PINT_remove_base_dir`, `PINT_lookup_parent`, `PVFS_sys_lookup`, `PVFS_sys_ref_lookup`, `PVFS_sys_getattr`, `PVFS_sys_setattr`, `PVFS_sys_finalize`, and `PVFS_util_translate`-compatible permission bit constants through `PVFS_permissions`.

## Control Flow
`parse_args` accepts `-v`, requires a three- or four-digit octal mode, validates each digit through `check_perm`, packs special/user/group/other bits into `PVFS_permissions`, and copies target strings. `main` initializes default PVFS state and iterates targets until one fails. `pvfs2_chmod` resolves a user path to filesystem ID and PVFS-relative path, generates credentials, finds the parent and basename (special-casing `/`), looks up the target without following the final link, fetches settable attributes, copies old attributes, changes `perms`, sets the mask to `PVFS_ATTR_SYS_PERM`, and calls `PVFS_sys_setattr`.

## State And Persistence
The persistent effect is modification of object permission metadata on OrangeFS. Runtime state consists of parsed options, path buffers, credentials, lookup/getattr responses, and old/new attribute structs. Target strings are allocated and not freed before process exit.

## Dependencies And Integration Points
It depends on the PVFS sysint, `str-utils`, and `pint-sysint-utils` parent/path helpers. It is integrated as an admin command and follows the same path-resolution pattern as `pvfs2-chown`.

## Risks And Test Signals
Risks include lack of symbolic chmod syntax, no recursive support, fixed `PVFS_NAME_MAX` buffers, root-path basename handling where `str_buf` remains empty, memory leaks, and stopping at the first failed target. Tests should cover mode parsing for UGO and SUGO forms, invalid digits, regular files/directories/symlinks, root handling, multiple targets, permission-denied failures, and verification with `pvfs2-stat`.
