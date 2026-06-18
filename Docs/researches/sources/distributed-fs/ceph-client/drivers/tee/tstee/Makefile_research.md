<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tee/tstee/Makefile

## Purpose

`tstee/Makefile` maps the `ARM_TSTEE` Kconfig symbol to the Arm Trusted Services TEE driver object.

## Important APIs, Types, and Functions

It defines `arm-tstee-objs := core.o` and builds `arm-tstee.o` when `CONFIG_ARM_TSTEE` is enabled. There are no functions or runtime APIs in this file.

## Control Flow

Kbuild compiles `core.c` into `core.o`, links it into the composite `arm-tstee.o`, and includes that object as built-in or module according to the tristate value.

## State and Persistence Behavior

The file has no runtime state. It only affects build artifacts and module composition.

## Dependencies and Integration Points

It integrates with Linux Kbuild and the `ARM_TSTEE` symbol defined in `Kconfig`. Any future additional source files for this driver would need to be added to `arm-tstee-objs`.

## Risks and Edge Cases

The assignment uses `obj-$(CONFIG_ARM_TSTEE) = arm-tstee.o` rather than `+=`; this is acceptable in the local file but could overwrite earlier `obj-*` entries if more were added above. The module is single-source today, so dependency tracking is simple.

## Test Signals

Build with `CONFIG_ARM_TSTEE=y` and `m`, verify `core.o` is included in `arm-tstee.o`, and check that disabling the symbol removes the object from the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Makefile -->
