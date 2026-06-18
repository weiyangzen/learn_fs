# sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.c

## Purpose
`xfs_healthmon.c` implements the live XFS health monitor anonymous file descriptor returned by `XFS_IOC_HEALTH_MONITOR`. It lets privileged userspace, specifically a filesystem healer/monitor daemon, subscribe to kernel events about filesystem health state, shutdown reasons, media errors, file range I/O failures, lost events, and unmount. The full 1260-line file was read.

## Important APIs, Types, and Functions
The mount-facing API consists of `xfs_ioc_health_monitor`, `xfs_healthmon_unmount`, `xfs_healthmon_report_fs`, `xfs_healthmon_report_group`, `xfs_healthmon_report_inode`, `xfs_healthmon_report_shutdown`, `xfs_healthmon_report_media`, and `xfs_healthmon_report_file_ioerror`. Object lifetime is handled by `xfs_healthmon_get`, `xfs_healthmon_put`, `xfs_healthmon_attach`, and `xfs_healthmon_detach`.

Queue handling is centered on `xfs_healthmon_push`, `xfs_healthmon_merge_events`, `xfs_healthmon_clear_lost_prev`, `__xfs_healthmon_insert`, and `__xfs_healthmon_push`. Userspace delivery is handled by `xfs_healthmon_read_iter`, `xfs_healthmon_poll`, `xfs_healthmon_format_v0`, `xfs_healthmon_copybuf`, `xfs_healthmon_format_pop`, and `xfs_healthmon_alloc_outbuf`. Reconfiguration and validation use `xfs_healthmon_validate`, `xfs_healthmon_reconfigure`, `xfs_healthmon_file_on_monitored_fs`, and `xfs_healthmon_ioctl`.

## Control Flow
`xfs_ioc_health_monitor` validates CAP_SYS_ADMIN, root-inode use, initial user namespace, format, flags, and zero padding. It allocates `struct xfs_healthmon`, queues an initial `RUNNING` event, preallocates an `UNMOUNT` event so unmount notification cannot fail later, attaches the monitor to `mp->m_healthmon`, and finally installs an anon inode fd.

Report functions take a ref to the monitor through RCU, build a stack event, optionally filter metadata masks via `metadata_event_mask`, and queue it. Queueing first emits any prior lost-event count, tries to merge with the last queued event, enforces `XFS_HEALTHMON_MAX_EVENTS`, and accounts dropped events through `lost_prev_event` and `total_lost`.

Reads wait for queued events, detached EOF, or buffered bytes. The read path serializes formatting with the anonymous inode lock, drains any prior output buffer bytes, pops queued events under `hm->lock`, converts them to `struct xfs_health_monitor_event` v0 records, copies to the caller iterator, and resets buffer cursors when empty. Poll reports `EPOLLIN` when event data or detach state is visible.

## State and Persistence Behavior
All health monitor state is memory resident. The weak mount association is represented by `mount_cookie`, which stores `mp->m_super` while attached and zero after detach; the code explicitly says not to dereference it except while synchronized with detach logic. `mp->m_healthmon` is RCU protected and pointer updates are serialized by `xfs_healthmon_lock`. The open fd, the mount attachment, and running event handlers hold references.

Events are heap objects on a singly linked queue with total and lost counters. `hm->buffer`, `bufhead`, and `buftail` persist partially formatted read data across short reads. No filesystem metadata is written by this file, though it exposes persistent-health observations and shutdown/media fault signals to userspace.

## Dependencies and Integration Points
The file integrates with XFS health flag translation (`xfs_healthmon_fs_mask`, per-AG, rtgroup, inode masks), mount state (`mp->m_healthmon`), anon inode fd creation, VFS file operations, poll/eventpoll, Linux `fserror` events, shutdown flag definitions, media device selection, tracepoints, and ioctls from `xfs_fs.h`/`xfs_ioctl.h`. It is a consumer of health reports from scrub/repair/metadata checking, buffer and direct I/O error notification, media failure reporting, and unmount.

## Risks and Edge Cases
Lifetime correctness is central: the monitor can outlive the mount, event reporters race with detach, and unmount must still wake readers. Queue capacity and allocation failure intentionally lose events but must preserve a later `LOST` count. Event merging must not combine unrelated inode generations, group numbers, file ranges, or devices. The read path must not return stale buffered data incorrectly after detach, and short userspace buffers require stable buffer cursor handling. The ioctl surface is deliberately privileged and format-versioned; accepting bad padding or unsupported flags would weaken ABI validation.

## Test Signals
Useful tests include creating a monitor only as init-namespace CAP_SYS_ADMIN on the root inode, double-monitor attach returning `-EEXIST`, first read returning `RUNNING`, poll wakeups after health events, verbose versus non-verbose health mask filtering, merged adjacent media and file-range errors, queue overflow producing a later lost-event record, short-buffer reads over multiple calls, fdinfo state/counters, `XFS_IOC_HEALTH_FD_ON_MONITORED_FS` success and `-ESTALE`, unmount injecting the preallocated event and later EOF, and racing fd close with unmount.
