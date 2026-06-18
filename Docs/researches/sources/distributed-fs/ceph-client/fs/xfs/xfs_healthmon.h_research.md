# sources/distributed-fs/ceph-client/fs/xfs/xfs_healthmon.h

## Purpose
`xfs_healthmon.h` defines the in-kernel state, event taxonomy, event payload layout, and reporting entry points for XFS live health monitoring. The complete 184-line header was read.

## Important APIs, Types, and Functions
`struct xfs_healthmon` is the monitor object attached weakly to an XFS mount. It contains the mount cookie, device number, reference count, event queue lock, first/last event pointers, preallocated unmount event, queue counters, verbose flag, wait queue, read formatting buffer, and total/lost counters.

`enum xfs_healthmon_type` names event types such as `RUNNING`, `LOST`, `UNMOUNT`, `SHUTDOWN`, `SICK`, `CORRUPT`, `HEALTHY`, `MEDIA_ERROR`, buffered/direct I/O errors, and data loss. `enum xfs_healthmon_domain` scopes events to mount, filesystem, allocation group, inode, realtime group, data/realtime/log devices, or file ranges. `struct xfs_healthmon_event` is a tagged union containing payloads for lost counts, metadata masks, group ids, inode id/generation, shutdown flags, media sector ranges, and file error ranges.

## Control Flow
The header declares report functions that filesystem subsystems call at event points. Consumers do not format userspace ABI structures directly; they pass native XFS event fields into `xfs_healthmon_report_*`, while `xfs_ioc_health_monitor` creates the file descriptor and `xfs_healthmon_unmount` detaches and notifies readers.

## State and Persistence Behavior
The structures are entirely incore. The queue and buffer fields define how reports survive until userspace reads them, while `total_events`, `total_lost`, and `lost_prev_event` keep accounting across event drops. The `mount_cookie` is intentionally a weak reference to prevent the monitor fd from pinning the filesystem.

## Dependencies and Integration Points
The header depends on XFS mount, inode, group, device, and health flag types plus the userspace ioctl structures in XFS headers. It is included by the health monitor implementation and by XFS subsystems that emit health, media, shutdown, or file I/O error events.

## Risks and Edge Cases
The event union relies on correct pairing of type and domain with payload fields. New event types or domains require synchronized updates to the enum, formatting maps, merge logic, tracepoints, and userspace ABI translation. The header documents that `mount_cookie` must not be dereferenced casually; violating that contract risks UAF after unmount.

## Test Signals
Compile-time coverage should catch missing prototypes and enum map updates. Runtime tests should verify all declared report APIs generate the expected domain/type/payload combinations and that ABI formatting remains stable when new enum values are added.
