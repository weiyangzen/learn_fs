# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Makefile

## Purpose
This Makefile defines the object composition for the Freescale DCU DRM driver. It tells kbuild which source files make up the `fsl-dcu-drm` driver and ties the aggregate object to `CONFIG_DRM_FSL_DCU`.

## Important APIs, Types, and Functions
The object list `fsl-dcu-drm-y` includes `fsl_dcu_drm_drv.o`, `fsl_dcu_drm_kms.o`, `fsl_dcu_drm_rgb.o`, `fsl_dcu_drm_plane.o`, `fsl_dcu_drm_crtc.o`, and `fsl_tcon.o`. The line `obj-$(CONFIG_DRM_FSL_DCU) += fsl-dcu-drm.o` makes the aggregate object conditional on the Kconfig symbol.

## Control Flow
There is no runtime control flow. During the kernel build, kbuild compiles the listed objects, links them into `fsl-dcu-drm.o`, and either links it built-in or emits it as a module depending on `CONFIG_DRM_FSL_DCU`.

## State and Persistence Behavior
The Makefile has no runtime state. Build state is represented in generated object files and the final built-in or module artifact.

## Dependencies and Integration Points
It integrates with the Kconfig symbol in the same directory and with kbuild. The object list expresses source-level integration: driver core, KMS setup, RGB connector, plane support, CRTC support, and timing-controller support all form one driver.

## Risks
Adding a new source file without updating this list leaves code unbuilt. Removing or renaming one listed source breaks the build. All objects are unconditional once `DRM_FSL_DCU` is enabled, so optional feature splits would require additional Makefile conditionals.

## Test Signals
Build `CONFIG_DRM_FSL_DCU=y` and `=m`, confirm all listed objects compile and link, inspect module contents with `modinfo`/symbol checks, and run incremental builds after touching each listed source.
