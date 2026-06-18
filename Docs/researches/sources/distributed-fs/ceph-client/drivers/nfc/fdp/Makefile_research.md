# sources/distributed-fs/ceph-client/drivers/nfc/fdp/Makefile

Purpose: Provides Kbuild object mapping for the Intel FDP NFC driver family.

Important APIs, types, and functions: `obj-$(CONFIG_NFC_FDP) += fdp.o` builds the core NCI driver, `obj-$(CONFIG_NFC_FDP_I2C) += fdp_i2c.o` builds the transport wrapper, and `fdp_i2c-objs = i2c.o` sets the module object composition.

Control flow: Build-time only; Kbuild turns selected symbols into modules or built-in objects.

State and persistence behavior: No runtime state. The module/object names are the persistent ABI visible to packaging and modprobe users.

Dependencies and integration points: Matches `fdp.c`, `i2c.c`, and the symbols from `fdp/Kconfig`.

Risks: Module name changes would affect userspace autoloading and documentation. Object composition must remain aligned with exported symbols from `fdp.c` consumed by `i2c.c`.

Test signals: Build `fdp.o` alone and with `fdp_i2c.o`, check generated module names, and run modpost for unresolved `fdp_nci_probe`/`fdp_nci_remove` symbols.
