# sources/distributed-fs/ceph-client/drivers/net/phy/realtek/realtek.h

Purpose: Provides the local Realtek PHY driver header used to share the hwmon initialization prototype with the main driver.

Important APIs and types: Includes `<linux/phy.h>` and declares `int rtl822x_hwmon_init(struct phy_device *phydev);`. Header guards prevent duplicate inclusion.

Control flow: No executable control flow.

State and persistence: No state is defined. The declaration allows caller-owned `struct phy_device` state to be passed into the hwmon registration helper.

Dependencies and integration: Integrates `realtek_main.c` with `realtek_hwmon.c` when `CONFIG_REALTEK_PHY_HWMON` links the optional object. It depends on phylib type definitions.

Risks and test signals: Risks are prototype drift and missing stubs if the main driver calls the function while hwmon support is not linked. Test all Realtek hwmon build combinations and compile checks for the shared prototype.
