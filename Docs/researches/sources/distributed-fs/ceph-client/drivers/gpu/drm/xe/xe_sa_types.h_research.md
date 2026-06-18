<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa_types.h

Purpose: defines the SA manager storage structure.

Important type: `struct xe_sa_manager` embeds `drm_suballoc_manager`, tracks primary and optional shadow BOs, a mutex for shadow swapping, CPU pointer to either direct mapping or staging memory, and whether the BO mapping is iomem.

Risks and test signals: lifetime is tied to DRM managed cleanup in `xe_sa.c`. Tests should verify `cpu_ptr` updates when primary/shadow BOs swap and that shadow state is unavailable unless requested by flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sa_types.h -->
