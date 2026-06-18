# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.h

## Summary
Defines NILFS2 sysfs constants, subgroup kobject storage, and macro helpers for typed sysfs attributes.

## Main Contents
- `NILFS_ROOT_GROUP_NAME` set to `nilfs2`.
- `struct nilfs_sysfs_dev_subgroups` containing kobjects and unregister completions for per-device subgroups.
- Attribute wrapper struct macros for global feature attrs, device attrs, internal subgroup attrs, and checkpoint/snapshot attrs.
- Attribute construction macros for info, read-only, and read-write sysfs files.
- Attribute-list helper macros for group arrays.

## Important Details
The macros encode the expected callback signatures:
- Feature attrs receive `struct kobject *`.
- Device/subgroup attrs receive `struct the_nilfs *`.
- Snapshot attrs receive `struct nilfs_root *`.

This keeps `sysfs.c` concise while still allowing type-specific show/store functions.

## Risks
The macro layer hides callback type differences. New attributes must use the matching macro family or callbacks will have incompatible signatures.
