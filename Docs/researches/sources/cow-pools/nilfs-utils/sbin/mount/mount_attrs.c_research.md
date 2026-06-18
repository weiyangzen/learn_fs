# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount_attrs.c

## Scope

Implements NILFS-specific mount attribute parsing and updating for libmount-based helpers.

## APIs And Behavior

- `nilfs_mount_attrs_init()` clears all attributes and sets protection period to `ULONG_MAX` as "not specified".
- `nilfs_mount_attrs_parse()` scans an option string with `mnt_optstr_next_option()`, recognizes `pp=<seconds>`, `nogc`, `pid=<gcpid>` from mtab/utab context, and dummy `none`; it can return matched NILFS attributes separately from remaining non-NILFS options.
- Invalid option forms produce warnings and `-EINVAL`, such as `nogc=value`, `pp` without value, `pid` outside mtab parsing, or nonnumeric values.
- `nilfs_mount_attrs_update()` clears libmount FS attributes and appends `nogc`, or `pid=<gcpid>` plus optional `pp=<seconds>`, or dummy `none` to force attribute removal on remount.

## State And Dependencies

The file uses libmount option string APIs and cleaner `PIDOPT_NAME`, plus shared NILFS mount option names.

## Risks And Invariants

`pid` and `none` are only valid when parsing stored mount-table attributes, not command-line options. Attribute update intentionally uses a dummy `none` when removing old attributes on remount so libmount notices the deletion.
