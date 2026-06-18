# sources/distributed-fs/ceph-client/include/linux/soc/samsung/exynos-regs-pmu.h

Purpose: This large Samsung header is a shared register-offset catalog for Exynos and Tensor GS101 PMU blocks used by power, reset, retention, PHY, wakeup, and low-power code.

Important APIs/types/functions: It defines central sequence, wake mask/stat, MIPI/USB/DP PHY control, inform/spare registers, CPU/core/L2/common power registers, low-power clock/reset/retention registers, pad retention options, PS_HOLD, local power bits, Exynos3/4/5/5420/5433/7870/990/2200/autov920-specific offsets, and extensive GS101 ALIVE/cluster/subblock/system/interrupt/PHY/PMLINK/HCU register offsets and helper macros.

Control flow: Exynos PM, clock, reset, PHY, and SoC drivers include this header to program PMU registers during boot, suspend entry/exit, CPU hotplug, PHY power, wake-mask setup, and shutdown/reboot.

State and persistence: PMU registers directly control retention, power gating, wake status, boot inform values, reset cause, and PHY enables. Some fields survive low-power modes and are used during resume.

Dependencies and integration: Uses `BIT` style masks and integrates with Exynos PMU regmap users, Samsung clock/reset/PHY drivers, CPU hotplug, and Tensor GS101 platform code.

Risks and test signals: Offset mistakes can write unrelated PMU registers, causing failed suspend, broken wake, or power loss. Test suspend/resume, CPU hotplug, wake masks, PHY enable/disable, reset reason, and SoC-specific register subsets.
