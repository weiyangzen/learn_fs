# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/Makefile

## Purpose
`Makefile` builds the ET8EK8 sensor driver as a composite object.

## Important APIs, Types, and Functions
`et8ek8-objs` is extended with `et8ek8_mode.o` and `et8ek8_driver.o`. `obj-$(CONFIG_VIDEO_ET8EK8)` adds the composite `et8ek8.o` to the kernel build when the Kconfig symbol is enabled.

## Control Flow
There is no runtime control flow. Kbuild first compiles the generated/static register-list mode object and the driver object, then links them into `et8ek8.o`.

## State and Persistence
The build recipe has no runtime state. It encodes the important link-time dependency that `et8ek8_driver.c` expects the external `meta_reglist` symbol supplied by `et8ek8_mode.o`.

## Dependencies and Integration Points
This file integrates the Kconfig symbol with kbuild and with the split ET8EK8 implementation. The driver source includes `et8ek8_reg.h`, while the mode object supplies the actual register tables declared there.

## Risks and Edge Cases
Dropping `et8ek8_mode.o` would leave `meta_reglist` unresolved. Reordering is not expected to matter for kbuild, but both objects must remain in the composite object whenever the driver is enabled.

## Test Signals
Build with `CONFIG_VIDEO_ET8EK8=m` and verify both constituent objects compile and link into `et8ek8.ko`; build with `=y` and verify no unresolved `meta_reglist`; build with the option disabled and verify no ET8EK8 objects are produced.
