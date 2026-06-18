# sources/distributed-fs/ceph-client/tools/hv/hv_vss_daemon.c

## Purpose

`hv_vss_daemon.c` implements the Hyper-V host-initiated guest snapshot service. It registers with `/dev/vmbus/hv_vss`, receives freeze/thaw/check messages from the kernel, and freezes or thaws mounted guest filesystems so the host can take a consistent backup checkpoint.

## Important APIs, Types, and Functions

The daemon uses `struct hv_vss_msg`, `VSS_OP_REGISTER1`, `VSS_OP_FREEZE`, `VSS_OP_THAW`, `VSS_OP_HOT_BACKUP`, and Hyper-V error codes from `<linux/hyperv.h>`. `vss_do_freeze` opens a mount point and issues `FIFREEZE` or `FITHAW`; it treats `EBUSY` on freeze and `EINVAL` on thaw as success for duplicate mounts of the same backing device. `is_dev_loop` walks `/sys/dev/block/<major>:<minor>` and its `slaves` recursively to skip loop-backed devices. `vss_operate` scans `/proc/mounts`, filters unsuitable mounts, freezes non-root mounts first, freezes root last, and rolls back on failure.

## Control Flow and State

Startup parses foreground/help options, optionally daemonizes, opens syslog, opens `/dev/vmbus/hv_vss`, and registers. The first read during handshake is a kernel module version, then the main loop blocks in `poll`, reads a full `hv_vss_msg`, performs the requested operation, stores `error`, and writes the response. `fs_frozen` is the only process state. On device reopen, the daemon thaws if `fs_frozen` is true before re-registering, preventing a stale frozen guest after hibernation or channel reset.

## Dependencies and Integration Points

It depends on the Hyper-V VSS kernel device, Linux freeze/thaw ioctls, `/proc/mounts`, `/sys/dev/block`, device major/minor mapping, syslog, and root privileges. It integrates with host backup/checkpoint orchestration and with filesystem drivers that support `FIFREEZE`/`FITHAW`.

## Risks and Test Signals

Freezing filesystems is high impact. The code intentionally avoids syslog inside `vss_do_freeze` because logging may write to frozen storage. The root-last ordering and rollback path are critical; bugs can leave filesystems frozen. Filtering skips read-only, `vfat`, loop-backed, and non-`/dev/` mounts, so coverage depends on mount topology. Tests should simulate `/proc/mounts` patterns where possible, run freeze/thaw on disposable filesystems, validate duplicate-mount handling, check loop-device skipping, and verify that failed freeze attempts thaw previous mounts and report `HV_E_FAIL`.
