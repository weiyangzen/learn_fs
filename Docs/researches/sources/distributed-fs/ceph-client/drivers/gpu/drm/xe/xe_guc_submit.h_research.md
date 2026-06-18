# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit.h

Purpose: public GuC submission interface for the Xe driver. It exposes lifecycle, reset, pause/unpause, G2H handling, snapshot, VF registration, MLRC detection, and HWSP rebase entry points implemented in `xe_guc_submit.c`.

Important APIs: initialization and enablement (`xe_guc_submit_init`, `xe_guc_submit_enable`, `xe_guc_submit_disable`), reset lifecycle (`xe_guc_submit_reset_prepare`, `xe_guc_submit_reset_wait`, `xe_guc_submit_stop`, `xe_guc_submit_start`), pause/replay (`xe_guc_submit_pause`, `xe_guc_submit_pause_vf`, `xe_guc_submit_unpause_prepare_vf`, `xe_guc_submit_unpause`, `xe_guc_submit_unpause_vf`, `xe_guc_submit_pause_abort`), wedging (`xe_guc_submit_wedge`), GuC notification handlers, snapshot capture/print/free, and `xe_guc_contexts_hwsp_rebase`.

Control flow: callers include GT init, GuC startup, reset handlers, CT G2H dispatch, VF recovery, devcoredump, and exec queue utilities. The header deliberately forward-declares objects to keep compile-time dependencies lower.

State/persistence: no state is declared here, but every function manipulates `struct xe_guc` submission state or per-queue GuC state described in the C file. Snapshot allocation returns a heap object that callers must free with `xe_guc_exec_queue_snapshot_free`.

Dependencies/integration: uses `u32`/`bool`, `struct drm_printer`, `struct xe_guc`, and `struct xe_exec_queue`. It is a central contract between GuC transport, reset, exec queue management, and diagnostics.

Risks/test signals: signature mismatches would break CT dispatch and reset integration. Tests should verify that all G2H handlers reject malformed message lengths and that snapshot users pair capture/free.
