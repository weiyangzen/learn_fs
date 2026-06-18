# sources/distributed-fs/ceph-client/drivers/media/pci/pluto2/Kconfig

Purpose: Defines the `DVB_PLUTO2` build option for Pluto2 FPGA-based PCI DVB-T cards such as the Satelco Easywatch Mobile Terrestrial receiver.

Important APIs, types, and functions: `config DVB_PLUTO2` is a tristate depending on `DVB_CORE`, `PCI`, and `I2C`. It selects `I2C_ALGOBIT` and `DVB_TDA1004X`.

Control flow: Build-time only. Enabling the option builds `pluto2.o` through the local Makefile and makes the driver available as built-in or module.

State and persistence: No runtime state. Kernel configuration controls whether the driver is compiled.

Dependencies and integration points: The selected dependencies match `pluto2.c`, which uses a bit-banged I2C adapter and the TDA10046 frontend driver.

Risks: The tuner is programmed directly in `pluto2.c` rather than through a separate selected tuner module, so Kconfig dependency coverage is small. Users still need appropriate TDA10046 firmware at runtime if the frontend requests it.

Test signals: Confirm valid module/built-in builds, impossible configs without PCI/I2C/DVB core are rejected, and enabling `DVB_PLUTO2` pulls in `I2C_ALGOBIT` and `DVB_TDA1004X`.
