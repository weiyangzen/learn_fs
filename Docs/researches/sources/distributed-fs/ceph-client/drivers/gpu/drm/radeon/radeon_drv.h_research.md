# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.h

## Purpose

`radeon_drv.h` is the private driver-entry header for the Radeon DRM driver. It centralizes driver identity strings, the historical non-KMS DRM ABI version, KMS load/open/close prototypes, the Radeon IOCTL wrapper prototype, and ATPX/vga-switcheroo handler declarations or stubs.

## Important APIs, Types, and Functions

- Driver metadata macros: `DRIVER_AUTHOR`, `DRIVER_NAME`, and `DRIVER_DESC`.
- Legacy DRM ABI version macros: `DRIVER_MAJOR`, `DRIVER_MINOR`, and `DRIVER_PATCHLEVEL`, with an in-file history of old UMS/DRI interface changes.
- Entry prototypes: `radeon_drm_ioctl()`, `radeon_driver_load_kms()`, `radeon_driver_unload_kms()`, `radeon_driver_open_kms()`, and `radeon_driver_postclose_kms()`.
- ATPX/switcheroo prototypes: `radeon_register_atpx_handler()`, `radeon_unregister_atpx_handler()`, `radeon_has_atpx_dgpu_power_cntl()`, and `radeon_is_atpx_hybrid()`, with inline no-op/false stubs when `CONFIG_VGA_SWITCHEROO` is disabled.

## Control Flow

The header does not execute logic, but it determines which external functions `radeon_drv.c` can call during module init/probe/open/close and whether ATPX behavior is compiled as real calls or stubs. Including `radeon_family.h` makes family and flag values available to PCI ID and entry code.

## State and Persistence Behavior

There is no runtime state here. The macros define stable identity and ABI constants that become part of module metadata and DRM driver registration. The compile-time switcheroo stubs change behavior by configuration rather than runtime state.

## Dependencies and Integration Points

This file depends on Linux firmware/platform headers and `radeon_family.h`. It is used by `radeon_drv.c` and KMS support code to share prototypes without exposing broader Radeon internals. The ATPX declarations integrate with the platform power management implementation built when switcheroo is enabled.

## Risks and Edge Cases

- The legacy ABI version history is documentation and should not be casually edited; userspace may rely on version reporting.
- Stubs hide ATPX functionality at compile time, so code paths must be safe when hybrid graphics detection always returns false.
- Adding broad declarations here can increase coupling between driver entry code and lower-level subsystems.

## Test Signals

Build both with and without `CONFIG_VGA_SWITCHEROO`, verify module metadata and DRM driver names, ensure KMS open/postclose/load prototypes stay synchronized with implementations, and check that legacy ABI constants match expected userspace-visible values.
