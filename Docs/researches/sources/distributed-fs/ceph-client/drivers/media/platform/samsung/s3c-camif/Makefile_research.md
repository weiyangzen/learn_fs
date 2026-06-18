# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/Makefile

## Purpose
Builds the Samsung S3C CAMIF driver objects under the `VIDEO_S3C_CAMIF` Kconfig option.

## Important APIs, Types, and Functions
Defines `s3c-camif-objs` as `camif-core.o`, `camif-capture.o`, and `camif-regs.o`, then adds `s3c-camif.o` to `obj-$(CONFIG_VIDEO_S3C_CAMIF)`.

## Control Flow
When the Kconfig symbol is enabled, Kbuild links the three component objects into one `s3c-camif` built-in object or module. When disabled, none of the directory's driver objects are built.

## State and Persistence
There is no runtime state; this is purely build-system metadata.

## Dependencies and Integration Points
Depends on the parent media Samsung Makefile including this directory and on Kconfig selecting `VIDEO_S3C_CAMIF`. It ties the core, capture, and register implementation files into one module.

## Risks and Edge Cases
The directory comment mentions `s3c244x/s3c64xx`, while Kconfig only exposes the S3C64XX driver option, so maintainers should verify whether that comment is historical. Missing any of the three object files breaks the module link.

## Test Signals
Build `CONFIG_VIDEO_S3C_CAMIF=m` and verify `s3c-camif.ko` contains all three objects; build `=y` for built-in linkage; and confirm clean no-op behavior when the option is unset.
