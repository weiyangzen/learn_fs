# sources/distributed-fs/ceph-client/fs/quota/Kconfig

## Purpose
This Kconfig file defines Linux quota subsystem options, quota control support, legacy and v2 on-disk quota formats, netlink notifications, and debug checks.

## Important APIs, types, and functions
It defines `QUOTA`, `QUOTA_NETLINK_INTERFACE`, `PRINT_QUOTA_WARNING`, `QUOTA_DEBUG`, `QUOTA_TREE`, `QFMT_V1`, `QFMT_V2`, and `QUOTACTL`.

## Control flow
Enabling `QUOTA` selects `QUOTACTL`; selecting v2 quota format selects `QUOTA_TREE`; netlink warnings depend on `QUOTACTL && NET`; obsolete console warnings are gated behind `BROKEN`.

## State and persistence
The file controls compiled quota capability and supported on-disk quota formats. Runtime quota state is implemented in the quota source files built by the Makefile.

## Dependencies and integration points
It integrates VFS quota operations, supported filesystems, netlink warning delivery, and quota userspace ABI support.

## Risks and test signals
Risks include missing support for needed quota formats, unexpected omission of netlink warning support, and confusion with filesystems that use independent quota systems. Test signals include builds with quota disabled, v1 only, v2 with quota tree, netlink enabled/disabled, and quota debug.
