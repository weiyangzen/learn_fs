# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-mvebu-v7.c

Purpose: provides cpuidle drivers for Marvell Armada XP, Armada 370, and Armada 38x v7 SoCs using a platform-provided suspend callback.

Important APIs and functions: `mvebu_v7_enter_idle()` wraps the suspend callback in `cpu_pm_enter/exit` and `ct_cpuidle_enter/exit`, passes a boolean `deepidle` when the selected state has `MVEBU_V7_FLAG_DEEP_IDLE`, and returns either the error or state index. Probe selects one of three static driver tables through platform-device ID `driver_data` and stores the platform suspend callback.

Control flow and state: global `mvebu_v7_cpu_suspend` points to platform low-level code. Armada XP has WFI, CPU idle, and deep idle; Armada 370 has WFI plus deep idle; Armada 38x has WFI plus idle. State flags include RCU idle and a private deep-idle bit.

Dependencies and integration points: depends on platform devices with IDs `cpuidle-armada-xp`, `cpuidle-armada-370`, or `cpuidle-armada-38x`, valid platform_data callback, ARM CPU PM tracking, and cpuidle core.

Risks and test signals: risks include no validation of the suspend callback, a typo-like driver name `cpuidle-mbevu`, fixed latency/power values, and no runtime unregister path for built-in driver. Test signals include correct platform ID selecting the expected state table, deepidle boolean matching state flags, CPU PM notifiers firing, and suspend callback returning zero for successful idle.
