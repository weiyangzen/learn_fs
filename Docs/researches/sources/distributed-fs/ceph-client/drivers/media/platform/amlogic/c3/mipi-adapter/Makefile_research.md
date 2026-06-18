
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Makefile

## Purpose

This Makefile connects `CONFIG_VIDEO_C3_MIPI_ADAPTER` to the C3 MIPI adapter object file. It is the build-system bridge between the Kconfig symbol and `c3-mipi-adap.c`.

## Important APIs, Types, And Functions

There are no C APIs. The key build directive is `obj-$(CONFIG_VIDEO_C3_MIPI_ADAPTER) += c3-mipi-adap.o`.

## Control Flow

During Kbuild evaluation, `c3-mipi-adap.o` is included in the built-in object list when the symbol is `y`, in the module list when the symbol is `m`, and omitted when disabled.

## State And Persistence

The file has no runtime state. The object-selection result is derived from the kernel configuration and persists only in build artifacts.

## Dependencies And Integration Points

It depends on the enclosing media platform Makefile including this directory. It integrates with the Kconfig file of the same directory and compiles exactly one source file into the adapter driver module or built-in object.

## Risks

The Makefile does not define composite objects, so any future split of adapter code into multiple C files must update this directive. A mismatch between the Kconfig symbol and object name would silently omit the driver, but the current names align.

## Test Signals

Build with `CONFIG_VIDEO_C3_MIPI_ADAPTER=m` and verify a `c3-mipi-adap.ko`-style module is produced. Build with the symbol disabled and verify no adapter object appears in the directory's generated objects.
