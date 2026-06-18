# sources/distributed-fs/ceph-client/security/tomoyo/file.c

## Purpose

`file.c` implements TOMOYO file-related ACL parsing and enforcement for path operations, two-path operations, path-plus-number operations, device node creation, and mount ACL storage. It translates Linux VFS hook inputs into TOMOYO policy tokens and request parameters, checks matching ACLs, and audits through the common supervisor path.

## Important APIs, types, and functions

Exported enforcement functions include `tomoyo_execute_permission()`, `tomoyo_check_open_permission()`, `tomoyo_path_perm()`, `tomoyo_path_number_perm()`, `tomoyo_mkdev_perm()`, and `tomoyo_path2_perm()`. `tomoyo_write_file()` parses file policy lines and dispatches to ACL update helpers. Shared operand helpers include `tomoyo_put_name_union()`, `tomoyo_compare_name_union()`, `tomoyo_put_number_union()`, and `tomoyo_compare_number_union()`.

The file defines operation-to-MAC mapping arrays: internal `tomoyo_p2mac` plus exported `tomoyo_pnnn2mac`, `tomoyo_pp2mac`, and `tomoyo_pn2mac`. Internal checkers include `tomoyo_check_path_acl()`, `tomoyo_check_path_number_acl()`, `tomoyo_check_path2_acl()`, and `tomoyo_check_mkdev_acl()`. Update helpers parse name/number unions, detect duplicates, and merge permission bitmasks for ACLs with the same operands.

## Control flow

For enforcement, each public checker initializes `tomoyo_request_info`, acquires `tomoyo_read_lock()`, resolves one or two paths with `tomoyo_realpath_from_path()`, normalizes directory names with trailing slash where TOMOYO policy expects directories, fills `tomoyo_obj_info` for condition evaluation, sets the appropriate `param_type`, calls `tomoyo_check_acl()`, and audits through a type-specific audit helper. Non-enforcing modes generally force the final return to success after logging/learning.

`tomoyo_execute_permission()` is special: it checks execute ACLs even when the execute profile mode is disabled so that a matched `file execute` condition can still provide a domain transition preference. Write parsing first tries single-path operation names, then two-path MAC names, path-number MAC names, mkdev MAC names, and finally mount.

## State and persistence behavior

File ACLs persist in domain ACL lists or namespace ACL groups as `tomoyo_path_acl`, `tomoyo_path2_acl`, `tomoyo_path_number_acl`, `tomoyo_mkdev_acl`, and `tomoyo_mount_acl` objects. These entries hold references to interned names, groups, and number unions. Enforcement allocates temporary encoded realpath strings and frees them before returning; matched execute ACL state is stored in the request so `domain.c` can reuse wildcard policy names for transition construction.

## Dependencies and integration points

This file depends on realpath encoding, TOMOYO pattern matching, name/number/group parsing from `util.c`/`group.c`, domain ACL update and scanning from `domain.c`, condition evaluation, and common audit/profile mode handling. LSM hook wrappers in `tomoyo.c` call these functions for open, getattr, truncate, unlink, mkdir, mknod, symlink, rename, link, chmod/chown/chgrp, ioctl-like number checks, chroot, unmount, and pivot root paths. Mount enforcement runtime is implemented in `mount.c`, while mount ACL parsing/storage is here.

## Risks

Path canonicalization and trailing slash rules are critical because policy matching is string based. Directory operations that forget `tomoyo_add_slash()` can miss intended directory ACLs. Permission-bit merging must be atomic enough for lockless readers; this file uses `READ_ONCE()`/`WRITE_ONCE()` while updates hold the policy mutex. Execute checks affect domain transitions beyond simple allow/deny. Non-enforcing modes returning success after errors can hide policy/parser issues unless audit signals are inspected.

## Test signals

Tests should cover every file operation token, slash normalization for directories, open read/write/append combinations, symlink target conditions, mknod major/minor/mode checks, chmod/chown/chgrp/ioctl radix rendering, rename/link/pivot-root directory handling, duplicate ACL merge/delete behavior, path groups and number groups, wildcard execute transition matching, and enforcement-mode return differences.
