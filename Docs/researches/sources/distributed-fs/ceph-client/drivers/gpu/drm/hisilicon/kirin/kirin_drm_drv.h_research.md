# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/kirin_drm_drv.h

Purpose: shared Kirin DRM private interface between the master driver and ADE backend.

Important APIs/types: container macros convert DRM CRTC/plane to Kirin wrappers. `struct kirin_format` maps DRM fourcc to hardware formats. `struct kirin_crtc` and `struct kirin_plane` extend DRM objects with hardware context and channel/enable state. `struct kirin_drm_data` packages per-display-controller callbacks, formats, limits, DRM driver, function tables, plane counts, and context lifecycle. `ade_driver_data` is declared externally.

Control flow: the master driver consumes `kirin_drm_data` from OF match data to allocate objects and call ADE context setup, while ADE fills the exported data.

State and persistence: defines runtime object wrappers and immutable driver-data contracts. No persistent storage.

Dependencies and integration points: integrates Kirin master, ADE backend, DRM atomic helpers, and platform resource allocation through function pointers.

Risks: function pointer table correctness controls all object initialization. `KIRIN_MAX_PLANE` in the C file must remain compatible with `num_planes`. Container macros assume exact embedding.

Test signals: compile/link of ADE data, platform bind using OF match data, object initialization for all `num_planes`, and cleanup callback execution.
