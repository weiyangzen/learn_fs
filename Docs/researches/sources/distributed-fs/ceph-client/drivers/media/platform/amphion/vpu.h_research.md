<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu.h

Purpose: central shared header for the Amphion VPU driver. It defines platform/core/instance state, format descriptors, buffer wrappers, operation-vector contracts, timeout constants, buffer state values, exported driver APIs, and tracing helpers.

Important APIs/types: `struct vpu_dev` represents the parent platform device, media/v4l2 devices, encoder/decoder functions, registered cores, runtime reference counters, power hooks, and debugfs root. `struct vpu_core` represents a firmware core with reserved firmware/RPC/log/activity buffers, mailbox channels, workqueues, message FIFOs, instance list, state, firmware version, hang mask, and debugfs handles. `struct vpu_inst` represents a V4L2 session with formats, controls, workqueue, firmware command queue, stream buffer, vb2 state, and codec-specific private data. `struct vpu_inst_ops` is the contract implemented by `vdec.c` and `venc.c`.

Control flow and state: instances call `vpu_request_core()`/`vpu_inst_register()` to bind to an active core and acquire an instance ID. Common V4L2 and message code uses `call_vop()`/`call_void_vop()` to dispatch codec-specific behavior. Buffer state constants layer driver-specific state on top of vb2 state, especially for decode frame-store ownership and encoded output readiness.

Dependencies and integration: pulls in V4L2 device/controls/mem2mem, mailbox, and kfifo APIs. Declares exported functions implemented across `vpu_drv.c`, `vpu_core.c`, `vpu_dbg.c`, `vdec.c`, and `venc.c`.

Risks: because this header defines shared mutable structures, lifetime and locking assumptions are spread across files. `instance_mask` and `hang_mask` are bitfields stored as `unsigned long` and depend on bounds from `supported_instance_count`. The misspelled `VPU_CODEC_STATE_DYAMIC_RESOLUTION_CHANGE` is ABI-internal but easy to propagate.

Test signals: build coverage catches struct/API drift. Runtime signals are correct core allocation/release, debugfs instance visibility, reference-counted cleanup, and consistent driver buffer-state transitions under both encoder and decoder workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu.h -->
