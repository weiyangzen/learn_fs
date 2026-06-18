# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/Kconfig

Purpose: Defines Realtek PHY driver build options, including optional hardware-monitoring support for temperature sensors on supported RTL822x devices.

Important options: `REALTEK_PHY` is the main tristate for RTL821x/RTL822x and fast Ethernet PHY support and selects `PHY_PACKAGE`. `REALTEK_PHY_HWMON` is a bool nested under `REALTEK_PHY`, depends on `HWMON`, and prevents the illegal combination where the Realtek driver is built in while hwmon is modular.

Control flow: This file has build-time control only. The nested `if REALTEK_PHY` makes the hwmon option available only when the Realtek driver is enabled.

State and persistence: State is Kconfig selection state only. The hwmon bool determines whether `realtek_hwmon.o` is included in the composite Realtek object.

Dependencies and integration: Integrates with the Realtek Makefile, phylib package support, and the hwmon subsystem. The dependency `!(REALTEK_PHY=y && HWMON=m)` protects built-in code from depending on modular hwmon symbols.

Risks and test signals: Risks are dependency drift with hwmon or package APIs and missed build combinations. Test `REALTEK_PHY` as disabled, module, and built-in; test hwmon enabled/disabled; and verify the forbidden built-in/module mix is rejected.
