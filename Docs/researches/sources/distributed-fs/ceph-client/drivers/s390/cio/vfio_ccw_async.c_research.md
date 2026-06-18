# sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_async.c

Purpose: registers the vfio-ccw asynchronous command region used by userspace to issue async requests to the vfio-ccw FSM.

Important APIs/types/functions: `vfio_ccw_register_async_dev_regions()` registers subtype `VFIO_REGION_SUBTYPE_CCW_ASYNC_CMD` with read/write flags and `vfio_ccw_async_region_ops`. Region callbacks read/write a `struct ccw_cmd_region` and trigger `VFIO_CCW_EVENT_ASYNC_REQ`.

Control flow: reads validate offset/count, lock `io_mutex`, copy the region to userspace, and unlock. Writes validate bounds, use `mutex_trylock()` to avoid blocking concurrent I/O, copy data from userspace, dispatch the async FSM event, and return either `region->ret_code` or the byte count.

State and persistence behavior: state is the registered region data, usually `private->cmd_region`, and the vfio-ccw private FSM state. It is runtime-only.

Dependencies and integration points: depends on vfio region registration, vfio-ccw private region tables, user copy helpers, and `vfio_ccw_fsm_event()`.

Risks and test signals: partial writes can trigger async requests with partially updated command regions if userspace writes slices intentionally. `mutex_trylock()` returns `-EAGAIN`, so userspace must retry. Tests should cover out-of-bounds access, EFAULT copy paths, concurrent write rejection, FSM event side effects, ret_code propagation, and readback consistency.
