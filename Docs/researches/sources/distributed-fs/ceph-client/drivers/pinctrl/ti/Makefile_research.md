# sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Makefile

## Purpose

This Makefile connects the `PINCTRL_TI_IODELAY` Kconfig symbol to the TI IO delay driver object. It is the build-system glue for the `drivers/pinctrl/ti` subdirectory.

## Important APIs, Types, and Functions

The only build rule is `obj-$(CONFIG_PINCTRL_TI_IODELAY) += pinctrl-ti-iodelay.o`. There are no C APIs, types, or functions in this file. The rule means built-in configuration produces a built-in object, module configuration produces a module object, and disabled configuration omits the driver.

## Control Flow

Kbuild expands `obj-y` or `obj-m` according to `CONFIG_PINCTRL_TI_IODELAY`. The compiled source is `pinctrl-ti-iodelay.c`, producing `pinctrl-ti-iodelay.o` and, for module builds, the corresponding loadable module.

## State and Persistence

Persistent effects are build artifacts under the kernel output tree. There is no runtime state.

## Dependencies and Integration Points

The rule depends on `drivers/pinctrl/ti/Kconfig` defining `PINCTRL_TI_IODELAY` and on the C source file having the expected basename. It integrates with top-level Kbuild traversal into the TI pinctrl directory.

## Risks

The risk surface is small: a symbol typo would prevent the driver from building, and an object-name typo would fail the build or silently omit the intended source. Because there is only one rule, any future TI pinctrl driver added to this directory must update both Kconfig and this Makefile.

## Test Signals

Build with `CONFIG_PINCTRL_TI_IODELAY=y` and verify `pinctrl-ti-iodelay.o` is linked into vmlinux. Build with `CONFIG_PINCTRL_TI_IODELAY=m` and verify a module is produced. Build with the symbol unset and verify no TI IO delay object is compiled.
