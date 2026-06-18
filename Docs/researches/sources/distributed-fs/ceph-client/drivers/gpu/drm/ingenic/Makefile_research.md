# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/Makefile

## Purpose
Builds the Ingenic DRM driver, optional IPU object, and optional DesignWare HDMI wrapper.

## Important APIs, types, and functions
- `obj-$(CONFIG_DRM_INGENIC) += ingenic-drm.o` builds the main module.
- `ingenic-drm-y = ingenic-drm-drv.o` makes the display controller driver the base object.
- `ingenic-drm-$(CONFIG_DRM_INGENIC_IPU) += ingenic-ipu.o` conditionally links IPU support into the main driver.
- `obj-$(CONFIG_DRM_INGENIC_DW_HDMI) += ingenic-dw-hdmi.o` builds the HDMI wrapper separately.

## Control flow
No runtime flow. Kbuild composes the main module and optional objects from Kconfig symbols.

## State and persistence
No runtime state exists. The Makefile records build-time module composition.

## Dependencies and integration points
Connects Kconfig options to the core Ingenic DRM source, the optional IPU integration source, and the DW-HDMI wrapper source.

## Risks
The IPU object is linked into `ingenic-drm.o`; mismatched `CONFIG_DRM_INGENIC_IPU` guards between sources can cause unresolved references. HDMI remains a separate module/object and must coordinate through OF graph rather than direct linking.

## Test signals
Build matrix should include main-only, main+IPU, HDMI-only dependencies satisfied, and all enabled together.
