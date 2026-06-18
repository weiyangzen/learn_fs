# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Kconfig

## Purpose

This top-level Renesas DRM Kconfig file includes the three Renesas display-driver configuration namespaces: R-Car DU, RZ/G2L DU, and legacy shmobile.

## Important APIs, Types, and Functions

- Sources `drivers/gpu/drm/renesas/rcar-du/Kconfig`.
- Sources `drivers/gpu/drm/renesas/rz-du/Kconfig`.
- Sources `drivers/gpu/drm/renesas/shmobile/Kconfig`.

## Control Flow

Kconfig evaluation enters this file from the parent DRM Kconfig and then evaluates the included subdriver menus/options.

## State and Persistence Behavior

No runtime state. The selected configuration symbols persist into the kernel build configuration and control compiled objects.

## Dependencies and Integration Points

Integrates Renesas DRM subdrivers into the main DRM configuration tree.

## Risks and Edge Cases

Renaming or moving subdirectories requires updating these source paths or the Renesas DRM menu will lose options.

## Test Signals

Configuration tests should confirm `DRM_RCAR_DU`, RZ DU, and shmobile options appear under DRM after Kconfig parsing.
