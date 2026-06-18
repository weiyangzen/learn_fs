# sources/distributed-fs/ceph-client/fs/xfs/xfs_health.c

## Purpose
`xfs_health.c` tracks runtime health state for filesystem-wide, per-group, per-rtgroup, and per-inode metadata. It records sick/corrupt/healthy transitions, reports errors to fsnotify/fserror and health monitors, maps internal sick masks to ioctl-visible masks, and warns at unmount about unfixed corruption.

## Important APIs, types, and functions
Public functions mark and measure fs, AG, rtgroup, group, inode, bmap, btree, dir/attr, and da-state sickness; fill health fields in geometry and bulkstat outputs; and translate masks for health monitor events. Internal tables map `XFS_SICK_*` bits to `XFS_FSOP_GEOM_*`, `XFS_AG_GEOM_*`, `XFS_RTGROUP_GEOM_*`, and `XFS_BS_SICK_*` ABI bits.

## Control flow
Mark-sick functions assert valid masks, take the relevant spinlock, OR sick bits, optionally set checked bits for corrupt/fsck-observed state, report metadata errors, and emit healthmon events with old and changed masks. Mark-healthy functions clear requested sick bits, clear secondary bits when no primary bits remain, set checked bits, and report healthy events. Measure functions sample sick/checked masks under locks. Unmount scans all perags and rtgroups plus fs-level masks, warns if unfixed corruption remains, and special-cases sick summary counters so repair guidance does not conflict with deliberate dirty-log recovery. Geometry/bulkstat helpers sample health state and translate internal masks to ioctl fields.

## State and persistence
Health state is in-memory in `mp->m_fs_sick/m_fs_checked`, `xg->xg_sick/xg_checked`, and `ip->i_sick/i_checked`. It does not directly persist as a standalone structure, but it reflects detected persistent metadata problems and influences unmount logging and user-visible health queries. Sick inodes are kept out of `I_DONTCACHE` so reports are not lost prematurely.

## Dependencies and integration points
It integrates with scrub and repair health updates, btree/dir/attr corruption detection, fserror/fsnotify reporting, health monitor event delivery, bulkstat and geometry ioctls, AG/rtgroup iterators, inode lifecycle, quota and realtime health masks, and tracepoints.

## Risks and test signals
Risks include lost health reports from inode reclaim, incorrect primary/secondary clearing, mismatched internal-to-ABI mask translation, reporting metadata inodes to file-level fserror incorrectly, health monitor event masks missing bits, and unmount behavior around sick counters. Test signals include marking sick/corrupt/healthy for fs/group/inode, scrub clearing health, btree sick marking for bmap and non-ephemeral btrees, dir/attr sick marking, bulkstat and geometry sick/checked outputs, rtgroup health reporting, unmount warning paths, shutdown suppression, and health monitor event verification.
