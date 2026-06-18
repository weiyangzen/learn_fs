<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/synclink.h -->
# sources/distributed-fs/ceph-client/include/linux/synclink.h

## Purpose

`synclink.h` is the kernel-side wrapper for SyncLink multiprotocol serial adapter ioctl definitions. It includes the UAPI header and adds 32-bit compatibility structures/ioctls on 64-bit kernels.

## Important APIs, types, and functions

When `CONFIG_COMPAT` is enabled, `struct MGSL_PARAMS32` mirrors UAPI `MGSL_PARAMS` with `compat_ulong_t` for fields whose size differs between 32-bit userspace and 64-bit kernel. `MGSL_IOCSPARAMS32` and `MGSL_IOCGPARAMS32` define compat ioctl numbers for setting and getting parameters.

## Control flow

Compat ioctl handlers can receive the 32-bit structure, translate it to the native structure, and call the normal SyncLink configuration path. Without compat, this header only re-exports UAPI definitions.

## State and persistence behavior

The header owns no state. Adapter state is changed by driver ioctl handling based on translated parameters.

## Dependencies and integration points

It depends on `uapi/linux/synclink.h` and, under compat, `linux/compat.h`. It integrates with SyncLink serial drivers and compat ioctl dispatch.

## Risks and test signals

Risks include structure layout drift versus UAPI, missing translation of widened fields, and ioctl number mismatch. Tests should validate 32-bit userspace ioctl set/get on 64-bit kernels, native ioctl compatibility, field round trips, and builds with `CONFIG_COMPAT` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/synclink.h -->
