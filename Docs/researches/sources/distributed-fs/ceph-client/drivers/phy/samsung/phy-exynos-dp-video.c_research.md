# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-dp-video.c

Purpose: Provides a small generic PHY provider for Exynos DisplayPort video PHY isolation control. It supports Exynos5250 and Exynos5420 PMU control offsets.

Important APIs and functions: `exynos_dp_video_phy_probe()` resolves the PMU regmap, creates one generic PHY, and registers an OF PHY provider. PHY operations are `exynos_dp_video_phy_power_on()` and `exynos_dp_video_phy_power_off()`, which set or clear `EXYNOS4_PHY_ENABLE` at a compatible-specific PMU offset. Match data is `struct exynos_dp_video_phy_drvdata`.

Control flow: Probe first tries the parent syscon regmap for backward-compatible DT layout, then falls back to `samsung,pmu-syscon`. Power-on disables isolation by writing the enable bit; power-off enables isolation by clearing it.

State and persistence: The only runtime state is `struct exynos_dp_video_phy` containing the PMU regmap and selected offset data. Hardware state persists as the PMU isolation bit until changed by this driver or firmware.

Dependencies and integration points: Depends on generic PHY, syscon/regmap, OF match data, platform devices, and `exynos-regs-pmu.h`. It is consumed by Exynos DisplayPort controller nodes through standard PHY phandles.

Risks: Parent syscon fallback and phandle lookup must match board DT. A wrong PMU offset can isolate the wrong PHY. There is no clock/reset sequencing here, so it assumes the DP controller or platform firmware handles the rest of the PHY bring-up.

Test signals: Probe success for both compatibles, PMU bit changes during DP enable/disable, DisplayPort link training/display output, suspend/resume display recovery, and no regressions for legacy DTs using parent syscon lookup.
