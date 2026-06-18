# sources/distributed-fs/ceph-client/drivers/devfreq/Kconfig

Purpose: Kconfig menu for the Linux devfreq framework, governors, and several platform devfreq drivers.

Important APIs/types/functions: `PM_DEVFREQ`, governor symbols for simple-ondemand, performance, powersave, userspace, passive, and platform driver symbols such as Exynos bus, HiSilicon uncore, i.MX bus/DDRC, Tegra, MediaTek CCI, Rockchip DMC, Sunxi MBUS, plus inclusion of `drivers/devfreq/event/Kconfig`.

Control flow and state: enabling `PM_DEVFREQ` selects OPP and opens governor/driver menus. Governors are separate tristates; platform drivers select required governors and event frameworks. Help text documents the devfreq model: one representative device frequency, optional OPP notifier use, and driver-supplied target callbacks.

Dependencies and integration: integrates with OPP, PM_DEVFREQ_EVENT, architecture/platform symbols, ACPI/PPTT/PCC, common clock, SMCCC, and devfreq event devices.

Risks and test signals: dependency mistakes can overbuild platform drivers or miss governor/event requirements. Test Kconfig combinations for each platform, governor module builds, event Kconfig inclusion, COMPILE_TEST paths, and OPP/devfreq core availability.
