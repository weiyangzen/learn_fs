# sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_chp.c

Purpose: exposes vfio-ccw channel-path related status regions for SCHIB state and queued channel report words.

Important APIs/types/functions: `vfio_ccw_register_schib_dev_regions()` registers read-only subtype `VFIO_REGION_SUBTYPE_CCW_SCHIB`; `vfio_ccw_register_crw_dev_regions()` registers read-only subtype `VFIO_REGION_SUBTYPE_CCW_CRW`. Region ops include SCHIB read and CRW read; writes always return `-EINVAL`.

Control flow: SCHIB reads validate bounds, lock `io_mutex`, refresh the subchannel with `cio_update_schib()`, copy SCHIB into the region, and copy to userspace. CRW reads pop the first queued `struct vfio_ccw_crw` if present, lock `io_mutex`, copy its value into the region, copy to userspace, clear the region field, free the popped CRW, and signal the eventfd again if more CRWs remain.

State and persistence behavior: SCHIB state is live hardware/subchannel state copied on demand. CRW state is an in-memory queue `private->crw` plus optional trigger eventfd; each read consumes one queued CRW.

Dependencies and integration points: depends on vfio-ccw private data, CIO `cio_update_schib()`, subchannel parent linkage, Linux list handling, eventfd signaling, and vfio region registration.

Risks and test signals: CRW list manipulation happens before `io_mutex`, so the queue needs external serialization from vfio-ccw core. SCHIB read can fail with `-ENODEV` if the subchannel is gone. Tests should cover partial reads, out-of-bounds reads, SCHIB refresh failure, CRW empty read clearing zero, queued CRW consumption order, eventfd retrigger with remaining entries, and write rejection.
