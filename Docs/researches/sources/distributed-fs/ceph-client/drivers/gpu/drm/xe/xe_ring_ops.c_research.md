<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.c

Purpose: emits Gen12-style ring commands around scheduled jobs for GSC, copy, video, render/compute, and migration queues. It handles timestamp copies, start seqno writes, TLB/cache invalidation, AuxCCS table invalidation, batch buffer starts, user fences, seqno signaling, and user interrupts.

Important APIs and control flow: `xe_ring_ops_get()` selects a `struct xe_ring_ops` by engine class and AuxCCS support. Internal emitters build bounded arrays of DWORD commands and write them to LRC rings. `__emit_job_gen12_simple()` serves copy/GSC-like engines, `__emit_job_gen12_video()` adds Aux table invalidation, `__emit_job_gen12_render_compute()` adds PIPE_CONTROL invalidation and render cache flushes, and `emit_migration_job_gen12()` emits two batch phases with migration flush flags. `emit_fake_watchdog()` supports forced engine reset tests.

State and dependencies: uses `xe_sched_job` fields such as `ptrs`, `user_fence`, `ring_ops_flush_tlb`, `ring_ops_force_reset`, `migrate_flush_flags`, and queue/LRC seqno addresses. It depends on MI/PIPE_CONTROL command definitions, engine registers, workarounds, VM/migration flags, SR-IOV VF timestamp sampling, and `MAX_JOB_SIZE_DW` assertions.

Risks and test signals: command streams must remain under `MAX_JOB_SIZE_DW`; tests should validate each engine class path, AuxCCS versus non-AuxCCS selection, VF duplicate timestamp storage, TLB invalidation flags, compute/no-render mask handling, user fence writes, and migration two-batch sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.c -->
