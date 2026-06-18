# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-at91.c

Purpose: registers AT91 ARM cpuidle states for simple WFI and WFI plus RAM self-refresh.

Important APIs and functions: `at91_cpuidle_probe()` stores a platform-data standby callback in `at91_standby` and registers `at91_idle_driver`. `at91_enter_idle()` invokes that standby callback and returns the selected index. State 0 uses `ARM_CPUIDLE_WFI_STATE`; state 1 is named `RAM_SR` with 10 us exit latency and 10000 us target residency.

Control flow and state: global state is the function pointer supplied by platform data. There is no remove path because the driver is built-in. The second state delegates all hardware sequencing to the platform callback.

Dependencies and integration points: depends on an AT91 platform device named `cpuidle-at91`, valid platform data, ARM cpuidle helpers, and cpuidle core registration.

Risks and test signals: risks include no NULL check for `at91_standby`, no DT parsing in this file, fixed latency/residency values, and no unregister path. Test signals include platform callback invocation on state 1, WFI state availability, DDR self-refresh observed in platform power registers, and no crash when the platform device binds.
