<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.h

Purpose: declares ring operation selection for GT engine classes.

Important API: `xe_ring_ops_get(struct xe_gt *gt, enum xe_engine_class class)` returns the command-emission vtable appropriate to an engine class and platform compression mode.

Dependencies and risks: depends on engine class enum and `struct xe_ring_ops`. Callers must handle NULL for unsupported classes and must initialize GT platform/compression info before selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ring_ops.h -->
