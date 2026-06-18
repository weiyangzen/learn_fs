# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vid-common.h

Purpose: shared declaration header for Vivid video helpers used by both capture and output. It declares the single-planar conversion callback type `fmtfunc`, `fmt_sp2mp`, `fmt_sp2mp_func`, the DV timing capability object, format lookup, loopback connection helpers, source-change helpers, selection adjustment, format enumeration, common standard/timing/EDID getters, and event subscription.

No control flow or persistent state lives here, but the header defines the API boundary between Vivid ioctl tables and common implementation. It depends on V4L2/vb2/media types supplied through includers and on `struct vivid_dev`/`struct vivid_fmt` definitions from vivid core. Integration points are capture/output format handlers, CEC/EDID paths, and V4L2 event subscription.

Risks are mainly prototype drift, especially `fmtfunc` signatures and helpers shared by single-planar and multiplanar paths. Test signals are build coverage and v4l2-compliance paths that exercise both RX and TX standard/timing/EDID common handlers.
