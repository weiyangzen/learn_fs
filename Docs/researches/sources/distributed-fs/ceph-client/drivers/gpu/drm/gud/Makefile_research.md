
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Makefile

## Purpose
`gud/Makefile` defines the object composition for the Generic USB Display DRM driver.

## Important APIs, Types, And Functions
It builds `gud.o` from `gud_drv.o`, `gud_pipe.o`, and `gud_connector.o`, and adds it to the kernel build when `CONFIG_DRM_GUD` is enabled.

## Control Flow
There is no runtime control flow. Kbuild uses `gud-y` to link the driver core, framebuffer flushing pipeline, and connector support into one module or built-in object.

## State And Persistence
The file owns only build graph state.

## Dependencies And Integration Points
The object list corresponds to the internal API split in `gud_internal.h`: `gud_drv.c` provides probe and USB control helpers, `gud_pipe.c` provides plane/CRTC update and bulk flushing, and `gud_connector.c` provides connector enumeration, EDID/mode handling, properties, and backlight integration.

## Risks
Omitting one object would produce unresolved symbols or a driver that probes but cannot expose connectors or flush pixels. Adding new source files requires updating this list.

## Test Signals
Build tests with `CONFIG_DRM_GUD=m` should produce `gud.ko` containing all three implementation units and no unresolved internal symbols.
