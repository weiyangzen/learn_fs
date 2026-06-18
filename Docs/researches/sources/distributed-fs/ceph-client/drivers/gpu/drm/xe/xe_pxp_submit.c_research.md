<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.c

Purpose: owns PXP command submission resources and packet emission. It allocates a VCS queue/batch for inline session termination and a GSCCS queue/VM/BO for HECI-style GSC firmware messages used by session init and stream-key invalidation.

Important APIs and control flow: `xe_pxp_allocate_execution_resources()` creates VCS and GSC resources; `xe_pxp_destroy_execution_resources()` frees them. `xe_pxp_submit_session_termination()` emits MFX wait, session selection, CRYPTO key exchange, and batch end into a GGTT batch, then creates/arms/pushes a `xe_sched_job` and waits up to one second. `xe_pxp_submit_session_init()` and `xe_pxp_submit_session_invalidation()` build PXP 4.3 firmware messages and submit via `gsccs_send_message()`.

State and persistence: `struct xe_pxp_gsc_client_resources` stores VM, BO, mapped batch/input/output iosys maps, queue, host-session handle, and in/out size. The GSC BO maps a batch page followed by input and output buffers. Headers are poisoned after use to avoid stale reply interpretation.

Dependencies and integration: uses `xe_vm_create()`, `xe_bo_create_pin_map()`, `xe_vm_bind_kernel_bo()`, `xe_exec_queue_create()`, `xe_sched_job`, GSC command helpers, PXP ABI structs, MI/MFX/GSC instruction definitions, and DMA fence waiting. `gsccs_send_message()` handles GSC pending responses by retrying for up to 40 times with 50 ms sleeps.

Risks and test signals: resource cleanup paths span VM, BO, and queue lifetimes; failure injection should cover bind timeout, queue creation failure, GSC invalid headers, message overflow, pending timeout, and firmware status errors. Command length assumptions are tight: PXP command size is currently small enough for a page, but new commands must revisit `inout_size` and batch layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_submit.c -->
