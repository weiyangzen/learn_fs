<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.h

Purpose: declares the per-device shrinker interface.

Important APIs: `xe_shrinker_mod_pages()` adjusts page accounting and `xe_shrinker_create()` registers the shrinker for a device.

Dependencies and risks: forward declares `struct xe_shrinker` and `struct xe_device`. Callers updating accounting must keep deltas balanced so final cleanup assertions do not fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_shrinker.h -->
