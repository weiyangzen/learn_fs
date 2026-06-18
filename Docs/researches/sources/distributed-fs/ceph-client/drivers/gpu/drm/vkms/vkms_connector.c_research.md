# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.c

## Purpose

`vkms_connector.c` implements VKMS virtual connector behavior: detection status, mode enumeration, encoder selection, connector initialization, and hotplug notification.

## Important APIs and functions

`vkms_connector_init()` allocates a managed `struct vkms_connector`, initializes a DRM virtual connector with atomic helper funcs, and attaches connector helper funcs. `vkms_connector_detect()` reads connector status from the live `vkms_config_connector` associated with the wrapper; if the config object has disappeared, it preserves the current connector status. `vkms_conn_get_modes()` publishes DRM no-EDID modes up to VKMS maximums and marks the default resolution preferred. `vkms_conn_best_encoder()` returns the first possible encoder. `vkms_trigger_connector_hotplug()` emits a KMS hotplug event.

## State and integration

The connector state comes from both DRM connector state and the configuration model. Configfs can change connector status and trigger hotplug while enabled. Output initialization links connectors to possible encoders according to the config.

## Risks and test signals

Risks include stale config pointers after configfs removal, missing possible encoders, and mode list assumptions without EDID. Tests should cover connector status transitions through configfs, hotplug event delivery, no-EDID mode enumeration, and atomic modesets through possible encoder paths.
