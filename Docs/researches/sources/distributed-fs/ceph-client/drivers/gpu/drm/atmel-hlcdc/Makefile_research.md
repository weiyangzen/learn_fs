<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Makefile

## Purpose

The Makefile defines how the Atmel HLCDC DRM driver is built from its CRTC, device-core, output, and plane components.

## Important APIs, Types, And Targets

- `atmel-hlcdc-dc-y`: composite object list containing `atmel_hlcdc_crtc.o`, `atmel_hlcdc_dc.o`, `atmel_hlcdc_output.o`, and `atmel_hlcdc_plane.o`.
- `obj-$(CONFIG_DRM_ATMEL_HLCDC) += atmel-hlcdc-dc.o`: builds the composite object when the Kconfig symbol is enabled.

## Control Flow

There is no runtime flow. Kbuild links the listed objects into one driver object in the declared order.

## State And Persistence Behavior

The file only affects build artifacts. It does not define runtime state.

## Dependencies And Integration Points

It integrates with the local Kconfig symbol and Linux DRM/Kbuild infrastructure. All runtime pieces in the folder are compiled together as one module or built-in unit.

## Risks And Edge Cases

Omitting one object breaks unresolved symbols across CRTC/device/output/plane boundaries. Object order is generally not semantically significant here, but all four pieces are required for a functional driver.

## Test Signals

Build `CONFIG_DRM_ATMEL_HLCDC=y` and `m`, run `modpost`, and boot/probe the module to ensure all cross-file symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Makefile -->
