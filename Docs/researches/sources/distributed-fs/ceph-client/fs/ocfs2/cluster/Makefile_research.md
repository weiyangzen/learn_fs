# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/Makefile

## Purpose
This Makefile builds the OCFS2 cluster/nodemanager support object when `CONFIG_OCFS2_FS` is enabled.

## Important APIs, types, and functions
It emits `ocfs2_nodemanager.o` from `heartbeat.o`, `masklog.o`, `sys.o`, `nodemanager.o`, `quorum.o`, `tcp.o`, and `netdebug.o`.

## Control flow
Kbuild includes the aggregate object under `obj-$(CONFIG_OCFS2_FS)`, so the cluster stack is compiled into the OCFS2 module/build only when the filesystem is selected.

## State and persistence behavior
The file has no runtime state. Its object list controls which cluster subsystems exist at runtime, including configfs, sysfs log masks, heartbeat, quorum, TCP messaging, and debugfs.

## Dependencies and integration points
It integrates the cluster directory with Linux Kbuild and the OCFS2 filesystem Kconfig option. The aggregate object order matters for linked symbols but module init remains driven by `nodemanager.c`.

## Risks and test signals
Risks are missing objects causing unresolved symbols or disabled diagnostics. Test signals include `CONFIG_OCFS2_FS=y/m` builds, `CONFIG_DEBUG_FS` builds for `netdebug.o`, and link verification for heartbeat/quorum/tcp cross-calls.
