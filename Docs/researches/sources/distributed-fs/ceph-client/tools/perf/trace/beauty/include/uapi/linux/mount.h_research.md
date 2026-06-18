# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/mount.h

## Purpose

`mount.h` defines Linux mount, mount-attribute, and mount-query UAPI constants and structs. Perf trace beauty uses it to decode legacy `mount(2)` flags, new file-descriptor-based mount API syscalls, `fsconfig` commands, `mount_setattr`, and newer `statmount`/`listmount` interfaces.

## Important APIs, Types, and Constants

Important definitions include legacy `MS_*` mount flags, propagation flags, atime flags, internal/reserved superblock flags, `MS_RMT_MASK`, `MS_MGC_VAL`, `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSOPEN_CLOEXEC`, `FSPICK_*`, `FSMOUNT_CLOEXEC`, `enum fsconfig_command`, `MOUNT_ATTR_*`, `struct mount_attr`, `struct statmount`, `struct mnt_id_req`, `STATMOUNT_*` mask bits, `LSMT_ROOT`, `LISTMOUNT_REVERSE`, and `STATMOUNT_BY_FD`.

## Control Flow and Integration

Legacy `mount(2)` consumes `MS_*`. New APIs split mount work across `open_tree`, `move_mount`, `fsopen`, `fspick`, `fsconfig`, and `fsmount`. `mount_setattr` uses `struct mount_attr` with set/clear masks, propagation, and optional idmap user namespace fd. `statmount` fills a size-versioned structure plus variable string buffer; `listmount` uses `mnt_id_req` to enumerate mount IDs. Perf must decode each flag namespace by syscall and argument.

## State and Persistence Behavior

Mount operations mutate VFS mount namespace state by creating, moving, cloning, remounting, or changing propagation and idmapped mount attributes. `statmount` and `listmount` query current state. The header itself stores no state.

## Dependencies and Integration Points

The header includes `linux/types.h` and uses the broader open/fcntl namespace for `O_CLOEXEC`. It integrates with VFS mount code, mount namespaces, idmapped mounts, filesystem context creation, statx-like mask handling, and proc mountinfo-compatible IDs.

## Risks

Some `MS_*` flags are internal but ABI-visible. `MS_VERBOSE` and `MS_SILENT` share a value. `MOUNT_ATTR__ATIME` is a mask, while relatime/noatime/strictatime are values inside that mask. `statmount` string fields are offsets into a variable buffer and require size-aware decoding. Version macros for `mount_attr` and `mnt_id_req` matter for compatibility.

## Test Signals

Decode legacy mount flags, `move_mount` from/to flags, `fsconfig` command values, `mount_setattr` attr/propgation/idmap fields, `statmount` masks, and special `LSMT_ROOT` listmount requests.
