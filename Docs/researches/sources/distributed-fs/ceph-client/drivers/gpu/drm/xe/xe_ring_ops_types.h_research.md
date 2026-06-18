<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops_types.h

Purpose: defines the ring operations vtable and command-size bounds.

Important types and constants: `MAX_JOB_SIZE_DW` is 74 DWORDs and `MAX_JOB_SIZE_BYTES` is its byte size. `struct xe_ring_ops` contains `emit_job(struct xe_sched_job *)` and optional `emit_aux_table_inv(struct xe_gt *, u32 *)`.

Risks and test signals: every emitter in `xe_ring_ops.c` asserts it stays within `MAX_JOB_SIZE_DW`. Adding commands, workarounds, or user-fence features must update size proofs or risk ring overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops_types.h -->
