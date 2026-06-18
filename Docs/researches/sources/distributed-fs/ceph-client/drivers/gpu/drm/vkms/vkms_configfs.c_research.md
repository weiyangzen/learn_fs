# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_configfs.c

## Purpose

`vkms_configfs.c` exposes runtime creation and configuration of VKMS devices through configfs. It maps configfs directories, attributes, and symlinks to the `vkms_config` topology model, then creates or destroys DRM devices when the device `enabled` attribute changes.

## Important APIs and functions

The public entry points are `vkms_configfs_register()` and `vkms_configfs_unregister()`. Internal configfs item types model devices, planes, CRTCs, encoders, connectors, and possible-link groups. Attribute handlers expose CRTC `writeback`, plane `type`, connector `status`, and device `enabled`. `allow_link`/`drop_link` handlers connect planes to CRTCs, encoders to CRTCs, and connectors to encoders.

## Control flow and state

Creating a directory under `/config/vkms` allocates `struct vkms_configfs_device`, creates a `vkms_config`, initializes a mutex, and adds default child groups for planes, CRTCs, encoders, and connectors. Child directory creation allocates configfs wrappers and corresponding config objects. Symlinks in `possible_*` groups call the config attach helpers. Most structural mutations reject changes with `-EBUSY` once the device is enabled.

Writing `enabled=1` validates the config and calls `vkms_create()`. Writing `enabled=0` calls `vkms_destroy()`. Connector status can be changed while enabled and triggers `vkms_trigger_connector_hotplug()`. Release handlers destroy underlying config objects and wrapper allocations; device release also destroys a live device and the owned config.

## Dependencies and integration

The file depends on Linux configfs, cleanup scoped guards, mutexes, VKMS config helpers, `vkms_create()`/`vkms_destroy()`, and connector hotplug support. It is registered at module init and gives users a way to instantiate non-default VKMS topologies.

## Risks and test signals

Risks include configfs lifetime ordering, symlink targets from other devices, lock coverage around live enable/disable, ensuring all structural edits are blocked while enabled, and preventing the reserved default device name from colliding with module-created VKMS. KUnit does not cover configfs directly; useful signals are configfs integration tests creating devices, linking topology, toggling enabled, and changing connector status live.
