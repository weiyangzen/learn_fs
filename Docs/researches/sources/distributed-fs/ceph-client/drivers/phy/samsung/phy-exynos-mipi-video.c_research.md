# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-mipi-video.c

Purpose: Implements MIPI CSI-2/DSI D-PHY power and reset control for S5PV210 and Exynos variants. It exposes multiple PHY instances from a single platform device and maps each phandle index to a CSIS or DSIM PHY.

Important APIs and functions: Device descriptions use `struct mipi_phy_device_desc` and per-PHY `struct exynos_mipi_phy_desc` to identify enable/reset registers, regmaps, reset bits, and coupled PHY relationships. Probe is `exynos_mipi_video_phy_probe()`. OF translation is `exynos_mipi_video_phy_xlate()`. Power operations are `exynos_mipi_video_phy_power_on()`, `exynos_mipi_video_phy_power_off()`, and shared `__set_phy_state()`.

Control flow: Probe obtains the compatible-specific descriptor, resolves one or more syscon regmaps, initializes a spinlock, creates `num_phys` generic PHY objects, and registers a custom xlate provider. Power-on asserts resetn first and then sets the PMU enable bit. Power-off clears resetn and, for coupled CSIS/DSIM pairs, clears PMU enable only when the companion PHY's `power_count` is zero. Different SoCs route reset control through PMU, display sysreg, camera sysreg, or register zero depending on descriptor data.

State and persistence: Runtime state stores regmaps and per-PHY descriptors. Hardware state persists in PMU/sysreg enable and resetn bits. Coupled PHY power state is inferred from the generic PHY `power_count`, so the driver avoids removing shared analog power while a coupled user remains active.

Dependencies and integration points: Depends on generic PHY, syscon/regmap, OF phandle arguments, Samsung PMU register definitions, and spinlocks around multi-register updates. It integrates with Exynos/S5PV210 camera and display drivers needing CSIS/DSIM PHYs by index.

Risks: Coupled PHY accounting relies on generic PHY power counts and descriptor correctness. Some descriptors use reset register zero in non-PMU sysregs, so regmap ordering and naming must match DT exactly. The spinlock protects driver-side sequencing, but regmap backends must be safe for this context. Incorrect xlate indices return the wrong PHY or fail at runtime.

Test signals: Power cycling each CSIS/DSIM index, concurrent coupled CSIS/DSIM use, register traces for PMU and sysreg writes, camera capture and DSI display output, invalid phandle index handling, and suspend/resume across active video pipelines.
