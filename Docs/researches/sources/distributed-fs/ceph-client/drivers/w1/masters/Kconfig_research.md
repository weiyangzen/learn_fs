## sources/distributed-fs/ceph-client/drivers/w1/masters/Kconfig

Purpose: this Kconfig menu defines selectable 1-Wire bus master drivers across platform, PCI, USB, I2C, GPIO, OMAP HDQ, SGI ASIC, and UART transports.

Important APIs/types/functions: symbols include `W1_MASTER_AMD_AXI`, `W1_MASTER_MATROX`, `W1_MASTER_DS2490`, `W1_MASTER_DS2482`, `W1_MASTER_MXC`, `W1_MASTER_GPIO`, `HDQ_MASTER_OMAP`, `W1_MASTER_SGI`, and `W1_MASTER_UART`.

Control flow: each symbol controls one object in the masters Makefile. Dependencies constrain selection to relevant subsystems, for example PCI for Matrox, USB for DS2490, I2C for DS2482, GPIOLIB for GPIO, SERIAL_DEV_BUS for UART, and architecture or `COMPILE_TEST` coverage for MXC/OMAP.

State and persistence behavior: no runtime state. Build-time choices determine which hardware adapters can register `struct w1_bus_master` instances.

Dependencies and integration points: integrates with platform drivers, subsystem buses, and the top-level w1 menu.

Risks: some help text contains legacy hardware names and limited detail about required device tree or board data. Build exposure through `COMPILE_TEST` helps compile coverage but cannot validate timing-sensitive 1-Wire bus behavior.

Test signals: Kconfig dependency checks for each transport and compile-test coverage for platform drivers on non-native architectures.
