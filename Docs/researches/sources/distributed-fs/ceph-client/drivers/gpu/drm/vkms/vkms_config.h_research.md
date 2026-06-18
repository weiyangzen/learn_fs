# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.h

## Purpose

`vkms_config.h` defines the topology data model and helper API for configuring VKMS devices before they are instantiated as DRM devices.

## Important APIs and types

`struct vkms_config` owns device name, lists of planes/CRTCs/encoders/connectors, and the live `struct vkms_device *dev` when instantiated. Per-object structs store their owner config, link node, user-visible attributes, xarray possible-link sets, and temporary runtime DRM object pointers. Iteration macros wrap list and xarray traversal for all object/link classes. Inline accessors expose device name, CRTC count, plane type/default pipeline, CRTC writeback flag, and connector status.

The header declares all creation/destruction, validation, debugfs, attachment, detachment, and lookup functions implemented in `vkms_config.c`.

## State and integration

The state model is pre-device configuration plus runtime back-references populated during device creation. Configfs mutates this model under its device lock; the default module path creates it from module parameters; output/plane/connector initialization consumes it to build DRM objects.

## Risks and test signals

The main risks are lifetime confusion between persistent config objects and transient runtime pointers, xarray link ownership, and callers mutating configs while a device is enabled. The KUnit config suite exercises this API directly, including list iteration, link iteration, validation, and status setters.
