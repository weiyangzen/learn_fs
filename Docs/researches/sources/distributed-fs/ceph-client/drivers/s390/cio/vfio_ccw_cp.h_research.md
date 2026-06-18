## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_cp.h

Purpose: declares the channel-program translation interface used by vfio-ccw. It is the narrow contract between the finite-state-machine I/O path and the lower-level CCW/IDAL translation implementation.

Important APIs/types/functions: `CCWCHAIN_LEN_MAX` caps a single chain at 256 CCWs. `struct channel_program` contains the translated chain list, saved ORB, initialization state, and `guest_cp` scratch storage. Public functions are `cp_init()`, `cp_free()`, `cp_prefetch()`, `cp_get_orb()`, `cp_update_scsw()`, and `cp_iova_pinned()`.

Control flow: users allocate or embed a `channel_program`, allocate `guest_cp`, call `cp_init()` with the userspace ORB, call `cp_prefetch()` before issuing I/O, pass `cp_get_orb()` to `ssch`, update completion status with `cp_update_scsw()`, and finally release resources with `cp_free()`. `cp_iova_pinned()` is an asynchronous invalidation guard used outside the normal start/completion flow.

State and persistence: the header exposes that the object is stateful and single-operation oriented. `initialized` prevents double initialization and allows free/update/pinned checks to no-op on inactive programs. The list contents are intentionally opaque to callers.

Dependencies and integration: includes s390 `cio`, `scsw`, local `orb.h`, and trace support. It is included by private vfio-ccw driver state and by the channel-program implementation.

Risks and test signals: callers must respect the lifecycle or they can leak pins or attempt I/O with stale translated CCWs. Test signals are correct behavior for repeated init, free without init, invalidation checks on inactive programs, and completion CPA update after successful, halted, and cleared I/O.
