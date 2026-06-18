<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.h

Purpose: declares SoC remapper initialization.

Important API: `xe_soc_remapper_init(struct xe_device *xe)` populates remapper locks and function pointers based on device capabilities.

Dependencies and risks: includes `xe_device_types.h` because initialization writes into the device structure. Tests should verify initialization is harmless when no remapper capabilities are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_soc_remapper.h -->
