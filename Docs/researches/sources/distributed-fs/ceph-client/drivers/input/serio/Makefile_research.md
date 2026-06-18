# sources/distributed-fs/ceph-client/drivers/input/serio/Makefile

## Purpose

`drivers/input/serio/Makefile` maps Kconfig symbols to serio subsystem object files. It tells Kbuild which source files compose the core serio bus and each optional serio driver.

## Important APIs, Types, and Functions

The file uses `obj-$(CONFIG_...) += ...` entries. `CONFIG_SERIO` builds `serio.o`; individual symbols map to drivers such as `i8042.o`, `serport.o`, `ambakmi.o`, `gscps2.o`, `libps2.o`, `altera_ps2.o`, `ams_delta_serio.o`, `arc_ps2.o`, `apbps2.o`, `ps2-gpio.o`, and `userio.o`. `CONFIG_HIL_MLC` builds two objects: `hp_sdc_mlc.o` and `hil_mlc.o`.

## Control Flow

There is no runtime control flow. Kbuild evaluates each `CONFIG_*` value. Enabled built-in symbols link the objects into the kernel; module symbols build `.ko` modules; disabled symbols omit objects.

## State and Persistence Behavior

The file affects build artifacts only. It does not persist runtime driver state. The object list is persistent build metadata that must stay synchronized with Kconfig and source filenames.

## Dependencies and Integration Points

The Makefile integrates the serio directory with the kernel build system and the Kconfig symbols declared beside it. It is the link between user-visible configuration choices and compiled driver code.

## Risks and Edge Cases

Adding or renaming a driver without updating this file causes missing modules or build failures. Multi-object symbol entries such as `CONFIG_HIL_MLC` need special attention. Mismatches between Kconfig module names and Makefile targets confuse users and packaging.

## Test Signals

Tests include `make M=drivers/input/serio`, allmodconfig/allnoconfig/randconfig builds, module-name checks for each help-text module, and build failures after source renames or Kconfig symbol changes.
