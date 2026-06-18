# sources/distributed-fs/ceph-client/include/drm/drm_ras_genl_family.h

## Purpose
`drm_ras_genl_family.h` declares lifecycle hooks for the DRM RAS generic netlink family.

## Important APIs, types, and functions
The only APIs are `drm_ras_genl_family_register` and `drm_ras_genl_family_unregister`. They are real declarations when `CONFIG_DRM_RAS` is enabled and inline no-op success/empty stubs otherwise.

## Control flow
DRM RAS subsystem initialization registers the generic netlink family before serving RAS queries. Cleanup unregisters it so userspace can no longer issue family commands.

## State and persistence
The header stores no state. Netlink family registration is global runtime state managed by the implementation and removed on subsystem exit.

## Dependencies and integration points
It integrates the DRM RAS node layer with Linux generic netlink registration. It is intentionally small to separate family lifecycle from node provider declarations.

## Risks and test signals
Risks include register/unregister ordering relative to node registration, double unregister, config-disabled code assuming a userspace API exists, and family registration failure propagation. Test signals include CONFIG_DRM_RAS on/off builds, module init failure injection, generic netlink family visibility, and cleanup after registered nodes.
