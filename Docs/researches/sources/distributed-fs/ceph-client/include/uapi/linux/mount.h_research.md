# sources/distributed-fs/ceph-client/include/uapi/linux/mount.h

## Purpose
Defines the Linux mount syscall UAPI: classic `mount(2)` flags, new mount API flags, fsconfig commands, mount attributes, and `statmount(2)`/`listmount(2)` query structures and masks.

## Important APIs, Types, And Functions
Key exports include `MS_*`, `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSOPEN_CLOEXEC`, `FSPICK_*`, `fsconfig_command`, `FSMOUNT_*`, `MOUNT_ATTR_*`, `mount_attr`, `statmount`, `mnt_id_req`, `STATMOUNT_*`, `LSMT_ROOT`, `LISTMOUNT_REVERSE`, and `STATMOUNT_BY_FD`.

## Control Flow
Classic mount calls use `MS_*` flags. New API flow creates/picks trees, configures filesystems with `fsconfig_command`, mounts/moves them, and changes attributes with `mount_setattr`. Query syscalls accept `mnt_id_req` and fill `statmount`, including variable strings after `str[]`.

## State, Persistence, And Dependencies
State persists in VFS mount namespace, superblock, propagation, and mount attributes. Depends on `linux/types.h` and externally on `O_CLOEXEC` availability.

## Integration Points
Used by mount utilities, container runtimes, namespace tools, systemd, and filesystem management libraries.

## Risks
Many flags are kernel-internal despite UAPI exposure. Struct version sizes must be honored. `statmount` string offsets and buffer sizing can return `EOVERFLOW`. Propagation and idmapped mount attributes have security implications.

## Test Signals
Validate classic remount masks, new API flag masks, fsconfig command handling, mount attribute set/clear behavior, `statmount` mask/string offsets, `listmount` ordering, versioned struct sizes, and fd-based queries.
