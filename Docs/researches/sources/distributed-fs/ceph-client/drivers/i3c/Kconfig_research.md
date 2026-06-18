# sources/distributed-fs/ceph-client/drivers/i3c/Kconfig

Purpose: Top-level Kconfig for the Linux I3C subsystem and dependency helper for drivers that can operate over either I2C or I3C.

Important APIs/types/functions: `menuconfig I3C` is a tristate, selects `I2C`, and enables the core module named `i3c`. It sources `drivers/i3c/master/Kconfig` when enabled. `config I3C_OR_I2C` is a tristate helper for drivers using `module_i3c_i2c_driver()`.

Control flow: Build configuration exposes the I3C menu, conditionally includes master-controller options, and sets `I3C_OR_I2C` to module when I3C is modular or to I2C otherwise. There is no runtime flow.

State and persistence: Kconfig state controls whether `device.o`, `master.o`, and selected controller drivers are built in or modular.

Dependencies/integration: Kernel Kconfig, I2C subsystem selection, master-driver Kconfig, and client-driver dependency expressions.

Risks: Dual-protocol drivers need `depends on I2C_OR_I3C` to avoid invalid built-in clients when `CONFIG_I3C=m`. `select I2C` couples I3C enablement to I2C core availability.

Test signals: Build matrix for `I3C=n/m/y`; validate dual I2C/I3C client drivers under modular and built-in combinations.
