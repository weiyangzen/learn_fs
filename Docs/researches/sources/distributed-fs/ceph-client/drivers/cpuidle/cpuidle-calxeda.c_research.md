# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-calxeda.c

Purpose: registers Calxeda Highbank cpuidle states for ARM WFI and PSCI-based CPU power gating.

Important APIs and functions: `calxeda_idle_finish()` calls `psci_ops.cpu_suspend()` with a fixed PSCI 0.2 power-down state and `cpu_resume` physical address. `calxeda_pwrdown_idle()` wraps `cpu_suspend()` with `cpu_pm_enter/exit`. The platform driver's probe registers `calxeda_idle_driver`.

Control flow and state: the driver is static and contains WFI plus `PG` power-gate state. No private mutable state is kept.

Dependencies and integration points: depends on PSCI operations being initialized, ARM suspend/resume code, CPU PM notifiers, and a platform device named `cpuidle-calxeda`.

Risks and test signals: risks include no check that `psci_ops.cpu_suspend` is present, fixed PSCI power-state encoding, no unregister path, and minimal error handling from `cpu_suspend()`. Test signals include state 1 invoking PSCI suspend, CPU resume reaching `cpu_resume`, PM notifiers firing, and cpuidle registration only on expected platform devices.
