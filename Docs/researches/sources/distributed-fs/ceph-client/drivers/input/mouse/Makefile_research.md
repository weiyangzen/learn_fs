# sources/distributed-fs/ceph-client/drivers/input/mouse/Makefile

## Purpose

This Kbuild file selects and composes Linux input mouse and touchpad drivers under `drivers/input/mouse`. In this subset it is the build integration point for legacy platform mouse drivers (`amimouse.o`, `atarimouse.o`), USB Apple touchpad drivers (`appletouch.o`, `bcm5974.o`), the Cypress APA I2C trackpad aggregate module (`cyapatp.o`), and PS/2 psmouse protocol extensions including ALPS and BYD.

## Important APIs, Types, and Functions

The important interface is Kbuild object composition rather than C APIs. `obj-$(CONFIG_MOUSE_...) += ...` binds each Kconfig option to an object or module. `cyapatp-objs := cyapa.o cyapa_gen3.o cyapa_gen5.o cyapa_gen6.o` composes one module from a bus/core file plus generation-specific protocol files. `psmouse-objs := psmouse-base.o synaptics.o focaltech.o` defines the base PS/2 module, then `psmouse-$(CONFIG_MOUSE_PS2_ALPS) += alps.o` and similar lines add protocol drivers into that same module when enabled.

## Control Flow

Kbuild evaluates the configuration symbols and builds either standalone objects or composite modules. Standalone USB/I2C/platform drivers register through their own module macros. ALPS, BYD, Elantech, TrackPoint, and other PS/2 protocols are linked into `psmouse.o`, so their `*_detect` and `*_init` entry points are called by psmouse core rather than by module init functions in those files.

## State and Persistence Behavior

The file has no runtime state. Its persistent effect is the build-time shape of kernel modules and symbol availability. Changing composite membership changes which protocol handlers are present in `psmouse.o` and therefore changes runtime detection order and exported device support.

## Dependencies and Integration Points

It depends on Kconfig symbols such as `CONFIG_MOUSE_CYAPA`, `CONFIG_MOUSE_PS2_ALPS`, and transport sub-options such as `CONFIG_MOUSE_ELAN_I2C_I2C` and `CONFIG_MOUSE_ELAN_I2C_SMBUS`. It integrates with Linux Kbuild conventions for composite objects and with source files in this directory that assume they are either standalone bus drivers or psmouse protocol plugins.

## Risks and Edge Cases

Composite object ordering matters for duplicate symbols and protocol registration availability. Adding a psmouse protocol as a standalone `obj-*` instead of `psmouse-*` would break its integration model. `cyapatp` requires all generation files to remain listed together because `cyapa.c` dispatches through `cyapa_gen3_ops`, `cyapa_gen5_ops`, and `cyapa_gen6_ops`.

## Test Signals

Useful checks are `make drivers/input/mouse/` with combinations of the relevant `CONFIG_MOUSE_*` options, verifying that `cyapatp` links all generation ops and that `psmouse.o` includes selected protocol objects. Runtime smoke tests should confirm that standalone USB/I2C/platform drivers bind independently while ALPS/BYD bind through psmouse detection.
