# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/Makefile

## Purpose

`tilcdc/Makefile` defines how the TI LCDC DRM driver and legacy panel overlay support are built.

## Important APIs, Types, and Functions

- Adds `-Werror` to `ccflags-y` unless `KCFLAGS` already contains `-W`.
- Builds the composite `tilcdc.o` from `tilcdc_plane.o`, `tilcdc_crtc.o`, `tilcdc_encoder.o`, and `tilcdc_drv.o`.
- Adds `tilcdc_panel_legacy.o` and the wrapped `tilcdc_panel_legacy.dtbo.o` when `CONFIG_DRM_TILCDC_PANEL_LEGACY` is enabled.

## Control Flow

Kbuild uses `obj-$(CONFIG_DRM_TILCDC)` to include the main driver object and `obj-$(CONFIG_DRM_TILCDC_PANEL_LEGACY)` for the legacy helper and embedded DT overlay.

## State and Persistence Behavior

The Makefile controls build artifacts only. The embedded DTBO symbols consumed by `tilcdc_panel_legacy.c` come from the `.dtbo.o` object listed here.

## Dependencies and Integration Points

It integrates with Kbuild composite-object rules, Kconfig symbols, and DT overlay wrapping via kernel build scripts.

## Risks and Edge Cases

- Enforced `-Werror` can break builds when compiler warnings change.
- The legacy C file depends on begin/end symbols generated only if the DTBO object is built; removing that object breaks linking.

## Test Signals

Build tests should cover different compilers and warning flags, main driver as built-in/module, and legacy overlay enabled to ensure DTBO symbol generation and linking succeed.
