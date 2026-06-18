# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/Makefile

## Purpose
Assembles the i.MX IPUv3 core object from its submodule implementation files. It controls which source files participate in `imx-ipu-v3.o`.

## Important APIs, Types, and Functions
There are no runtime APIs. The central build artifact is `imx-ipu-v3.o`, enabled by `obj-$(CONFIG_IMX_IPUV3_CORE)`. The base object list includes common IPU core, CPMEM, CSI, DC, DI, DP, DMFC, IC, CSC, image-convert, SMFC, and VDI implementation files. Under `CONFIG_DRM`, it adds `ipu-pre.o` and `ipu-prg.o`.

## Control Flow
Kbuild compiles the listed objects into one module or built-in object depending on `CONFIG_IMX_IPUV3_CORE`. The conditional DRM block keeps PRE/PRG support tied to DRM builds because those modules are used for tiled framebuffer/display paths.

## State and Persistence
Build state is encoded in generated objects. There is no runtime state in this file.

## Dependencies and Integration Points
Couples with `Kconfig` and with `ipu-common.c`, whose module init registers not only the main IPU platform driver but also `ipu_pre_drv` and `ipu_prg_drv` when DRM is enabled. It also implies that symbols exported across these files are intra-module as well as available to other GPL modules.

## Risks
Adding a new submodule API without listing its source here will produce link failures or missing runtime functionality. PRE/PRG references in common code must remain guarded consistently with `CONFIG_DRM`, because these files disappear from non-DRM builds.

## Test Signals
The primary tests are compile/link coverage for `CONFIG_IMX_IPUV3_CORE=y/m`, `CONFIG_DRM=y/m/n`, and COMPILE_TEST. Undefined references to `ipu_pre_drv`, `ipu_prg_drv`, or submodule init/exit functions are direct Makefile/Kconfig mismatch signals.
