# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_debugfs.h

## Purpose

`drbd_debugfs.h` declares the DRBD debugfs lifecycle hooks and provides no-op inline stubs when debugfs is disabled. It lets the rest of the DRBD driver call debugfs integration points unconditionally without scattering `#ifdef CONFIG_DEBUG_FS` through core code.

## Important APIs

With `CONFIG_DEBUG_FS` enabled, the header declares:

- `drbd_debugfs_init()` and `drbd_debugfs_cleanup()`.
- `drbd_debugfs_resource_add()` / `drbd_debugfs_resource_cleanup()`.
- `drbd_debugfs_connection_add()` / `drbd_debugfs_connection_cleanup()`.
- `drbd_debugfs_device_add()` / `drbd_debugfs_device_cleanup()`.
- `drbd_debugfs_peer_device_add()` / `drbd_debugfs_peer_device_cleanup()`.

With debugfs disabled, it defines static inline no-op versions of the same functions.

## Control Flow

There is no independent runtime control flow in the header. It determines whether calls from DRBD initialization and object lifecycle code link to real debugfs implementation in `drbd_debugfs.c` or compile away to no-ops.

## State and Persistence Behavior

The header owns no state. In debugfs builds, state is maintained by `drbd_debugfs.c` and the dentry pointers embedded in DRBD objects. In non-debugfs builds, no debugfs state exists.

## Dependencies and Integration Points

- Includes kernel, module, and debugfs headers, plus `drbd_int.h` for DRBD object types.
- Must match the function definitions in `drbd_debugfs.c`.
- Integrated by DRBD resource, connection, device, and peer-device lifecycle paths.

## Risks and Edge Cases

- Prototype drift between this header and `drbd_debugfs.c` breaks debugfs builds or silently changes no-op behavior.
- The no-op stubs must preserve attributes such as `__init` where relevant so call sites compile in all configurations.
- Including `drbd_int.h` can increase dependency coupling; changes in core type declarations may affect debugfs consumers.

## Test Signals

- Compile DRBD with `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`.
- Verify core DRBD code can call every debugfs lifecycle hook without local preprocessor guards.
- Check that module init/cleanup and object add/remove paths have no unresolved debugfs symbols in non-debugfs builds.
