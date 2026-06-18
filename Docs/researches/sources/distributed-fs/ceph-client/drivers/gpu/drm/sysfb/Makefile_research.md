# sources/distributed-fs/ceph-client/drivers/gpu/drm/sysfb/Makefile

## Purpose

`sysfb/Makefile` maps the sysfb Kconfig symbols to object files and assembles the shared `drm_sysfb_helper` composite object.

## Important APIs, Types, and Definitions

- `drm_sysfb_helper-y`: includes `drm_sysfb.o` and `drm_sysfb_modeset.o`.
- `drm_sysfb_helper-$(CONFIG_SCREEN_INFO)`: conditionally adds `drm_sysfb_screen_info.o`.
- `obj-$(CONFIG_DRM_SYSFB_HELPER)`: builds the helper module/object.
- `obj-$(CONFIG_DRM_COREBOOTDRM/EFIDRM/OFDRM/SIMPLEDRM/VESADRM)`: builds concrete drivers.

## Control Flow and State

Kernel build logic includes helper sources only when selected. `drm_sysfb_screen_info.o` is omitted without `CONFIG_SCREEN_INFO`, matching header guards around screen-info helper declarations.

## Dependencies and Integration Points

It integrates directly with `sysfb/Kconfig` and the source files in this directory. The composite helper must include every exported symbol used by the concrete drivers.

## Risks and Edge Cases

- Adding a new helper source without updating `drm_sysfb_helper-y` creates unresolved symbols.
- Screen-info helper users must remain guarded by `CONFIG_SCREEN_INFO`.
- Concrete object names must match platform driver module expectations and Kconfig symbols.

## Test Signals

Build tests should cover helper-only, each concrete driver as built-in and module, and `CONFIG_SCREEN_INFO=n` where available. `modpost` unresolved-symbol checks are the key signal.
