# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Kconfig

## Purpose

`armada/Kconfig` declares the `DRM_ARMADA` kernel configuration option for Marvell Armada SoC LCD controller DRM support.

## Important APIs, Types, And Functions

The config symbol is `DRM_ARMADA`, a tristate labeled "DRM support for Marvell Armada SoCs". It depends on `DRM`, `HAVE_CLK`, `ARM`, and `MMU`. It selects `DRM_CLIENT_SELECTION`, `DRM_KMS_HELPER`, and conditionally `FB_IOMEM_HELPERS` when `DRM_FBDEV_EMULATION` is enabled.

## Control Flow

Kconfig has no runtime control flow. Build selection controls whether the Armada DRM module is built in, built as a module, or omitted. Selected helper symbols ensure the driver has KMS and fbdev helper support needed by the Makefile-selected objects.

## State And Persistence Behavior

No runtime state is stored here. Build-time state determines object compilation, module availability, and whether fbdev helper code can use I/O-memory fb operations.

## Dependencies And Integration Points

This file integrates the Armada driver with the kernel DRM build system. The help text documents support for Armada 510 LCD controllers, graphics/video overlays, KMS, and userspace buffer management without built-in acceleration.

## Risks And Edge Cases

The `ARM && MMU` dependency excludes other architectures or no-MMU builds even if code compiles. Selecting `DRM_CLIENT_SELECTION` affects DRM client behavior. If fbdev emulation is enabled without `FB_IOMEM_HELPERS`, the fbdev object would miss required helper ops, hence the conditional select.

## Test Signals

Build tests should cover `DRM_ARMADA=m`, `DRM_ARMADA=y`, fbdev emulation on/off, and dependency-disabled configurations. Runtime probe tests validate the config actually produces `armada-drm`/`armada-lcd` platform driver registration.
