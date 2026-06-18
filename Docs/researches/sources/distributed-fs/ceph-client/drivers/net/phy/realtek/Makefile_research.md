# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Makefile

Purpose: Builds the Realtek PHY driver as a composite kbuild object with optional hwmon support.

Important entries: `realtek-y += realtek_main.o` always includes the main driver when `REALTEK_PHY` is enabled. `realtek-$(CONFIG_REALTEK_PHY_HWMON) += realtek_hwmon.o` conditionally includes temperature sensor support. `obj-$(CONFIG_REALTEK_PHY) += realtek.o` exposes the final built-in or module object.

Control flow: kbuild combines the listed objects into `realtek.o` according to Kconfig values. Runtime behavior is determined by which object files are linked.

State and persistence: No runtime state. This file persists build composition metadata.

Dependencies and integration: Integrates with `realtek/Kconfig`, `realtek_main.c`, and `realtek_hwmon.c`. Optional hwmon code is linked into the same driver object rather than a separate module.

Risks and test signals: Risks are object name drift, optional hwmon code not being linked when enabled, or unresolved `rtl822x_hwmon_init()` calls if Kconfig/Makefile diverge. Test Realtek built-in and module builds with hwmon on and off.
