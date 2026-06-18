# sources/distributed-fs/ceph-client/drivers/input/misc/Makefile

## Purpose

This Kbuild Makefile maps miscellaneous input `CONFIG_*` symbols to the object files compiled into the kernel or emitted as modules. It is the build integration point for all drivers configured by `drivers/input/misc/Kconfig`.

## Important APIs, Types, and Functions

Relevant entries include `obj-$(CONFIG_INPUT_88PM860X_ONKEY) += 88pm860x_onkey.o`, `obj-$(CONFIG_INPUT_88PM80X_ONKEY) += 88pm80x_onkey.o`, `obj-$(CONFIG_INPUT_88PM886_ONKEY) += 88pm886-onkey.o`, `obj-$(CONFIG_INPUT_AB8500_PONKEY) += ab8500-ponkey.o`, `obj-$(CONFIG_INPUT_AD714X) += ad714x.o`, `obj-$(CONFIG_INPUT_AD714X_I2C) += ad714x-i2c.o`, and `obj-$(CONFIG_INPUT_AD714X_SPI) += ad714x-spi.o`.

## Control Flow

There is no runtime flow. During Kbuild, each `obj-$(CONFIG_...)` expands to an object list when the symbol is `y` or `m`. Parent/common objects such as `ad714x.o` are built when the parent symbol is enabled, while bus glue modules are built by their bus-specific symbols.

## State and Persistence Behavior

The file affects generated build artifacts only. It determines which translation units are linked built-in or compiled as modules and therefore which module names exist.

## Dependencies and Integration Points

It consumes Kconfig symbols from the same directory and integrates source files with the broader input subsystem build. It also reflects module naming contracts documented in Kconfig help text.

## Risks and Edge Cases

Kconfig/Makefile mismatches can make an enabled driver fail to build or produce a module with an unexpected name. Parent/bus split drivers such as AD714x require the common object and at least one transport object to be selected coherently. Typographical whitespace inconsistency is mostly harmless but can obscure review. Adding a new misc input driver requires synchronized Kconfig and Makefile changes.

## Test Signals

Test `make M=drivers/input/misc` for relevant symbols as `m`, built-in link coverage for `y`, missing-object detection after file renames, AD714x parent plus I2C/SPI combinations, and module alias/autoload smoke tests for onkey and AD714x transport drivers.
