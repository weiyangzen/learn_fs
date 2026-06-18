# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-kirkwood.c

Purpose: registers Marvell Kirkwood cpuidle states for WFI and WFI with DDR self-refresh.

Important APIs and functions: probe maps the DDR operation register resource into `ddr_operation_base` and registers `kirkwood_idle_driver`. `kirkwood_enter_idle()` writes `0x7` to the DDR operation register, executes `cpu_do_idle()`, and returns the selected index. Remove unregisters the driver.

Control flow and state: global state is the devm-managed DDR operation MMIO pointer. The driver exposes state 0 WFI and state 1 `DDR SR` with 10 us latency and 100000 us target residency.

Dependencies and integration points: depends on a platform device named `kirkwood_cpuidle`, ARM cpuidle helpers, and the SoC DDR self-refresh register semantics.

Risks and test signals: risks include global MMIO pointer, fixed magic value `0x7`, long target residency assumptions, and no CPU PM notifier wrapping. Test signals include successful resource map, DDR self-refresh request before WFI, wakeup from interrupts, and unregister on module/platform removal.
