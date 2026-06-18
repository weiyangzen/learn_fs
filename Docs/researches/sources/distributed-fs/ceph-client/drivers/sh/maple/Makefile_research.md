# sources/distributed-fs/ceph-client/drivers/sh/maple/Makefile

Purpose: Kbuild file for the Dreamcast Maple bus core.

Important build rule: `obj-$(CONFIG_MAPLE) := maple.o`, so the Maple bus implementation is built only when `CONFIG_MAPLE` is enabled.

Control flow and integration: the parent SH Makefile descends into this directory for `CONFIG_MAPLE`, and this Makefile contributes the bus core object. Runtime behavior is in `maple.c`.

State and dependencies: no runtime state. Dependencies include the `CONFIG_MAPLE` symbol and Kbuild. Risks are minimal; the main risk is missing this object when Dreamcast Maple drivers depend on exported bus APIs. Test signals are successful link of Maple client drivers and presence of `maple_driver_register` when `CONFIG_MAPLE=y/m`.
