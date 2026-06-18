## sources/distributed-fs/ceph-client/drivers/w1/Kconfig

Purpose: this Kconfig file gates the Dallas/Maxim 1-Wire subsystem and its userspace connector option.

Important APIs/types/functions: it defines `menuconfig W1` as a tristate depending on `HAS_IOMEM`, and `config W1_CON` as an optional connector-backed userspace communication path depending on `CONNECTOR` and defaulting to enabled.

Control flow: enabling `W1` opens the menu and sources `drivers/w1/masters/Kconfig` and `drivers/w1/slaves/Kconfig`, so bus master and slave family drivers are only visible when core 1-Wire support is selected.

State and persistence behavior: no runtime state. Build-time selections determine whether `wire.o`, master drivers, slave drivers, and connector support are compiled.

Dependencies and integration points: integrates with kernel Kconfig and the w1 core Makefile. `W1_CON` aligns with `w1_netlink.c` and connector documentation.

Risks: `HAS_IOMEM` excludes systems without MMIO support even though some masters are USB/I2C; this is a broad subsystem-level dependency. Connector defaults to yes when possible, increasing default surface area.

Test signals: Kconfig matrix with `W1=y/m/n`, `CONNECTOR=y/n`, and representative master/slave selections.
