# sources/distributed-fs/ceph-client/security/tomoyo/mount.c

## Purpose

`mount.c` implements runtime enforcement for TOMOYO `file mount` permissions. It normalizes Linux mount syscall variants into TOMOYO device, mount point, filesystem type, and flag operands, then checks those operands against mount ACLs stored by `file.c`.

## Important APIs, types, and functions

`tomoyo_mount_permission()` is the exported enforcement entry point. Internal `tomoyo_mount_acl()` performs path/type/device normalization and ACL checking. `tomoyo_check_mount_acl()` matches a request against `struct tomoyo_mount_acl`, and `tomoyo_audit_mount_log()` formats supervisor/audit output. The static `tomoyo_mounts[]` table maps special mount operations to policy pseudo-filesystem strings such as `--bind`, `--move`, `--remount`, and propagation changes.

## Control flow

`tomoyo_mount_permission()` initializes a request for `TOMOYO_MAC_FILE_MOUNT`, strips legacy `MS_MGC_*`, converts remount/bind/move/shared/private/slave/unbindable flag combinations into TOMOYO pseudo-types, validates incompatible propagation flag combinations, defaults missing type to `<NULL>`, then calls `tomoyo_mount_acl()` under `tomoyo_read_lock()`.

`tomoyo_mount_acl()` encodes the filesystem type, resolves the mount point realpath, determines whether the device operand is ignored, a directory path, a block device path, or a raw encoded string, fills request operands and object paths, calls `tomoyo_check_acl()`, and audits through `tomoyo_supervisor()` until no retry is requested. It releases encoded strings, filesystem type references, and `kern_path()` references before returning.

## State and persistence behavior

This file stores no persistent policy besides the static special-operation string table. Runtime state is request-local: encoded device/type strings, resolved mount point strings, optional `struct file_system_type` reference, optional `struct path` for the device/source, and `tomoyo_obj_info` paths for condition checks.

## Dependencies and integration points

It depends on Linux mount flags, `get_fs_type()`/`put_filesystem()`, `kern_path()`, path reference management, TOMOYO realpath/encoding helpers, number/name union matchers, domain ACL scanning, and supervisor/audit logic. `tomoyo.c` calls `tomoyo_mount_permission()` from the mount LSM hook. Mount ACL parsing is handled in `file.c` through `tomoyo_update_mount_acl()`.

## Risks

Special mount flag normalization must track kernel mount API semantics. Incorrect `need_dev` classification can require a device when policy should ignore it or ignore a device/source path that policy expects to constrain. Device path lookup with `LOOKUP_FOLLOW` may differ from userspace textual input, so policy must be based on resolved TOMOYO realpaths. Error handling before policy mode checks returns lookup/type errors such as `-ENODEV` or `-ENOENT`; enforcement mode handling is delegated through the supervisor result rather than a final non-enforcing override in this file.

## Test signals

Tests should cover normal block-device mounts, pseudo filesystems with no device, bind and move mounts with directory sources, remount and propagation operations, incompatible propagation flags, missing type/device behavior, flag masking, mount ACL group/range matching, condition checks on path1/path2 attributes, and enforcing/permissive/learning responses.
