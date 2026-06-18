# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec.h

This header provides the minimal public decoder interface for other Venus files. It forward declares `struct venus_inst` and exports decoder control initialization.

The only API is `int vdec_ctrl_init(struct venus_inst *inst)`, implemented in `vdec_ctrls.c` and called from `vdec_open()` before the instance is exposed through V4L2 file-handle setup.

Control flow is simple: decoder instance allocation calls `vdec_ctrl_init()`, which initializes the V4L2 control handler and stores decoder-specific defaults in `inst->controls.dec` as users set controls.

The header has no state. It depends only on a forward declaration, keeping V4L2 control details private to the implementation.

Risks are limited to lifecycle ordering: callers must free the control handler on later open failures and during close/common cleanup. Test signals include successful decoder open, visible decoder controls through V4L2 query APIs, and clean error unwind if control initialization fails.
