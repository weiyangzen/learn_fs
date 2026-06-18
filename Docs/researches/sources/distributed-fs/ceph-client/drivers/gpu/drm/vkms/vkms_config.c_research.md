# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_config.c

## Purpose

`vkms_config.c` implements the in-memory VKMS topology configuration model. It creates/destroys device configs, builds default topologies from module parameters, validates plane/CRTC/encoder/connector relationships, exposes a debugfs summary, and manages xarray-backed possible-link relationships.

## Important APIs and functions

Public helpers include `vkms_config_create()`, `vkms_config_default_create()`, `vkms_config_destroy()`, `vkms_config_is_valid()`, `vkms_config_register_debugfs()`, create/destroy helpers for each topology object, attach/detach helpers for possible CRTCs/encoders, and lookup helpers for a CRTC primary or cursor plane. Many functions are exported for KUnit.

## Control flow and state

`vkms_config_create()` allocates a config, duplicates the device name, and initializes lists. The default constructor creates one primary plane, one CRTC, optional overlays/cursor, one encoder, and one connector, linking all possible paths. Destroy walks all lists safely; CRTC and encoder destruction also detaches reverse links from dependent objects.

Validation enforces 1 to 31 planes/CRTCs/encoders/connectors, at least one possible CRTC for every plane/encoder, at least one primary and no duplicate primary/cursor per CRTC, at least one encoder for every CRTC, and at least one possible encoder for every connector. Link attach helpers reject cross-config attachments and duplicates, then allocate xarray entries.

## Dependencies and integration

The file depends on Linux lists/xarrays, DRM plane/connector status types, debugfs helpers, and VKMS driver types. It feeds both `vkms_drv.c` default-device creation and `vkms_configfs.c` user-created devices. `vkms_output_init()` consumes the config object's runtime pointers during DRM object creation.

## Risks and test signals

Risks include reverse-link cleanup gaps, duplicate topology acceptance, xarray allocation errors, and using internal runtime pointers after device teardown. The `vkms-config` KUnit suite thoroughly covers default creation, validation rules, object iteration, link attach/detach, cross-config rejection, and connector status.
