# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/Makefile

## Purpose
Builds the i.MX IPUv3 DRM core module and optional output encoder modules according to the Kconfig symbols.

## Important APIs, types, and functions
- `imxdrm-objs := imx-drm-core.o ipuv3-crtc.o ipuv3-plane.o` groups the core DRM master, CRTC, and plane code into the `imxdrm` module.
- `obj-$(CONFIG_DRM_IMX) += imxdrm.o` builds the core when enabled.
- Optional objects are `parallel-display.o`, `imx-tve.o`, `imx-ldb.o`, and `dw_hdmi-imx.o`.

## Control flow
There is no runtime control flow. Kbuild expands symbol-controlled `obj-*` assignments to compile built-in or module objects.

## State and persistence
No runtime state. The object list persists as the build contract between Kconfig symbols and source files.

## Dependencies and integration points
Connects Kconfig options to the component drivers consumed by the i.MX DRM master. The core object grouping is important because `imx-drm-core.c` registers both the master platform driver and the `ipu_drm_driver` exported by `ipuv3-crtc.c`.

## Risks
Removing `ipuv3-crtc.o` or `ipuv3-plane.o` from `imxdrm-objs` would break symbols used by the core. Optional encoder objects must remain separate because they are independently controlled and may be modules.

## Test signals
Build tests should confirm the `imxdrm` module contains the core/CRTC/plane objects and each optional Kconfig symbol emits its corresponding object or module.
