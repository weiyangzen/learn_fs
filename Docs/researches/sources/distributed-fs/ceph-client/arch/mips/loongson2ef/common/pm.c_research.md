<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pm.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pm.c

Purpose: Implements generic Loongson2EF suspend support and interrupt masking around wait-mode sleep.

Important APIs/types/functions: `arch_suspend_disable_irqs()`, `arch_suspend_enable_irqs()`, weak `setup_wakeup_events()`, weak `wakeup_loongson()`, weak `mach_suspend()`/`mach_resume()`, and `loongson_pm_ops`.

Control flow: Suspend masks local, i8259, and Bonito interrupts, lets board code enable wake sources, stops Loongson perf counters, clears CPU frequency bits to enter wait mode, polls board wakeup logic, restores chip config, and runs board resume hooks.

State and persistence: Caches PIC and Bonito masks and the chip configuration register across suspend. Registers platform suspend operations at arch init.

Dependencies and integration: Board-specific Lemote PM overrides wakeup and MFGPT handling. Uses `LOONGSON_CHIPCFG`, i8259 IO ports, and Linux suspend core.

Risks: Polling wake events can loop forever if board wake detection is broken. Interrupt mask restore ordering may lose wake events if hardware status is not latched.

Test signals: `PM_SUSPEND_MEM` and standby should enter/leave wait mode, wake only on configured events, and restore timer/peripheral interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pm.c -->
