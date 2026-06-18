# sources/distributed-fs/ceph-client/fs/qnx4/Kconfig

## Purpose
This Kconfig entry enables read-only QNX4 filesystem support.

## Important APIs, types, and functions
It defines `QNX4FS_FS` as a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`.

## Control flow
When selected, Kbuild can build the `qnx4` module or builtin driver; otherwise the QNX4 VFS code is excluded.

## State and persistence
It controls build-time availability only. Mounted filesystems are read-only and do not persist kernel-side modifications.

## Dependencies and integration points
It integrates with the block layer, buffer-head based reads, and filesystem module aliasing.

## Risks and test signals
Risks are limited to build selection and user expectations: the help text mentions QNX6/RTP even though QNX6 has a separate driver. Test signals are built-in and module builds with block support enabled.
