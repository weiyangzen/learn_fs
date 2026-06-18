# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_connector.h

## Purpose

`vkms_connector.h` defines the VKMS connector wrapper and declares connector lifecycle/hotplug helpers.

## Important APIs and types

`struct vkms_connector` wraps `struct drm_connector`. `drm_connector_to_vkms_connector()` converts from DRM connector to wrapper. `vkms_connector_init()` creates the connector for a VKMS device, and `vkms_trigger_connector_hotplug()` emits a hotplug notification for connector status changes.

## Integration, state, and risks

The wrapper is used by output initialization and config connector runtime pointers. It has no standalone persistence beyond managed DRM allocation. The main risk is ensuring conversions are only applied to VKMS-owned connectors.

## Test signals

Build coverage verifies declarations. Runtime signals are successful connector initialization, status detection, and hotplug event behavior.
