# sources/distributed-fs/ceph-client/drivers/media/platform/via/Makefile

## Purpose
Connects the VIA media platform Kconfig symbol to the camera driver object.

## Important APIs, Types, And Functions
- Adds `via-camera.o` to the build when `CONFIG_VIDEO_VIA_CAMERA` is enabled.

## Control Flow
No runtime control flow exists. Kbuild includes or omits the object based on the Kconfig symbol.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Integrated with `drivers/media/platform/via/Kconfig` and the kernel media platform build system.

## Risks And Edge Cases
The Makefile has a single object and no composite object list, so future multi-file VIA camera changes would need build updates.

## Test Signals
Build with `CONFIG_VIDEO_VIA_CAMERA=m` should produce `via-camera.ko`; built-in configuration should link the object into the kernel image.
