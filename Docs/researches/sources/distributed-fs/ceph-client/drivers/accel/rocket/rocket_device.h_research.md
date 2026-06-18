# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.h

Purpose: declares the Rocket DRM facade device container.

Important APIs and types: `struct rocket_device` embeds `struct drm_device`, a scheduler mutex, a dynamic array of `rocket_core`, and a core count. It declares init/fini and `to_rocket_device`.

Control flow: driver open, GEM, and job code convert DRM devices to `rocket_device` through the macro to access cores and scheduling state.

State and persistence: one instance exists for the facade DRM device while at least one NPU core is present.

Dependencies and integration: includes DRM device, IOMMU/platform declarations, and `rocket_core.h`.

Risks and test signals: ensure container conversion remains valid with `devm_drm_dev_alloc`, and verify users cannot open the facade before cores are initialized.
