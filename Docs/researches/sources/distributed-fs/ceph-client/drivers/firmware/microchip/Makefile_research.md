# sources/distributed-fs/ceph-client/drivers/firmware/microchip/Makefile

Purpose: Builds the Microchip PolarFire SoC Auto Update driver.

Important APIs/types/functions: `obj-$(CONFIG_POLARFIRE_SOC_AUTO_UPDATE) += mpfs-auto-update.o`.

Control flow: No runtime flow. Kbuild includes the object according to the Kconfig setting.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with Microchip firmware Kconfig and the platform firmware build.

Risks and test signals: Build-only risk; test module and built-in configurations.
