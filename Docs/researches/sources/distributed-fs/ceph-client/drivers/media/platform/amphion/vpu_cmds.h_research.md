<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.h

Purpose: declares the command/session control API used by codec implementations, debugfs, message handling, and core power-management paths.

Important APIs: session helpers cover configure, start, stop, abort, reset-buffer, encode-frame, frame-store allocation/release, timestamp submission, parameter update, and debug. Core helpers cover snapshot and software reset. `vpu_response_cmd()` and `vpu_clear_request()` expose response and cleanup hooks.

Control/state behavior: the header itself has no state; it formalizes that callers operate on `struct vpu_inst` or `struct vpu_core` and that command synchronization is centralized in `vpu_cmds.c`.

Dependencies and integration: depends on `struct vpu_inst`, `struct vpu_core`, `struct vpu_fs_info`, and `struct vpu_ts_info` definitions from shared Amphion headers.

Risks and test signals: API drift is the primary risk. Build tests should catch mismatched prototypes, while runtime testing should verify every declared command path reaches firmware and receives the expected response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_cmds.h -->
