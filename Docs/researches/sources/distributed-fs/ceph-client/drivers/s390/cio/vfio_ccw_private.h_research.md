## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_private.h

Purpose: central private header for vfio-ccw. It defines device private state, dynamic region plumbing, parent mdev structures, FSM states/events, debug macros, and cross-file globals.

Important APIs/types/functions: `struct vfio_ccw_private` embeds `struct vfio_device`, FSM state, synchronization objects, user-visible regions, dynamic region array, active `channel_program`, IRB/SCSW snapshots, CRW list, eventfd triggers, and work items. It also defines `struct vfio_ccw_region`, `struct vfio_ccw_regops`, `struct vfio_ccw_parent`, `struct vfio_ccw_crw`, state/event enums, `vfio_ccw_fsm_event()`, and registration prototypes for extra regions.

Control flow: the inline `vfio_ccw_fsm_event()` traces state/event against the parent subchannel id and dispatches through `vfio_ccw_jumptable`. Dynamic region offsets are partitioned by a 10-bit offset shift/mask so VFIO region index and intra-region offset can share a file position.

State and persistence: this header documents all durable per-device state boundaries. The active CP, region buffers, eventfds, and work structs live for the mdev lifetime; some additional regions are registered only during open. CRW list entries persist until consumed or device release.

Dependencies and integration: includes VFIO, mdev, eventfd, workqueue, s390 CRW/debug, css, and channel-program APIs. It is consumed by driver, ops, FSM, and region support files.

Risks and test signals: risks are ABI drift in region layout, state table mismatches, alignment assumptions on `vfio_ccw_private`, and missing release callbacks for extra regions. Test compile-time coverage across all users, state/event table completeness, open/close allocation lifecycle, and debug trace visibility.
