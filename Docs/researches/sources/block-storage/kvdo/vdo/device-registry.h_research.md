# File Research: sources/block-storage/kvdo/vdo/device-registry.h

## Purpose
Declares the VDO global registry API.

## API
- `vdo_filter_t`: predicate callback for matching a `struct vdo`.
- `vdo_initialize_device_registry_once()`: one-time setup.
- `vdo_register()` / `vdo_unregister()`: manage registry membership.
- `vdo_find_matching()`: returns the first VDO matching a supplied predicate/context.

## Integration
Used by the DM target constructor to prevent backing-device sharing and to locate an existing VDO by device name during table reload.
